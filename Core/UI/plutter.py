import ast
from datetime import datetime
import threading
import time
from pytz import utc
import paho.mqtt.client as mqtt
from Config.Data.hardcoded_tele_templates import HardcodedTeleKeys
from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.brokers_and_topics import MqttTopics
from Core.authentication.authenticator import Authenticator

class MqttService:
    def __init__(self, broker_address="localhost", port=1883, client = None, orgId="NONE",allTopics=MqttTopics.getAllTopicSets(),allTopicsTele=MqttTopics.getTeleTopics(),allTopicsUI=MqttTopics.getUiTopics(),automation=None):
        self.broker_address = broker_address
        self.port = port
        self.allTopics = allTopics
        self.allTopicsTele=allTopicsTele
        self.allTopicsUI=allTopicsUI
        self.temp = 0
        self.IR = []
        
        self.script = ""
        self.parsedProcedure = None
        
        self.formPanelData={}

        self.client = client if client else (mqtt.Client(client_id="PlutterPy", clean_session=True, userdata=None, protocol=mqtt.MQTTv311))
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.on_subscribe = self.onSubscribe
        #self.client.on_publish=self.onPublish
        
        self.topicIDs={}

        self.saidItOnce=False
        self.isSubscribed = {}

        self.lastMsgFromTopic={}
        self.dataQueue=DataSetFDD([])
        self.logData=False
        self.lastReceivedTime={}
        self.minTeleInterval=0.5
        
        self.orgId=orgId
        
        self.automation=automation if automation else (FlowChemAutomation())
        
        #Authentication
        self.authenticator=Authenticator()
        
        self.zeroTime=None
        
        self.databaseOperations=None
        
        #TODO - random test related var
        self.runTest=False
        self.currTestlistId=None
        self.currTestrunId=None
        self.abort=False
        
        #TODO - Temp fix for repeated connecting
        #self.connected=False
        
        #Telemetry
        self.registeredTeleDevices={}
        
        #self.dbInstructions={"createStdExp":DatabaseOperations.createStdExp}

    def onSubscribe(self, client, userdata, mid, granted_qos):
        if mid in self.topicIDs:
            print("WJ - Subscribed to topic " + self.topicIDs[mid] + " with Qos " + str(granted_qos[0]) + "!")
    
    def onConnect(self, client, userdata, flags, rc):
        print("WJ - Connected!")
        #if self.connected:
            #return
        if rc == 0:
            for _x in self.allTopics:
                for tpc in _x.values():
                    qos=MqttTopics.getTopicQos(tpc)
                    ret=self.client.subscribe(tpc,qos=qos)
                    if ret[0].real==0:
                        self.topicIDs[ret[1]]=tpc
                    else:
                        print("WJ - could not subscribe to topic "+tpc+"!")
            self.connected=True
        else:
            print("Connection failed with error code " + str(rc))
        print(self.topicIDs)
    
    def onConnectTele(self, client, userdata, flags, rc):
        print("WJ - Connected!")
        if rc == 0:
            for tpc in self.allTopicsTele.values():
                ret=self.client.subscribe(tpc)
                if ret[0].real==0:
                    self.topicIDs[ret[1]]=tpc
                else:
                    print("WJ - could not subscribe to topic "+tpc+"!")
            for tpc in self.allTopicsUI.values():
                ret=self.client.subscribe(tpc,qos=2)
                if ret[0].real==0:
                    self.topicIDs[ret[1]]=tpc
                else:
                    print("WJ - could not subscribe to topic "+tpc+"!")
            #Test settings
            tpc="test/settings"
            ret=self.client.subscribe(topic="test/settings",qos=2)
            if ret[0].real==0:
                self.topicIDs[ret[1]]=tpc
            #
        else:
            print("Connection failed with error code " + str(rc))

    def onMessage(self, client, userdata, msg):
        _msgContents = msg.payload.decode()
        topic=msg.topic
        _msgContents = _msgContents.replace("true", "True").replace("false", "False")
        _msgContents=_msgContents.replace("null","None")
        _msgContents = ast.literal_eval(_msgContents)
        self.lastMsgFromTopic[topic]=_msgContents
        ##
        if "deviceName" in _msgContents:
            #Add to db streaming queue? Minimum wait passed?
            if self.runTest:
                if (self.currTestlistId != None  and self.currTestrunId != None and self.logData):
                    if "tele" in _msgContents:
                        if not _msgContents["deviceName"] in self.lastReceivedTime:
                            self.lastReceivedTime[_msgContents["deviceName"]]=time.perf_counter()
                        else:
                            if time.perf_counter() - self.lastReceivedTime[_msgContents["deviceName"]] < self.minTeleInterval:
                                return #TODO - make sure it's fine to jump ship here
                            else:
                                if not _msgContents["deviceName"] in self.registeredTeleDevices:
                                    self.registeredTeleDevices[_msgContents["deviceName"]]=HardcodedTeleKeys.devicesAndTheirTele[_msgContents["deviceName"]]
                                    self.databaseOperations.registerAvailableTele(testrunId=self.currTestrunId,device=_msgContents["deviceName"],setting=self.registeredTeleDevices[_msgContents["deviceName"]])
                                    print('WJ - Adding tele source "' + _msgContents["deviceName"] + '"!')
                                #print(f'Adding tele datapoint for {_msgContents["deviceName"]}!')
                                self.dataQueue.addDataPoint(
                                    DataPointFDE(
                                        testlistId=self.currTestlistId,
                                        testrunId=self.currTestrunId,
                                        data=_msgContents,
                                        timestamp=datetime.now(utc)
                                    )
                                )
                    else:
                        if not _msgContents["deviceName"] in self.registeredTeleDevices:
                            self.registeredTeleDevices[_msgContents["deviceName"]]=HardcodedTeleKeys.devicesAndTheirTele[_msgContents["deviceName"]]
                            self.databaseOperations.registerAvailableTele(testrunId=self.currTestrunId,device=_msgContents["deviceName"],setting=self.registeredTeleDevices[_msgContents["deviceName"]])
                        #print(f'Adding command datapoint for {_msgContents["deviceName"]}!')
                        self.dataQueue.addDataPoint(
                            DataPointFDE(
                                testlistId=self.currTestlistId,
                                testrunId=self.currTestrunId,
                                data=_msgContents,
                                timestamp=datetime.now(utc)
                            )
                        )                    
                        
        elif "script" in _msgContents:
            _msgContents=_msgContents["script"]
            print('############')
            print('############')
            print("WJ - Script message contents: "+str(_msgContents))
            print('############')
            self.script=self.automation.parsePlutterIn(_msgContents)
            print("WJ - Parsed script: "+str(self.script))
            print('############')
            print('############')
        ##
        elif "FormPanelWidget" in _msgContents:
            _msgContents=_msgContents["FormPanelWidget"]
            self.formPanelData=_msgContents
            print(f"WJ - Received FormPanelData: {_msgContents}")
        ##
        elif "LoginPageWidget" in _msgContents:
            _msgContents=_msgContents["LoginPageWidget"]
            if ("password" in _msgContents):
                print(f'WJ - Login page details: {_msgContents}')
                self.authenticator.signIn(orgId=_msgContents["orgId"],password=_msgContents["password"])
            else:
                print(_msgContents)
        ##
        elif topic=="ui/dbCmnd/in":
            _msgContents=_msgContents["instructions"]
            _func=_msgContents["function"]
            _params=_msgContents["params"]

            if (_func=="getAllExpWidgetInfo"):
                self.client.publish(
                    "ui/dbCmnd/ret",
                    self.databaseOperations.getAllExpWidgetInfo(
                        orgId=self.authenticator.user.orgId
                    )
                )
            elif (_func=="createReplicate"):
                self.databaseOperations.createReplicate(
                    labNotebookBaseRef=_params["labNotebookBaseRef"],
                    testScript=_params["testScript"],
                    flowScript=_params["flowScript"],
                    notes=_params["notes"]
                )
                self.client.publish(
                    "ui/dbCmnd/ret",
                    self.databaseOperations.getAllExpWidgetInfo(
                        orgId=self.authenticator.user.orgId
                    )
                )
            elif (_func=="handleStreamRequest"):
                if not self.databaseOperations.mongoDb.currZeroTime:
                    self.databaseOperations.mongoDb.currZeroTime=datetime.now()
                self.client.publish(
                    "ui/dbCmnd/ret",
                    self.databaseOperations.handleStreamRequest(
                        _params
                    )
                )
            elif (_func=="updateTestrunDetails"):
                self.currTestlistId=_params["testlistId"]
                self.currTestrunId=_params["testrunId"]
                self.currLabNotebookBaseRef=_params["labNotebookBaseRef"]
                print(f'WJ - Set testrun to {self.currTestrunId} for testlist entry {self.currTestlistId}')
            elif (_func=="enableLogging"):
                self.logData=True
                print(f'WJ - Streaming to db enabled')
            elif (_func=="disableLogging"):
                self.logData=False
                print(f'WJ - Streaming to db disabled')
            elif (_func=="abort"):
                self.databaseOperations.mongoDb.currZeroTime=None
                if not self.abort:
                    self.abort=True
                    print(f'WJ - Aborting run!')
            elif (_func=="goCommand"):
                if self.abort:
                    self.abort=False
                self.runTest=True
                print("WJ - Let's go!")
                                    
    def start(self):
        self.authenticator.initPlutter(mqttService=self)
        self.client.connect(self.broker_address, self.port)
        self.databaseOperations=DatabaseStreamer(mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mySqlDb=MySQLDatabase(host='146.64.91.174'),mqttService=self)
        self.databaseOperations.connect()
        thread = threading.Thread(target=self._run)
        thread.start()
        return thread

    def _run(self):
        self.client.loop_start()
        
    def publish(self,topic,payload):
        _ret=self.client.publish(topic,payload)
        print(f'MQTT message info: {_ret}')

    def getTemp(self):
        return self.temp
    def getIR(self):
        return self.IR
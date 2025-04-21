import ast
from datetime import datetime
import json
import threading
import time
import uuid
from pytz import utc
import paho.mqtt.client as mqtt
from Config.Data.hardcoded_tele_templates import HardcodedTeleKeys
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder
from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.Fluids.FlowPath import FlowSystem
from Core.UI.brokers_and_topics import MqttTopics
from Core.authentication.authenticator import Authenticator

class MqttService:
    def __init__(self, broker_address="localhost", port=1883, client = None, orgId="NONE",allTopics=MqttTopics.getAllTopicSets(),allTopicsTele=MqttTopics.getTeleTopics(),allTopicsUI=MqttTopics.getUiTopics(),allTopicsOptimization=MqttTopics.getOptimizationTopics(),automation=None):
        self.broker_address = broker_address
        self.port = port
        self.allTopics = allTopics
        self.allTopicsTele=allTopicsTele
        self.allTopicsUI=allTopicsUI
        self.allTopicsOptimization=allTopicsOptimization
        self.temp = 0
        self.IR = []
        
        #Script handling
        self.currKwargs = {
            "conditionFunc": None,
            "conditionParam": None
        }
        self.script = ""
        self.parsedProcedure = None
        self.fdpDecoder=FdpDecoder(currKwargs=self.currKwargs)
        
        self.formPanelData={}

        self.client = client if client else (mqtt.Client(client_id=f"PlutterPy_{uuid.uuid4()}", clean_session=True, userdata=None, protocol=mqtt.MQTTv311))
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.on_subscribe = self.onSubscribe
        self.client.on_disconnect=self.onDisconnect
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
        self.connectDb=True
        
        #TODO - random test related var
        self.runTest=False
        self.currTestlistId=None
        self.currTestrunId=None
        self.abort=False
        
        self.armed=False
        
        #TODO - Temp fix for repeated subscription
        #self.connected=False
        self.subscribed={}
        
        #Telemetry
        self.registeredTeleDevices={}
        
        self.irAvailable=False
        
        self.optimizationReqSettings={}
        self.reqOptimization=False
        self.flowSystem=FlowSystem()
        self.flowSystem.flowpath.mqttService=self
        
        self.uiPingInt=30
        self.lastUiPing=-1
        
        self.reqUIhandlers={
            "FlowSketcher":{
                "parseFlowsketch":self.flowSystem.flowpath.parseFlowSketch
            }
        }
        
        #self.dbInstructions={"createStdExp":DatabaseOperations.createStdExp}
        
        self.connected=False
        
        self.pingThread=None

    def onSubscribe(self, client, userdata, mid, granted_qos):
        if mid in self.topicIDs:
            print("WJ - Subscribed to topic " + self.topicIDs[mid] + " with Qos " + str(granted_qos[0]) + "!")
    
    def onDisconnect(self, client, userdata, rc):
        print(f"Disconnected! {[client,userdata,rc]}")
        self.client.connect(self.broker_address, self.port)
        
    def onConnect(self, client, userdata, flags, rc):
        #if self.connected:
            #return
        # print("WJ - Connected!")
        if rc == 0:
            for _x in self.allTopics:
                for tpc in _x.values():
                    if tpc in self.subscribed:
                        if self.subscribed[tpc]:
                            continue
                    qos=MqttTopics.getTopicQos(tpc)
                    ret=self.client.subscribe(tpc,qos=qos)
                    if ret[0].real==0:
                        self.topicIDs[ret[1]]=tpc
                        self.subscribed[tpc]=True
                    else:
                        print("WJ - could not subscribe to topic "+tpc+"!")
            self.connected=True
        else:
            print("Connection failed with error code " + str(rc))
            self.connected=False
        # print(self.topicIDs)
    
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
        '''
        TODO - To be refactored with "request" format - self.requestHandlers={} will have pointers to functions handling incoming messages
        eg. {"deviceName":...} becomes {"req":{"deviceAdj":{"deviceName":...}}} with self.requestHandlers={"deviceAdj":_funcPointer}
        '''
        msgContents, topic = self._receive(msg)
        
        ##
        if "reqUI" in msgContents:
            self._routeMsg(msgContents["reqUI"])
        ##
        elif "pingUI" in msgContents:
            self.lastUiPing=time.time()
        ##
        elif "deviceName" in msgContents:
            if msgContents["deviceName"] == "reactIR702L1":
                self.IR = msgContents["tele"]["state"]["data"]
                self.irAvailable=True
            #Add to db streaming queue? Minimum wait passed?
            if self.runTest:
                if (self.currTestlistId != None  and self.currTestrunId != None and self.logData):
                    if "tele" in msgContents:
                        if not msgContents["deviceName"] in self.lastReceivedTime:
                            self.lastReceivedTime[msgContents["deviceName"]]=time.perf_counter()
                        else:
                            if time.perf_counter() - self.lastReceivedTime[msgContents["deviceName"]] < self.minTeleInterval:
                                return #TODO - make sure it's fine to jump ship here
                            else:
                                if not msgContents["deviceName"] in self.registeredTeleDevices:
                                    self.registeredTeleDevices[msgContents["deviceName"]]=HardcodedTeleKeys.devicesAndTheirTele[msgContents["deviceName"]]
                                    self.databaseOperations.registerAvailableTele(testrunId=self.currTestrunId,device=msgContents["deviceName"],setting=self.registeredTeleDevices[msgContents["deviceName"]])
                                    print('WJ - Adding tele source "' + msgContents["deviceName"] + '"!')
                                #print(f'Adding tele datapoint for {msgContents["deviceName"]}!')
                                self.dataQueue.addDataPoint(
                                    DataPointFDE(
                                        testlistId=self.currTestlistId,
                                        testrunId=self.currTestrunId,
                                        data=msgContents,
                                        timestamp=datetime.now(utc)
                                    )
                                )
                    else:
                        if not msgContents["deviceName"] in self.registeredTeleDevices:
                            self.registeredTeleDevices[msgContents["deviceName"]]=HardcodedTeleKeys.devicesAndTheirTele[msgContents["deviceName"]]
                            self.databaseOperations.registerAvailableTele(testrunId=self.currTestrunId,device=msgContents["deviceName"],setting=self.registeredTeleDevices[msgContents["deviceName"]])
                        #print(f'Adding command datapoint for {msgContents["deviceName"]}!')
                        self.dataQueue.addDataPoint(
                            DataPointFDE(
                                testlistId=self.currTestlistId,
                                testrunId=self.currTestrunId,
                                data=msgContents,
                                timestamp=datetime.now(utc)
                            )
                        )                    
                        
        elif "script" in msgContents:
            print("Plutter received script.")
            msgContents=msgContents["script"]
            self.script=self.automation.parsePlutterIn(msgContents)
        ##
        elif "FormPanelWidget" in msgContents:
            msgContents=msgContents["FormPanelWidget"]
            self.formPanelData=msgContents
            print(f"WJ - Received FormPanelData: {msgContents}")
        ##
        elif "FormPanelWidget" in msgContents:
            msgContents=msgContents["FormPanelWidget"]
            self.formPanelData=msgContents
            print(f"WJ - Received FormPanelData: {msgContents}")
        ##
        elif "LoginPageWidget" in msgContents:
            msgContents=msgContents["LoginPageWidget"]
            if ("password" in msgContents):
                print(f'WJ - Login page details: {msgContents}')
                self.authenticator.signIn(orgId=msgContents["orgId"],password=msgContents["password"])
            else:
                print(msgContents)
        ##
        elif topic=="ui/dbCmnd/in":
            msgContents=msgContents["instructions"]
            _func=msgContents["function"]
            _params=msgContents["params"]

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
                if not self.reqOptimization:
                    self.reqOptimization=False
                if not self.abort:
                    self.abort=True
                    print(f'WJ - Aborting run!')
            elif (_func=="goCommand"):
                if self.abort:
                    self.abort=False
                self.runTest=True
                print("WJ - Let's go!")
        elif topic==MqttTopics.getUiTopic("optIn"):
            self.optimizationReqSettings=msgContents["optInstructUI"]
            self.reqOptimization=True
        
    def start(self):
        self.authenticator.initPlutter(mqttService=self)
        self.client.connect(self.broker_address, self.port)
        if self.connectDb:
            self.databaseOperations=DatabaseStreamer(mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mySqlDb=MySQLDatabase(host='146.64.91.174'),mqttService=self)
            self.databaseOperations.connect()
        self._startPingUiLoop()
        thread = threading.Thread(target=self._run)
        thread.start()
        return thread

    def arm(self):
        if not self.armed:
            self.armed=True

    def disarm(self):
        if self.armed:
            self.armed=False

    def _run(self):
        self.client.loop_start()
    
    def _receive(self,msg):
        topic=msg.topic
        msg=msg.payload.decode()
        msg = msg.replace("true", "True").replace("false", "False")
        msg=msg.replace("null","None")
        msg = ast.literal_eval(msg)
        self.lastMsgFromTopic[topic]=msg
        return msg, topic
    
    def _routeMsg(self,msg):
        key=list(msg.keys())
        if len(key) != 1:
            return None
        key=key[0]
        action=list(msg[key].keys())
        if len(action) != 1:
            return None
        action=action[0]
        func=self.reqUIhandlers[key][action]
        return func(msg[key][action])

    def publish(self,topic,payload):
        if not self.armed:
            pass
        else:
            _ret=self.client.publish(topic,payload)
            print(f'MQTT message info: {_ret}')

    def _startPingUiLoop(self):
        self.pingThread=threading.Thread(target=self._pingUiLoop)
        self.pingThread.start()

    def _pingUiLoop(self):
        while not self.connected:
            time.sleep(1)
        while True:
            self.publish(MqttTopics.getUiTopic("uiPingOut"),json.dumps({"pingUI":True}))
            time.sleep(self.uiPingInt)
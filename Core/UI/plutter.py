import ast
import json
import threading
import paho.mqtt.client as mqtt
from Config.Data.hardcoded_command_templates import HardcodedTeleAddresses
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
from Core.Data.data import DataPointFDE
from Core.Data.database import DatabaseOperations, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.Data.experiment import StandardExperiment
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
        self.dataQueue=[]
        self.logData=False
        
        self.orgId=orgId
        
        self.automation=automation if automation else (FlowChemAutomation())
        
        #Authentication
        self.authenticator=Authenticator()
        
        self.zeroTime=None
        
        self.databaseOperations=None
        
        #self.dbInstructions={"createStdExp":DatabaseOperations.createStdExp}

    def onSubscribe(self, client, userdata, mid, granted_qos):
        if mid in self.topicIDs:
            print("WJ - Subscribed to topic " + self.topicIDs[mid] + " with Qos " + str(granted_qos[0]) + "!")
    
    def onConnect(self, client, userdata, flags, rc):
        print("WJ - Connected!")
        if rc == 0:
            for _x in self.allTopics:
                for tpc in _x.values():
                    qos=MqttTopics.getTopicQos(tpc)
                    ret=self.client.subscribe(tpc,qos=qos)
                    if ret[0]==0:
                        self.topicIDs[ret[1]]=tpc
                    else:
                        print("WJ - could not subscribe to topic "+tpc+"!")
        else:
            print("Connection failed with error code " + str(rc))
    
    def onConnectTele(self, client, userdata, flags, rc):
        print("WJ - Connected!")
        if rc == 0:
            for tpc in self.allTopicsTele.values():
                ret=self.client.subscribe(tpc)
                if ret[0]==0:
                    self.topicIDs[ret[1]]=tpc
                else:
                    print("WJ - could not subscribe to topic "+tpc+"!")
            for tpc in self.allTopicsUI.values():
                ret=self.client.subscribe(tpc,qos=2)
                if ret[0]==0:
                    self.topicIDs[ret[1]]=tpc
                else:
                    print("WJ - could not subscribe to topic "+tpc+"!")
            #Test settings
            tpc="test/settings"
            ret=self.client.subscribe(topic="test/settings",qos=2)
            if ret[0]==0:
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
        if "deviceName" in _msgContents:
            '''
            if (self.logData):
                self.addDataToQueue(_msgContents["deviceName"],_msgContents,self.labNotebookBaseRef,self.orgId)
            '''
            if _msgContents["deviceName"]=="hotcoil1":
                if 'state' in _msgContents:
                    self.temp = _msgContents['state']['temp']
            if _msgContents["deviceName"]=="reactIR702L1":
                if 'state' in _msgContents:
                    self.IR = _msgContents['state']['data']
            else:
                pass
        elif "script" in _msgContents:
            _msgContents=_msgContents["script"]
            print('############')
            print("WJ - Script message contents: "+str(_msgContents))
            print('############')
            self.script=self.automation.parsePlutterIn(_msgContents)
            print('############')
            print("WJ - Parsed script: "+str(self.script))
            print('############')
        elif "FormPanelWidget" in _msgContents:
            _msgContents=_msgContents["FormPanelWidget"]
            self.formPanelData=_msgContents
            print(f"WJ - Received FormPanelData: {_msgContents}")
        elif "LoginPageWidget" in _msgContents:
            _msgContents=_msgContents["LoginPageWidget"]
            if ("password" in _msgContents):
                print(f'WJ - Login page details: {_msgContents}')
                self.authenticator.signIn(orgId=_msgContents["orgId"],password=_msgContents["password"])
            else:
                print(_msgContents)
        elif topic=="ui/dbCmnd/in":
            _msgContents=_msgContents["instructions"]
            _func=_msgContents["function"]
            _params=_msgContents["params"]
            '''
            if (_func=="createStdExp"):
                _func=self.dbInstructions[_func]

                (self,labNotebookBaseRef,nameTest="Short description",description="Long description",flowScript=b"",testScript=b"script_content")

                nameTest=_params["nameTest"] #Short description
                description=_params["description"] #Long description
                testScript=self.script #Generated in UI, check if received and parsed!!
                lockScript=0
                flowScript="TODO" #Generated in UI
                labNotebookBaseRef=_params["labNotebookBaseRef"] #Needs to be built up automatically
                self.databaseOperations.createStdExp(nameTest=nameTest,description=description,testScript=testScript,flowScript=flowScript,labNotebookBaseRef=labNotebookBaseRef)
                #Then what?
            '''
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
                '''
                self.client.publish( #Create a return for 
                    "ui/dbCmnd/ret",
                    self.databaseOperations.getAllExpWidgetInfo(
                        orgId=self.authenticator.user.orgId
                    )
                )
                '''
                            
    def start(self):
        self.authenticator.initPlutter(mqttService=self)
        self.client.connect(self.broker_address, self.port)
        self.databaseOperations=DatabaseOperations(mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mySqlDb=MySQLDatabase(host='146.64.91.174'),mqttService=self)
        self.databaseOperations.connect()
        thread = threading.Thread(target=self._run)
        thread.start()
        return thread

    def _run(self):
        self.client.loop_start()

    def getTemp(self):
        return self.temp
    def getIR(self):
        return self.IR
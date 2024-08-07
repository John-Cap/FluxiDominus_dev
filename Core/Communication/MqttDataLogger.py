'''
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
from Core.UI.brokers_and_topics import MqttTopics


import paho.mqtt.client as mqtt


import ast
import threading

class MqttService:
    def __init__(self, broker_address="localhost", port=1883, client = None, allTopics=MqttTopics.getAllTopicSets(),allTopicsTele=MqttTopics.getTeleTopics(),automation=None):
        self.broker_address = broker_address
        self.port = port
        self.allTopics = allTopics
        self.allTopicsTele=allTopicsTele
        self.temp = 0
        self.IR = []
        self.script = ""

        self.client = client if client else (mqtt.Client(client_id="PlutterPy", clean_session=True, userdata=None, protocol=mqtt.MQTTv311))
        self.client.on_connect = self.onConnectTele #self.onConnect
        self.client.on_message = self.onMessage
        self.client.on_subscribe = self.onSubscribe
        
        self.topicIDs={}

        self.saidItOnce=False
        self.isSubscribed = {}

        self.lastMsgFromTopic={}
        
        self.automation=automation if automation else (FlowChemAutomation())

    def onSubscribe(self, client, userdata, mid, granted_qos):
        if mid in self.topicIDs:
            print("WJ - Subscribed to topic " + self.topicIDs[mid] + " with Qos " + str(granted_qos[0]) + "!")

    def onConnect(self, client, userdata, flags, rc):
        print("WJ - Connected!")
        if rc == 0:
            for _x in self.allTopics:
                for tpc in _x.values():
                    ret=self.client.subscribe(tpc)
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
            #Test settings
            tpc="test/settings"
            ret=self.client.subscribe(topic="test/settings",qos=2)
            if ret[0]==0:
                self.topicIDs[ret[1]]=tpc
            #
        else:
            print("Connection failed with error code " + str(rc))

    def onMessage(self, client, userdata, msg):
        #print(msg)
        _msgContents = msg.payload.decode()
        topic=msg.topic
        #print("WJ - topic: "+topic)
        _msgContents = _msgContents.replace("true", "True").replace("false", "False")
        _msgContents = ast.literal_eval(_msgContents)
        #print("Message received: " + str(_msgContents))
        self.lastMsgFromTopic[topic]=_msgContents
        if "deviceName" in _msgContents:
            #self.lastMsgFromTopic[_msgContents["deviceName"]]=_msgContents
            if _msgContents["deviceName"]=="hotcoil1":
                if 'state' in _msgContents:
                    self.temp = _msgContents['state']['temp']
                    #print(self.temp)
            if _msgContents["deviceName"]=="reactIR702L1":
                if 'state' in _msgContents:
                    self.IR = _msgContents['state']['data']
                    #print(self.IR)
            else:
                pass
                #print("Message received: " + str(_msgContents))
        elif "script" in _msgContents:
            _msgContents=_msgContents["script"]
            print('############')
            print("WJ - Script message contents: "+str(_msgContents))
            print('############')
            self.script=self.automation.parsePlutterIn(_msgContents)
            print('############')
            print("WJ - Parsed script: "+str(self.script))
            print('############')

    def start(self):
        self.client.connect(self.broker_address, self.port)
        thread = threading.Thread(target=self.run)
        thread.start()
        return thread

    def run(self):
        self.client.loop_start()
        #while True:
            #time.sleep(1)

    def getTemp(self):
        return self.temp
    def getIR(self):
        return self.IR
'''
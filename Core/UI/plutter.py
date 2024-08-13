import ast
import threading
import time
import paho.mqtt.client as mqtt
import json
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
from Core.Data.data import DataPointFDE
from Core.UI.brokers_and_topics import MqttTopics

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
        #self.client.on_publish=self.onPublish
        
        self.topicIDs={}

        self.saidItOnce=False
        self.isSubscribed = {}

        self.lastMsgFromTopic={}
        self.dataQueue=[]
        self.logData=False
        
        self.automation=automation if automation else (FlowChemAutomation())
        
    def addDataToQueue(self,device,data):
        self.dataQueue.append(DataPointFDE(
            experimentId="exp123",
            deviceName=device,
            data=data,
            metadata={"location": "Room 101", "type": "This particular type"}
        ).toDict())
        
    def onSubscribe(self, client, userdata, mid, granted_qos):
        if mid in self.topicIDs:
            print("WJ - Subscribed to topic " + self.topicIDs[mid] + " with Qos " + str(granted_qos[0]) + "!")
    '''
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
    '''
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
            if (self.logData):
                self.addDataToQueue(_msgContents["deviceName"],_msgContents)
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
class MqttService:
    def __init__(self, broker_address='146.64.91.174', port=1883, automation=FlowChemAutomation(),topicSets=MqttTopics.getAllTopicSets(),topicsTele=MqttTopics.getTeleTopics()):
        self.brokerAddress = broker_address
        self.port = port
        self.commands = {}
        self.client = mqtt.Client()
        self.client.on_message = self.onMessage
        self.client.on_connect = self.onConnect
        self.client.on_subscribe = self.onSubscribed
        self.automation = automation
        self.topicSets=topicSets
        self.topicsTele=topicsTele
        
        #TODO - move to config
        self.lastMsgFromTopic={}
        
    def updateLastMsg(self,topic,msg):
        self.lastMsgFromTopic[topic]=msg

    def registerCmnd(self, command, handler):
        self.commands[command] = handler

    def onConnect(self, client, userdata, flags, rc):
        for val in set.values():
            self.client.subscribe(val)

        for set in self.topicSets:
            for val in set.values():
                self.client.subscribe(val)

        print("Connected to MQTT broker")

    def onSubscribed(self, client, userdata, mid, reason_code_list):
        print('WJ - subscribed to topic ')

    def onMessage(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        self.updateLastMsg(message.topic,payload)
        print(self.lastMsgFromTopic)
        device = payload.get('device')
        command = payload.get('command')
        value = payload.get('value')

        #print('Received message: '+str(payload))

        if device in self.commands:
            self.commands[device](device, command, value)
        else:
            print(f"Unknown device: {device}")

    def start(self):
        self.client.connect(self.brokerAddress, self.port)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

def handle_command(command, value):
    print(f"Handling command: {command} with value: {value}")
    # Add logic to handle the command using FlowChemAutomation

def main():
    command_handler = MqttService()
    command_handler.registerCmnd('Delay', handle_command)
    # Register more commands as needed

    command_handler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        command_handler.stop()

if __name__ == "__main__":
    main()
'''
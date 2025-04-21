
import ast
import datetime
import threading
from time import sleep
import paho.mqtt.client as mqtt

from Core.Diagnostics.Logging import Diag_log

class MQTTReader:

    def __init__(self):

        self.currentScript=""
        self.runTest=False

        self.IrUpdated=False
        self.currentIrScan=[]

        # MQTT Broker Settings
        self.brokerAddress="localhost"
        self.port=1883

        self.topicTestCommandsNRtoPY="test/settings/"
        self.topicTestCommandsPYtoNR="test/status/"

        self.topic_SF10="subflow/sf10vapourtec1/cmnd"  # Change this to the topic you want to publish to
        self.topic_SF10_tele="subflow/sf10vapourtec1/tele"  # Change this to the topic you want to publish to
        self.topic_flowsynmaxi2="subflow/flowsynmaxi2/cmnd"  # Change this to the topic you want to publish to
        self.topic_flowsynmaxi2_tele="subflow/flowsynmaxi2/tele"  # Change this to the topic you want to publish to
        self.topic_hotchip1="subflow/hotchip1/cmnd"  # Change this to the topic you want to publish to
        self.topic_hotchip2="subflow/hotchip2/cmnd"  # Change this to the topic you want to publish to
        self.topic_hotcoil1="subflow/hotcoil1/cmnd"  # Change this to the topic you want to publish to
        self.topic_hotchip1_tele="subflow/hotchip1/tele"  # Change this to the topic you want to publish to
        self.topic_hotchip2_tele="subflow/hotchip2/tele"  # Change this to the topic you want to publish to
        self.topic_hotcoil1_tele="subflow/hotcoil1/tele"  # Change this to the topic you want to publish to
        self.topic_reactIR1_tele="subflow/reactIR702L1/tele"
        self.topic_reactIR1="subflow/reactIR702L1/cmnd"

        self.topics=[
            self.topicTestCommandsNRtoPY,
            self.topicTestCommandsPYtoNR,
            self.topic_SF10,
            #topic_SF10_tele,
            self.topic_flowsynmaxi2,
            #topic_flowsynmaxi2_tele,
            self.topic_hotchip1,
            self.topic_hotchip2,
            self.topic_hotcoil1,
            #topic_hotchip1_tele,
            #topic_hotchip2_tele,
            #topic_hotcoil1_tele,
            self.topic_reactIR1_tele,
            self.topic_reactIR1
        ]

    def clearScript(self):
        self.currentScript=""

    # Callback function to handle when the client receives a CONNACK response from the server
    def on_connect(self,client,userdata,flags,rc):
        if rc == 0:
            #print("Connected to broker")
            for _x in self.topics:
                client.subscribe(_x)
                #print("Subscribed to topic:",_x)
        else:
            print("Connection failed with error code " + str(rc))
    # Callback function to handle when a message is received from the broker
    def on_message(self,client,userdata,msg):

        _msgContents=(msg.payload.decode())
        #print(_msgContents)
        _msgContents=_msgContents.replace("true","True")
        _msgContents=_msgContents.replace("false","False")

        _msgContents=ast.literal_eval(_msgContents)
        #print("MQTT payload received!")
        #print("MQTT payload received: " + str(_msgContents))
        if "script" in _msgContents:
            print(_msgContents)
            _msgContents=_msgContents["script"]
            #print("Received message: " + _msgContents)
            self.currentScript=_msgContents
            return _msgContents
        if "running" in _msgContents:
            _msgContents=_msgContents["running"]
            #print("Received message: " + str(_msgContents))
            self.runTest=_msgContents
            return _msgContents        
        if "deviceName" in _msgContents:
            #print(_msgContents["deviceName"])
            _name=_msgContents["deviceName"]
            if _name == "reactIR702L1":
                #print("IR scan received")
                # Get the current time
                current_time = datetime.datetime.now()

                # Format the time as HH:MM:SS
                timestamp = current_time.strftime("%H:%M:%S")
                _msgContents=timestamp+"->"+str((_msgContents["state"])["data"])
                Diag_log().toLog(_msgContents)

                if not self.IrUpdated:
                    self.currentIrScan=((_msgContents["state"])["data"])
                    #self.IrUpdated=True

                return _msgContents
            elif _name=="flowsynmaxi2":
                pass
                #print("Maxi command: " + str(_msgContents))
            elif _name=="sf10Vapourtec1":
                pass
                #print("SF10 command: " + str(_msgContents))
                        
    def readMQTTLoop(self):

        # Create MQTT client instance
        client=mqtt.Client(client_id="",clean_session=True,userdata=None,protocol=mqtt.MQTTv311)

        # Assign callbacks to client
        client.on_connect=self.on_connect
        client.on_message=self.on_message

        # Connect to MQTT broker
        client.connect(self.brokerAddress,self.port,1)
        # Start loop to process callbacks
        client.loop_start()

class MQTTTemperatureUpdater:
    def __init__(self, broker_address="localhost", port=1883, topic="subflow/hotcoil1/tele"):
        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        self.temp = 0
        self.client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            self.client.subscribe(self.topic)
        else:
            print("Connection failed with error code " + str(rc))

    def on_message(self, client, userdata, msg):
        _msgContents = msg.payload.decode()
        _msgContents = _msgContents.replace("true", "True").replace("false", "False")
        _msgContents = ast.literal_eval(_msgContents)
        
        if "deviceName" in _msgContents:
            self.temp = _msgContents['state']['temp']
            print(self.temp)
            
    def getTemp(self):
        return self.temp

    def start(self):
        self.client.connect(self.broker_address, self.port)
        thread = threading.Thread(target=self.run)
        thread.start()
        return thread

    def run(self):
        self.client.loop_start()
        while True:
            sleep(1)

from datetime import datetime
import time
import threading
import ast
import paho.mqtt.client as mqtt

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Utils.Utils import DataLogger, TimestampGenerator

class MQTTTemperatureUpdater:
    def __init__(self, broker_address="localhost", port=1883, topic="subflow/hotcoil1/tele"):
        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        self.temp = 0
        self.IR=[]
        self.client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.saidItOnce=False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Temperature reader connected to broker")
            self.client.subscribe(self.topic)
            #self.client.subscribe("subflow/hotcoil1/cmnd")
            self.client.subscribe("subflow/reactIR702L1/tele")
        else:
            print("Connection failed with error code " + str(rc))
    def on_message(self, client, userdata, msg):
        _msgContents = msg.payload.decode()
        _msgContents = _msgContents.replace("true", "True").replace("false", "False")
        _msgContents = ast.literal_eval(_msgContents)
        #print("Message received: " + str(_msgContents))
        
        if "deviceName" in _msgContents:
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

# Create an instance of MQTTTemperatureUpdater
updater = MQTTTemperatureUpdater()
thread = updater.start()
time.sleep(2)

temps = [30, 60, 90, 80, 70, 30]
sequenceComplete=False
targetIndex = 0
maxIndex = len(temps)-1
targetTemp = temps[targetIndex]

hitBracket=2 #abs distance from target temp to be considered reached

def checkTempFunc(value):
    #print(value)
    global targetIndex, targetTemp, sequenceComplete
    if sequenceComplete:
        return True
    _b = hitBracket >= abs(value-targetTemp)
    if _b:
        print("Target temperature "+str(targetTemp)+" reached!")
        targetIndex += 1
        if targetIndex > maxIndex:
            print("All temperatures reached!")
            sequenceComplete=True
            return True
        targetTemp = temps[targetIndex]
    return _b

def pullTemp():
    return updater.getTemp()

# Example script, parser and decoder setup
#
#{'deviceName': 'hotcoil1', 'command': 'SET', 'temperatureSet': 25}

script ='''
startPumps=[
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 0.83
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    },
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpAFlowRate",
            "command": "SET",
            "value": 0.83
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    }
];
commandBlock_1=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 30,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 900, "initTimestamp": None}}
];
commandBlock_2=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 60,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 900, "initTimestamp": None}}
];
commandBlock_3=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 90,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 900, "initTimestamp": None}}
];
commandBlock_4=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 80,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 900, "initTimestamp": None}}
];
commandBlock_5=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 70,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 900, "initTimestamp": None}}
];
end=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET",
        "temperatureSet": 25,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}}
];
'''

# Set up MQTT client
client = mqtt.Client()
client.connect("localhost", 1883, 60)

# Create script parser and decoder
# Assuming ScriptParser and FdpDecoder are defined elsewhere
script_parser = ScriptParser(script, client)
decoder_kwargs = {
    "conditionFunc": checkTempFunc,
    "conditionParam": pullTemp
}

fdpDecoder = FdpDecoder(currKwargs=decoder_kwargs)
parser = ScriptParser(script, client)
procedure = parser.createProcedure(fdpDecoder)

doIt = True
_reportSleep=5
_reportDelay=Delay(_reportSleep)
logger = DataLogger('time_degrees_IR_1.txt')
logger.logData(-1,[-1])
while doIt:
    if _reportDelay.elapsed():
        _reportDelay=Delay(_reportSleep)
        logger.logData(updater.getTemp(),updater.getIR())
    if len(procedure.currConfig.commands) == 0:
        procedure.next()
        if procedure.currConfig is None:
            print("Procedure complete")
            doIt = False
        else:
            print("Next procedure!")
    else:
        procedure.currConfig.sendMQTT()
    time.sleep(0.1)
thread.join()
exit()
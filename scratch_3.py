import time
import paho.mqtt.client as mqtt

from Core.Communication.IO import IO
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser

script = '''
commandBlock_1=[
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 1.0
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    },
    {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": 15, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 5, "initTimestamp": None}},
    {
        "deviceName":"sf10Vapourtec1",
        "inUse":True,
        "settings":{"command":"SET","mode":"FLOW","flowrate":0.5},
        "topic":"subflow/sf10vapourtec1/cmnd",
        "client":"client"
    },
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 1
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    },    
    {"Delay": {"sleepTime": 10, "initTimestamp": None}},
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 0.5
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    },
    {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": 30, "initTimestamp": None, "completionMessage": "No message!"}}
];
commandBlock_2=[
    {"Delay": {"sleepTime": 5, "initTimestamp": None}},
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 1.5
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    },
    {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": 30, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 5, "initTimestamp": None}},
    {
        "deviceName":"sf10Vapourtec1",
        "inUse":True,
        "settings":{"command":"SET","mode":"FLOW","flowrate":1.2},
        "topic":"subflow/sf10vapourtec1/cmnd",
        "client":"client"
    },
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 0.8
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    },
    {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": 30, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 5, "initTimestamp": None}},
    {
        "deviceName":"sf10Vapourtec1",
        "inUse":True,
        "settings":{"command":"SET","mode":"FLOW","flowrate":0},
        "topic":"subflow/sf10vapourtec1/cmnd",
        "client":"client"
    },
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 0
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    }
];
'''
import threading
import time
import random

class IRThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.value = 0
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        while self.running:
            with self.lock:
                self.value = random.randint(0, 20)  # Simulate value change
            time.sleep(0.5)  # Simulate delay in value update

    def get_value(self):
        with self.lock:
            return self.value

    def stop(self):
        self.running = False

def checkValFunc(value):
    return value > 18

# Start IR thread
ir_thread = IRThread()
ir_thread.start()

def getLivingValue():
    return ir_thread.get_value()

# Set up MQTT client
client = mqtt.Client()
client.connect("146.64.91.174", 1883, 60)
#client.connect("localhost", 1883, 60)
# Create script parser and decoder
script_parser = ScriptParser(script, client)
decoder_kwargs = {
    "conditionFunc": checkValFunc,
    "conditionParam": getLivingValue
}

fakeClient=1
fdpDecoder = FdpDecoder(currKwargs=decoder_kwargs)
parser = ScriptParser(script, client)
procedure = parser.createProcedure(fdpDecoder)

doIt=True
while doIt:
    if (len(procedure.currConfig.commands))==0:
        print("Next procedure!")
        procedure.next()
    if procedure.currConfig is None:
        print("Procedure complete")
        exit()
    else:
        #Send a command
        procedure.currConfig.sendMQTT()
    time.sleep(0.01)
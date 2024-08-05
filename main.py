from datetime import datetime
import time
import paho.mqtt.client as mqtt

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Utils.Utils import DataLogger, TimestampGenerator
from Core.Communication.MqttDataLogger import MqttDataLogger

# Create an instance of MQTTTemperatureUpdater
updater = MqttDataLogger()
thread = updater.start()
time.sleep(2)

temps = [60, 70, 80, 90, 95, 0.5]
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

 #Real script
script='''
startPumps=[
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 2.5
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
            "value": 2.5
        },
        "topic": "subflow/flowsynmaxi2/cmnd",
        "client": "client"
    },
    {"Delay": {"sleepTime": 15, "initTimestamp": None}}
];
commandBlock_1=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 60,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 950, "initTimestamp": None}}
];
commandBlock_2=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 70,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 950, "initTimestamp": None}}
];
commandBlock_3=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 80,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 950, "initTimestamp": None}}
];
commandBlock_4=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 90,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 950, "initTimestamp": None}}
];
commandBlock_5=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET", 
        "temperatureSet": 95,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}},
    {"Delay": {"sleepTime": 950, "initTimestamp": None}}
];
end=[
    {
        "deviceName":"hotcoil1", 
        "inUse" : True,
        "command":"SET",
        "temperatureSet": 10,
        "topic":"subflow/hotcoil1/cmnd",
        "client":"client"
    },
    {"Delay": {"sleepTime": 950, "initTimestamp": None}},
    {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": 1500, "initTimestamp": None, "completionMessage": "No message!"}}
];
'''
'''
mr_block=[{"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 1.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 15}}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.5}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.5}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 0}}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.3}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.7}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 5}}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.85}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": 
True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.15}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}];
flowsyn_fr_2=[{"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}];
'''
# Set up MQTT client
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()

# Data logger


# Create script parser and decoder
# Assuming ScriptParser and FdpDecoder are defined elsewhere
script_parser = ScriptParser(script, client)
decoder_kwargs = {
    "conditionFunc": checkTempFunc,
    "conditionParam": pullTemp
}

fdpDecoder = FdpDecoder(currKwargs=decoder_kwargs)

doIt = True
_reportSleep=5
_reportDelay=Delay(_reportSleep)
logger = DataLogger('time_degrees_IR_1.txt')
logger.logData(-1,[-1])

parser=None
procedure=None

# Main loop!
while True:
    #Script posted?
    
    print("WJ - Waiting for script")
    while (not "test/settings" in updater.lastMsgFromTopic) or updater.script=="":
        time.sleep(0.5)
        
    try:
        parser = ScriptParser((updater.lastMsgFromTopic["test/settings"]["script"]), client)
        procedure = parser.createProcedure(fdpDecoder)
        updater.script=""
        print("WJ - Script received!")
    except:
        print("Script parsing error!")
        exit()
    
    doIt=True
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
            procedure.currConfig.sendMQTT(waitForDelivery=True)
        time.sleep(0.1)
thread.join()
exit()
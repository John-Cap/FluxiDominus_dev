import json
import sys
import time
import ast
import re
import paho.mqtt.client as mqtt

from Core.Communication.IO import IO
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Fluids.FlowPath import FlowPathAdjustment

class Procedure:
    def __init__(self, device="", sequence=[]) -> None:
        self.sequence = sequence
        self.device = device
        self.currItemIndex = 0
        self.completed = False
        self.currConfig = None

    def setSequence(self, sequence):
        self.sequence = sequence
        self.currConfig = self.sequence[self.currItemIndex]
        return self.currConfig
        
    def next(self):
        self.currItemIndex += 1
        if len(self.sequence) == self.currItemIndex:
            self.currConfig = None
        else:
            self.currConfig = self.sequence[self.currItemIndex]
                
    def currConfiguration(self):
        if len(self.sequence) == self.currItemIndex:
            return None
        return self.sequence[self.currItemIndex]

    def currItemComplete(self, **kwargs):
        _thisItem = self.sequence[self.currItemIndex]
        _return = (_thisItem.isComplete(self.device, **kwargs))
        if _return:
            if (self.currItemIndex + 1) != len(self.sequence):
                self.currItemIndex += 1
            else:
                self.currItemIndex = -2
                self.completed = True
            return _return
        else:
            return False

    def executeNext(self):
        pass

    def execute(self):
        pass

class FdpDecoder:
    def __init__(self, currKwargs=None, confNum=0):
        self.currKwargs = currKwargs if currKwargs else {}
        self.decoderClasses = {
            "Delay": self._decodeDelay,
            "WaitUntil": self._decodeWaitUntil,
            "FlowPathAdjustment": self._decodeFlowPathAdjustment,
        }
        self.confNum = confNum

    def _decodeDelay(self, data):
        return Delay(initTimestamp=data["initTimestamp"], sleepTime=data["sleepTime"])

    def _decodeWaitUntil(self, data):
        return WaitUntil(
            conditionFunc=self.currKwargs["conditionFunc"],
            conditionParam=self.currKwargs["conditionParam"],
            timeout=data["timeout"],
            initTimestamp=data["initTimestamp"],
            completionMessage=data["completionMessage"]
        )

    def _decodeFlowPathAdjustment(self, data):
        instance = self.currKwargs.get(data["instance"])
        attributeName = self.currKwargs.get(data["attributeName"], data["attributeName"])
        valueOrMethod = self.currKwargs.get(data["valueOrMethod"])
        args = self.currKwargs.get(data["args"], [])
        return FlowPathAdjustment(instance, attributeName, valueOrMethod, args)

    def decode(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in self.decoderClasses:
                    return self.decoderClasses[key](value)
        return obj
    
class ScriptParser:
    def __init__(self, script, client, confNum=0):
        self.client = client
        self.script = self._removeComments(script)
        self.blocks = self._parseScript()
        self.decoderClasses = {
            "Delay": Delay,
            "WaitUntil": WaitUntil,
            "FlowPathAdjustment": FlowPathAdjustment,
            "client": client,
        }
        self.confNum = confNum
        
    def convertJsonToPython(self, string):
        replacements = {
            "true": "True",
            "false": "False",
            "null": "None"
        }
        for jsonValue, pythonValue in replacements.items():
            string = string.replace(jsonValue, pythonValue)
        return string

    def _removeComments(self, text):
        pattern = r"/\*.*?\*/"
        return re.sub(pattern, "", text, flags=re.DOTALL)

    def _parseScript(self):
        blocks = {}
        currentBlock = None

        for line in self.script.split(';'):
            line = line.strip()
            if '=' in line:
                blockName, blockContent = line.split('=', 1)
                blockName = blockName.strip()
                if blockContent.startswith('[') and blockContent.endswith(']'):
                    blockContent = blockContent[1:-1].strip()
                    try:
                        parsedBlock = ast.literal_eval(f'[{blockContent}]')
                        blocks[blockName] = parsedBlock
                        currentBlock = blockName
                    except Exception as e:
                        print(f"Error parsing block {blockName}: {e}")
                else:
                    currentBlock = None
            elif currentBlock and line.startswith('{') and line.endswith('}'):
                try:
                    parsedContent = ast.literal_eval(line)
                    blocks[currentBlock].append(parsedContent)
                except Exception as e:
                    print(f"Error parsing additional block content: {e}")
        
        return blocks

    def convertToNodeScripts(self, blockName, blockContent, fdpDecoder):
        nodeScripts = []
        for entry in blockContent:
            processedEntry = self._processEntry(entry, fdpDecoder)
            nodeScripts.append(processedEntry)
        return nodeScripts

    def _processEntry(self, entry, fdpDecoder):
        for key in entry:
            if key in self.decoderClasses:
                entry[key] = fdpDecoder.decode({key: entry[key]})
            if key == "client":
                entry[key] = self.client
        return entry
    
    def createProcedure(self, fdpDecoder):
        configurations = []
        for blockName, blockContent in self.blocks.items():
            nodeScripts = self.convertToNodeScripts(blockName, blockContent, fdpDecoder)
            configurations.append(ConfigurationMock(nodeScripts, setMessage=("Config " + str(self.confNum) + " is complete!")))
            self.confNum += 1
        _proc = Procedure()
        _proc.setSequence(configurations)
        return _proc

class ConfigurationMock:
    def __init__(self, commands, setMessage="Configuration set") -> None:
        self.devices = []
        self.commands = commands
        self.setMessage = setMessage

    def sendMQTT(self, waitForDelivery=False):
        if (len(self.commands)) == 0:
            print("No commands left!")
            return
        _currentCommand = (self.commands[0])
        if "Delay" in _currentCommand:
            if _currentCommand["Delay"].elapsed():
                del self.commands[0]
                return
            else:
                return
        elif "WaitUntil" in _currentCommand:
            if _currentCommand["WaitUntil"].check():
                del self.commands[0]
                return
            else:
                return
        else:
            print(self.commands[0])
            del self.commands[0]

class WaitUntil:
    def __init__(self, conditionFunc, conditionParam, timeout=60, initTimestamp=None, completionMessage="WaitUntil complete"):
        self.conditionFunc = conditionFunc
        self.conditionParam = conditionParam
        self.timeout = timeout
        self.initTimestamp = None
        self.completionMessage = completionMessage

    def check(self):
        if self.initTimestamp is None:
            self.initTimestamp = time.time()
        current_time = time.time()
        if current_time - self.initTimestamp > self.timeout:
            print("WaitUntil timed out!")
            return True
        print(self.conditionFunc(self.conditionParam()))
        return self.conditionFunc(self.conditionParam())

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
        "topic": "subflow/flowsynmax2/cmnd",
        "client": "client"
    },
    {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": 15, "initTimestamp": None, "completionMessage": "No message!"}},
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 1.0
        },
        "topic": "subflow/flowsynmax2/cmnd",
        "client": "client"
    },    
    {"Delay": {"sleepTime": 2, "initTimestamp": None}}
];
commandBlock_2=[
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 1.0
        },
        "topic": "subflow/flowsynmax2/cmnd",
        "client": "client"
    },
    {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": 15, "initTimestamp": None, "completionMessage": "No message!"}},
    {
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 69
        },
        "topic": "subflow/flowsynmax2/cmnd",
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
client.connect("test.mosquitto.org", 1883, 60)

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
    time.sleep(1)
    
print("Done!")


import json
import sys
import time

from Core.Communication.IO import IO
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay, Procedure
import ast
import re
#from Core.Control.Commands import Configuration, Delay, Procedure, WaitUntil
from Core.Fluids.FlowPath import FlowPathAdjustment
import paho.mqtt.client as mqtt

class FdpDecoder:
    def __init__(self, currKwargs=None,confNum=0):
        self.currKwargs = currKwargs if currKwargs else {}
        self.decoderClasses = {
            "Delay": self._decodeDelay,
            "WaitUntil": self._decodeWaitUntil,
            "FlowPathAdjustment": self._decodeFlowPathAdjustment,
        }
        self.confNum=confNum

    def _decodeDelay(self, data):
        #print("_decodeDelay data: " + str (data))
        return Delay(initTimestamp=data["initTimestamp"], sleepTime=data["sleepTime"])

    def _decodeWaitUntil(self, data):
        '''
        print(self.currKwargs["conditionFunc"]),
        print(self.currKwargs["conditionParam"]),
        print(data["timeout"]),
        print(data["initTimestamp"]),
        print(data["completionMessage"])
        '''
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
        self.confNum=confNum
        
    def convertJsonToPython(string):
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
                    blockContent = blockContent[1:-1].strip()  # Remove the outer brackets and trim whitespace
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
                    blocks[currentBlock].append(parsedContent)  # Append additional JSON objects to current block
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
        #print(entry)
        return entry
    
    def createProcedure(self, fdpDecoder):
        configurations = []
        for blockName, blockContent in self.blocks.items():
            nodeScripts = self.convertToNodeScripts(blockName, blockContent, fdpDecoder)
            configurations.append(ConfigurationMock(nodeScripts,setMessage=("Config " + str(self.confNum) + " is complete!")))
            self.confNum+=1
        return Procedure(sequence=configurations)

checkVal=0;
def checkValFunc(val):
    print("Checking val "+str(val)+"!")
    return val==1

class ConfigurationMock:
    def __init__(self,commands,setMessage="Configuration set") -> None:
        self.devices=[]
        self.commands=commands
        self.setMessage=setMessage

    def sendAndSet(self):
        if (len(self.commands))==0:
            return
        if isinstance(self.commands[0],Delay):
            if (self.commands[0]).elapsed():
                del self.commands[0]
                return
            else:
                return
        elif isinstance(self.commands[0],WaitUntil):
            if (self.commands[0]).check():
                print("Waituntil true!")
                del self.commands[0]
                return
            else:
                print("Waituntil false!")
                return
        else:
            _io=IO()
            _io.write(json.dumps(self.commands[0]))
            sys.stdout.flush()
            del self.commands[0]

    def sendMQTT(self,waitForDelivery=False):
        if (len(self.commands))==0:
            print("No commands left!")
            return
        _currentCommand=(self.commands[0])
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
            del self.commands[0]
            return
            _topic=_currentCommand["topic"]
            _client=_currentCommand["client"]
            if not _client.is_connected():
                _client.connect("localhost",1883)
            del _currentCommand["topic"]
            del _currentCommand["client"]
            _result=_client.publish(_topic,json.dumps(_currentCommand))
            if waitForDelivery:
                _result.wait_for_publish(5)
                #print(_result.is_published())
            del self.commands[0]
            #return _result

class WaitUntil:
    def __init__(self, conditionFunc, conditionParam, timeout=60, initTimestamp=None, completionMessage="WaitUntil complete"):
        self.conditionFunc = conditionFunc
        self.conditionParam = conditionParam
        self.timeout = timeout
        self.initTimestamp = initTimestamp if initTimestamp else time.time()
        self.completionMessage = completionMessage

    def check(self):
        #print("Checking...")
        current_time = time.time()
        print(current_time)
        print(self.initTimestamp)        
        print(self.timeout)
        if current_time - self.initTimestamp > self.timeout:
            print("WaitUntil timed out!")
            return True
        return self.conditionFunc(self.conditionParam)
'''
(
    conditionFunc: (val: Any) -> Any,
    conditionParam: int,
    timeout: int = 60,
    initTimestamp: Any | None = None,
    completionMessage: str = "WaitUntil complete"
)
'''
script = '''
commandBlock_1=[
    {
        "deviceName": "flowsynmaxi2",
        "inUse":True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 1.0
        },
        "topic":"subflow/flowsynmax2/cmnd",
        "client":"client"
    },
    {"WaitUntil":{"conditionFunc":'checkValFunc',"conditionParam":1,"timeout":60,"initTimestamp":None,"sleepTime":10,"completionMessage":"No message!"}},
    {
        "deviceName":"sf10Vapourtec1",
        "inUse":True,
        "settings":{"command":"SET","mode":"FLOW","flowrate":1},
        "topic":"subflow/sf10vapourtec1/cmnd",
        "client":"client"
    },
    {"Delay":{"initTimestamp":None,"sleepTime":10}}
];
commandBlock_2=[
    {
        "deviceName": "flowsynmaxi2",
        "inUse":True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 0.0
        },
        "topic":"subflow/flowsynmax2/cmnd",
        "client":"client"
    }
];
'''
currKwargs={"conditionFunc":checkValFunc,"conditionParam":checkVal};
fakeClient=1
fdpDecoder = FdpDecoder(currKwargs=currKwargs)
parser = ScriptParser(script, fakeClient)
procedure = parser.createProcedure(fdpDecoder)
_currentConf=procedure.currConfiguration()
print(_currentConf)
doIt=True
while doIt:
    _currentConf.sendMQTT()
    time.sleep(1)
    
print("Done!")
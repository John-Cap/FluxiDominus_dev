import ast
import re
from Core.Control.Commands import Configuration, Delay, Procedure, WaitUntil
from Core.Fluids.FlowPath import FlowPathAdjustment
import paho.mqtt.client as mqtt

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
        '''         
        blocks = {}
        currentBlock = None
        '''
        #print(blocks)
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
            configurations.append(Configuration(nodeScripts, setMessage=("Config " + str(self.confNum) + " is complete!")))
            self.confNum += 1
        _proc = Procedure()
        _proc.setSequence(configurations)
        return _proc

if __name__ == "__main__":
    script = '''
    myBlock_123=[{"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 1.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 15}}];
    myBlock_456=[{"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpAFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}];
    '''

    fdpDecoder = FdpDecoder()
    parser = ScriptParser(script, mqtt.Client())
    procedure = parser.createProcedure(fdpDecoder)

    # Now use the procedure as needed
    print(f"Procedure created with {len(procedure.sequence)} configurations.")
    for idx, config in enumerate(procedure.sequence):
        print(f"Configuration {idx + 1}: {config.commands}")

#import json
import copy
import os

#from Core.Control.Commands import Delay, WaitUntil
#from Core.Utils.Utils import Utils

class CustomCommands:
    def __init__(self):
        self.commands = {}

    def registerCommand(self, commandClass):
        commandName = commandClass.__name__
        commandParams = [param for param in vars(commandClass()).keys()]
        self.commands[commandName] = commandParams

    def getCommandParams(self, commandName):
        return self.commands.get(commandName, None)

class FlowChemAutomation:

    def __init__(self):
        self.output=""
        self.varBrackets={
            ">float<":float,
            ">bool<":bool,
            ">string<":str
        }
        self.blocks={}
        self.blockNames=[]
        self.commandTemplates={
            #Vapourtec SF10
            "sf10vapourtec1fr":'''
                {
                    "deviceName":"sf10vapourtec1", 
                    "inUse" : True,
                    "settings":{
                        "command":"SET", 
                        "mode": "FLOW",
                        "valve": "A",
                        "flowrate":>float<
                    },
                    "topic":"subflow/sf10vapourtec1/cmnd",
                    "client":"client"
                }
            ''',
            "sf10vapourtec2fr":'''
                {
                    "deviceName":"sf10vapourtec2", 
                    "inUse" : True,
                    "settings":{
                        "command":"SET", 
                        "mode": "FLOW",
                        "valve": "A",
                        "flowrate":>float<
                    },
                    "topic":"subflow/sf10vapourtec2/cmnd",
                    "client":"client"
                }
            ''',
            
            #Hotcoils
            "hotcoil1temp":'''
                {
                    "deviceName":"hotcoil1", 
                    "inUse" : True,
                    "command":"SET", 
                    "temperatureSet":>float<,
                    "topic":"subflow/hotcoil1/cmnd",
                    "client":"client"                    
                }
            ''',
            "hotcoil2temp":'''
                {
                    "deviceName":"hotcoil2", 
                    "inUse" : True,
                    "command":"SET", 
                    "temperatureSet":>float<,
                    "topic":"subflow/hotcoil2/cmnd",
                    "client":"client"                    
                }
            ''',
            
            #Hotchips
            "hotchip1temp":'''
                {
                    "deviceName":"hotchip1", 
                    "inUse" : True,
                    "command":"SET", 
                    "temperatureSet":>float<,
                    "topic":"subflow/hotchip1/cmnd",
                    "client":"client"                    
                }
            ''',
            "hotchip2temp":'''
                {
                    "deviceName":"hotchip2", 
                    "inUse" : True,
                    "command":"SET", 
                    "temperatureSet":>float<,
                    "topic":"subflow/hotchip2/cmnd",
                    "client":"client"                    
                }
            ''',
            
            #Maxi
            "flowsynmaxi1pafr":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings": {
                        "subDevice": "PumpAFlowRate",
                        "command": "SET",
                        "value": >float<
                    },
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi1pbfr":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings": {
                        "subDevice": "PumpBFlowRate",
                        "command": "SET",
                        "value": >float<
                    },
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi1sva":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings": {
                        "subDevice": "FlowSynValveA",
                        "command": "SET",
                        "value": >bool<
                    },
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi1svb":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings": {
                        "subDevice": "FlowSynValveB",
                        "command": "SET",
                        "value": >bool<
                    },
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi1svcw":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings": {
                        "subDevice": "FlowCWValve",
                        "command": "SET",
                        "value": >bool<
                    },
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi2pafr":'''
                {
                    "deviceName": "flowsynmaxi2",
                    "inUse": True,
                    "settings": {
                        "subDevice": "PumpAFlowRate",
                        "command": "SET",
                        "value": >float<
                    },
                    "topic":"subflow/flowsynmaxi2/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi2pbfr":'''
                {
                    "deviceName": "flowsynmaxi2",
                    "inUse": True,
                    "settings": {
                        "subDevice": "PumpBFlowRate",
                        "command": "SET",
                        "value": >float<
                    },
                    "topic":"subflow/flowsynmaxi2/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi2sva":'''
                {
                    "deviceName": "flowsynmaxi2",
                    "inUse": True,
                    "settings": {
                        "subDevice": "FlowSynValveA",
                        "command": "SET",
                        "value": >bool<
                    },
                    "topic":"subflow/flowsynmaxi2/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi2svb":'''
                {
                    "deviceName": "flowsynmaxi2",
                    "inUse": True,
                    "settings": {
                        "subDevice": "FlowSynValveB",
                        "command": "SET",
                        "value": >bool<
                    },
                    "topic":"subflow/flowsynmaxi2/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi2svcw":'''
                {
                    "deviceName": "flowsynmaxi2",
                    "inUse": True,
                    "settings": {
                        "subDevice": "FlowCWValve",
                        "command": "SET",
                        "value": >bool<
                    },
                    "topic":"subflow/flowsynmaxi2/cmnd",
                    "client":"client"
                }
            ''',
            
            #Custom commands
            "Delay":'''
                {"Delay": {"initTimestamp": None, "sleepTime": >float<}}
            ''',
            "WaitUntil":'''
                {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": >float<, "initTimestamp": None, "completionMessage": "No message!"}},
            '''
        }

    def parseBlockElement(self,setting,val):
        if not setting in self.commandTemplates:
            #throw
            return
        setThis=copy.deepcopy(self.commandTemplates[setting])
        #Valid setting?
        for key in self.varBrackets: #TODO - this is stupid
            if key in setThis:
                if isinstance(val,self.varBrackets[key]):
                    return ((setThis.replace(key,str(val))).replace(" ","")).replace("\n","")
                else:
                    #Throw
                    exit()

    def addBlock(self,blockName):
        #TODO - Check if block exists then throw
        self.blocks[blockName]=[]
        self.blockNames.append(blockName)

    def addBlockElement(self,blockName,setting,val):
        if not blockName in self.blocks:
            self.addBlock(blockName)
        self.blocks[blockName].append(self.parseBlockElement(setting,val))
        
    def saveBlocksToFile(self, filename="default_script",save_directory=""):
        if save_directory=="":
            home_directory = os.path.expanduser("~")
            save_directory = os.path.join(home_directory, "flowchem_scripts")

        # Ensure the directory exists
        os.makedirs(save_directory, exist_ok=True)

        file_path = os.path.join(save_directory, filename)
        if not file_path.endswith('.fdp'):
            file_path += '.fdp'
        try:
            with open(file_path, 'w') as file:
                '''
                blocks = ';\n'.join([
                    f"{name}={json.dumps(block)}"
                    for name, block in self.generatedBlocks.items()
                ]) + ';'
                blocks = self.convertJsonToPython(blocks)
                '''
                for blockName in self.blockNames:
                    blockElements=self.blocks[blockName]
                    self.output=self.output + blockName + "=["
                    finalIndex=len(blockElements)-1
                    for index, element in enumerate(blockElements):
                        if index == finalIndex:
                            self.output=self.output + element
                        else:
                            self.output=self.output + element + ","
                    self.output=self.output + "];" + "\n"
                print(self.output)
                file.write(self.output)
            print(f"File saved successfully at {file_path}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

# Define custom command classes
# Example usage
if __name__ == "__main__":
    automation = FlowChemAutomation()
    automation.addBlockElement("block_1","sf10vapourtec1fr",1.0)
    automation.addBlockElement("block_1","flowsynmaxi1pafr",1.0)
    automation.addBlockElement("block_1","flowsynmaxi1sva",False)
    
    automation.addBlockElement("block_2","sf10vapourtec2fr",1.0)
    automation.addBlockElement("block_2","flowsynmaxi2pbfr",1.0)
    automation.addBlockElement("block_3","Delay",100.0)
    automation.addBlockElement("block_2","flowsynmaxi1svcw",True)
    
    automation.saveBlocksToFile(save_directory=r"C:\Python_Projects\FluxiDominus_dev\devJunk")
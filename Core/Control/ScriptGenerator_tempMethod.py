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
            #Vapourtec SF10's
            "sf10vapourtec1_fr":'''
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
            "sf10vapourtec2_fr":'''
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
            "hotcoil1_temp":'''
                {
                    "deviceName":"hotcoil1", 
                    "inUse" : True,
                    "command":"SET", 
                    "temperatureSet":>float<,
                    "topic":"subflow/hotcoil1/cmnd",
                    "client":"client"                    
                }
            ''',
            "hotcoil2_temp":'''
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
            "hotchip1_temp":'''
                {
                    "deviceName":"hotchip1", 
                    "inUse" : True,
                    "command":"SET", 
                    "temperatureSet":>float<,
                    "topic":"subflow/hotchip1/cmnd",
                    "client":"client"                    
                }
            ''',
            "hotchip2_temp":'''
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
            "flowsynmaxi1_pafr":'''
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
            "flowsynmaxi1_pbfr":'''
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
            "flowsynmaxi1_sva":'''
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
            "flowsynmaxi1_svb":'''
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
            "flowsynmaxi1_svcw":'''
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
            "flowsynmaxi2_pafr":'''
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
            "flowsynmaxi2_pbfr":'''
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
            "flowsynmaxi2_sva":'''
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
            "flowsynmaxi2_svb":'''
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
            "flowsynmaxi2_svcw":'''
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
        self.commandTemplatesNested = {
            "Delay":{
                "sleepTime":'''
                    {"Delay": {"initTimestamp": None, "sleepTime": >float<}}
                '''
            },
            "WaitUntil":{
                "timeout":'''
                    {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": >float<, "initTimestamp": None, "completionMessage": "No message!"}},
                '''
            },
            "sf10vapourtec1": {
                "fr": '''
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
                '''
            },
            "sf10vapourtec2": {
                "fr": '''
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
                '''
            },
            "hotcoil1": {
                "temp": '''
                    {
                        "deviceName":"hotcoil1", 
                        "inUse" : True,
                        "command":"SET", 
                        "temperatureSet":>float<,
                        "topic":"subflow/hotcoil1/cmnd",
                        "client":"client"
                    }
                '''
            },
            "hotcoil2": {
                "temp": '''
                    {
                        "deviceName":"hotcoil2", 
                        "inUse" : True,
                        "command":"SET", 
                        "temperatureSet":>float<,
                        "topic":"subflow/hotcoil2/cmnd",
                        "client":"client"
                    }
                '''
            },
            "hotchip1": {
                "temp": '''
                    {
                        "deviceName":"hotchip1", 
                        "inUse" : True,
                        "command":"SET", 
                        "temperatureSet":>float<,
                        "topic":"subflow/hotchip1/cmnd",
                        "client":"client"
                    }
                '''
            },
            "hotchip2": {
                "temp": '''
                    {
                        "deviceName":"hotchip2", 
                        "inUse" : True,
                        "command":"SET", 
                        "temperatureSet":>float<,
                        "topic":"subflow/hotchip2/cmnd",
                        "client":"client"
                    }
                '''
            },
            "flowsynmaxi1": {
                "pafr": '''
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
                "pbfr": '''
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
                "sva": '''
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
                "svb": '''
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
                "svcw": '''
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
                '''
            },
            "flowsynmaxi2": {
                "pafr": '''
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
                "pbfr": '''
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
                "sva": '''
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
                "svb": '''
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
                "svcw": '''
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
                '''
            }
        }

    def parsePlutterIn(self,blocks):
        print("WJ - Blocks in: " + str(blocks))
        for key, val in blocks.items():
            for cmnd in val:
                print("Adding " + str(cmnd) + " to block " + key)
                if isinstance(cmnd["value"],int):
                    cmnd["value"]=float(cmnd["value"])
                self.addBlockElement(key,cmnd["device"],cmnd["setting"],cmnd["value"])
        return (self.parseToScript())

    def parseBlockElement(self,device,setting,val):
        if not device in self.commandTemplatesNested:
            #throw
            return
        setThis=copy.deepcopy(self.commandTemplatesNested[device][setting])
        #Valid setting?
        for key in self.varBrackets: #TODO - this is stupid
            if key in setThis:
                if isinstance(val,self.varBrackets[key]):
                    return ((setThis.replace(key,str(val))).replace(" ","")).replace("\n","")
                else:
                    #Throw
                    print("WJ - Error!")

    def addBlock(self,blockName):
        #TODO - Check if block exists then throw
        self.blocks[blockName]=[]
        self.blockNames.append(blockName)

    def addBlockElement(self,blockName,device,setting,val):
        if not blockName in self.blocks:
            self.addBlock(blockName)
        self.blocks[blockName].append(self.parseBlockElement(device,setting,val))
        
    def parseToScript(self):
        if len(self.blockNames) != 0:  
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
            return self.output
        else:
            print("WJ - No blocks!")

            
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
    #automation.addBlockElement("block_1","sf10vapourtec1","fr",1.0)
    #automation.addBlockElement("block_1","WaitUntil",50.0)
    #automation.addBlockElement("block_1","flowsynmaxi1sva",False)
    
    #automation.addBlockElement("block_2","sf10vapourtec2fr",1.0)
    #automation.addBlockElement("block_2","flowsynmaxi2pbfr",1.0)
    #automation.addBlockElement("block_3","Delay",100.0)
    #automation.addBlockElement("block_2","flowsynmaxi1","svcw",True)
    theseBlocks={"myBlock_1":[{"device":"hotcoil1","setting":"temp","value":3},{"device":"Delay","setting":"sleepTime","value":34.5}],"myBlock_2":[{"device":"sf10vapourtec1","setting":"fr","value":3.1}]}    
    automation.parsePlutterIn(theseBlocks)
    print(automation.parseToScript())
    #automation.saveBlocksToFile(save_directory=r"C:\Python_Projects\FluxiDominus_dev\devJunk")    
    #automation.saveBlocksToFile(save_directory=r"C:\Python_Projects\FluxiDominus_dev\devJunk")
    
    '''
    Output:
    
    myBlock_123=[{"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 1.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 15}}];
    myBlock_456=[{"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpAFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}];
    '''
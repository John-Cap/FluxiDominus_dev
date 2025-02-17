#import json
import copy
import os

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
                    "deviceName":"sf10Vapourtec1",
                    "inUse":True,
                    "connDetails":{
                        "serialCom":{
                            "port":"/dev/ttyUSB0",
                            "baud":9600,
                            "dataLength":8,
                            "parity":"N",
                            "stopbits":1
                        }
                    },
                    "settings":{"command":"SET","mode":"FLOW","flowrate":>float<},
                    "topic":"subflow/sf10vapourtec1/cmnd",
                    "client":"client"
                }
            ''',
            "sf10vapourtec2_fr":'''
                {
                    "deviceName":"sf10Vapourtec2",
                    "inUse":True,
                    "connDetails":{
                        "serialCom":{
                            "port":"/dev/ttyUSB0",
                            "baud":9600,
                            "dataLength":8,
                            "parity":"N",
                            "stopbits":1
                        }
                    },
                    "settings":{"command":"SET","mode":"FLOW","flowrate":>float<},
                    "topic":"subflow/sf10vapourtec2/cmnd",
                    "client":"client"
                }
            ''',
            
            #Hotcoils
            "hotcoil1_temp":'''
                {
                    "deviceName":"hotcoil1",
                    "inUse":True,
                    "connDetails":{
                        "ipCom":{
                            "addr":"192.168.1.213",
                            "port":81
                        }
                    },
                    "settings": {"command":"SET","temp":>float<},
                    "topic":"subflow/hotcoil1/cmnd",
                    "client":"client"
                }
            ''',
            "hotcoil2_temp":'''
                {
                    "deviceName":"hotcoil2",
                    "inUse":True,
                    "connDetails":{
                        "ipCom":{
                            "addr":"192.168.1.202", !!Change IP
                            "port":81
                        }
                    },
                    "settings": {"command":"SET","temp":>float<},
                    "topic":"subflow/hotcoil2/cmnd",
                    "client":"client"
                }
            ''',
            
            #Hotchips
            "hotchip1_temp":''' #TODO
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
                    "inUse":True,
                    "connDetails": {
                        "ipCom": {
                            "addr": "192.168.1.202",
                            "port": 80
                        }
                    },
                    "settings": {
                        "command": "SET",
                        "subDevice": "PumpAFlowRate",
                        "value": >float<
                    },
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi1_pbfr":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse":True,
                    "connDetails": {
                        "ipCom": {
                            "addr": "192.168.1.202",
                            "port": 80
                        }
                    },
                    "settings": {
                        "command": "SET",
                        "subDevice": "PumpBFlowRate",
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
                    "settings":{"command":"SET", "subDevice":"FlowSynValveA", "value":>bool<},
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi1_svb":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings":{"command":"SET","subDevice":"FlowSynValveB","value":>bool<},
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
            "flowsynmaxi1_svia":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings":{"command":"SET", "subDevice":"FlowSynInjValveA", "value": >bool<},
                    "topic":"subflow/flowsynmaxi1/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi1_svib":'''
                {
                    "deviceName": "flowsynmaxi1",
                    "inUse": True,
                    "settings":{"command":"SET", "subDevice":"FlowSynInjValveB", "value": >bool<},
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
            "flowsynmaxi2_svia":'''
                {
                    "deviceName": "flowsynmaxi2",
                    "inUse": True,
                    "settings":{"command":"SET", "subDevice":"FlowSynInjValveA", "value": >bool<},
                    "topic":"subflow/flowsynmaxi2/cmnd",
                    "client":"client"
                }
            ''',
            "flowsynmaxi2_svib":'''
                {
                    "deviceName": "flowsynmaxi2",
                    "inUse": True,
                    "settings":{"command":"SET", "subDevice":"FlowSynInjValveB", "value": >bool<},
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
                "fr":self.commandTemplates["sf10vapourtec1_fr"]
            },
            "sf10vapourtec2": {
                "fr":self.commandTemplates["sf10vapourtec2_fr"]
            },
            "hotcoil1": {
                "temp":self.commandTemplates["hotcoil1_temp"]
            },
            "hotcoil2": {
                "temp":self.commandTemplates["hotcoil2_temp"]
            },
            "hotchip1": {
                "temp":self.commandTemplates["hotchip1_temp"]
            },
            "hotchip2": {
                "temp":self.commandTemplates["hotchip2_temp"]
            },
            "flowsynmaxi1": {
                "pafr":self.commandTemplates["flowsynmaxi1_pafr"],
                "pbfr":self.commandTemplates["flowsynmaxi1_pbfr"],
                "sva":self.commandTemplates["flowsynmaxi1_sva"],
                "svb":self.commandTemplates["flowsynmaxi1_svb"],
                "svcw":self.commandTemplates["flowsynmaxi1_svcw"],
                "svia":self.commandTemplates["flowsynmaxi1_svia"],
                "svib":self.commandTemplates["flowsynmaxi1_svib"]
            },
            "flowsynmaxi2": {
                "pafr":self.commandTemplates["flowsynmaxi2_pafr"],
                "pbfr":self.commandTemplates["flowsynmaxi2_pbfr"],
                "sva":self.commandTemplates["flowsynmaxi2_sva"],
                "svb":self.commandTemplates["flowsynmaxi2_svb"],
                "svcw":self.commandTemplates["flowsynmaxi2_svcw"],
                "svia":self.commandTemplates["flowsynmaxi2_svia"],
                "svib":self.commandTemplates["flowsynmaxi2_svib"]
            }
        }

    def parsePlutterIn(self,blocks):
        #print("WJ - Blocks in: " + str(blocks))
        for key, val in blocks.items():
            for cmnd in val:
                #print("Adding " + str(cmnd) + " to block " + key)
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
            self.output=""
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
            #print(self.output)
            self.blocks={}
            self.blockNames=[]
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
    print(1)
    automation.addBlockElement("block_1","sf10vapourtec1","fr",1.0)
    print(2)
    automation.addBlockElement("block_1","WaitUntil","timeout",50.0)
    print(3)
    automation.addBlockElement("block_1","flowsynmaxi1","sva",False)
    print(4)
    automation.addBlockElement("block_2","sf10vapourtec2","fr",1.0)
    automation.addBlockElement("block_2","flowsynmaxi2","pbfr",1.0)
    automation.addBlockElement("block_3","Delay","sleepTime",100.0)
    automation.addBlockElement("block_2","flowsynmaxi1","svcw",True)

    print(automation.parseToScript())
    #automation.saveBlocksToFile(save_directory=r"C:\Python_Projects\FluxiDominus_dev\devJunk")    
    #automation.saveBlocksToFile(save_directory=r"C:\Python_Projects\FluxiDominus_dev\devJunk")
    
    '''
    Output:
    
    myBlock_123=[{"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 1.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 15}}];
    myBlock_456=[{"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpAFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}];
    '''
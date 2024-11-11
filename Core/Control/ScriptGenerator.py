#import json
import copy
import os

from Config.Data.hardcoded_command_templates import HardcodedCommandTemplates

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

        self.commandTemplatesNested = HardcodedCommandTemplates.commandTemplatesNested
        
    def parsePlutterIn(self,blocks):
        #print("WJ - Blocks in: " + str(blocks))
        for key, val in blocks.items():
            for cmnd in val:
                #print("Adding " + str(cmnd) + " to block " + key)
                if isinstance(cmnd["value"],bool):
                    pass
                elif isinstance(cmnd["value"],int):
                    #print('WJ - ' + str(cmnd["value"]) + ' is an int')
                    cmnd["value"]=float(cmnd["value"])
                self.addBlockElement(key,cmnd["device"],cmnd["setting"],cmnd["value"])
        return (self.parseToScript())

    def parseBlockElement(self,device,setting,val):
        if not device in self.commandTemplatesNested:
            print('WJ - Device not found!!')
            return
        setThis=copy.deepcopy(self.commandTemplatesNested[device][setting])
        #Valid setting?
        for key in self.varBrackets: #TODO - this is stupid
            if key in setThis:
                #print('WJ - Val is ' + str(val))
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
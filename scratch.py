import json
import os
import random
import paho.mqtt.client as mqtt
from Core.Control.Commands import Delay
from Core.Utils.Utils import Utils

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
        self.devices = {
            "flowsynmaxi2": {
                "FlowSynValveA": {
                    "command": "SET",
                    "value": [True, False]
                },
                "FlowSynValveB": {
                    "command": "SET",
                    "value": [True, False]
                },
                "FlowCWValve": {
                    "command": "SET",
                    "value": [True, False]
                },
                "PumpBFlowRate": {
                    "command": "SET",
                    "value": "float"  # any float
                },
                "PumpAFlowRate": {
                    "command": "SET",
                    "value": "float"  # any float
                }
            },
            "sf10Vapourtec1": {
                "command": "SET",
                "mode": "FLOW",
                "flowrate": "float"  # any float
            },
            "hotchip1":{
                "command":"SET",
                "temp": "float"
            },
            "hotchip2":{
                "command":"SET",
                "temp": "float"
            },
            "hotcoil1":{
                "command":"SET",
                "temp": "float"
            },
            "hotcoil2":{
                "command":"SET",
                "temp": "float"
            }
        }
        self.blockCounter = 1
        self.generatedBlocks = {}
        self.blocksString=""
        self.customCommandsInst = CustomCommands()
        self.customCommandsInst.registerCommand(Delay)
        
    def convertJsonToPython(self,string):
        replacements = {
            "true": "True",
            "false": "False",
            "null": "None"
        }
        for jsonValue, pythonValue in replacements.items():
            string = string.replace(jsonValue, pythonValue)
        return string.replace("'",'"')

    def generateBlock(self, deviceName, subDevice, value):
        value=Utils().parseValue(value)
        if deviceName in self.customCommandsInst.commands:
            if isinstance(value,str):
                value=eval(value)
            for _x in value:
                value[_x]=eval(value[_x])
            jsonBlock = {
                deviceName: value #{"Delay":{"initTimestamp":None,"sleepTime":20}}
            }
            #print("DeviceName and.. " + str(deviceName) + " " + str(value))
        elif deviceName in self.devices:
            if deviceName == "flowsynmaxi2":
                if subDevice not in self.devices[deviceName]:
                    raise ValueError(f"Sub-device '{subDevice}' not found for device {deviceName}")
                setting = self.devices[deviceName][subDevice]
                if setting["value"] == "float" and not (isinstance(value, float) or isinstance(value, int)):
                    raise ValueError("Setting value must be a float!")
                elif setting["value"] != "float" and value not in setting["value"]:
                    raise ValueError(f"Invalid value for {subDevice}!")

                jsonBlock = {
                    "deviceName": deviceName,
                    "inUse": True,
                    "settings": {
                        "subDevice": subDevice,
                        "command": setting["command"],
                        "value": value
                    },
                    "topic": f"subflow/flowsynmaxi2/cmnd",
                    "client": "client"
                }

            elif deviceName == "sf10Vapourtec1":
                setting = self.devices[deviceName]
                if not (isinstance(value, float) or isinstance(value, int)):
                    raise ValueError("Setting value must be a float or int!")

                jsonBlock = {
                    "deviceName": deviceName,
                    "inUse": True,
                    "settings": {
                        "command": setting["command"],
                        "mode": setting["mode"],
                        "flowrate": value
                    },
                    "topic": f"subflow/{deviceName.lower()}/cmnd",
                    "client": "client"
                }
            elif "hotchip" in deviceName or "hotcoil" in deviceName:
                setting = self.devices[deviceName]
                if not (isinstance(value, float) or isinstance(value, int)):
                    raise ValueError("Setting value must be a float or int!")

                jsonBlock = {
                    "deviceName": deviceName,
                    "inUse": True,
                    "settings": {
                        "command": setting["command"],
                        "temp": value
                    },
                    "topic": f"subflow/{deviceName}/cmnd",
                    "client": "client"
                }
        else:
            raise ValueError(f"Device '{deviceName}' not found!")

        return jsonBlock

    def addBlock(self, deviceSettingsList, blockName=""):
        print("WJ - 'deviceSettingsList': " + str(deviceSettingsList))
        _received=[]
        for _x in deviceSettingsList:
            _received.append([_x["device"],_x["command"],_x["value"]])
        if blockName == "":
            blockName = f"anonBlock_{self.blockCounter}"
            self.blockCounter += 1

        self.generatedBlocks[blockName] = [self.generateBlock(device, subDevice, value) for device, subDevice, value in _received]

        #self.saveBlocksToFile()

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
                blocks = ';\n'.join([
                    f"{name}={json.dumps(block)}"
                    for name, block in self.generatedBlocks.items()
                ]) + ';'
                blocks = self.convertJsonToPython(blocks)
                self.blocksString=blocks
                file.write(blocks)
            print(f"File saved successfully at {file_path}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

# Define custom command classes
# Example usage
if __name__ == "__main__":
    automation = FlowChemAutomation()
    automation.customCommandsInst.registerCommand(Delay)

    # Add blocks using the new method


    _max=2
    _min=0
    _i=30
    while 0 < _i:
        _max=round(random.uniform(0.05,1.95),2)
        _min=round(2-_max,2)
        automation.addBlock(
            [
                {"device":"flowsynmaxi2", "command":"PumpBFlowRate", "value":str(_max)}, #Example of device-specific commands. The array contains values that will come from Flutter 
                {"device":"sf10Vapourtec1", "command":'None', "value":str(_min)},
                {'device': 'Delay', 'command': 'None', 'value': '{"initTimestamp":"None","sleepTime":"15"}'}
            ]
        )
        
        _i-=1
    automation.addBlock(
        [
            {"device":"flowsynmaxi2", "command":"PumpBFlowRate", "value":'0'}, #Example of device-specific commands. The array contains values that will come from Flutter 
            {"device":"sf10Vapourtec1", "command":'None', "value":'0'}
        ]
    )        
    def mess(client, userdata, message):
        print(eval(message.payload))
    def con(client, userdata, connect_flags, reason_code):
        print("Connected!")
    # Save blocks to a file
    automation.saveBlocksToFile('automation_script.fdp',r"C:/Python_Projects/fluxidominus_dev")
    print(automation.blocksString)
    _client=mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
    _client.on_message=mess
    _client.on_connect=con
    
    _client.connect("146.64.91.174",1883)
    
    #_client.loop_forever()
    #while not _client.is_connected():
        #pass
    #print("Connected!")
    _client.subscribe(topic="test/settings/")
    _client.publish(topic="test/settings/",payload=json.dumps({"script":automation.blocksString}))
    _client.loop_forever()
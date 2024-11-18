
#General class for a pump

class PumpBase:
    def __init__(self,deviceName,settingName,pumpName=None,pumpAlias="",flowrateMax = None,flowrateMin = None,pressureMax = None) -> None:
        self.deviceName=deviceName
        self.settingName=settingName
        self.pumpAlias=pumpAlias
        self.flowrate = 0
        self.flowrateMax = flowrateMax
        self.flowrateMin = flowrateMin
        self.pressureMax = pressureMax #TODO - Class Pressure
        self.status = False #TODO - false -> off, true -> available
        
        if not pumpName:
            self.pumpName=deviceName + "_" + settingName
        else:
            self.pumpName=pumpName

    def setFlowrate(self,rate):
        self.flowrate = rate

class Pump(PumpBase):
    def __init__(self, deviceName, settingName, pumpName=None, pumpAlias="", flowrateMax=None, flowrateMin=None, pressureMax=None) -> None:
        super().__init__(deviceName, settingName, pumpName, pumpAlias, flowrateMax, flowrateMin, pressureMax)

class SF10(Pump):
    def __init__(self,settings) -> None:
        super().__init__()

        self.type = "sf10Vapourtec1"

        '''
        self.input = eval(input)
        self.component = self.input["payload"]
        self.lastMessageID = self.input["_msgid"]
        self.settings = self.input["settings"]
        self.state = self.input["state"]
        self.valve = self.input["valve"]
        self.allParams = {
            "component":self.component,
            "lastMessageID":self.lastMessageID,
            "settings":self.settings,
            "state":self.state,
            "valve":self.valve
        }
        '''
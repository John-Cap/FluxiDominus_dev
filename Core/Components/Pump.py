
#General class for a pump

class PumpBase:
    def __init__(self) -> None:
        self.type = ""
        self.flowrate = None #TODO - Class Flowrate
        self.flowrateMax = None
        self.flowrateMin = None
        self.pressureMax = None #TODO - Class Pressure
        self.status = False #TODO - false -> off, true -> on

    def setFlowrate(self,rate):
        self.flowrate = rate

class Pump(PumpBase):
    def __init__(self) -> None:
        super().__init__()

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
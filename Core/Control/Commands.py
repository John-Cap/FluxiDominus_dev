from datetime import datetime
import enum
import json
import time

import numpy as np

from Core.Communication.IO import IO
from Core.Diagnostics.Logging import Diag_log

######################################################
#Procedures and items

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

#Item

class Item:
    def __init__(self,instruction="UNDEFINED",completionCode="False") -> None:
        self.instruction=instruction
        self.completionCode=completionCode #separate class?
        self.codeDescription=""
    def isComplete(self,device,**kwargs):
        namespace = {"device":device,**kwargs}
        return eval(self.completionCode,namespace)
    def setCompletionCode(self,completionCode):
        self.completionCode=completionCode

#Enumerated list of items
class CompletionCodes(enum.Enum):
    TEMP_REACHED="abs(currTemp - targetTemp) < 2"
    FLOWRATE_SET="set == actual"
    VALVE_SWITCHED="set == actual"

class Settings:
    def __init__(self,settings={}) -> None:
        self.settings = settings

    def unpackSettings(self,settings):
        _currentSettings = self.settings
        for _key in settings:
            _currentSettings[_key] = settings[_key]
        return _currentSettings
    
    def getSetting(self,setting):
        return (self.settings[setting])
        
    def setSetting(self,setting,value):
        self.settings[setting]=value
        return (self.settings[setting])
    
    def getAllSettings(self):
        return (self.settings)
    
    def getAllAvailableSettingTypes(self):
        _availableSettings=[]
        for _key in self.settings:
            _availableSettings.append(_key)
        return _availableSettings
    
class State:
    def __init__(self,state={}) -> None:
        self.state = state

    def unpackState(self,state):
        _currentState = self.state
        for _key in state:
            _currentState[_key] = state[_key]
        return _currentState
    
    def getState(self):
        return (self.state)

    def getStateElement(self,element):
        return (self.state[element])
                
    def setStateElement(self,state,value):
        self.state[state]=value
        return (self.state[state])
    
    def getAllAvailableStateTypes(self):
        _availableState=[]
        for _key in self.state:
            _availableState.append(_key)
        return _availableState

class Devices:
    def __init__(self) -> None:
        self.allDevices={}
    def deviceInitialized(self,deviceName):
        if deviceName in self.allDevices:
            True
        else:
            False
    def addDevice(self,deviceName,deviceType):
        device=Device(deviceName,deviceType)
        self.allDevices[deviceName]=device
    def getDevice(self,deviceName):
        return (self.allDevices[deviceName])

class Device:
    def __init__(self,deviceName,deviceType,settings=Settings(),state=State(),procedure=Procedure()) -> None:
        self.deviceType=deviceType
        self.deviceName=deviceName
        self.settings=settings
        self.procedure=procedure
        self.state=state

    def getStateElement(self,element):
        return self.state.getStateElement(element)
    def getSettings(self):
        return self.settings.allSettings
    def setDeviceSettings(self,settings):
        _theseSettings=settings.getAllSettings()
        self.settings=_theseSettings
        return self.settings
    def setSetting(self,setting,val):
        self.settings.setSetting(setting,val)
    def setStateElement(self,element,val):
        self.state.setStateElement(element,val)
    def currItemComplete(self,**kwargs):
        return (self.procedure.currItemComplete(**kwargs))
    def runProcedure(self):   
        pass

class Command:
    def __init__(self,val) -> None:
        pass

class Configuration:
    def __init__(self, commands, setMessage="Configuration set") -> None:
        self.devices = []
        self.commands = commands
        self.setMessage = setMessage

    def sendMQTT(self, waitForDelivery=False,debugDelaySkip=False):
        if (len(self.commands)) == 0:
            print("No commands left!")
            return
        _currentCommand = (self.commands[0])
        if "Delay" in _currentCommand:
            if _currentCommand["Delay"].elapsed() or debugDelaySkip:
                del self.commands[0]
                print("Delay elapsed!")
                return
            else:
                return
        elif "WaitUntil" in _currentCommand:
            if _currentCommand["WaitUntil"].check():
                print("WaitUntil returned True!")
                del self.commands[0]
                return
            else:
                return
        else:
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
            print("Published: " + str(self.commands[0]))
            del self.commands[0]
            return

class TimeChecker:
    def __init__(self,allotted_seconds=0):
        self.allotted_seconds = allotted_seconds
        self.start_time = datetime.now()

    def check_time_elapsed(self):
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()
        return elapsed_seconds > self.allotted_seconds

class Delay:
    def __init__(self,sleepTime=1,initTimestamp=None):
        self.sleepTime=sleepTime
        self.initTimestamp=initTimestamp
        self.saidItOnce=False
    def elapsed(self):
        if not self.saidItOnce:
            self.saidItOnce=True
            #print("Delay started!")
        if self.initTimestamp is None:
            self.initTimestamp=time.time()
        return (time.time() - self.initTimestamp) > self.sleepTime

class IRCategorizer:
    def __init__(self, compound_1_data, compound_2_data, thresholdR=0.9,thresholdB=0.5):
        self.compound_1_data = self._normalize(compound_1_data)
        self.compound_2_data = self._normalize(compound_2_data)
        self.thresholdR = thresholdR
        self.thresholdB=thresholdB

    def categorize(self, ir_scan):
        ir_scan_normalized = self._normalize(ir_scan)
        compound_1_similarity = self.calculateSimilarity(ir_scan_normalized, self.compound_1_data)
        compound_2_similarity = self.calculateSimilarity(ir_scan_normalized, self.compound_2_data)
        if compound_1_similarity > self.thresholdR:
            Diag_log().toLog("Red detected! R/B similarities: " + str([compound_1_similarity,compound_2_similarity]))
            return "Red"
        elif compound_2_similarity > self.thresholdB:
            Diag_log().toLog("Blue detected! R/B similarities: " + str([compound_1_similarity,compound_2_similarity]))
            return "Blue"
        else:
            Diag_log().toLog("Baseline detected! R/B similarities: " + str([compound_1_similarity,compound_2_similarity]))
            return "Baseline"

    def calculateSimilarity(self, ir_scan1, ir_scan2):
        # Simple similarity calculation (e.g., cosine similarity)
        return np.dot(ir_scan1, ir_scan2) / (np.linalg.norm(ir_scan1) * np.linalg.norm(ir_scan2))

    def _normalize(self, data):
        # Normalize the data to have zero mean and unit variance
        return (data - np.mean(data)) / np.std(data)

class IrSwitch:
    def __init__(self,currentLock="Baseline"):
        self.currentLock=currentLock
        self.makeSures=2
        self.makeSuresOrig=2
    def statusChanged(self,input):
        if self.currentLock != input:
            if self.makeSures - 1 <= 0:
                #Diag_log().toLog(datetime.now().time().strftime("%H:%M:%S") + "->IR status changed from " + self.currentLock + " to " + input)
                self.makeSures=self.makeSuresOrig
                self.currentLock=input
                return True
            else:
                self.makeSures-= 1
                return False
        else:
            self.makeSures=self.makeSuresOrig
            return False

class Condition:
    def __init__(self) -> None:
        pass
    def check(self):
        return False

class RedDetected(Condition):
    def __init__(self,irSwitch=IrSwitch()) -> None:
        super().__init__()
        self.irSwitch=irSwitch
    def check(self):
        return self.irSwitch.currentLock=="Red"

class BaselineDetected(Condition):
    def __init__(self,irSwitch=IrSwitch()) -> None:
        super().__init__()
        self.irSwitch=irSwitch
    def check(self):
        return self.irSwitch.currentLock=="Baseline"

class ColourChanged(Condition):
    def __init__(self,irSwitch=IrSwitch()) -> None:
        super().__init__()
        self.irSwitch=irSwitch
        self.thisLock=self.irSwitch.currentLock
    def check(self):
        return self.irSwitch.currentLock!=self.thisLock

class BlueDetected(Condition):
    def __init__(self,irSwitch=IrSwitch()) -> None:
        super().__init__()
        self.irSwitch=irSwitch
    def check(self):
        return self.irSwitch.currentLock=="Blue"

class SlugCollected(Condition):
    def __init__(self,slug) -> None:
        super().__init__()
        self.slug=slug
    def check(self):
        return self.slug.collected
    
class WaitUntil:
    def __init__(self, conditionFunc, conditionParam, timeout=60, initTimestamp=None, completionMessage="WaitUntil complete"):
        self.conditionFunc = conditionFunc
        self.conditionParam = conditionParam
        self.timeout = timeout
        self.initTimestamp = None
        self.completionMessage = completionMessage
        self.saidItOnce=False

    def check(self):
        if not self.saidItOnce:
            self.saidItOnce=True
            print("WaitUntil started!")
        if self.initTimestamp is None:
            self.initTimestamp = time.time()
        current_time = time.time()
        if current_time - self.initTimestamp > self.timeout:
            print("WaitUntil timed out!")
            return True
        #print(self.conditionFunc(self.conditionParam()))
        _b=self.conditionFunc(self.conditionParam())
        if _b:
            print("WaitUntil function "+str(self.conditionFunc)+" is True!")
        return _b

class TempReached:
    def __init__(self,condition,timeout=60,initTimestamp=datetime.now().time(),completionMessage="WaitUntil complete"):
        self.condition=condition
        self.timeout=timeout
        self.initTimestamp=initTimestamp
        self.completionMessage=completionMessage
    def check(self):
        return self.condition.check()

######################################
#Examples
'''
#Heating device
theseSettings=Settings({"temp":15})
thisState=State({"temp":22.34,"state":"ON"})
#Pump --> {"deviceName":"sf10Vapourtec1","deviceType":"Pump","cmnd":"","settings":{"mode":"","flowrate":0,"pressure":0,"dose":0,"gasflowrate":0,"rampStartRate":0,"rampStopRate":0,"rampTime":0},"state":{"status":"STOP","valve":"A","response":""},"timestamp":"1705308554579"}
pumpSettings=Settings({"mode":"","flowrate":0,"pressure":0,"dose":0,"gasflowrate":0,"valve":"B","rampStartRate":0,"rampStopRate":0,"rampTime":0})
pumpState=State({"status":"STOP","valve":"A","response":""})

_item_1=Item("Temperature reached",CompletionCodes.TEMP_REACHED.value)
#_item_2=Item("Flowrate adjusted successfully",CompletionCodes.FLOWRATE_SET.value)
_item_3=Item("Valve switched",CompletionCodes.VALVE_SWITCHED.value)
thisProcedure=Procedure("bobProcedure",[_item_1,_item_3])
thisDevice=Device("nmr1","bobDevice",settings=theseSettings,state=thisState,procedure=thisProcedure)

theseKwargs={'currTemp':thisState.getStateElement('temp'),'targetTemp':theseSettings.getSetting("temp")}
thoseKwargs={'actual':pumpState.getStateElement('valve'),'set':pumpSettings.getSetting("valve")}

# Calling the is_complete method with device and additional_kwargs
while True:
    result = thisDevice.currItemComplete(**theseKwargs)

    print(result)  # This will print True since kwargVar_1 is greater than 5
    if result:
        print("Target temp reached")
        break
    _newTemp=eval(input("New temp: "))
    thisDevice.setStateElement("temp",_newTemp)
    theseKwargs={'currTemp':thisDevice.getStateElement('temp'),'targetTemp':theseSettings.getSetting("temp")}

while True:
    result = thisDevice.currItemComplete(**thoseKwargs)
    print(result)  # This will print True since kwargVar_1 is greater than 5
    if result:
        print("Target valve selected")
        break
    _newValve=(input("New valve: "))
    thisDevice.setStateElement("valve",_newValve)
    thoseKwargs={'actual':pumpState.getStateElement('valve'),'set':pumpSettings.getSetting("valve")}


#Multiple inputs

#_deviceNames=["nmr_1","pump_1","pump_2","pump_3","hotChip_1","hotCoil_1"]
_deviceNames=["nmr_1"]
_allDevices=Devices()

while True:
    _thisDevice=input("Add new identified device: ")
    if not _allDevices.deviceInitialized(_thisDevice):
        _allDevices.addDevice(_thisDevice,"GENERAL")
    
    print(_allDevices.allDevices)
'''

from Core.Fluids.FlowPath import BPR, IR, Chip, Coil, CompoundDevice, FlowOrigin, FlowTerminus, Pump, TPiece, Tubing, Valve

class FlowsynMaxi(CompoundDevice):
    def __init__(self):
        self.subDevices={
            "pumpA":Pump(volume=5), #TODO - check hierdie volumes
            "pumpB":Pump(volume=5),
            "valveCW":Valve(volume=0.1),
            "valveSolvReagA":Valve(volume=0.1),
            "valveSolvReagB":Valve(volume=0.1),
            "heater1":None,
            "heater2":None
        }

class VapourtecR4(CompoundDevice):
    def __init__(self):
        self.subDevices={
            "pumpA":Pump(volume=5), #TODO - check hierdie volumes
            "pumpB":Pump(volume=5),
            "valveCW":Valve(volume=0.1),
            "valveSolvReagA":Valve(volume=0.1),
            "valveSolvReagB":Valve(volume=0.1)
        }
        
class ReactIR702L1(IR):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
        
class UniqsisHotcoil(Coil):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)

class UniqsisHotchip(Chip):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)

class StandardConfiguratedDevices:
    deviceClasses={
        "FlowsynMaxi":FlowsynMaxi,
        "VapourtecR4":VapourtecR4,
        "ReactIR702L1":ReactIR702L1,
        "UniqsisHotcoil":UniqsisHotcoil,
        "UniqsisHotchip":UniqsisHotchip,
        
        #Generalized
        "Tubing":Tubing,
        "TPiece":TPiece,
        "Coil":Coil,
        "Valve":Valve,
        "FlowOrigin":FlowOrigin,
        "FlowTerminus":FlowTerminus,
        "IR":IR,
        "Chip":Chip,
        "Pump":Pump,
        "BPR":BPR
    }

    @staticmethod
    def initializeComponent(component,params):
        return (StandardConfiguratedDevices.deviceClasses[component](params[0],params[1]))

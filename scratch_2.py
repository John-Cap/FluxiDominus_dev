#Flow trackerscript
import datetime
import threading
import time

from Core.Fluids.FlowPath import IR, Chip, Coil, FlowAddress, FlowOrigin, FlowPath, FlowTerminus, Pump, Slugs, Tubing, Valve


_path=FlowPath()

#Stocks + pumps up to t piece
_maxiColourStock=FlowOrigin(volume=0,name="MAXI_COLOUR",flowrateIn=0)
_maxiSolv=FlowOrigin(volume=0,name="MAXI_SOLV",flowrateIn=1/60)
_SF10ColourStock=FlowOrigin(volume=0,name="SF10_COLOUR",flowrateIn=0)
_SF10Solv=FlowOrigin(volume=0,name="SF10_SOLV",flowrateIn=0)
#Pumps
_maxiB=Pump(volume=0.5,name="PUMP_MAXI_B",flowrateIn=0)
_SF10=Pump(volume=0.5,name="PUMP_SF10",flowrateIn=0)
#Valves
_maxiValve=(Valve(volume=0.005,name="MAXI_VALVE"))
_SF10Valve=(Valve(volume=0.005,name="SF10_VALVE"))
_collectValve=(Valve(volume=0.005,name="COLL_VALVE"))
#Mixing chip
_chip=Chip(volume=2,name="MIXING_CHIP",flowrateIn=0)
#Coil
_coil=Coil(volume=25,name="COIL",flowrateIn=0)
#IR
_IR=(IR(volume=0.025,name="IR"))
#Tubing
_tubingToSF10=(Tubing(volume=0.22,name="TUBING_TO_SF10"))
_tubingFromSF10=(Tubing(volume=0.22,name="TUBING_FROM_SF10"))
_tubingToMaxi=(Tubing(volume=0.22,name="TUBING_TO_MAXI"))
_tubingFromMaxi=(Tubing(volume=0.22,name="TUBING_FROM_MAXI"))
_tubingToWC=(Tubing(volume=0.4712,name="TUBING_TO_WC"))
#Terminus
_waste=FlowTerminus(volume=0,name="WASTE")
_collect=FlowTerminus(volume=0,name="COLLECT")

_collectWaste=FlowAddress('TO_WASTE',[],[[_collectValve,"WASTE"]])
_collectColour=FlowAddress('TO_BLUE',[],[[_collectValve,"COLLECT"]])

###################
#Connect components
_maxiColourStock.flowInto(_maxiValve,setNameIn="COLOUR")
_maxiSolv.flowInto(_maxiValve,setNameIn="PUSH")
_SF10ColourStock.flowInto(_SF10Valve,setNameIn="COLOUR")
_SF10Solv.flowInto(_SF10Valve,setNameIn="PUSH")

_maxiValve.flowInto(_tubingToMaxi)
_SF10Valve.flowInto(_tubingToSF10)

_tubingToMaxi.flowInto(_maxiB)
_tubingToSF10.flowInto(_SF10)

_maxiB.flowInto(_tubingFromMaxi)
_SF10.flowInto(_tubingFromSF10)

_tubingFromMaxi.flowInto(_chip)
_tubingFromSF10.flowInto(_chip)

_chip.flowInto(_coil)
_coil.flowInto(_IR)

_IR.flowInto(_tubingToWC)

_tubingToWC.flowInto(_collectValve)

_collectValve.flowInto(_waste,setNameOut="WASTE")
_collectValve.flowInto(_collect,setNameOut="WASTE")

#Create paths
_path.addPath(
    [
        _maxiColourStock,
        _maxiSolv,
        _SF10ColourStock,
        _SF10Solv,
        _tubingToMaxi,
        _tubingToSF10,

        _maxiValve,
        _SF10Valve,

        _maxiB,
        _SF10,

        _tubingFromMaxi,
        _tubingFromSF10,

        _chip,
        _coil,
        _IR,

        _tubingToWC,

        _collectValve,
        _collect,
        _waste
    ]
)

_path.selectPath()
_maxiColourStock.associatedFlowPath=_path
_maxiSolv.associatedFlowPath=_path
_SF10ColourStock.associatedFlowPath=_path
_SF10Solv.associatedFlowPath=_path
'''
for _x in _path.segments:
    print("*********")
    print(_x.name)
    print(_x.inletSets)
    print(_x.outletSets)
    print(_x.inlets)
    print(_x.outlets)
'''
global _currOrigin
_currOrigin=_maxiColourStock
global _currTerminus
_currTerminus=_waste

# Flag variable to indicate whether the thread should continue running
running=True
allSlugs=Slugs()

_intervalStamp=time.perf_counter()

def flowTracker():
    global _intervalStamp
    global _IR
    global running
    global allSlugs
    global _currTerminus
    while running:
        _slug=_currOrigin.dispense()
        allSlugs.slugs.append(_slug)
        print(str(_slug.slugVolume()) + " mL")

        _path.updateFlowrates()
        for _x in _path.segments:
            print(_x.flowrateOut)

        _switched=False
        _now=time.perf_counter()
        _path.timePrev=time.perf_counter()
        while not (_slug.tailHost is _currTerminus):
            _path.advanceSlugs()
            _vol=_slug.slugVolume()
            if _slug.frontHost is _IR and not _switched:
                _currOrigin.terminateDispensing()
                _switched=True
                _stamp=datetime.now()
                print(_stamp.strftime("%H:%M:%S") + "->Flow tracker predicts slug has reached IR!")
            if time.perf_counter()-_intervalStamp>10:
                _intervalStamp=time.perf_counter()
                print("Time: " + str(round(time.perf_counter() - _now, 0)) + " seconds, Fro h/pos: " + str(
                    _slug.frontHost.name) + ", " + str(round(_slug.frontHostPos, 2)) + "/" + str(
                    _slug.frontHost.volume) + " mL, tail h/pos: " + str(_slug.tailHost.name) + ", " + str(
                    round(_slug.tailHostPos, 2)) + "/" + str(_slug.tailHost.volume) + " mL, fr: " + str(
                    round(_slug.frontHost.flowrateOut*60, 2)) + " mL.min-1, slug vol: " + str(
                    round(_vol, 2)) + " mL, vol collected: " + str(round(_slug.collectedVol, 2)) + " mL")

        print("************")
        print(str(time.perf_counter() - _now) + " seconds")
        print("Collected slug volumes")
        for _x in _path.collectedSlugs:
            print(_x.collectedVol)
        print("Slug took " + str(round(time.perf_counter() - _now, 0)) + " seconds to reach terminus")
        print("************")


# Create a thread for running the code
thread=threading.Thread(target=flowTracker)

# Start the thread
thread.start()

while True:
    pass
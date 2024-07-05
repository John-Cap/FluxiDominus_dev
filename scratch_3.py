
import threading
import time

from Core.Fluids.FlowPath import IR, FlowAddress, FlowOrigin, FlowPath, FlowTerminus, Pump, Slugs, TPiece, Tubing, Valve


_path=FlowPath()

###############################################################
# Fluid tracker + flow line
#Stocks + pumps up to t piece
_redStock=FlowOrigin(volume=0,name="RED_STOCK_LINE",flowrateIn=1.0)
_blueStock=FlowOrigin(volume=0,name="BLUE_STOCK_LINE",flowrateIn=1.0)
_pumplineSolv=FlowOrigin(volume=0,name="PUSH_SOLV_LINE",flowrateIn=1.0)
#Pump lines
_pumpline_1=Pump(volume=1.5,name="PUMP_1_LINE")
#Valves
_stocksValve=(Valve(volume=0,name="STOCKS_VALVE"))
_collectValve=(Valve(volume=0,name="COLL_VALVE"))
_RBValve=(Valve(volume=0,name="RB_VALVE"))
#IR
_IR=(IR(volume=0.05,name="IR"))
#TPiece
_Tpiece=(TPiece(volume=0.05,name="T_PIECE"))
#Tubing
_tubingToIR=(Tubing(volume=0.2513,name="TUBING_TO_IR"))
_tubingToWC=(Tubing(volume=0.4712,name="TUBING_TO_WC"))
_tubingToRBC=(Tubing(volume=0.2513,name="TUBING_TO_RBC"))
#Terminus
_waste=FlowTerminus(volume=0,name="WASTE")
_blueCollect=FlowTerminus(volume=0,name="BLUE_COLLECT")
_redCollect=FlowTerminus(volume=0,name="RED_COLLECT")

_collectWaste=FlowAddress('TO_WASTE',[],[[_collectValve,"WASTE"]])
_collectBlue=FlowAddress('TO_BLUE',[],[[_collectValve,"COLLECT"],[_RBValve,"BLUE"]])
_collectRed=FlowAddress('TO_RED',[],[[_collectValve,"COLLECT"],[_RBValve,"RED"]])
###################
#Connect components

#Stock solutions
_redStock.flowInto(_stocksValve,setNameIn="RED",setNameOut="VALVE")
_blueStock.flowInto(_stocksValve,setNameIn="BLUE",setNameOut="VALVE")
_stocksValve.flowInto(_pumpline_1)
_stocksValve.switchToInlets("RED")
#Pumplines
_pumpline_1.flowInto(_Tpiece)
_pumplineSolv.flowInto(_Tpiece)
#Tubing etc to WC
_Tpiece.flowInto(_tubingToIR)
_tubingToIR.flowInto(_IR)
_IR.flowInto(_tubingToWC)
_tubingToWC.flowInto(_collectValve)
_collectValve.flowInto(_waste,setNameOut="WASTE")
_collectValve.flowInto(_tubingToRBC,setNameOut="COLLECT")
_collectValve.switchToOutlets("WASTE")
#R/B collect
_tubingToRBC.flowInto(_RBValve)
_RBValve.flowInto(_blueCollect,setNameOut="BLUE")
_RBValve.flowInto(_redCollect,setNameOut="RED")

#Create paths

_path.addPath(
    [
        _redStock,
        _blueStock,
        _stocksValve,

        _pumpline_1,
        _pumplineSolv,
        _Tpiece,

        _tubingToIR,
        _IR,

        _tubingToWC,
        _collectValve,
        _waste,

        _tubingToRBC,
        _RBValve,
        _blueCollect,
        _redCollect
    ]
)

#_path.addPath([_redStock,_blueStock,_stocksValve,_pumpline_1])
_path.selectPath()
_redStock.associatedFlowPath=_path
_blueStock.associatedFlowPath=_path
_pumplineSolv.associatedFlowPath=_path

for _x in _path.segments:
    print("*********")
    print(_x.name)
    print(_x.inletSets)
    print(_x.outletSets)
    print(_x.inlets)
    print(_x.outlets)

_currOrigin=_redStock
_currTerminus=_waste

# Flag variable to indicate whether the thread should continue running
running=True
trackingCycleComplete=False
allSlugs=Slugs()

_slugVol=1

def run_code():
    global running
    global allSlugs
    global trackingCycleComplete
    while running:
        while trackingCycleComplete:
            pass

        _slug=_stocksValve.inlets[0].dispense()
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
            print("Time: " + str(round(time.perf_counter() - _now, 0)) + " seconds, Fro h/pos: " + str(
                _slug.frontHost.name) + ", " + str(round(_slug.frontHostPos, 2)) + "/" + str(
                _slug.frontHost.volume) + " mL, tail h/pos: " + str(_slug.tailHost.name) + ", " + str(
                round(_slug.tailHostPos, 2)) + "/" + str(_slug.tailHost.volume) + " mL, fr: " + str(
                round(_slug.frontHost.flowrateOut*60, 2)) + " mL.min-1, slug vol: " + str(
                round(_vol, 2)) + " mL, vol collected: " + str(round(_slug.collectedVol, 2)) + " mL")
            if not _switched and _vol > _slugVol:
                _stocksValve.inlets[0].dispensing=False
                _switched=True
        print("************")
        print(str(time.perf_counter() - _now) + " seconds")
        print("Collected slug volumes")
        for _x in _path.collectedSlugs:
            print(_x.collectedVol)
        print("Slug took " + str(_now-_slug.reachedTerminusAt) + " seconds to reach terminus")
        print("************")

        trackingCycleComplete=True

# Create a thread for running the code
thread=threading.Thread(target=run_code)

# Start the thread
thread.start()

while True:
    pass;
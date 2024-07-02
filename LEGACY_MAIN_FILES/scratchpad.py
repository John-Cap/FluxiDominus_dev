#Flow jiggler
from Core.Fluids.FlowPath import FlowJiggler, Pump


_pump_1=Pump(volume=0.5,name="PUMP_1",flowrateIn=2)
_pump_2=Pump(volume=0.5,name="PUMP_2",flowrateIn=1)
_pump_3=Pump(volume=0.5,name="PUMP_3",flowrateIn=3)
_jiggler=FlowJiggler(
    flowrates={
        _pump_1.id:_pump_1.flowrateIn,
        _pump_2.id:_pump_2.flowrateIn,
        _pump_3.id:_pump_3.flowrateIn
    },
    pumps=[_pump_1,_pump_2,_pump_3]
)
_jiggler.setFlowKeepConst(_pump_1,1.79)
for _x,_y in _jiggler.flowrates.items():
    print(str(_x)+" "+str(_y))
print("")
_jiggler.setFlowKeepConst(_pump_2,2)
for _x,_y in _jiggler.flowrates.items():
    print(str(_x)+" "+str(_y))
print("")
_jiggler.setFlowKeepConst(_pump_3,0.5)
for _x,_y in _jiggler.flowrates.items():
    print(str(_x)+" "+str(_y))
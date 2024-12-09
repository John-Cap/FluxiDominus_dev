import time
import threading
from Core.Utils.Utils import Utils

class FlowAddress:
    def __init__(self,name,inletsSett=[],outletsSett=[]) -> None: #inlets
        self.name=name
        self.inletsSett=inletsSett
        self.outletsSett=outletsSett
    def setAddress(self,inletsSett,outletsSett):
        self.inletsSett=inletsSett
        self.outletsSett=outletsSett

class VolumeObject:

    #Class var
    idCounter=0

    def __init__(self,volume=None,inlets=None,outlets=None,name=None,deviceName=None,deviceType=None,flowrateOut=None,flowrateIn=None,slugs=None,lastAdvance=None,outletSets=None,inletSets=None,currOutlets=None,currInlets=None,remainder=None,settings=None,state=None,availableCommands=None,dispensing=False,associatedFlowPath=None) -> None:
        self.volume=volume
        self.inlets=inlets
        self.outlets=outlets
        self.name=name
        self.deviceName=deviceName
        self.deviceType=deviceType
        self.flowrateIn=flowrateIn
        self.flowrateOut=flowrateOut
        self.slugs=slugs
        self.lastAdvance=lastAdvance
        self.outletSets=outletSets
        self.currOutlets=currOutlets
        self.dispensing=dispensing
        self.associatedFlowPath=associatedFlowPath
        self.inletSets=inletSets
        self.currInlets=currInlets
        self.remainder=remainder
        #Boolean flags
        self.flowrateShifted=False
        #Settings and commands
        self.settings=settings
        self.state=state
        self.availableCommands=availableCommands
        #Hashmap id generator
        self.id=VolumeObject.idCounter
        VolumeObject.idCounter+=1
    
    #def addCommand(self,command=Command()):
    #    pass
    
    #def setFlowrate(self,command=Command()):
    #    pass

    def dispense(self,targetTerminus=None):
        if not (self.dispensing) and not self.associatedFlowPath is None:
            print(str(self.name) + " is busy dispensing!")
            self.dispensing=True
            _return=Slug(frontHost=self,tailHost=self,frontHostPos=0,tailHostPos=0,targetTerminus=targetTerminus)
            self.associatedFlowPath.slugs.append(_return)
            return _return
    def terminateDispensing(self):
        if self.dispensing:
            self.dispensing=False

    def addInlet(self,comp,setName="DEFAULT"):
        _thisInletSet=self.getInletSet(setName)
        if len(_thisInletSet)==0:
            print(str(self)+"InletHere1")
            self.inletSets[setName]=[comp]
            self.inlets=self.inletSets[setName]
            #print(self.inletSets)          
            self.flowrateShifted=True
        elif len(_thisInletSet)==1 and _thisInletSet[0] is None:
            print(str(self)+"InletHere2")            
            self.inletSets[setName]=[comp]
            self.inlets=self.inletSets[setName]
            self.flowrateShifted=True
        else:
            print(str(self)+"InletHere3")
            if not comp in _thisInletSet:
                _thisInletSet.append(comp)
    def addOutlet(self,comp,setName="DEFAULT"):
        _thisOutletSet=self.getOutletSet(setName)
        if len(_thisOutletSet)==0:
            print(str(self)+"OutletHere1")            
            _thisOutletSet.append(comp)
            self.outlets=_thisOutletSet
            #print(self.getOutletSet(setName))
            self.flowrateShifted=True
        elif len(_thisOutletSet)==1 and _thisOutletSet[0] is None:
            print(str(self)+"OutletHere2")
            _thisOutletSet=[(comp)]
            self.outlets=_thisOutletSet
            self.flowrateShifted=True
        else:
            print(str(self)+"OutletHere3")
            if not comp in _thisOutletSet:
                _thisOutletSet.append(comp)

    def flowInto(self,outlet,setNameIn="DEFAULT",setNameOut="DEFAULT"):
        self.addOutlet(outlet,setNameOut)
        outlet.addInlet(self,setNameIn)
            
    def addInletSet(self,setName="DEFAULT",inlets=[],overwrite=True):
        if not setName in self.inletSets:
            self.inletSets[setName]=inlets
            return self.inletSets[setName]
        elif overwrite:
            self.inletSets[setName]=inlets
            return self.inletSets[setName]
        else:
            return KeyError.add_note("Inlet-set name already used")
    def addOutletSet(self,setName="DEFAULT",outlets=[],overwrite=True):
        if not setName in self.outletSets:
            self.outletSets[setName]=outlets
            return self.outletSets[setName]
        elif overwrite:
            self.outletSets[setName]=outlets
            return self.outletSets[setName]          
        else:
            return KeyError.add_note("Outlet-set name already used")

    def switchToInlets(self,setName="DEFAULT"):
        if setName in self.inletSets:
            self.inlets=self.inletSets[setName]
    def switchToOutlets(self,setName="DEFAULT"):
        if setName in self.outletSets:
            self.outlets=self.outletSets[setName]

    def getInletSet(self,setName="DEFAULT"):
        if self.inletSets is None:
            self.inletSets={}
        if setName in self.inletSets:
            return self.inletSets[setName]
        else:
            self.inletSets[setName]=[]
            return self.inletSets[setName]
    def getOutletSet(self,setName="DEFAULT"):
        if self.outletSets is None:
            self.outletSets={}
        if setName in self.outletSets:
            return self.outletSets[setName]
        else:
            self.outletSets[setName]=[]
            return self.outletSets[setName]
        
    def switchToDefaultInlets(self):
        if len(self.inletSets) <= 1:
            return self.inlets
        else:
            self.switchToInlet("DEFAULT")
            return self.inlets
    def switchToDefaultOutlets(self):
        if len(self.outletSets) <= 1:
            return self.outlets
        else:
            self.switchToOutlets("DEFAULT")
            return self.outlets
        
    def cumulativeFlowrates(self):
        if not self.inlets:
            self.inlets = []

        # If no inputs, propagate flowrateOut directly from flowrateIn
        if len(self.inlets) == 0:
            self.flowrateOut = self.flowrateIn
            return

        # Calculate flowrate from all resolved inlets
        _flowrate = 0
        unresolved = False

        for inlet in self.inlets:
            if inlet.flowrateOut is not None:
                _flowrate += inlet.flowrateOut
            else:
                unresolved = True

        # Update flowrate if all inputs are resolved
        if not unresolved:
            self.flowrateIn = _flowrate
            self.flowrateOut = _flowrate  # Assume a single outlet for now
            self.flowrateShifted = False
        else:
            raise ValueError(f"Unresolved flowrate inputs for {self.name}.")

    def hostSlug(self,slug,initPos):
        self.slugs.insert(0,slug)
        slug.frontHost=self
        slug.frontHostPos=initPos

class Inlets:
    def __init__(self) -> None:
        self.inletIndex=0
        self.inlets={}

    def addInlet(self,inlet):
        self.inlets[self.inletIndex]=inlet
        self.inletIndex+=self.inletIndex

    def getInlet(self,index):
        return Utils().getOrDef(self.inlets,index,None)
class Outlets:
    def __init__(self) -> None:
        pass    
    def addOutlet(self,outlet):
        self.outlets[self.outletIndex]=outlet
        self.outletIndex+=self.outletIndex

class VolObjNull(VolumeObject):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)

class FlowPath:
    def __init__(self,segments=[],segmentSets={},slugs=[],flowrate=0,time=time.perf_counter(),collectedSlugs=[]) -> None:
        self.segments=segments
        self.segmentSets=segmentSets
        self.volume=0
        self.componentIndex=0
        self.slugs=slugs
        self.flowrate=flowrate
        self.timePrev=time
        self.collectedSlugs=collectedSlugs

    def setAddress(self,address):
        _inlets=address.inletsSett
        _outlets=address.outletsSett
        for _x in _inlets:
            _x[0].switchToInlets(_x[1])
        for _x in _outlets:
            _x[0].switchToOutlets(_x[1])            

    def pathVolume(self,segmentSet=None):
        if segmentSet is None:
            segmentSet=self.segments
        _vol=0
        for _x in segmentSet:
            _vol=_vol + _x.volume
        return _vol

    def addPath(self,segments,pathName="DEFAULT"):
        self.segmentSets[pathName]=segments
        if len(self.segmentSets.keys())==1:
            self.selectPath()

    def selectPath(self,pathName="DEFAULT"):
        self.segments=self.segmentSets[pathName]
        for _x in self.segments:
            _x.associatedFlowPath=self
        return self.segments
    
    def appendComponent(self,comp,pathName="DEFAULT"):
        if not pathName in self.segmentSets:
            self.addPath([comp],pathName)
            return
        else:
            _theseSeg=self.segmentSets[pathName]
            _theseSeg.append(comp)
        self.volume=self.pathVolume()
        self.updateFlowrates()
        
    def updateFlowrates(self):
        from collections import defaultdict, deque

        # Build a dependency graph and calculate indegrees
        graph = defaultdict(list)
        indegree = defaultdict(int)

        for segment in self.segments:
            for inlet in segment.inlets:
                graph[inlet].append(segment)
                indegree[segment] += 1

        # Initialize queue with segments that have no unresolved dependencies (indegree == 0)
        queue = deque(segment for segment in self.segments if indegree[segment] == 0)

        resolved = set()
        while queue:
            current = queue.popleft()
            resolved.add(current)

            # Update flowrates for the current segment
            current.cumulativeFlowrates()

            # Process downstream segments
            for downstream in graph[current]:
                indegree[downstream] -= 1
                if indegree[downstream] == 0:
                    queue.append(downstream)

        # Check if all segments were resolved
        if len(resolved) < len(self.segments):
            unresolved = [segment for segment in self.segments if segment not in resolved]
            raise ValueError(f"Unresolved dependencies in flow path: {unresolved}")

    def updateSlugs(self):
        for _x in self.segments:
            pass

    def advanceSlugs(self):
        _nowTime=time.perf_counter()
        _dT=_nowTime-self.timePrev        
        self.timePrev=_nowTime

        #Front
        for _slug in self.slugs:
            _frontHost=_slug.frontHost
            if isinstance(_frontHost,FlowTerminus):
                if _slug.reachedTerminusAt==-1:
                    _slug.reachedTerminusAt=time.perf_counter()
                continue
            if _frontHost is None:
                continue

            _frontHostPos=_slug.frontHostPos
         
            _dV=_frontHost.flowrateOut*_dT
            _newVol=_frontHostPos+_dV

            if _newVol>_frontHost.volume:
                _nextHost=_frontHost.outlets[0]          
                if isinstance(_nextHost,FlowTerminus):
                    _slug.frontHost=_nextHost
                    _slug.frontHostPos=0
                    _slug.collecting=True
                else:                      
                    _remainder=_newVol-_frontHost.volume
                    print("Next host fr: " + str(_nextHost.flowrateOut))
                    if _nextHost.flowrateOut!=_frontHost.flowrateOut:
                        _currHostLeftToFill=(_frontHost.volume-_frontHostPos)
                        _frontHostFillTime=_currHostLeftToFill/(_frontHost.flowrateOut)
                        _dTRemainder=_dT-_frontHostFillTime
                        #print("dTremainder: " + str(_dTRemainder) + ", next host fr: " + str((_nextHost.flowrateOut)))
                        _volumeAdd=_dTRemainder*(_nextHost.flowrateOut)
                        _slug.frontHost=_nextHost
                        _slug.frontHostPos=_volumeAdd
                        #print("_dV: " + str(_dV) + " _dT: " + str(_dT) + " _dtRemainder: " + str(_dTRemainder) + " _currHostLeftToFill: " + str(_currHostLeftToFill) + " _volumeAdd: " + str(_volumeAdd))
                    else:
                        _slug.frontHost=_nextHost
                        _slug.frontHostPos=_remainder                   
            else:
                _slug.frontHostPos=_newVol
        #Tail
        for _slug in self.slugs:
            _tailHost=_slug.tailHost

            if isinstance(_tailHost,FlowTerminus):
                if _slug.collected==False:
                    _slug.collected=True
                continue
            #elif isinstance(_tailHost,FlowOrigin) and _tailHost.dispensing:
            elif _tailHost.dispensing:
                continue
                
            _tailHostPos=_slug.tailHostPos
         
            _dV=_tailHost.flowrateOut*_dT

            if isinstance(_slug.frontHost,FlowTerminus):
                _slug.collectedVol=_slug.collectedVol+_dV

            _newVol=_tailHostPos+_dV

            if _newVol>_tailHost.volume:
                _nextHost=_tailHost.outlets[0]                
                if isinstance(_nextHost,FlowTerminus):
                    _slug.tailHost=_nextHost
                    _slug.tailHostPos=0
                    self.collectedSlugs.append(_slug)
                    del self.slugs[self.slugs.index(_slug)]
                else:                      
                    _remainder=_newVol-_tailHost.volume

                    if _nextHost.flowrateOut!=_tailHost.flowrateOut:
                        _currHostLeftToFill=(_tailHost.volume-_tailHostPos)
                        _tailHostFillTime=_currHostLeftToFill/(_tailHost.flowrateOut)
                        _dTRemainder=_dT-_tailHostFillTime
                        _volumeAdd=_dTRemainder*(_nextHost.flowrateOut)
                        _slug.tailHost=_nextHost
                        _slug.tailHostPos=_volumeAdd
                        #print("_dV: " + str(_dV) + " _dT: " + str(_dT) + " _dtRemainder: " + str(_dTRemainder) + " _currHostLeftToFill: " + str(_currHostLeftToFill) + " _volumeAdd: " + str(_volumeAdd))
                    else:
                        _slug.tailHost=_nextHost
                        _slug.tailHostPos=_remainder                   
            else:
                _slug.tailHostPos=_newVol
                
class FlowComponent(VolumeObject):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
class Tubing(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
class TPiece(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
class IR(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
    def scan(self):
        pass

class Chip(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)

class Coil(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)

class Valve(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
class Pump(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
class FlowOrigin(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
    '''
    def dispense(self,targetTerminus=None):
        if not (self.dispensing) and not self.associatedFlowPath is None:
            self.dispensing=True
            _return=Slug(frontHost=self,tailHost=self,frontHostPos=0,tailHostPos=0,targetTerminus=targetTerminus)
            self.associatedFlowPath.slugs.append(_return)
            return _return
    '''
class FlowTerminus(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)
class FlowVelocity:  # mL per minute
    def __init__(self,speed=0) -> None:
        self.speed=speed

class Slugs:
    def __init__(self,slugs=[],slugsCollected=[]) -> None:
        self.slugs=slugs
        self.slugsCollected=slugsCollected

class SlugNull:
    def __init__(self,volume=None,location=None,parentSlug=None,childSlug=None,elastic=None,hosts=None,tailHost=None,frontHost=None,tailHostPos=None,frontHostPos=None,stationary=True,collectedVol=0,collecting=False,reachedTerminusAt=0,targetTerminus=None,collected=False) -> None:
        self.volume=volume
        self.location=location
        self.parentSlug=parentSlug
        self.childSlug=childSlug
        self.elastic=elastic #If elastic,the slug will be 'stretched' at junctions and not branched into new one
        self.hosts=hosts
        self.tailHost=tailHost
        self.frontHost=frontHost
        self.tailHostPos=tailHostPos #Volume of progress
        self.frontHostPos=frontHostPos
        self.stationary=stationary
        self.collectedVol=collectedVol
        self.collecting=collecting
        self.reachedTerminusAt=reachedTerminusAt
        self.targetTerminus=targetTerminus
        self.collected=collected

    def setTargetTerminus(self,terminus):
        self.targetTerminus=terminus

    def branchSlug(self):
        if self.elastic:
            return self
        _child=Slug(parentSlug=self)
        return _child

    def slugVolume(self):
        _frontHost=self.frontHost
        _tailHost=self.tailHost

        if (_frontHost is _tailHost):
            return (self.frontHostPos-self.tailHostPos)
        else:
            _thisComp=_tailHost
            _volume=_tailHost.volume - self.tailHostPos
            while True:
                _thisComp=_thisComp.outlets[0]
                if isinstance(_thisComp,FlowTerminus):
                    return _volume
                elif _thisComp is _frontHost:
                    return (_volume+self.frontHostPos)
                else:
                    _volume=_volume+_thisComp.volume

class Slug(SlugNull):
    def __init__(self, volume=None, location=None, parentSlug=None, childSlug=None, elastic=None, hosts=None, tailHost=None, frontHost=None, tailHostPos=None, frontHostPos=None, stationary=True, collectedVol=0, collecting=False, reachedTerminusAt=0, targetTerminus=None, collected=False) -> None:
        super().__init__(volume, location, parentSlug, childSlug, elastic, hosts, tailHost, frontHost, tailHostPos, frontHostPos, stationary, collectedVol, collecting, reachedTerminusAt, targetTerminus, collected)

class FlowPathAdjustment:
    def __init__(self, instance=None, attributeName="", valueOrMethod=None, *args) -> None:
        self.instance=instance;
        self.attributeName=attributeName;
        self.valueOrMethod=valueOrMethod;
        self.args=args;
        #self.kwargs=kwargs
    
    def effect(self):
        if self.instance is None:
            return None
        if callable(self.valueOrMethod):  # If value_or_method is callable, it's a method
            method = self.valueOrMethod
            method(*self.args)
        else:  # Otherwise, it's a property
            setattr(self.instance, self.attributeName, self.valueOrMethod)

class FlowJiggler: #Handles compound flowrates at a junction, i.e. correct flowrates for pumps to result in a constant flowrate at junction
    def __init__(self,flowrates={},pumps=[]) -> None:
        self.flowrates=flowrates
        self.pumps=pumps

    def addPump(self,pump,flowrate):
        self.addPump(pump)
        self.flowrates[pump.id]=flowrate

    def setFlowKeepConst(self,pump,flowrate):
        _id=pump.id
        _len=len(self.pumps)
        if _len==1:
            self.flowrates[_id]=flowrate
            return
        elif _len==0:
            self.addPump(pump,flowrate)
            return
        _totalFlowrate=0
        for _x in self.flowrates.values():
            _totalFlowrate=_totalFlowrate+_x
        self.flowrates[_id]=flowrate
        _remainder=_totalFlowrate-flowrate
        if _remainder!=0:
            _portion=_remainder/(_len-1)
            for _x, _y in self.flowrates.items():
                if _x!=_id:
                    _new=_portion
                    if _new<0:
                        _new=0
                    self.flowrates[_x]=_new
        elif _remainder==0:
            return
#######################################################################################
###Examples
if __name__ == "__main__":
    _path=FlowPath()

    #Stocks + pumps up to t piece

    _redStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="RED_STOCK",flowrateIn=0.0,slugs=[])
    _blueStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="BLUE_STOCK",flowrateIn=0.0,slugs=[])
    _pinkStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="PINK_STOCK",flowrateIn=0.0,slugs=[])
    #Pump lines
    _pump_1=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_1",flowrateIn=0.0,slugs=[])
    _pump_2=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_2",flowrateIn=0.0,slugs=[])
    #Valves
    _cwValve=(Valve(volume=0.05,inlets=[],outlets=[],name="CW_VALVE",slugs=[]))
    #TPiece
    _Tpiece=TPiece(dispensing=False,volume=0,inlets=[],outlets=[],name="T_PIECE",flowrateIn=0.0,slugs=[])
    #Coil
    _coil=(Coil(volume=10,inlets=[],outlets=[],name="COIL",slugs=[]))
    _pump_3=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_3",flowrateIn=0.0,flowrateOut=0.0,slugs=[])
    #IR
    _IR=(IR(volume=0.5,inlets=[],outlets=[],name="IR",slugs=[]))
    #Terminus
    _waste=FlowTerminus(volume=0,inlets=[],outlets=[None],name="WASTE",flowrateIn=0,flowrateOut=0,slugs=[])
    _collect=FlowTerminus(volume=0,inlets=[],outlets=[None],name="COLLECT",flowrateIn=0,flowrateOut=0,slugs=[])

    ###################
    #Connect components

    #Stock solutions
    _redStock.flowInto(_pump_1)
    _blueStock.flowInto(_pump_2)
    #Pumplines
    _pump_1.flowInto(_Tpiece)
    _pump_2.flowInto(_Tpiece)
    #Tubing etc to WC
    _Tpiece.flowInto(_coil)
    _pinkStock.flowInto(_pump_3)
    _pump_3.flowInto(_IR)
    _coil.flowInto(_IR)
    _IR.flowInto(_cwValve)
    _cwValve.flowInto(_waste,setNameOut="WASTE")
    _cwValve.flowInto(_collect,setNameOut="COLLECT")
    #select one of the termini
    _cwValve.switchToOutlets("WASTE")
    '''
    #Create path
    '''
    _path.addPath(
        [
            _redStock,
            _blueStock,
            _pinkStock,

            _pump_1,
            _pump_2,
            _pump_3,
            
            _Tpiece,

            _coil,
            _IR,

            _cwValve,

            _collect,
            _waste
        ]
    )

    for _x in _path.segments:
        print("*********")
        print(_x.name)
        print(_x.inletSets)    
        print(_x.outletSets)
        print(_x.inlets)   
        print(_x.outlets)

    #Manually assign starting point and ending point
    _currOrigin=_Tpiece
    _currTerminus=_waste
    
    
    # Flag variable to indicate whether the thread should continue running?
    running=True
    allSlugs=Slugs()

    def run_code():
        global running
        global allSlugs
        while running:
            _flow_1=eval(input("Pump 1 flowrate: "))
            _flow_2=eval(input("Pump 2 flowrate: "))
            _flow_3=eval(input("Pump 3 flowrate: "))
            _slugVol=eval(input("Vol to dispense: "))
            _redStock.flowrateIn=_flow_1/60
            _blueStock.flowrateIn=_flow_2/60
            _pinkStock.flowrateIn=_flow_3/60

            _path.updateFlowrates()

            for _x in _path.segments:
                print(_x.flowrateOut)
            
            _slug=_currOrigin.dispense()
            allSlugs.slugs.append(_slug)
            print(str(_slug.slugVolume()) + " mL")

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
                    _currOrigin.dispensing=False
                    _switched=True
                time.sleep(0.25)
            print("************")
            print("Collected slug volumes")
            for _x in _path.collectedSlugs:
                print(f'{_x.collectedVol} mL')
            print("Slug took " + str(time.perf_counter() - _now) + " seconds to reach terminus")
            print("************")

    # Create a thread for running the code
    thread=threading.Thread(target=run_code)
    thread.start()

    # Wait for the thread to finish
    thread.join()
    print("We're done here")

    #######################################################################################
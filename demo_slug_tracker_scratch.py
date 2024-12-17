import time
import threading
import uuid
from Core.Utils.Utils import Utils
from collections import defaultdict, deque

class FlowAddresses:
    def __init__(self,addressBookName) -> None: #inlets
        self.addressBookName=addressBookName
        self.addresses={}
        
    def addAddress(self,targetComponent,address):
        '''
        Add the neccessary outlets to select for each component to reach 'targetComponent' in the
        flowline.
        targetComponent: volObj
        address: dict with component names as keys and array [inletName,outletName] for each
        '''
        if not isinstance(targetComponent,str):
            targetComponent=targetComponent.name
        self.addresses[targetComponent]=address

class VolumeObject:

    #Class var
    idCounter=0

    def __init__(self,volume=None,inlets=None,outlets=None,name=None,deviceName=None,deviceType=None,flowrateOut=None,flowrateIn=None,slugs=None,lastAdvance=None,outletSets=None,inletSets=None,currOutlets=None,currInlets=None,remainder=None,settings=None,state=None,availableCommands=None,dispensing=False,associatedFlowPath=None) -> None:
        self.volume=volume
        #######################################################################################
        #Inlet/outlet control
        self.inlets=inlets #Array with currently used inlets (array with any number of flow components)
        self.outlets=outlets #Array with currently used outlets (array with only one element, an outlet set can have only a single flow component for now)
        self.inletSets=inletSets #Dict with named sets of 'inlets'. One will be selected to act as self.inlets
        self.outletSets=outletSets #Dict with named sets of 'outlets'. One will be selected to act as self.outlets
        #######################################################################################
        self.name=name
        self.deviceName=deviceName
        self.deviceType=deviceType
        self.flowrateIn=flowrateIn
        self.flowrateOut=flowrateOut
        self.slugs=slugs
        self.lastAdvance=lastAdvance
        self.dispensing=dispensing
        self.associatedFlowPath=associatedFlowPath
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
            self.inletSets[setName]=[comp]
            self.inlets=self.inletSets[setName]
            self.flowrateShifted=True
        elif len(_thisInletSet)==1 and _thisInletSet[0] is None:   
            self.inletSets[setName]=[comp]
            self.inlets=self.inletSets[setName]
            self.flowrateShifted=True
        else:
            if not comp in _thisInletSet:
                _thisInletSet.append(comp)
                
    def addOutlet(self,comp,setName="DEFAULT"):
        _thisOutletSet=self.getOutletSet(setName)
        if len(_thisOutletSet)==0:       
            _thisOutletSet.append(comp)
            self.outlets=_thisOutletSet
            self.flowrateShifted=True
        elif len(_thisOutletSet)==1 and _thisOutletSet[0] is None:
            _thisOutletSet=[(comp)]
            self.outlets=_thisOutletSet
            self.flowrateShifted=True
        else:
            if not comp in _thisOutletSet:
                _thisOutletSet.append(comp)

    def flowInto(self,outlet,setNameIn="DEFAULT",setNameOut="DEFAULT"):
        self.addOutlet(outlet,setNameOut)
        outlet.addInlet(self,setNameIn)

    def switchToInlets(self,setName="DEFAULT"):
        if setName in self.inletSets:
            self.inlets=self.inletSets[setName]
            
    def switchToOutlets(self,setName="DEFAULT"):
        if setName in self.outletSets:
            self.outlets=self.outletSets[setName]
        if isinstance(self.outlets[0],FlowTerminus) and not self.associatedFlowPath.currTerminus:
            print(f"Setting currTerminus as: {self.outlets[0]}")
            self.associatedFlowPath.currTerminus=self.outlets[0]

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

class VolObjNull(VolumeObject):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)

class FlowPath:
    def __init__(self,flowPathName=uuid.uuid4(),segments=[],segmentSets={},slugs=[],flowrate=0,time=time.perf_counter(),collectedSlugs=[]) -> None:
        self.flowPathName=flowPathName
        self.segments=segments
        self.segmentSets=segmentSets
        self.volume=0
        self.componentIndex=0
        self.slugs=slugs
        self.flowrate=flowrate
        self.timePrev=time
        self.collectedSlugs=collectedSlugs
        
        self.addresses=FlowAddresses("DEFAULT")
        self.addressesAll={}
        
        self.currTerminus=None
        self.currRelOrigin=None #Relative starting point in flow path that 'dispenses' slugs

    def switchToAddress(self,address):
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

    def mapPathTermini(self):
        # Identify all FlowTerminus objects
        termini = [seg for seg in self.segments if isinstance(seg, FlowTerminus)]

        if not termini:
            # Nothing to map
            return

        # Identify the origin component from which we should map paths.
        # If currRelOrigin is defined, use that. Otherwise, try to find a FlowOrigin or a node with no inlets.
        if self.currRelOrigin:
            start = self.currRelOrigin
        else:
            # Try to find a FlowOrigin
            origins = [seg for seg in self.segments if isinstance(seg, FlowOrigin)]
            if origins:
                start = origins[0]
            else:
                # If no FlowOrigin, pick a segment with no inlets as start
                # (i.e., a node that doesn't receive flow from any other node)
                candidates = []
                for seg in self.segments:
                    # If no inlets or inlets empty, it's a potential start
                    if not seg.inlets or len(seg.inlets) == 0:
                        candidates.append(seg)
                if candidates:
                    start = candidates[0]
                else:
                    # If no clear start found, just pick the first segment as start (fallback)
                    start = self.segments[0]

        # Build a graph from segments: component -> list of downstream components
        # Note: we consider the currently active outlets. If multiple outlet sets exist,
        # we still have them stored in outletSets, but for pathfinding we just need the structure.
        self.graph = {}
        for seg in self.segments:
            # Combine all possible outlet sets to know the potential downstream connections
            # For mapping, we just want to know topologically who can be reached from who.
            # We'll store the union of all outlets in current sets for pathfinding.
            # If a component can switch outlets, they must appear in some outletSet.
            # We'll union all sets to find possible paths.
            
            downstream_nodes = set()
            if seg.outletSets:
                for oSet in seg.outletSets.values():
                    for outcomp in oSet:
                        if outcomp is not None:
                            downstream_nodes.add(outcomp)

            self.graph[seg] = list(downstream_nodes)

        # Now for each terminus, find a path and record the necessary outlet sets
        self.addressesAll = {}
        for terminus in termini:
            path = self._findPath(start, terminus)
            if path is None:
                # No path found to this terminus
                continue

            # path is a list of components from start to terminus
            # We want to record the outlet sets chosen at branching components
            # The address form: TerminusName: [ [ValveX, "A"], [ValveY, "B"] ... ]
            addresses = []

            # Iterate through path components and figure out which outletSet leads to the next node in the path
            # We look at pairs (currentComp, nextComp)
            for i in range(len(path)-1):
                currComp = path[i]
                nextComp = path[i+1]

                # Check if currComp has multiple outlet sets
                if currComp.outletSets and len(currComp.outletSets.keys()) > 1:
                    # Find the outletSet that contains nextComp
                    chosenSetName = None
                    for oSetName, oSetComps in currComp.outletSets.items():
                        if nextComp in oSetComps:
                            chosenSetName = oSetName
                            break
                    if chosenSetName is not None:
                        addresses.append([currComp, chosenSetName])

            self.addressesAll[terminus.name] = addresses

    def setCurrDestination(self, terminus):
        if not isinstance(terminus, FlowTerminus):
            name = terminus
        else:
            name = terminus.name

        if name not in self.addressesAll:
            print(f"No route info available for {name}")
            return

        theseAddresses = self.addressesAll[name]
        # each element in theseAddresses is [component, outletSetName]
        for comp, outletSetName in theseAddresses:
            comp.switchToOutlets(outletSetName)

        # Optionally, we can set self.currTerminus to the target terminus
        # if we have a reference to the actual terminus object:
        self.currTerminus = terminus
        
    # Helper function to find a path from start to end
    def _findPath(self,start, end, visited=None):
        if visited is None:
            visited = set()
        if start == end:
            return [start]
        visited.add(start)
        for nxt in self.graph.get(start, []):
            if nxt not in visited:
                p = self._findPath(nxt, end, visited)
                if p:
                    return [start] + p
        return None

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

class FlowTerminus(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, dispensing=False, associatedFlowPath=None) -> None:
        super().__init__(volume, inlets, outlets, name, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, dispensing, associatedFlowPath)

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

#######################################################################################
###Examples
if __name__ == "__main__":
    _path=FlowPath()

    #Stocks
    _redStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="RED_STOCK",flowrateIn=0.0,slugs=[])
    _blueStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="BLUE_STOCK",flowrateIn=0.0,slugs=[])
    _pinkStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="PINK_STOCK",flowrateIn=0.0,slugs=[])
    #Pump lines
    _pump_1=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_1",flowrateIn=0.0,slugs=[])
    _pump_2=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_2",flowrateIn=0.0,slugs=[])
    _pump_3=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_3",flowrateIn=0.0,slugs=[])
    #Valves
    _cwValve=Valve(volume=0.05,inlets=[],outlets=[],name="CW_VALVE",slugs=[])
    _valve_1=Valve(volume=0.05,inlets=[],outlets=[],name="DIVERT_VALVE",slugs=[])
    _flushCoilValve=Valve(volume=0.05,inlets=[],outlets=[],name="FLUSH_VALVE",slugs=[])
    #IR
    _IR=(IR(volume=0.5,inlets=[],outlets=[],name="IR",slugs=[]))
    #Coil
    _coil=(Coil(volume=10,inlets=[],outlets=[],name="COIL",slugs=[]))
    #Termini
    _waste=FlowTerminus(volume=0,inlets=[],outlets=[None],name="WASTE",flowrateIn=0,flowrateOut=0,slugs=[])
    _collect=FlowTerminus(volume=0,inlets=[],outlets=[None],name="COLLECT",flowrateIn=0,flowrateOut=0,slugs=[])
    _terminus_3=FlowTerminus(volume=0,inlets=[],outlets=[None],name="TERMINUS_3",flowrateIn=0,flowrateOut=0,slugs=[])
    _terminus_4=FlowTerminus(volume=0,inlets=[],outlets=[None],name="TERMINUS_4",flowrateIn=0,flowrateOut=0,slugs=[])

    ###################
    #Connect components

    #Stock solutions
    _redStock.flowInto(_pump_1)
    _blueStock.flowInto(_pump_2)
    _pinkStock.flowInto(_pump_3)
    #Pumplines
    _pump_1.flowInto(_valve_1)
    _pump_2.flowInto(_valve_1)
    _pump_3.flowInto(_IR)
    #Divert valve
    _valve_1.flowInto(_coil,setNameOut="TO_COIL")
    _valve_1.flowInto(_flushCoilValve,setNameOut="TO_FLUSH_VALVE")
    #Flush coil valve
    _flushCoilValve.flowInto(_terminus_3,setNameOut="TO_TERMINUS_3")
    _flushCoilValve.flowInto(_terminus_4,setNameOut="TO_TERMINUS_4")
    #Coil
    _coil.flowInto(_IR)
    
    _IR.flowInto(_cwValve)
    _cwValve.flowInto(_waste,setNameOut="WASTE")
    _cwValve.flowInto(_collect,setNameOut="COLLECT")
    #select one of the termini
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
            
            _valve_1,
            _flushCoilValve,

            _coil,
            _IR,

            _cwValve,

            _collect,
            _waste,
            _terminus_3,
            _terminus_4
        ]
    )

    #TODO - Manually assign starting point for now
    _path.currRelOrigin=_redStock
    _path.mapPathTermini()
    print(f"Generated addresses: {_path.addressesAll}")
    _path.setCurrDestination(_terminus_4)

    for _x in _path.segments:
        print("*********")
        print(_x.name)
        print(_x.inletSets)    
        print(_x.outletSets)
        print(_x.inlets)   
        print(_x.outlets)
    
    
    # Flag variable to indicate whether the thread should continue running?
    running=True
    allSlugs=Slugs()
    def run_code():
        global running
        global allSlugs
        global _path
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
            
            _slug=_path.currRelOrigin.dispense()
            allSlugs.slugs.append(_slug)
            print(str(_slug.slugVolume()) + " mL")

            _switched=False
            _now=time.perf_counter()
            _path.timePrev=time.perf_counter()
            while not (isinstance(_slug.tailHost,FlowTerminus)):
                _path.advanceSlugs()
                _vol=_slug.slugVolume()
                print("Time: " + str(round(time.perf_counter() - _now, 0)) + " seconds, Fro h/pos: " + str(
                    _slug.frontHost.name) + ", " + str(round(_slug.frontHostPos, 2)) + "/" + str(
                    _slug.frontHost.volume) + " mL, tail h/pos: " + str(_slug.tailHost.name) + ", " + str(
                    round(_slug.tailHostPos, 2)) + "/" + str(_slug.tailHost.volume) + " mL, fr: " + str(
                    round(_slug.frontHost.flowrateOut*60, 2)) + " mL.min-1, slug vol: " + str(
                    round(_vol, 2)) + " mL, vol collected: " + str(round(_slug.collectedVol, 2)) + " mL")
                if not _switched and _vol > _slugVol:
                    _path.currRelOrigin.dispensing=False
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
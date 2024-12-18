import random
import time
import threading
import uuid
from Core.Utils.Utils import Utils
from collections import defaultdict, deque

FLOW_PATH=None

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

    def __init__(self,volume=None,inlets=None,outlets=None,name=None,deviceName=None,deviceType=None,flowrateOut=None,flowrateIn=None,slugs=None,lastAdvance=None,outletSets=None,inletSets=None,currOutlets=None,currInlets=None,remainder=None,settings=None,state=None,availableCommands=None,dispensing=False) -> None:
        self.volume=volume
        #######################################################################################
        #Inlet/outlet control
        self.inlets=inlets #Array with currently used inlets (array with any number of flow components)
        self.outlets=outlets #Array with currently used outlets (array with only one element, an outlet set can have only a single flow component for now)
        self.inletSets=inletSets #Dict with named sets of 'inlets'. One will be selected to act as self.inlets
        self.outletSets=outletSets #Dict with named sets of 'outlets'. One will be selected to act as self.outlets
        self.currInletSet=None
        self.currOutletSet=None
        #######################################################################################
        self.name=name
        self.deviceName=deviceName
        self.deviceType=deviceType
        self.flowrateIn=flowrateIn
        self.flowrateOut=flowrateOut
        self.slugs=slugs
        self.lastAdvance=lastAdvance
        self.dispensing=dispensing
        self.remainderToDispense=None
        #FLOW_PATH=FLOW_PATH
        self.remainder=remainder
        #Boolean flags
        #Settings and commands
        self.settings=settings
        self.state=state
        self.availableCommands=availableCommands
        #Hashmap id generator
        self.id=VolumeObject.idCounter
        VolumeObject.idCounter+=1
    
    def dispense(self,vol=-1):
        if not (self.dispensing) and FLOW_PATH:
            print(str(self.name) + " has started dispensing!")
            self.dispensing=True
            _return=Slug(frontHost=self,tailHost=self,frontHostPos=0,tailHostPos=0)
            FLOW_PATH.slugs.append(_return)
            if vol != -1:
                self.remainderToDispense=vol
            return _return

    @NotImplementedError        
    def start(self):
        '''
        start pumping whatever is in flow path
        '''
        pass

    @NotImplementedError
    def stop(self):
        '''
        stop pumping whatever is in flow path (does not cancel dispensing=True!)
        '''
        pass

    def setFlowrate(self,fr):
        '''
        Alter flowrate and notify FLOW_PATH of change
        '''
        self.flowrateIn=fr
        self.cumulativeFlowrates()
        FLOW_PATH.flowrateShifted=True
     
    def terminateDispensing(self):
        if self.dispensing:
            self.dispensing=False

    def _addInlet(self,comp,setName):
        inletSet=self._getInletSet(setName)
        if len(inletSet)==0:
            self.inletSets[setName]=[comp]
            self.inlets=self.inletSets[setName]
        elif len(inletSet)==1 and inletSet[0] is None:   
            self.inletSets[setName]=[comp]
            self.inlets=self.inletSets[setName]
        else:
            if not comp in inletSet:
                inletSet.append(comp)

    def _addOutlet(self,comp,setName):
        outletSet=self._getOutletSet(setName)
        if len(outletSet)==0:
            self.outletSets[setName]=[comp]
            self.outlets=outletSet
        elif len(outletSet)==1 and outletSet[0] is None:
            outletSet=[(comp)]
            self.outlets=outletSet
        else:
            if not comp in outletSet:
                outletSet.append(comp)

    def flowInto(self,outlet,setNameIn="DEFAULT",setNameOut=""):
        if setNameOut == "":
            setNameOut=f"{self.name}_{self.id}_to_{outlet.name}_{outlet.id}"
        self._addOutlet(outlet,setNameOut)
        outlet._addInlet(self,setNameIn)
        if not len(self.outlets):
            self.switchToOutlets(setNameOut)
        if not len(outlet.inlets):
            outlet.switchToInlets(setNameIn)
        FLOW_PATH.flowrateShifted=True
            
    def switchToInlets(self,setName):
        if setName in self.inletSets:
            self.inlets=self.inletSets[setName]
            self.currInletSet=setName
            return self.inlets
        else:
            return []
        
    def switchToOutlets(self,setName):
        if setName in self.outletSets:
            self.outlets=self.outletSets[setName]
        if isinstance(self.outlets[0],FlowTerminus) and not FLOW_PATH.currTerminus:
            print(f"Setting currTerminus as: {self.outlets[0].name}")
            FLOW_PATH.currTerminus=self.outlets[0]
        self.currOutletSet=setName
        return self.outlets

    def _getInletSet(self,setName):
        if self.inletSets is None:
            self.inletSets={}
        if setName in self.inletSets:
            return self.inletSets[setName]
        else:
            self.inletSets[setName]=[]
            return self.inletSets[setName]
        
    def _getOutletSet(self,setName):
        if self.outletSets is None:
            self.outletSets={}
        if setName in self.outletSets:
            return self.outletSets[setName]
        else:
            self.outletSets[setName]=[]
            return self.outletSets[setName]

    def cumulativeFlowrates(self):
        if not self.inlets:
            self.inlets = []

        # If no inputs, propagate flowrateOut directly from flowrateIn
        if len(self.inlets) == 0:
            self.flowrateOut = self.flowrateIn
            FLOW_PATH.flowrateShifted=True
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
            if not FLOW_PATH.flowrateShifted:
                FLOW_PATH.flowrateShifted=True
        else:
            raise ValueError(f"Unresolved flowrate inputs for {self.name}.")

    def hostSlug(self,slug,initPos):
        self.slugs.insert(0,slug)
        slug.frontHost=self
        slug.frontHostPos=initPos

class VolObjNull(VolumeObject):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)

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
        self.flowrateShifted=True
        
        self.addresses=FlowAddresses("DEFAULT") #TODO - impliment instead of below
        self.addressesAll={}
        
        self.currTerminus=None
        self.currRelOrigin=None #Relative starting point in flow path that 'dispenses' slugs
        
        global FLOW_PATH
        FLOW_PATH=self

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

    def addPath(self,segments):
        self.segments=segments
        if not self.currRelOrigin:
            for x in segments:
                if not self.currRelOrigin and isinstance(x,FlowOrigin):
                    self.currRelOrigin=x

    # def selectPath(self,pathName="DEFAULT"):
    #     self.segments=self.segmentSets[pathName]
    #     for _x in self.segments:
    #         _x.associatedFlowPath=self
    #         if not self.currRelOrigin and isinstance(_x,FlowOrigin):
    #             self.currRelOrigin=_x
    #     return self.segments

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
        if isinstance(terminus, str):
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

    def appendComponent(self,comp):
        if not self.currRelOrigin and isinstance(comp,FlowOrigin):
            self.currRelOrigin=comp
        self.segments.append(comp)
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
        if self.flowrateShifted:
            self.updateFlowrates()
            self.flowrateShifted = False

        _nowTime = time.perf_counter()
        _dT = _nowTime - self.timePrev
        self.timePrev = _nowTime

        # Front movement
        for slug in self.slugs:
            _frontHost = slug.frontHost

            # If frontHost is None, no advancement
            if _frontHost is None:
                continue

            # If slug has reached a terminus and is collecting
            if isinstance(_frontHost, FlowTerminus):
                if not slug.collected:
                    # Increase collected volume by input flow * dT
                    slug.collectedVol += _frontHost.flowrateIn * _dT
                    if slug.reachedTerminusAt == 0:
                        slug.reachedTerminusAt = _nowTime
                # No further advancement needed for a terminus
                continue

            # Calculate displacement volume for this timestep
            _dV = _frontHost.flowrateOut * _dT
            _newVol = slug.frontHostPos + _dV

            # Check if slug surpasses the current frontHost volume
            if _newVol > _frontHost.volume:
                # We have leftover volume after filling this component
                _remainder = _newVol - _frontHost.volume

                # Move to next host(s)
                # Compute initial leftover time at the moment slug left _frontHost
                _currHostLeftToFill = (_frontHost.volume - slug.frontHostPos)
                _frontHostFillTime = _currHostLeftToFill / _frontHost.flowrateOut
                _dTRemainder = _dT - _frontHostFillTime

                # Identify the next host
                if len(_frontHost.outlets) == 0:
                    # No next host, slug stops here
                    slug.frontHostPos = _frontHost.volume
                    continue

                _nextHost = _frontHost.outlets[0]

                # If flowrates differ between hosts, adjust volume based on the nextHost’s flowrate
                if isinstance(_nextHost, FlowTerminus):
                    # If next host is a terminus, slug enters and is collected
                    slug.frontHost = _nextHost
                    # Adjust collectedVol by remainder
                    slug.collectedVol += _remainder
                    slug.frontHostPos = 0
                    slug.collecting = True
                else:
                    # If next host has a different flowrate
                    if _nextHost.flowrateOut != _frontHost.flowrateOut:
                        _volumeAdd = _dTRemainder * _nextHost.flowrateOut
                    else:
                        _volumeAdd = _remainder

                    # Now, potentially continue through multiple hosts
                    slug.frontHost = _nextHost
                    # Use a loop to handle multiple jumps
                    _stillToFill = _volumeAdd

                    while _stillToFill > _nextHost.volume:
                        # Surpass this host entirely
                        _stillToFill -= _nextHost.volume

                        # Move to the next outlet
                        if len(_nextHost.outlets) == 0:
                            # No further hosts, slug ends here
                            slug.frontHostPos = _nextHost.volume
                            break

                        _nextHost = _nextHost.outlets[0]

                        if isinstance(_nextHost, FlowTerminus):
                            # Slug enters terminus and is collected
                            slug.frontHost = _nextHost
                            slug.collectedVol += _stillToFill
                            slug.frontHostPos = 0
                            slug.collecting = True
                            _stillToFill = 0
                            break

                        # If next host differs in flowrate, we’d need additional logic here
                        # But for now we assume the computed _stillToFill works directly
                        slug.frontHost = _nextHost

                    # If we still have leftover that doesn't surpass the new host fully
                    if 0 < _stillToFill <= _nextHost.volume and not isinstance(_nextHost, FlowTerminus):
                        slug.frontHostPos = _stillToFill

            else:
                # Slug remains within the same host
                slug.frontHostPos = _newVol

        # Tail movement
        # Similar logic applies for the tail. We allow multiple host jumps if needed.
        for slug in self.slugs[:]:  # copy list since we may remove slugs
            _tailHost = slug.tailHost

            # If tail is in a terminus, slug is collected
            if isinstance(_tailHost, FlowTerminus):
                if not slug.collected:
                    slug.collected = True
                continue

            _dV = _tailHost.flowrateOut * _dT
            
            if _tailHost.dispensing:
                # Only dispense up to the remainder
                if _tailHost.remainderToDispense is not None:
                    if _dV > _tailHost.remainderToDispense:
                        # Cap _dV so we don't overshoot
                        _dV = _tailHost.remainderToDispense
                
                slug.totalDispensed += _dV

                if _tailHost.remainderToDispense is not None:
                    _tailHost.remainderToDispense -= _dV
                    if _tailHost.remainderToDispense <= 0:
                        _tailHost.dispensing = False
                        _tailHost.remainderToDispense = 0
                continue

            _tailHostPos = slug.tailHostPos
            _newVol = _tailHostPos + _dV

            # Check if we surpass the tailHost's volume
            if _newVol > _tailHost.volume:
                _remainder = _newVol - _tailHost.volume

                # Move on to next host
                if len(_tailHost.outlets) == 0:
                    # No further hosts, so slug remains here
                    slug.tailHostPos = _tailHost.volume
                    continue

                _nextHost = _tailHost.outlets[0]

                if isinstance(_nextHost, FlowTerminus):
                    # Slug tail enters terminus - slug is collected
                    slug.tailHost = _nextHost
                    slug.tailHostPos = 0
                    self.collectedSlugs.append(slug)
                    self.slugs.remove(slug)
                else:
                    # Handle multiple jumps for the tail
                    _currHostLeftToFill = (_tailHost.volume - _tailHostPos)
                    _tailHostFillTime = _currHostLeftToFill / (_tailHost.flowrateOut)
                    _dTRemainder = _dT - _tailHostFillTime

                    if _nextHost.flowrateOut != _tailHost.flowrateOut:
                        _volumeAdd = _dTRemainder * _nextHost.flowrateOut
                    else:
                        _volumeAdd = _remainder

                    slug.tailHost = _nextHost
                    _stillToFill = _volumeAdd

                    while _stillToFill > _nextHost.volume:
                        _stillToFill -= _nextHost.volume
                        if len(_nextHost.outlets) == 0:
                            # No further hosts for the tail
                            slug.tailHostPos = _nextHost.volume
                            break

                        _nextHost = _nextHost.outlets[0]

                        if isinstance(_nextHost, FlowTerminus):
                            # Slug tail enters terminus
                            slug.tailHost = _nextHost
                            slug.tailHostPos = 0
                            self.collectedSlugs.append(slug)
                            if slug in self.slugs:
                                self.slugs.remove(slug)
                            _stillToFill = 0
                            break

                        slug.tailHost = _nextHost

                    if 0 < _stillToFill <= _nextHost.volume and not isinstance(_nextHost, FlowTerminus):
                        slug.tailHostPos = _stillToFill
            else:
                # Tail remains within the same host
                slug.tailHostPos = _newVol

class FlowComponent(VolumeObject):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Tubing(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class TPiece(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class IR(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
    def scan(self):
        pass
class Chip(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Coil(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Valve(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Pump(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class FlowOrigin(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class FlowTerminus(FlowComponent):
    def __init__(self, volume=None, inlets=None, outlets=None, name=None, deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, inlets, outlets, name, deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)

class Slugs:
    def __init__(self,slugs=[],slugsCollected=[]) -> None:
        self.slugs=slugs
        self.slugsCollected=slugsCollected

class SlugNull:
    def __init__(self,volume=None,location=None,parentSlug=None,childSlug=None,elastic=None,hosts=None,tailHost=None,frontHost=None,tailHostPos=None,frontHostPos=None,stationary=True,collectedVol=0,collecting=False,reachedTerminusAt=0,collected=False,totalDispensed=None,lastDispenseCycleTime=None) -> None:
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
        self.collected=collected
        
        self.totalDispensed=totalDispensed
        self.lastDispenseCycleTime=lastDispenseCycleTime

    def branchSlug(self):
        if self.elastic:
            return self
        _child=Slug(parentSlug=self)
        return _child

    def dispensedSlugVolume(self):
        """
        Volume of slug dispensed from origin
        """
        return self.totalDispensed

    def slugVolume(self):
        '''
        Volume of slug currently in flow path
        '''
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
    def __init__(self, volume=None, location=None, parentSlug=None, childSlug=None, elastic=None, hosts=None, tailHost=None, frontHost=None, tailHostPos=None, frontHostPos=None, stationary=True, collectedVol=0, collecting=False, reachedTerminusAt=0,  collected=False, totalDispensed=None, lastDispenseCycleTime=None):
        super().__init__(volume, location, parentSlug, childSlug, elastic, hosts, tailHost, frontHost, tailHostPos, frontHostPos, stationary, collectedVol, collecting, reachedTerminusAt, collected, totalDispensed=0, lastDispenseCycleTime=0)
#######################################################################################
###Examples
if __name__ == "__main__":
    _path=FlowPath()
    comp=[]
    
    #Stocks
    _redStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="RED_STOCK",flowrateIn=0.0,slugs=[])
    comp.append(_redStock)
    _blueStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="BLUE_STOCK",flowrateIn=0.0,slugs=[])
    comp.append(_blueStock)
    _pinkStock=FlowOrigin(dispensing=False,volume=0,inlets=[],outlets=[],name="PINK_STOCK",flowrateIn=0.0,slugs=[])
    comp.append(_pinkStock)
    
    #Pump lines
    _pump_1=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_1",flowrateIn=0.0,slugs=[])
    comp.append(_pump_1)
    _pump_2=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_2",flowrateIn=0.0,slugs=[])
    comp.append(_pump_2)
    _pump_3=Pump(volume=1.5,inlets=[],outlets=[],name="PUMP_3",flowrateIn=0.0,slugs=[])
    comp.append(_pump_3)
    #Valves
    _cwValve=Valve(volume=0.05,inlets=[],outlets=[],name="CW_VALVE",slugs=[])
    comp.append(_cwValve)
    _valve_1=Valve(volume=0.05,inlets=[],outlets=[],name="DIVERT_VALVE",slugs=[])
    comp.append(_valve_1)
    _flushCoilValve=Valve(volume=0.05,inlets=[],outlets=[],name="FLUSH_VALVE",slugs=[])
    comp.append(_flushCoilValve)
    #IR
    _IR=(IR(volume=0.5,inlets=[],outlets=[],name="IR",slugs=[]))
    comp.append(_IR)
    #Coil
    _coil=(Coil(volume=5,inlets=[],outlets=[],name="COIL",slugs=[]))
    comp.append(_coil)
    #Termini
    _waste=FlowTerminus(volume=0,inlets=[],outlets=[None],name="WASTE",flowrateIn=0,flowrateOut=0,slugs=[])
    comp.append(_waste)
    _collect=FlowTerminus(volume=0,inlets=[],outlets=[None],name="COLLECT",flowrateIn=0,flowrateOut=0,slugs=[])
    comp.append(_collect)
    _terminus_3=FlowTerminus(volume=0,inlets=[],outlets=[None],name="TERMINUS_3",flowrateIn=0,flowrateOut=0,slugs=[])
    comp.append(_terminus_3)
    _terminus_4=FlowTerminus(volume=0,inlets=[],outlets=[None],name="TERMINUS_4",flowrateIn=0,flowrateOut=0,slugs=[])
    comp.append(_terminus_4)
    
    _tPiece_1=TPiece(volume=0.05,inlets=[],outlets=[],name="TPIECE_1",slugs=[])
    comp.append(_tPiece_1)
    _tPiece_2=TPiece(volume=0.05,inlets=[],outlets=[],name="TPIECE_2",slugs=[])
    comp.append(_tPiece_2)
    
    _tubing_1=Tubing(volume=0.5,inlets=[],outlets=[],name="TUBE_1",slugs=[])
    comp.append(_tubing_1)
    _tubing_2=Tubing(volume=1,inlets=[],outlets=[],name="TUBE_2",slugs=[])
    comp.append(_tubing_2)
    _tubing_3=Tubing(volume=0.5,inlets=[],outlets=[],name="TUBE_3",slugs=[])
    comp.append(_tubing_3)
    _tubing_4=Tubing(volume=1,inlets=[],outlets=[],name="TUBE_4",slugs=[])
    comp.append(_tubing_4)
    ###################
    #Connect components

    #Stock solutions
    _redStock.flowInto(_pump_1)
    _blueStock.flowInto(_pump_2)
    _pinkStock.flowInto(_pump_3)
    #Pumplines 1/2
    _pump_1.flowInto(_tPiece_1)
    _pump_2.flowInto(_tPiece_1)
    #Divert valve
    _tPiece_1.flowInto(_tubing_1)
    _tubing_1.flowInto(_valve_1)
    _valve_1.flowInto(_coil)
    _valve_1.flowInto(_tubing_2)
    #Flush coil valve
    _tubing_2.flowInto(_flushCoilValve)
    _flushCoilValve.flowInto(_terminus_3)
    _flushCoilValve.flowInto(_terminus_4)
    #Coil
    _coil.flowInto(_tPiece_2)
    _pump_3.flowInto(_tPiece_2)
    _tPiece_2.flowInto(_tubing_3)
    _tubing_3.flowInto(_IR)
    _IR.flowInto(_tubing_4)
    _tubing_4.flowInto(_cwValve)
    _cwValve.flowInto(_waste)
    _cwValve.flowInto(_collect)
    #select one of the termini
    '''
    #Create path
    '''
    _path.addPath(comp)

    #TODO - Manually assign starting point for now
    _path.mapPathTermini()
    adrses=[str(key) for key in _path.addressesAll.keys()]
    
    print("*********************Segment details*********************")
    for _x in _path.segments:
        print(f"Comp name: {_x.name}")
        print(f" Inlet sets: {_x.inletSets}")
        print(f" Outlet sets: {_x.outletSets}")
        print(f" Curr inlets: {_x.inlets}")   
        print(f" Curr outlets: {_x.outlets}")
        print("--")
        
    print("************************Addresses*************************")
    for _x, _y in _path.addressesAll.items():
        print(f"Address for {_x}:")
        for x in _y:
            print(f" Comp: {x[0].name}")
            print(f"  Inlet set: UNDEFINED")
            print(f"  Outlet set: {x[1]}")
        print("--")
    #Some example things:
    flowRates=[0,1,2,3,4]
    dispVol=[1,2,3,4,5]
    
    # Flag variable to indicate whether the thread should continue running?
    running=True
    allSlugs=Slugs()
    def run_code():
        global running
        global allSlugs
        global _path
        _i=10
        while running:
            '''
            _flow_1=eval(input("Pump 1 flowrate: "))
            _flow_2=eval(input("Pump 2 flowrate: "))
            _flow_3=eval(input("Pump 3 flowrate: "))
            _slugVol=eval(input("Vol to dispense: "))
            '''
            _flow_1=random.choice(flowRates)
            _flow_2=random.choice(flowRates)
            _flow_3=random.choice(flowRates)
            _slugVol=random.choice(dispVol)
            
            _redStock.setFlowrate(_flow_1/60)
            _blueStock.setFlowrate(_flow_2/60)
            _pinkStock.setFlowrate(_flow_3/60)

            _path.updateFlowrates()

            _path.setCurrDestination(random.choice(adrses))
            _slug=_path.currRelOrigin.dispense(_slugVol)
            allSlugs.slugs.append(_slug)

            _now=time.perf_counter()
            _nowRefresh=_now
            _jiggleFlowrate=time.perf_counter() + 5
            #_path.timePrev=time.perf_counter()
            while not (isinstance(_slug.tailHost,FlowTerminus)):
                if time.time() - _jiggleFlowrate > 30:
                    _flow_1=random.choice(flowRates)
                    if _flow_1 == 0:
                        _flow_1=1
                    _flow_2=random.choice(flowRates)
                    _flow_3=random.choice(flowRates)
                    print("--")
                    print(f"New flowrates: {_flow_1}, {_flow_2}, {_flow_3}")
                    print("--")
                                        
                    _redStock.setFlowrate(_flow_1/60)
                    _blueStock.setFlowrate(_flow_2/60)
                    _pinkStock.setFlowrate(_flow_3/60)
                    
                    _jiggleFlowrate=time.time()

                _path.advanceSlugs()
                if time.time() - _nowRefresh > 1:
                    _vol=_slug.slugVolume()
                    _nowRefresh=time.time()
                    rep=f"""--------------------------------------------------\nTime: {round(time.perf_counter() - _now, 0)} sec,\nAll fr: {[_flow_1,_flow_2,_flow_3]}\nFront in: {_slug.frontHost.name},\n {round(_slug.frontHost.flowrateOut*60, 2)} mL.min-1,\n {round(_slug.frontHostPos, 2)}/{_slug.frontHost.volume} mL\nTail in: {_slug.tailHost.name},\n {round(_slug.tailHost.flowrateOut*60, 2)} mL.min-1,\n {round(_slug.tailHostPos, 2)}/{_slug.tailHost.volume} mL\nslug vol: {round(_vol, 2)} mL, vol collected: {(round(_slug.collectedVol, 2))} mL"""
                    print(rep)
                time.sleep(0.1)
            print("***************************************")
            print("Collected slug volumes")
            for _x in _path.collectedSlugs:
                print(f'Slug {_x} dispensed as {_x.totalDispensed} mL from origin and collected as {_x.collectedVol} mL')
                print(f'Slug was collected at terminus "{_x.frontHost.name}"')
            print("***************************************")
            _i+=1
            if _i > 10:
                exit()
            time.sleep(10)

    # Create a thread for running the code
    thread=threading.Thread(target=run_code)
    thread.start()

    # Wait for the thread to finish
    thread.join()
    print("We're done here")

    #######################################################################################
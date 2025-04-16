import json
import random
import time
import threading
import uuid
from Core.UI.brokers_and_topics import MqttTopics
from Core.Utils.Utils import Utils
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt


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

    def __init__(self,volume=None,name=None,inlets=None,outlets=None,deviceName=None,deviceType=None,flowrateOut=None,flowrateIn=None,slugs=None,lastAdvance=None,outletSets=None,inletSets=None,currOutlets=None,currInlets=None,remainder=None,settings=None,state=None,availableCommands=None,dispensing=False) -> None:
        self.volume=volume
        #######################################################################################
        #Inlet/outlet control
        self.inlets=inlets if inlets else []
        self.outlets=outlets if outlets else []
        self.inletSets=inletSets if inletSets else {}
        self.outletSets=outletSets if outletSets else {}
        self.currInletSet=None
        self.currOutletSet=None
        #######################################################################################
        self.name=name
        self.deviceName=deviceName
        self.deviceType=deviceType
        self.flowrateIn=flowrateIn if flowrateIn else 0
        self.flowrateOut=flowrateOut if flowrateOut else 0
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
        
        self.associatedPath=None
    
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
        if isinstance(outlet,Valve): #TODO - Temp fix for switchable valves inlets being lumped into same set
            setNameIn=setNameIn + "_" + str(outlet.valveCntr)
            outlet.valveCntr+=1
        self._addOutlet(outlet,setNameOut)
        outlet._addInlet(self,setNameIn)
        if not self.currOutletSet:
            self.switchToOutlets(setNameOut)
        if not outlet.currInletSet:
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
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)

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
        self.terminiMapped=False
        
        self.publishUI=False
        
        self.dumpNo=1
        
        self.slugCntr=1
        
        self.mqttService=None
        
        global FLOW_PATH
        FLOW_PATH=self
        
    def parseFlowSketch(self, sketchJson):
        self.terminiMapped=False
        """
        Parse the FlowSketch JSON format from the frontend and build the full flow path,
        connecting all components and tubing into a usable FlowPath structure.
        """
        self.segments = []
        self._componentLookup = {}
        self._tubingCounter = 1

        # Create components
        for uid, entry in sketchJson.items():
            component = self._createComponent(uid, entry)
            self.segments.append(component)

        # Wire up connections
        for uid, entry in sketchJson.items():
            source = self._componentLookup[uid]
            for targetUid in entry.get("flowsInto", []):
                print(f"WJ - Target UUID: {targetUid}")
                target = self._componentLookup.get(targetUid)
                if target:
                    source.flowInto(target)

        # print(f"Segments: {self.segments}")

        # Register path
        self.addPath(self.segments)

        # Map possible outlet routing
        self.mapPathTermini()

    def publishSlugTrackingInfo(self, slug, origin, dest):
        # Slug route: list of segments from origin to terminus
        print(f"Attempting to find path between {[origin,dest]}")
        route = self._findPath(origin, dest)
        if not route:
            print("No path found")
            return

        tracking = {}
        curr_pos = 0
        flowrate = slug.frontHost.flowrateOut  # mL/s

        for comp in route:
            if not hasattr(comp, 'volume'):
                continue  # Skip tubing or unknowns

            comp_id = comp.uid if hasattr(comp, 'uid') else comp.name
            vol = comp.volume  # mL
            time_in = vol / flowrate if flowrate > 0 else 0
            time_start = curr_pos / flowrate if flowrate > 0 else 0
            time_end = (curr_pos + vol) / flowrate if flowrate > 0 else 0

            tracking[comp_id] = {
                "componentName": comp.name,
                "volume": round(vol, 3),
                "slugFrontArrivesAt": round(time_start, 2),
                "slugFrontExitsAt": round(time_end, 2),
                "slugTailArrivesAt": round(time_start + slug.slugVolume() / flowrate, 2),
                "slugTailExitsAt": round(time_end + slug.slugVolume() / flowrate, 2),
            }

            curr_pos += vol

        payload = {
            "slugId": str(slug.slugId),
            "slugName": self.slugCntr,
            "slugVolume": slug.slugVolume(),
            "route": tracking,
            "timestamp": time.time(),
        }
        
        self.slugCntr+=1

        self.mqttService.publish(MqttTopics.getUiTopic("FlowTrackerOut"), json.dumps(payload))

    def dispense(self,vol=-1,comp=None):
        if not comp:
            comp=self.currRelOrigin
        slug=comp.dispense(vol)
        slug.targetTerminus=self._findComponentByName(self.currTerminus)
        print(f"Dispensing slug {[slug,slug.targetTerminus]}")
        if self.publishUI:
            self.publishSlugTrackingInfo(slug,comp,slug.targetTerminus)
        return slug
        
    def pullFromOrigin(self, origin):
        """
        Given a FlowOrigin component, trace a valid path to the current terminus and
        update inlets and outlets along that path to activate the route.
        """
        if not self.currTerminus:
            print("No terminus selected — cannot pull from origin.")
            return

        # Use name strings if necessary
        if isinstance(origin, str):
            origin = self._findComponentByName(origin)
        if isinstance(self.currTerminus, str):
            terminus = self._findComponentByName(self.currTerminus)
        else:
            terminus = self.currTerminus

        if origin is None or terminus is None:
            print("Could not resolve origin or terminus.")
            return

        # Trace path from origin to terminus using graph traversal
        path = self._findPath(origin, terminus)
        
        print(f"Priv func path: {[x.name for x in path]}")

        if not path:
            print(f"No valid path from {origin.name} to {terminus.name}")
            return

        # For each segment in path, set correct outlet/inlet pairs
        for i in range(len(path) - 1):
            currComp = path[i]
            nextComp = path[i + 1]

            # Set outlet
            for setName, comps in currComp.outletSets.items():
                if nextComp in comps:
                    currComp.switchToOutlets(setName)
                    break

            # Set inlet
            for setName, comps in nextComp.inletSets.items():
                if currComp in comps:
                    nextComp.switchToInlets(setName)
                    break

        self.currRelOrigin = origin
        print(f"Routing from '{origin.name}' to '{terminus.name}' is now active.")
        
    def visualizeFlowPath(self):

        G = nx.DiGraph()
        nodeLabels = {}
        nodeColors = []

        for comp in self.segments:
            # Enhanced Valve labeling
            if isinstance(comp, Valve):
                inletLabel = str([x.name for x in comp.inlets]) if comp.inlets else "None"
                outletLabel = str([x.name for x in comp.outlets]) if comp.outlets else "None"
                nodeLabels[comp] = f"{comp.name}\nIN: {inletLabel} | OUT: {outletLabel}"
            else:
                nodeLabels[comp] = comp.name

            # Node coloring
            if isinstance(comp, FlowOrigin):
                nodeColors.append("green")
            elif isinstance(comp, FlowTerminus):
                nodeColors.append("red")
            elif isinstance(comp, Valve):
                nodeColors.append("orange")
            elif isinstance(comp, Pump):
                nodeColors.append("blue")
            elif isinstance(comp, Tubing):
                nodeColors.append("grey")
            else:
                nodeColors.append("lightblue")

            for oSet in comp.outletSets.values():
                for target in oSet:
                    if target:
                        G.add_edge(comp, target)

        # --- Assign node depth via topological sort ---
        levels = defaultdict(list)
        nodeDepths = {}
        try:
            topoOrder = list(nx.topological_sort(G))
            for node in topoOrder:
                preds = list(G.predecessors(node))
                depth = max([nodeDepths[p] for p in preds], default=-1) + 1
                nodeDepths[node] = depth
                levels[depth].append(node)
        except Exception as e:
            print("Topological sort error:", e)
            return

        # --- Assign layout positions ---
        pos = {}
        for depth, nodes in levels.items():
            for i, node in enumerate(nodes):
                pos[node] = (depth * 2.0, -i * 2.0)

        # --- Active routing check ---
        terminus = self.currTerminus
        if isinstance(terminus, str):
            terminus = self._findComponentByName(terminus)

        pathEdges = []
        addressInfo = self.addressesAll.get(terminus.name) if terminus else None

        if terminus and addressInfo:
            routedSwitches = {comp: setName for comp, setName, *_ in addressInfo}

            for origin in [node for node in G.nodes if isinstance(node, FlowOrigin)]:
                try:
                    pathNodes = nx.shortest_path(G, source=origin, target=terminus)
                except nx.NetworkXNoPath:
                    continue

                valid = True
                for i in range(len(pathNodes) - 1):
                    comp = pathNodes[i]
                    nxt = pathNodes[i + 1]

                    if nxt not in comp.outlets or comp not in nxt.inlets:
                        print(f"{[x.name for x in comp.outlets]} and {[x.name for x in nxt.inlets]} have no common current connections!")
                        valid = False
                        break

                if valid:
                    print(f"{[x.name for x in comp.outlets]} and {[x.name for x in nxt.inlets]} have valid common current connections!")
                    edges = list(zip(pathNodes[:-1], pathNodes[1:]))
                    pathEdges.extend(edges)

        # --- Draw the graph ---
        fig, ax = plt.subplots(figsize=(14, 8))
        nx.draw(
            G, pos, with_labels=False, node_size=1500, node_color=nodeColors,
            edgecolors="black", linewidths=1.2,
            arrows=True, arrowsize=20, connectionstyle="arc3,rad=0.05", ax=ax
        )

        for node, (x, y) in pos.items():
            ax.text(
                x, y - 0.6, nodeLabels[node],
                ha='center', va='top',
                fontsize=8, fontweight='bold'
            )

        if pathEdges:
            nx.draw_networkx_edges(
                G, pos, edgelist=pathEdges,
                edge_color="black", width=3.8,
                arrows=True, arrowsize=15, connectionstyle="arc3,rad=0.05", ax=ax
            )

        print(f"WJ - current relative origin: {self.currRelOrigin.name}")
        ax.set_title("Flow System — Topological Layout", fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.show()
        
    def _findComponentByName(self, name):
        for comp in self.segments:
            if comp.name == name:
                return comp
        return None
    
    def dumpInletOutletSets(self):
        for seg in self.segments:
            if seg.inletSets:
                print(f"\n[INFO #{self.dumpNo}] {seg.name}: Inlet Sets")
                for name, comps in seg.inletSets.items():
                    print(f"  Set '{name}': {[x.name for x in comps]}")
                print(f"  Currently selected: {seg.currInletSet}")

            if seg.outletSets:
                print(f"[INFO #{self.dumpNo}] {seg.name}: Outlet Sets")
                for name, comps in seg.outletSets.items():
                    print(f"  Set '{name}': {[x.name for x in comps]}")
                print(f"  Currently selected: {seg.currOutletSet}")
        self.dumpNo+=1

    def _createComponent(self, uid, entry):
        """
        Create a component based on its deviceType from the JSON description.
        """
        name = entry.get("name", f"Unnamed_{uid}")
        volume = entry.get("volume", 0)
        deviceType = entry.get("deviceType", "null")
        deviceName = entry.get("deviceName", None)

        classMap = {
            "Pump": Pump,
            "Valve": Valve,
            "FlowOrigin": FlowOrigin,
            "FlowTerminus": FlowTerminus,
            "TPiece": TPiece,
            "Tubing": Tubing,
            "Coil": Coil,
            "IR": IR
        }

        componentClass = classMap.get(deviceType, VolObjNull)

        if deviceType == "Tubing":
            name = f"TUBE_{self._tubingCounter}"
            self._tubingCounter += 1

        obj = componentClass(
            volume=volume,
            name=name,
            deviceType=deviceType,
            deviceName=deviceName
        )
        
        obj.associatedPath=self

        self._componentLookup[uid] = obj
        return obj

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
                        # Also record inlet set name from nextComp
                        # This assumes the inletSet that contains currComp is unique
                        inletSetName = None
                        for iSetName, iSetComps in nextComp.inletSets.items():
                            print(f"Inletset names, components for {currComp}: {[iSetName,iSetComps]}")
                            if currComp in iSetComps:
                                inletSetName = iSetName
                                break
                        addresses.append([currComp, chosenSetName, nextComp, inletSetName])
                    else:
                        print(f"ChosenSetName for {[oSetName,oSetComps]} is None")
            self.addressesAll[terminus.name] = addresses
            self.terminiMapped=True

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
        for comp, outletSetName, nextComp, inletSetName in theseAddresses:
            comp.switchToOutlets(outletSetName)
            if inletSetName:
                nextComp.switchToInlets(inletSetName)

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
            print(f"This segment and inlets: {[segment.name,segment.inlets]}")
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
            
            # Check if outlet/inlets match and can actually flow forwards (TODO - Performance!)
            _nextHosts=_frontHost.outlets
            pathForward=False
            for x in _nextHosts:
                if _frontHost in x.inlets:
                    pathForward=True
                    break
            if not pathForward:
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
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class BPR(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Tubing(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class TPiece(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class IR(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
    def scan(self):
        pass
class Chip(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Coil(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Valve(FlowComponent):
    valveCntr=0
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class Pump(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class FlowOrigin(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)
class FlowTerminus(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing)

class CompoundDevice:
    def __init__(self):
        self.subDevices={}

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
        
        self.targetTerminus=None
        
        self.totalDispensed=totalDispensed
        self.lastDispenseCycleTime=lastDispenseCycleTime
        
        self.slugId=uuid.uuid4()

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

class FlowSystem:
    def __init__(self):
        self.flowpath=FlowPath()
        self.allSlugs=Slugs()
        
#######################################################################################
###Examples
if __name__ == "__main__":
    from Core.Fluids.FlowPath import FlowPath, Slugs, FlowTerminus, FlowOrigin
    from OPTIMIZATION_TEMP.Plutter_TEMP.plutter import MqttService
    
    updater = MqttService(broker_address="172.30.243.138")
    updater.connectDb=False
    updater.start()
    
    while not updater.flowSystem.flowpath.terminiMapped:
      time.sleep(1)
      
    path = updater.flowSystem.flowpath

    allSlugs = updater.flowSystem.allSlugs

    #Find component references from names
    origins = [comp for comp in path.segments if isinstance(comp,FlowOrigin)]
    
    print(f'Origins: {origins}')
    
    adrses = [name for name in path.addressesAll.keys()]

    #Some example things:
    #flowRates=[0,1,2,3,4]
    flowRates=[0.5,1,2]
    dispVol=[1]
    
    #Flag variable to indicate whether the thread should continue running?
    running=True
    time.sleep(1)
    def run_code():
      global running
      global allSlugs
      global path
      _i=0
      while running:

        for orig in origins:
          orig.setFlowrate((random.choice(flowRates)/60))

        path.updateFlowrates()

        path.setCurrDestination(random.choice(adrses))
        _slug=path.currRelOrigin.dispense(1)
        allSlugs.slugs.append(_slug)

        _now=time.perf_counter()
        _nowRefresh=_now
        _jiggleFlowrate=time.perf_counter() + 5
        #path.timePrev=time.perf_counter()
        while not (isinstance(_slug.tailHost,FlowTerminus)):
            path.advanceSlugs()
            if time.time() - _nowRefresh > 1:
                _vol=_slug.slugVolume()
                _nowRefresh=time.time()
                rep=f"""--------------------------------------------------\nTime: {round(time.perf_counter() - _now, 0)} sec,\nAll fr: {[orig.flowrateOut for orig in origins]}\nFront in: {_slug.frontHost.name},\n {round(_slug.frontHost.flowrateOut*60, 2)} mL.min-1,\n {round(_slug.frontHostPos, 2)}/{_slug.frontHost.volume} mL\nTail in: {_slug.tailHost.name},\n {round(_slug.tailHost.flowrateOut*60, 2)} mL.min-1,\n {round(_slug.tailHostPos, 2)}/{_slug.tailHost.volume} mL\nslug vol: {round(_vol, 2)} mL, vol collected: {(round(_slug.collectedVol, 2))} mL"""
                print(rep)
            time.sleep(0.1)
        print("***************************************")
        print("Collected slug volumes")
        for _x in path.collectedSlugs:
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
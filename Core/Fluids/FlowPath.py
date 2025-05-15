import json
import random
import time
import threading
import uuid
from Config.Data.hardcoded_command_templates import HardcodedCmndAddresses, HardcodedTeleAddresses
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

    def __init__(self,volume=None,name=None,inlets=None,outlets=None,deviceName=None,deviceType=None,flowrateOut=None,flowrateIn=None,slugs=None,lastAdvance=None,outletSets=None,inletSets=None,currOutlets=None,currInlets=None,remainder=None,settings=None,state=None,availableCommands=None,dispensing=False,uiId="",associatedCmndSource=None) -> None:
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
        self.associatedDevice=deviceName
        self.deviceType=deviceType
        self.flowrateIn=flowrateIn if flowrateIn else 0
        self.flowrateOut=flowrateOut if flowrateOut else 0
        self.slugs=slugs
        self.lastAdvance=lastAdvance
        self.dispensing=dispensing
        self.remainderToDispense=None
        self.remainder=remainder
        #Boolean flags
        #Settings and commands
        self.reservoirVolume=0 #Volume depletes as contents are dispensed
        self.isReservoir=False
        
        self.settings=settings
        self.state=state
        self.availableCommands=availableCommands
        #Hashmap id generator
        self.id=VolumeObject.idCounter
        VolumeObject.idCounter+=1
        
        self.residenceTime=None
        
        #UIid
        self.uiId=uiId
        
        self.associatedPath=None
        
        self.associatedCmndSource = associatedCmndSource if associatedCmndSource else {}
    
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
        print(f"Setting flowrate for {self.name} to {fr}")
        self.flowrateIn=fr
        self.cumulativeFlowrates()
     
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

    def setReservoirVol(self,vol):
        if not self.isReservoir:
            print(f"{self} is not a reservoir object!")
        self.reservoirVolume=vol

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

        #If no inputs, propagate flowrateOut directly from flowrateIn
        if len(self.inlets) == 0:
            self.flowrateOut = self.flowrateIn
            FLOW_PATH.flowrateShifted=True
            return

        #Calculate flowrate from all resolved inlets
        _flowrate = 0
        unresolved = False

        for inlet in self.inlets:
            if inlet.flowrateOut is not None:
                _flowrate += inlet.flowrateOut
            else:
                unresolved = True

        #Update flowrate if all inputs are resolved
        if not unresolved:
            self.flowrateIn = _flowrate
            self.flowrateOut = _flowrate  #Assume a single outlet for now
            
            if _flowrate != 0:
                self.residenceTime = (self.volume/_flowrate) #Residence time in min
            else:
                self.residenceTime = 0
            if not FLOW_PATH.flowrateShifted:
                FLOW_PATH.flowrateShifted=True
        else:
            raise ValueError(f"Unresolved flowrate inputs for {self.name}.")

    def hostSlug(self,slug,initPos):
        self.slugs.insert(0,slug)
        slug.frontHost=self
        slug.frontHostPos=initPos

class VolObjNull(VolumeObject):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)

class FlowPath:
    def __init__(self,mqttService,flowPathName=uuid.uuid4(),segments=[],segmentSets={},slugs=[],flowrate=0,time=time.perf_counter(),collectedSlugs=[]) -> None:
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
        self.recalcUiSlugs=False
        
        self.addresses=FlowAddresses("DEFAULT") #TODO - impliment instead of below
        self.addressesAll={}
        
        self.currTerminus=None
        self.currRelOrigin=None #Relative starting point in flow path that 'dispenses' slugs
        self.terminiMapped=False
        
        self.publishUI=False
        
        self.dumpNo=1
        
        self.slugCntr=1
        
        self.mqttService=mqttService
        
        self.initialized=False
        
        self.active=False
        
        self.flowLoopThread=None
        
        self.updateCmnd={} #a set
        self.updateCmndDevices=[]
        
        global FLOW_PATH
        FLOW_PATH=self
        
    def reset(self):
        self.segments=[]
        self.segmentSets=[]
        self.componentIndex=0
        self.slugs=[]
        self.flowPathName=uuid.uuid4()
        self.active=False
        self.flowLoopThread=None
        self.timePrev=time.time()
        
        self.addresses=FlowAddresses("DEFAULT") #TODO - impliment instead of below
        self.addressesAll={}
        
        self.currTerminus=None
        self.currRelOrigin=None #Relative starting point in flow path that 'dispenses' slugs
        self.terminiMapped=False
        
        self.initialized=False
        
        self.flowrateShifted=True
        self.recalcUiSlugs=False
        
        self.updateCmnd={} #a set
        self.updateCmndDevices=[]
        
        global FLOW_PATH
        FLOW_PATH=self
        
    def parseFlowSketch(self, sketchJson):
        print(f"Received flowsketch. Parsing...")
        self.terminiMapped=False
        """
        Parse the FlowSketch JSON format from the frontend and build the full flow path,
        connecting all components and tubing into a usable FlowPath structure.
        """
        self.segments = []
        self._componentLookup = {}
        self._tubingCounter = 1

        #Create components
        for uid, entry in sketchJson.items():
            component = self._createComponent(uid, entry)
            self.segments.append(component)

        #Wire up connections
        for uid, entry in sketchJson.items():
            source = self._componentLookup[uid]
            for targetUid in entry.get("flowsInto", []):
                # print(f"WJ - Target UUID: {targetUid}")
                target = self._componentLookup.get(targetUid)
                if target:
                    source.flowInto(target)

        #Register path
        self.addPath(self.segments)

        #Map possible outlet routing
        self.mapPathTermini()

    def publishSlugTrackingInfo(self, slug, origin=None, dest=None):
        if not origin:
            origin=slug.tailHost
        if not dest:
            dest=self.currTerminus
        #Slug route: list of segments from origin to terminus
        print(f"Attempting to find path between {[origin,dest]}")
        route = self._findPath(origin, dest) #TODO - 'origin' is whichever component tail/head are in
        if not route:
            print("No path found")
            return

        currCompFront = slug.frontHost
        currCompTail = None
        if slug.dispensed: #Is the tail moving yet?
            currCompTail = slug.tailHost
            
        tracking={}
        
        timeStartFront=-1
        timeEndFront=-1
        timeStartTail=-1
        timeEndTail=-1
        
        #Have the current positions been reached in loop?
        tailHit=False if currCompTail else True
        frontHit=False
        
        #0 if component already passed or NA
        for comp in route:

            vol = comp.volume  #mL
                            
            if not tailHit:
                if comp is currCompTail:
                    tailHit=True
                else:
                    tracking[comp.uiId] = {
                        "componentName": comp.name,
                        "volume": vol,
                        "slugFrontArrivesAt": timeStartFront,
                        "slugFrontExitsAt": timeEndFront,
                        "slugTailArrivesAt": timeStartTail,
                        "slugTailExitsAt": timeEndTail,
                    }
                    continue #No point checking headHit
                
            if not frontHit:
                if comp is currCompFront:
                    frontHit=True
            
            if tailHit:

                if slug.dispensed:
                    if comp is currCompTail:
                        timeEndTail = ((comp.residenceTime)*(1 - slug.tailHostPos/vol)) if vol != 0 else 0
                    else:
                        timeStartTail=timeEndTail
                        timeEndTail=timeEndTail + comp.residenceTime
                    
                if frontHit:
                    if comp is currCompFront:
                        timeStartFront = -1
                        timeEndFront  = ((comp.residenceTime)*(1 - slug.frontHostPos/vol)) if vol != 0 else 0
                    else:
                        timeStartFront = timeEndFront
                        timeEndFront = timeEndFront + comp.residenceTime
                
            tracking[comp.uiId] = {
                "componentName": comp.name,
                "volume": vol,
                "flowrate":comp.flowrateOut,
                "slugFrontArrivesAt": timeStartFront,
                "slugFrontExitsAt": timeEndFront,
                "slugTailArrivesAt": timeStartTail,
                "slugTailExitsAt": timeEndTail,
            }

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
        self.pullFromOrigin(comp)
        slug=comp.dispense(vol)
        slug.targetTerminus=self.currTerminus
        print(f"Dispensing slug, from, to {[slug,comp,slug.targetTerminus.name]}")
        if self.publishUI:
            self.publishSlugTrackingInfo(slug,comp.name,slug.targetTerminus.name)
        return slug
    
    def findPumpOrigin(self, pump):
        '''
        Iterate upstream and find first FlowOrigin. Assumes pump only pulls from one origin.
        '''
        if not isinstance(pump, Pump):
            return None

        visited = set()
        return self._recursiveOriginSearch(pump, visited)

    def _recursiveOriginSearch(self, component, visited):
        if component in visited:
            return None
        visited.add(component)

        if isinstance(component, FlowOrigin):
            return component

        if not hasattr(component, 'inlets') or not component.inlets:
            return None

        for inlet in component.inlets:
            origin = self._recursiveOriginSearch(inlet, visited)
            if origin:
                return origin

        return None

    def pullFromOrigin(self, origin):
        """
        Given a FlowOrigin component, trace a valid path to the current terminus and
        update inlets and outlets along that path to activate the route.
        """
        if not self.currTerminus:
            print("No terminus selected — cannot pull from origin.")
            return

        #Use name strings if necessary
        if isinstance(origin, str):
            origin = self._findComponentByName(origin)
        if isinstance(self.currTerminus, str):
            terminus = self._findComponentByName(self.currTerminus)
        else:
            terminus = self.currTerminus

        if origin is None or terminus is None:
            print("Could not resolve origin or terminus.")
            return

        #Trace path from origin to terminus using graph traversal
        path = self._findPath(origin, terminus)
        
        print(f"Priv func path: {[x.name for x in path]}")

        if not path:
            print(f"No valid path from {origin.name} to {terminus.name}")
            return

        #For each segment in path, set correct outlet/inlet pairs
        for i in range(len(path) - 1):
            currComp = path[i]
            nextComp = path[i + 1]

            #Set outlet
            for setName, comps in currComp.outletSets.items():
                if nextComp in comps:
                    currComp.switchToOutlets(setName)
                    break

            #Set inlet
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
            #Enhanced Valve labeling
            if isinstance(comp, Valve):
                inletLabel = str([x.name for x in comp.inlets]) if comp.inlets else "None"
                outletLabel = str([x.name for x in comp.outlets]) if comp.outlets else "None"
                nodeLabels[comp] = f"{comp.name}\nIN: {inletLabel} | OUT: {outletLabel}"
            else:
                nodeLabels[comp] = comp.name

            #Node coloring
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

        #--- Assign node depth via topological sort ---
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

        #--- Assign layout positions ---
        pos = {}
        for depth, nodes in levels.items():
            for i, node in enumerate(nodes):
                pos[node] = (depth * 2.0, -i * 2.0)

        #--- Active routing check ---
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

        #--- Draw the graph ---
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
                print(f"Found comp {comp.name}")
                return comp
        for comp in self.segments:
            if comp.uiId == name:
                print(f"Found comp {comp.uiId}")
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
        associatedCmndSource = entry.get("associatedCmndSource", {})
        
        print(f"0. AssociatedCmnds: {associatedCmndSource}")

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
            deviceName=deviceName,
            uiId=uid,
            associatedCmndSource=associatedCmndSource
        )
        
        obj.associatedPath=self

        self._componentLookup[uid] = obj
        
        if bool(associatedCmndSource):
            print(f"1. Received associated commands")
            if not deviceName in self.updateCmnd:
                self.updateCmnd[deviceName]={}
            if "flowrate" in associatedCmndSource:
                self.updateCmnd[deviceName]['flowrate']=associatedCmndSource["flowrate"]
            if 'valveState' in associatedCmndSource:
                pass
            self.updateCmndDevices.append(obj)
            
            self.mqttService.cmndUpdates[deviceName]={}

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

    def mapPathTermini(self):
        print("Mapping termini...")
        #Identify all FlowTerminus objects
        termini = [seg for seg in self.segments if isinstance(seg, FlowTerminus)]
        print("Term 1")

        if not termini:
            #Nothing to map
            print("No termini to map!")
            return
        print("Term 2")

        #Identify the origin component from which we should map paths.
        #If currRelOrigin is defined, use that. Otherwise, try to find a FlowOrigin or a node with no inlets.
        if self.currRelOrigin:
            start = self.currRelOrigin
        else:
            #Try to find a FlowOrigin
            origins = [seg for seg in self.segments if isinstance(seg, FlowOrigin)]
            if origins:
                start = origins[0]
            else:
                #If no FlowOrigin, pick a segment with no inlets as start
                #(i.e., a node that doesn't receive flow from any other node)
                candidates = []
                for seg in self.segments:
                    #If no inlets or inlets empty, it's a potential start
                    if not seg.inlets or len(seg.inlets) == 0:
                        candidates.append(seg)
                if candidates:
                    start = candidates[0]
                else:
                    #If no clear start found, just pick the first segment as start (fallback)
                    start = self.segments[0]
        print("Term 3")

        #Build a graph from segments: component -> list of downstream components
        #Note: we consider the currently active outlets. If multiple outlet sets exist,
        #we still have them stored in outletSets, but for pathfinding we just need the structure.
        self.graph = {}
        for seg in self.segments:
            #Combine all possible outlet sets to know the potential downstream connections
            #For mapping, we just want to know topologically who can be reached from who.
            #We'll store the union of all outlets in current sets for pathfinding.
            #If a component can switch outlets, they must appear in some outletSet.
            #We'll union all sets to find possible paths.
            
            downstream_nodes = set()
            if seg.outletSets:
                for oSet in seg.outletSets.values():
                    for outcomp in oSet:
                        if outcomp is not None:
                            downstream_nodes.add(outcomp)

            self.graph[seg] = list(downstream_nodes)

        #Now for each terminus, find a path and record the necessary outlet sets
        self.addressesAll = {}
        print("Term 4")
        for terminus in termini:
            path = self._findPath(start, terminus)
            if path is None:
                #No path found to this terminus
                print("Term 5")
                continue

            #path is a list of components from start to terminus
            #We want to record the outlet sets chosen at branching components
            #The address form: TerminusName: [ [ValveX, "A"], [ValveY, "B"] ... ]
            addresses = []

            #Iterate through path components and figure out which outletSet leads to the next node in the path
            #We look at pairs (currentComp, nextComp)
            for i in range(len(path)-1):
                print("Term 6")
                currComp = path[i]
                nextComp = path[i+1]

                #Check if currComp has multiple outlet sets
                if currComp.outletSets and len(currComp.outletSets.keys()) > 1:
                    #Find the outletSet that contains nextComp
                    chosenSetName = None
                    for oSetName, oSetComps in currComp.outletSets.items():
                        if nextComp in oSetComps:
                            chosenSetName = oSetName
                            print("Term 7")
                            break
                    if chosenSetName is not None:
                        print("Term 8")
                        #Also record inlet set name from nextComp
                        #This assumes the inletSet that contains currComp is unique
                        inletSetName = None
                        for iSetName, iSetComps in nextComp.inletSets.items():
                            print(f"Inletset names, components for {currComp}: {[iSetName,iSetComps]}")
                            if currComp in iSetComps:
                                inletSetName = iSetName
                                break
                        addresses.append([currComp, chosenSetName, nextComp, inletSetName])
                    else:
                        print(f"ChosenSetName for {[oSetName,oSetComps]} is None")
            print("Termini mapped.")
            self.addressesAll[terminus.name] = addresses
            self.terminiMapped=True

    def setCurrDestination(self, terminus):
        name=""
        if isinstance(terminus, str):
            compT = self._findComponentByName(terminus)
            if not (compT is None):
                name = compT.name
        else:
            compT = terminus
            name = terminus.name

        if name not in self.addressesAll:
            print(f"No route info available for {name}")
            return

        theseAddresses = self.addressesAll[name]
        #each element in theseAddresses is [component, outletSetName]
        for comp, outletSetName, nextComp, inletSetName in theseAddresses:
            comp.switchToOutlets(outletSetName)
            if inletSetName:
                nextComp.switchToInlets(inletSetName)

        #Optionally, we can set self.currTerminus to the target terminus
        #if we have a reference to the actual terminus object:
        if not isinstance(terminus, str):
            self.currTerminus = terminus
        else:
            self.currTerminus = compT
            
        self.flowrateShifted=True

    #Helper function to find a path from start to end
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

        #Build a dependency graph and calculate indegrees
        graph = defaultdict(list)
        indegree = defaultdict(int)

        for segment in self.segments:
            # print(f"This segment and inlets: {[segment.name,segment.inlets]}")
            for inlet in segment.inlets:
                graph[inlet].append(segment)
                indegree[segment] += 1

        #Initialize queue with segments that have no unresolved dependencies (indegree == 0)
        queue = deque(segment for segment in self.segments if indegree[segment] == 0)

        resolved = set()
        while queue:
            current = queue.popleft()
            resolved.add(current)

            #Update flowrates for the current segment
            current.cumulativeFlowrates()

            #Process downstream segments
            for downstream in graph[current]:
                indegree[downstream] -= 1
                if indegree[downstream] == 0:
                    queue.append(downstream)

        #Check if all segments were resolved
        if len(resolved) < len(self.segments):
            unresolved = [segment for segment in self.segments if segment not in resolved]
            raise ValueError(f"Unresolved dependencies in flow path: {unresolved}")

    def updateSlugs(self):
        for _x in self.segments:
            pass
        
    def allOrigins(self):
        return [x for x in self.segments if isinstance(x,FlowOrigin)]
    
    def allTermini(self):
        return [x for x in self.segments if isinstance(x,FlowTerminus)]

    def advanceSlugs(self):
        if self.flowrateShifted:
            self.updateFlowrates()
            if self.publishUI:
                #For now, only leading slug
                if len(self.slugs) != 0:
                    self.publishSlugTrackingInfo(self.slugs[0],dest=self.currTerminus)
            self.flowrateShifted = False

        _nowTime = time.perf_counter()
        _dT = _nowTime - self.timePrev
        self.timePrev = _nowTime

        if _dT <= 0:
            return

        if len(self.slugs) == 0: #Flowpath is homogenous
            return
        
        #Front movement
        for slug in self.slugs:
            _frontHost = slug.frontHost
            
            #If frontHost is None, no advancement
            if _frontHost is None:
                continue
            
            #If slug has reached a terminus and is collecting
            if isinstance(_frontHost, FlowTerminus):
                if not slug.collected:
                    #Increase collected volume by input flow * dT
                    slug.collectedVol += _frontHost.flowrateIn * _dT
                    if slug.reachedTerminusAt == 0:
                        slug.reachedTerminusAt = _nowTime
                #No further advancement needed for a terminus
                continue
            
            #Check if outlet/inlets match and can actually flow forwards (TODO - Performance!)
            _nextHosts=_frontHost.outlets
            pathForward=False
            for x in _nextHosts:
                if _frontHost in x.inlets:
                    pathForward=True
                    break
            if not pathForward:
                continue
            
            #Calculate displacement volume for this timestep
            _dV = _frontHost.flowrateOut * _dT
            _newVol = slug.frontHostPos + _dV

            #Check if slug surpasses the current frontHost volume
            if _newVol > _frontHost.volume:
                #We have leftover volume after filling this component
                _remainder = _newVol - _frontHost.volume

                #Move to next host(s)
                #Compute initial leftover time at the moment slug left _frontHost
                _currHostLeftToFill = (_frontHost.volume - slug.frontHostPos)
                _frontHostFillTime = _currHostLeftToFill / _frontHost.flowrateOut
                _dTRemainder = _dT - _frontHostFillTime

                #Identify the next host
                if len(_frontHost.outlets) == 0:
                    #No next host, slug stops here
                    slug.frontHostPos = _frontHost.volume
                    continue

                _nextHost = _frontHost.outlets[0]

                #If flowrates differ between hosts, adjust volume based on the nextHost’s flowrate
                if isinstance(_nextHost, FlowTerminus):
                    #If next host is a terminus, slug enters and is collected
                    slug.frontHost = _nextHost
                    #Adjust collectedVol by remainder
                    # slug.collectedVol += _remainder
                    slug.frontHostPos = 0
                    slug.collecting = True
                else:
                    #If next host has a different flowrate
                    if _nextHost.flowrateOut != _frontHost.flowrateOut:
                        _volumeAdd = _dTRemainder * _nextHost.flowrateOut
                    else:
                        _volumeAdd = _remainder

                    #Now, potentially continue through multiple hosts
                    slug.frontHost = _nextHost
                    #Use a loop to handle multiple jumps
                    _stillToFill = _volumeAdd

                    while _stillToFill > _nextHost.volume:
                        #Surpass this host entirely
                        _stillToFill -= _nextHost.volume

                        #Move to the next outlet
                        if len(_nextHost.outlets) == 0:
                            #No further hosts, slug ends here
                            slug.frontHostPos = _nextHost.volume
                            break

                        _nextHost = _nextHost.outlets[0]

                        if isinstance(_nextHost, FlowTerminus):
                            #Slug enters terminus and is collected
                            slug.frontHost = _nextHost
                            # slug.collectedVol += _stillToFill
                            slug.frontHostPos = 0
                            slug.collecting = True
                            _stillToFill = 0
                            break

                        #If next host differs in flowrate, we’d need additional logic here
                        #But for now we assume the computed _stillToFill works directly
                        slug.frontHost = _nextHost

                    #If we still have leftover that doesn't surpass the new host fully
                    if 0 < _stillToFill <= _nextHost.volume:
                        slug.frontHostPos = _stillToFill
                        
                if self.publishUI:
                    #For now, only leading slug
                    if len(self.slugs) != 0:
                        self.publishSlugTrackingInfo(self.slugs[0])
            else:
                #Slug remains within the same host
                slug.frontHostPos = _newVol

        #Tail movement
        #Similar logic applies for the tail. We allow multiple host jumps if needed.
        for slug in self.slugs[:]:  #copy list since we may remove slugs
            _tailHost = slug.tailHost

            #If tail is in a terminus, slug is collected
            if isinstance(_tailHost, FlowTerminus):
                if not slug.collected:
                    slug.collected = True
                    self.collectedSlugs.append(slug)
                    self.slugs.remove(slug)
                continue

            _dV = _tailHost.flowrateOut * _dT
            
            if _tailHost.dispensing:
                #Only dispense up to the remainder
                if _tailHost.remainderToDispense is not None:
                    if _dV > _tailHost.remainderToDispense:
                        #Cap _dV so we don't overshoot
                        _dV = _tailHost.remainderToDispense
                
                slug.totalDispensed += _dV

                if _tailHost.remainderToDispense is not None:
                    _tailHost.remainderToDispense -= _dV
                    if _tailHost.remainderToDispense <= 0:
                        _tailHost.dispensing = False
                        slug.dispensed=True
                        _tailHost.remainderToDispense = 0
                        if self.publishUI:
                            #For now, only leading slug
                            if len(self.slugs) != 0:
                                self.publishSlugTrackingInfo(self.slugs[0])
                continue

            _tailHostPos = slug.tailHostPos
            _newVol = _tailHostPos + _dV

            #Check if we surpass the tailHost's volume
            if _newVol > _tailHost.volume:
                _remainder = _newVol - _tailHost.volume

                #Move on to next host
                if len(_tailHost.outlets) == 0:
                    #No further hosts, so slug remains here
                    slug.tailHostPos = _tailHost.volume
                    continue

                _nextHost = _tailHost.outlets[0]

                if isinstance(_nextHost, FlowTerminus):
                    #Slug tail enters terminus - slug is collected
                    slug.collectedVol -= _remainder
                    slug.tailHost = _nextHost
                    slug.tailHostPos = 0
                    self.collectedSlugs.append(slug)
                    self.slugs.remove(slug)
                else:
                    #Handle multiple jumps for the tail
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
                            #No further hosts for the tail
                            slug.tailHostPos = _nextHost.volume
                            break

                        _nextHost = _nextHost.outlets[0]

                        if isinstance(_nextHost, FlowTerminus):
                            #Slug tail enters terminus
                            slug.collectedVol -= _stillToFill
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
                #Tail remains within the same host
                slug.tailHostPos = _newVol

    def flowPathLoop(self):
        
        print("Waiting for connection")
        while not self.mqttService.connected:
            time.sleep(0.5)

        print("Waiting for termini mapping")
        
        while not self.terminiMapped:
            time.sleep(0.5)
        
        self.updateFlowrates()
        # self.pullFromOrigin(self.currRelOrigin)
        
        self.active=True
        print(f"Flowpath {self.flowPathName} has started looping!")
        while self.active:
            if self.mqttService.cmndAvailable: #TODO - better solution
                print(f"5. A command is available")
                #TODO - net flowrate vir nou
                for dev in self.updateCmndDevices:
                    for x in self.updateCmnd[dev.associatedDevice].keys():
                        if x == "flowrate":
                            if isinstance(dev,Pump):
                                fr=HardcodedCmndAddresses.getVal(self.mqttService.cmndUpdates[dev.associatedDevice],dev.associatedDevice,self.updateCmnd[dev.associatedDevice]['flowrate'])
                                self.findPumpOrigin(dev).setFlowrate(fr/60)
                                print(f'Flowrate set to {fr}')
                        elif x == "valveState":
                            pass
                            
                self.mqttService.cmndAvailable=False
            self.advanceSlugs()
            time.sleep(0.1)
        print("Flow loop terminated!")

    def startFlowPathLoop(self):
        # Create a thread for running the code
        thread=threading.Thread(target=self.flowPathLoop)
        self.flowLoopThread=thread
        self.flowLoopThread.start()
        
        return self.flowLoopThread
    
    def stopFlowPathLoop(self):
        self.active = False
        if self.flowLoopThread.is_alive():
            self.flowLoopThread.join()

class FlowComponent(VolumeObject):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class BPR(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class Tubing(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class TPiece(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class IR(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
    def scan(self):
        pass
class Chip(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class Coil(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class Valve(FlowComponent):
    valveCntr=0
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class Pump(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class FlowOrigin(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)
class FlowTerminus(FlowComponent):
    def __init__(self, volume=None, name=None,  inlets=None, outlets=None,deviceName=None, deviceType=None, flowrateOut=None, flowrateIn=None, slugs=None, lastAdvance=None, outletSets=None, inletSets=None, currOutlets=None, currInlets=None, remainder=None, settings=None, state=None, availableCommands=None, dispensing=False, uiId="", associatedCmndSource=None):
        super().__init__(volume, name, inlets, outlets,deviceName, deviceType, flowrateOut, flowrateIn, slugs, lastAdvance, outletSets, inletSets, currOutlets, currInlets, remainder, settings, state, availableCommands, dispensing, uiId, associatedCmndSource)

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
        
        self.dispensed=False #Done dispensing?
        
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
    def __init__(self,mqttService):
        self.mqttService=mqttService
        self.flowpath=FlowPath(self.mqttService)
        self.allSlugs=Slugs()

if __name__ == "__main__":

    from OPTIMIZATION_TEMP.Plutter_TEMP.plutter import MqttService

    example={
    "reqUI": {
        "FlowSketcher": {
        "parseFlowsketch":{
            "3f6e37eb-40ee-4ed3-862e-d9800cd0c43e": {
            "name": "R4 Pump A",
            "flowsInto": [
                "tubing_1_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "vapourtecR4P1700",
            "deviceType": "Pump",
            "volume": 2
            },
            "tubing_1_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9": {
            "name": "Tubing",
            "flowsInto": [
                "29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "11aff382-a458-4a25-a311-db62c3c45843": {
            "name": "SR_A",
            "flowsInto": [
                "tubing_2_11aff382-a458-4a25-a311-db62c3c45843_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e"
            ],
            "deviceName": "null",
            "deviceType": "Valve",
            "volume": 0.25
            },
            "tubing_2_11aff382-a458-4a25-a311-db62c3c45843_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e": {
            "name": "Tubing",
            "flowsInto": [
                "3f6e37eb-40ee-4ed3-862e-d9800cd0c43e"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "ad33a7da-5b9d-4963-b9b3-9ed61d029bd2": {
            "name": "AllylIsoval",
            "flowsInto": [
                "tubing_3_ad33a7da-5b9d-4963-b9b3-9ed61d029bd2_11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_3_ad33a7da-5b9d-4963-b9b3-9ed61d029bd2_11aff382-a458-4a25-a311-db62c3c45843": {
            "name": "Tubing",
            "flowsInto": [
                "11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "e76868c1-4c46-4c35-be71-7cf388c4765d": {
            "name": "PushSolventA",
            "flowsInto": [
                "tubing_4_e76868c1-4c46-4c35-be71-7cf388c4765d_11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_4_e76868c1-4c46-4c35-be71-7cf388c4765d_11aff382-a458-4a25-a311-db62c3c45843": {
            "name": "Tubing",
            "flowsInto": [
                "11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "fcd5fb07-66aa-4b21-a306-6d8a873d60d9": {
            "name": "SR_B",
            "flowsInto": [
                "tubing_5_fcd5fb07-66aa-4b21-a306-6d8a873d60d9_59e6ec63-6719-483c-8467-c5ccffa0f563"
            ],
            "deviceName": "null",
            "deviceType": "Valve",
            "volume": 0.25
            },
            "tubing_5_fcd5fb07-66aa-4b21-a306-6d8a873d60d9_59e6ec63-6719-483c-8467-c5ccffa0f563": {
            "name": "Tubing",
            "flowsInto": [
                "59e6ec63-6719-483c-8467-c5ccffa0f563"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "59e6ec63-6719-483c-8467-c5ccffa0f563": {
            "name": "R4 Pump B",
            "flowsInto": [
                "tubing_6_59e6ec63-6719-483c-8467-c5ccffa0f563_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "vapourtecR4P1700",
            "deviceType": "Pump",
            "volume": 2
            },
            "tubing_6_59e6ec63-6719-483c-8467-c5ccffa0f563_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9": {
            "name": "Tubing",
            "flowsInto": [
                "29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "5915e364-75c6-49d0-b6af-f641f7b45754": {
            "name": "KOH_sol",
            "flowsInto": [
                "tubing_7_5915e364-75c6-49d0-b6af-f641f7b45754_fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_7_5915e364-75c6-49d0-b6af-f641f7b45754_fcd5fb07-66aa-4b21-a306-6d8a873d60d9": {
            "name": "Tubing",
            "flowsInto": [
                "fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "f926cf59-bfbc-4a69-9d52-e63d58f0d695": {
            "name": "PushSolventB",
            "flowsInto": [
                "tubing_8_f926cf59-bfbc-4a69-9d52-e63d58f0d695_fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_8_f926cf59-bfbc-4a69-9d52-e63d58f0d695_fcd5fb07-66aa-4b21-a306-6d8a873d60d9": {
            "name": "Tubing",
            "flowsInto": [
                "fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "29b52a6f-8bb5-41c0-baa8-3bab6d685ae9": {
            "name": "StaticMixer",
            "flowsInto": [
                "tubing_9_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9_d25f31e2-002b-48c7-b060-992d321ed9c4"
            ],
            "deviceName": "null",
            "deviceType": "TPiece",
            "volume": 0.05
            },
            "tubing_9_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9_d25f31e2-002b-48c7-b060-992d321ed9c4": {
            "name": "Tubing",
            "flowsInto": [
                "d25f31e2-002b-48c7-b060-992d321ed9c4"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "d25f31e2-002b-48c7-b060-992d321ed9c4": {
            "name": "Hotcoil_1",
            "flowsInto": [
                "tubing_10_d25f31e2-002b-48c7-b060-992d321ed9c4_fdcc2834-213b-42f7-bdde-b38e6a5c8172"
            ],
            "deviceName": "hotcoil1",
            "deviceType": "Coil",
            "volume": 5
            },
            "tubing_10_d25f31e2-002b-48c7-b060-992d321ed9c4_fdcc2834-213b-42f7-bdde-b38e6a5c8172": {
            "name": "Tubing",
            "flowsInto": [
                "fdcc2834-213b-42f7-bdde-b38e6a5c8172"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "fdcc2834-213b-42f7-bdde-b38e6a5c8172": {
            "name": "ReactIR 702L1",
            "flowsInto": [
                "tubing_11_fdcc2834-213b-42f7-bdde-b38e6a5c8172_e64f27b7-c346-4c86-94cd-c00398796894"
            ],
            "deviceName": "reactIR702L1",
            "deviceType": "IR",
            "volume": 0.25
            },
            "tubing_11_fdcc2834-213b-42f7-bdde-b38e6a5c8172_e64f27b7-c346-4c86-94cd-c00398796894": {
            "name": "Tubing",
            "flowsInto": [
                "e64f27b7-c346-4c86-94cd-c00398796894"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "e64f27b7-c346-4c86-94cd-c00398796894": {
            "name": "WasteOrCollect",
            "flowsInto": [
                "tubing_12_e64f27b7-c346-4c86-94cd-c00398796894_27151161-8edf-4152-9ea6-ce1df14f6f46",
                "tubing_13_e64f27b7-c346-4c86-94cd-c00398796894_f14f0372-3504-4559-ad7e-6a8661fdb7b4"
            ],
            "deviceName": "null",
            "deviceType": "Valve",
            "volume": 0.25
            },
            "tubing_12_e64f27b7-c346-4c86-94cd-c00398796894_27151161-8edf-4152-9ea6-ce1df14f6f46": {
            "name": "Tubing",
            "flowsInto": [
                "27151161-8edf-4152-9ea6-ce1df14f6f46"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "tubing_13_e64f27b7-c346-4c86-94cd-c00398796894_f14f0372-3504-4559-ad7e-6a8661fdb7b4": {
            "name": "Tubing",
            "flowsInto": [
                "f14f0372-3504-4559-ad7e-6a8661fdb7b4"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "27151161-8edf-4152-9ea6-ce1df14f6f46": {
            "name": "Product",
            "flowsInto": [],
            "deviceName": "null",
            "deviceType": "FlowTerminus",
            "volume": 0
            },
            "f14f0372-3504-4559-ad7e-6a8661fdb7b4": {
            "name": "Waste",
            "flowsInto": [],
            "deviceName": "null",
            "deviceType": "FlowTerminus",
            "volume": 0
            }
        }
        }
    }
    }

    mqttService=MqttService(broker_address="172.30.243.138")
    mqttService.connectDb=False
    mqttService.arm()
    mqttService.start()
    
    while not mqttService.connected:
        time.sleep(1)
    
    path=mqttService.flowSystem.flowpath
    path.mqttService.publish("ui/FlowSketcher",json.dumps(example))
    
    while not path.terminiMapped:
        time.sleep(1)
    
    path.startFlowPathLoop()
    
    origins=path.allOrigins()
    termini=path.allTermini()
    
    doExample=True
    numOfDisp=0
    numCollectedSlugs=1
        
    _now=time.time()
    _nowRefresh=time.time()
        
    while doExample and numOfDisp < 3:
        
        thisOrigin=random.choice(origins)
        thisTerminus=random.choice(termini)
        path.setCurrDestination(thisTerminus)
        
        path.visualizeFlowPath()
        
        thisOrigin.setFlowrate(2/60)
        slug=thisOrigin.dispense(1)
        while path.collectedSlugs != numCollectedSlugs:
            if time.time() - _nowRefresh > 1:
                _vol=slug.slugVolume()
                _nowRefresh=time.time()
                rep=f"""--------------------------------------------------\nTime: {round(time.time() - _now, 0)} sec,\nAll fr: {[orig.flowrateOut*60 for orig in origins]}\nFront in: {slug.frontHost.name},\n {round(slug.frontHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.frontHostPos, 2)}/{slug.frontHost.volume} mL\nTail in: {slug.tailHost.name},\n {round(slug.tailHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.tailHostPos, 2)}/{slug.tailHost.volume} mL\nslug vol: {round(_vol, 2)} mL, vol collected: {(round(slug.collectedVol, 2))} mL\n Current valve states:\n {
                    [[x.name,x.inlets[0].name,x.outlets[0].name] for x in path.segments if isinstance(x,Valve)]  
                })"""
                print(rep)
            time.sleep(2)
        
        numCollectedSlugs+=1
        numOfDisp+=1
        
        
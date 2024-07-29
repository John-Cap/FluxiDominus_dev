import time
from typing import List, Dict, Optional, Union

class FlowAddress:
    def __init__(self, name: str, inletsSett: Dict[str, List['FlowComponent']] = None, outletsSett: Dict[str, List['FlowComponent']] = None) -> None:
        self.name = name
        self.inletsSett = inletsSett or {}
        self.outletsSett = outletsSett or {}

    def setAddress(self, inletsSett: Dict[str, List['FlowComponent']], outletsSett: Dict[str, List['FlowComponent']]) -> None:
        self.inletsSett = inletsSett
        self.outletsSett = outletsSett


class VolumeObject:
    idCounter = 0

    def __init__(self, volume: Optional[float] = None, inlets: Optional[List['FlowComponent']] = None, outlets: Optional[List['FlowComponent']] = None,
                 name: Optional[str] = None, deviceName: Optional[str] = None, deviceType: Optional[str] = None, flowrateOut: Optional[float] = None,
                 flowrateIn: Optional[float] = None, slugs: Optional[List['Slug']] = None, lastAdvance: Optional[float] = None, outletSets: Optional[Dict[str, List['FlowComponent']]] = None,
                 inletSets: Optional[Dict[str, List['FlowComponent']]] = None, currOutlets: Optional[List['FlowComponent']] = None, currInlets: Optional[List['FlowComponent']] = None,
                 remainder: Optional[float] = None, settings: Optional[Dict[str, Union[str, float, bool]]] = None, state: Optional[str] = None,
                 availableCommands: Optional[List[str]] = None, dispensing: bool = False, associatedFlowPath: Optional['FlowPath'] = None) -> None:
        self.volume = volume
        self.inlets = inlets or []
        self.outlets = outlets or []
        self.name = name
        self.deviceName = deviceName
        self.deviceType = deviceType
        self.flowrateIn = flowrateIn
        self.flowrateOut = flowrateOut
        self.slugs = slugs or []
        self.lastAdvance = lastAdvance
        self.outletSets = outletSets or {}
        self.inletSets = inletSets or {}
        self.currOutlets = currOutlets or []
        self.currInlets = currInlets or []
        self.remainder = remainder
        self.flowrateShifted = False
        self.settings = settings
        self.state = state
        self.availableCommands = availableCommands or []
        self.dispensing = dispensing
        self.associatedFlowPath = associatedFlowPath
        self.id = VolumeObject.idCounter
        VolumeObject.idCounter += 1

    def dispense(self, targetTerminus: Optional['FlowTerminus'] = None) -> Optional['Slug']:
        if not self.dispensing and self.associatedFlowPath:
            print(f"{self.name} is busy dispensing!")
            self.dispensing = True
            _return = Slug(frontHost=self, tailHost=self, frontHostPos=0, tailHostPos=0, targetTerminus=targetTerminus)
            print(_return)
            self.associatedFlowPath.slugs.append(_return)
            return _return
        return None

    def terminateDispensing(self) -> None:
        if self.dispensing:
            self.dispensing = False

    def addInlet(self, comp: 'FlowComponent', setName: str = "DEFAULT") -> None:
        _thisInletSet = self.getInletSet(setName)
        if not _thisInletSet or (_thisInletSet == [None]):
            self.inletSets[setName] = [comp]
            self.inlets = self.inletSets[setName]
            self.flowrateShifted = True
        elif comp not in _thisInletSet:
            _thisInletSet.append(comp)

    def addOutlet(self, comp: 'FlowComponent', setName: str = "DEFAULT") -> None:
        _thisOutletSet = self.getOutletSet(setName)
        if not _thisOutletSet or (_thisOutletSet == [None]):
            self.outletSets[setName] = [comp]
            self.outlets = self.outletSets[setName]
            self.flowrateShifted = True
        elif comp not in _thisOutletSet:
            _thisOutletSet.append(comp)

    def flowInto(self, outlet: 'FlowComponent', setNameIn: str = "DEFAULT", setNameOut: str = "DEFAULT") -> None:
        self.addOutlet(outlet, setNameOut)
        outlet.addInlet(self, setNameIn)

    def addInletSet(self, setName: str = "DEFAULT", inlets: List['FlowComponent'] = None, overwrite: bool = True) -> Union[List['FlowComponent'], KeyError]:
        if setName not in self.inletSets:
            self.inletSets[setName] = inlets or []
        elif overwrite:
            self.inletSets[setName] = inlets or []
        else:
            return KeyError("Inlet-set name already used")
        return self.inletSets[setName]

    def addOutletSet(self, setName: str = "DEFAULT", outlets: List['FlowComponent'] = None, overwrite: bool = True) -> Union[List['FlowComponent'], KeyError]:
        if setName not in self.outletSets:
            self.outletSets[setName] = outlets or []
        elif overwrite:
            self.outletSets[setName] = outlets or []
        else:
            return KeyError("Outlet-set name already used")
        return self.outletSets[setName]

    def switchToInlets(self, setName: str = "DEFAULT") -> None:
        if setName in self.inletSets:
            self.inlets = self.inletSets[setName]

    def switchToOutlets(self, setName: str = "DEFAULT") -> None:
        if setName in self.outletSets:
            self.outlets = self.outletSets[setName]

    def getInletSet(self, setName: str = "DEFAULT") -> List['FlowComponent']:
        return self.inletSets.setdefault(setName, [])

    def getOutletSet(self, setName: str = "DEFAULT") -> List['FlowComponent']:
        return self.outletSets.setdefault(setName, [])

    def switchToDefaultInlets(self) -> List['FlowComponent']:
        return self.switchToInlets("DEFAULT") if len(self.inletSets) > 1 else self.inlets

    def switchToDefaultOutlets(self) -> List['FlowComponent']:
        return self.switchToOutlets("DEFAULT") if len(self.outletSets) > 1 else self.outlets

    def cumulativeFlowrates(self) -> None:
        if self.inlets is None:
            self.inlets = []
        if not self.inlets:
            self.flowrateOut = self.flowrateIn
        else:
            _flowrate = sum(
                _x.flowrateIn if isinstance(_x, FlowOrigin) else _x.flowrateOut
                for _x in self.inlets if _x is not None
            )
            self.flowrateIn = _flowrate
            self.flowrateOut = _flowrate  # only one outlet for now!
            self.flowrateShifted = False

    def hostSlug(self, slug: 'Slug', initPos: float) -> None:
        self.slugs.insert(0, slug)
        slug.frontHost = self
        slug.frontHostPos = initPos


class FlowComponent(VolumeObject):
    pass


class Tubing(FlowComponent):
    pass


class TPiece(FlowComponent):
    pass


class IR(FlowComponent):
    def scan(self) -> None:
        pass


class Chip(FlowComponent):
    pass


class Coil(FlowComponent):
    pass


class Valve(FlowComponent):
    pass


class Pump(FlowComponent):
    pass


class FlowOrigin(FlowComponent):
    pass


class FlowTerminus(FlowComponent):
    pass


class FlowPath:
    def __init__(self, segments: List[VolumeObject] = None, segmentSets: Dict[str, List[VolumeObject]] = None, slugs: List['Slug'] = None,
                 flowrate: float = 0, time: float = time.perf_counter(), collectedSlugs: List['Slug'] = None) -> None:
        self.segments = segments or []
        self.segmentSets = segmentSets or {}
        self.slugs = slugs or []
        self.flowrate = flowrate
        self.timePrev = time
        self.collectedSlugs = collectedSlugs or []

    def setAddress(self, address: FlowAddress) -> None:
        for _x in address.inletsSett.values():
            for comp in _x:
                comp.switchToInlets(address.inletsSett.get(comp.name, "DEFAULT"))
        for _x in address.outletsSett.values():
            for comp in _x:
                comp.switchToOutlets(address.outletsSett.get(comp.name, "DEFAULT"))

    def pathVolume(self, segmentSet: Optional[List[VolumeObject]] = None) -> float:
        segmentSet = segmentSet or self.segments
        return sum(_x.volume for _x in segmentSet)

    def addPath(self, segments: List[VolumeObject], pathName: str = "DEFAULT") -> None:
        self.segmentSets[pathName] = segments
        self.segments = segments

    def addSlug(self, slug: 'Slug') -> None:
        self.slugs.append(slug)

    def hostSlug(self, slug: 'Slug', initPos: float) -> None:
        self.slugs.insert(0, slug)
        slug.frontHost = self
        slug.frontHostPos = initPos

    def terminate(self, slug: 'Slug') -> None:
        self.slugs.remove(slug)
        slug.tailHost.terminateSlug(slug)

    def terminateSlug(self, slug: 'Slug') -> None:
        if slug in self.slugs:
            self.slugs.remove(slug)


class Slug:
    def __init__(self, frontHost: VolumeObject, tailHost: VolumeObject, frontHostPos: float, tailHostPos: float, targetTerminus: Optional[FlowTerminus] = None) -> None:
        self.frontHost = frontHost
        self.tailHost = tailHost
        self.frontHostPos = frontHostPos
        self.tailHostPos = tailHostPos
        self.targetTerminus = targetTerminus

    def __repr__(self) -> str:
        return f"Slug(frontHost={self.frontHost.name}, tailHost={self.tailHost.name}, frontHostPos={self.frontHostPos}, tailHostPos={self.tailHostPos})"


def main() -> None:
    # Create components
    pump1 = Pump(name="Pump1", flowrateIn=10.0)
    valve1 = Valve(name="Valve1")
    tubing1 = Tubing(name="Tubing1", flowrateIn=10.0)
    terminus = FlowTerminus(name="Terminus")

    # Create a flow path
    path = FlowPath()

    # Define address
    address = FlowAddress(name="FlowPathAddress")
    address.setAddress(
        inletsSett={pump1.name: [pump1]},
        outletsSett={terminus.name: [terminus]}
    )

    # Create a volume object
    volume = VolumeObject(volume=100.0, name="Volume1", associatedFlowPath=path)
    volume.addInlet(pump1)
    volume.addOutlet(valve1)

    # Dispense a slug
    slug = volume.dispense(targetTerminus=terminus)
    if slug:
        print(f"Dispensed slug: {slug}")

    # Add path segments
    path.addPath([volume, tubing1, terminus])

    # Print volume and path details
    print(f"Volume: {volume.volume} L")
    print(f"Path Volume: {path.pathVolume()} L")
    print(f"Slugs in path: {path.slugs}")

if __name__ == "__main__":
    main()

import json

from Config.devices.standard import StandardConfiguratedDevices
from Core.Fluids.FlowPath import FlowPath

class ParseFlowpath:
    def __init__(self, json_string):
        self.json_data = (json.loads(json_string.replace('"null"',"null")))
        self.components = {}  # Store instantiated components
        self.flow_path = FlowPath()
    
    def parse(self):
        """Parses the JSON and sets up the flow path."""
        # Step 1: Instantiate components
        for uuid, data in self.json_data.items():
            component_type = data["deviceType"]
            params = (data["volume"],data["name"])
            self.components[uuid] = StandardConfiguratedDevices.initializeComponent(component_type, params)
        
        # Step 2: Set up connections based on "flowsInto"
        for uuid, data in self.json_data.items():
            component = self.components[uuid]
            if data["flowsInto"]:
                for target_uuid in data["flowsInto"]:
                    target_component = self.components.get(target_uuid)
                    if target_component:
                        component.flowInto(target_component)
        
        # Step 3: Add components to the flow path
        self.flow_path.addPath(list(self.components.values()))
        self.flow_path.mapPathTermini()
    
    def get_flow_path(self):
        return self.flow_path

# Example usage
if __name__ == "__main__":
    jsonStringFromFlutter="""
{"8af0317e-da46-4691-b626-3cd4bd112824":{"name":"ReactIR 702L1","flowsInto":["25bbb0be-174d-4c96-8b49-524c57a4f7fd"],"deviceName":"reactIR702L1","deviceType":"IR","volume":0.25},"10519cdc-ca37-4f94-9936-7b70e17638bc":{"name":"Push","flowsInto":["cc700217-c23a-4589-b3dc-e4781b9f9a1a"],"deviceName":"null","deviceType":"FlowOrigin","volume":0},"51172d2d-f4e5-4801-bc37-e03c2ff25eb7":{"name":"Hotcoil (20 mL)","flowsInto":["8af0317e-da46-4691-b626-3cd4bd112824"],"deviceName":"hotcoil1","deviceType":"Coil","volume":20},"6a95e31c-30b0-45ab-9fff-5ffc2e6565fb":{"name":"R4 (Peristaltic)","flowsInto":["51172d2d-f4e5-4801-bc37-e03c2ff25eb7"],"deviceName":"vapourtecR4P1700","deviceType":"vapourtecR4","volume":5},"d9b9844f-9a16-436d-ba31-635f936765cf":{"name":"Stock","flowsInto":["cc700217-c23a-4589-b3dc-e4781b9f9a1a"],"deviceName":"null","deviceType":"FlowOrigin","volume":0},"cc700217-c23a-4589-b3dc-e4781b9f9a1a":{"name":"Valve","flowsInto":["6a95e31c-30b0-45ab-9fff-5ffc2e6565fb"],"deviceName":"null","deviceType":"Valve","volume":0.25},"25bbb0be-174d-4c96-8b49-524c57a4f7fd":{"name":"BPR (8 Bar)","flowsInto":["c86132da-f576-4f00-93c2-1ea5291d9d68"],"deviceName":"null","deviceType":"BPR","volume":0.1},"c86132da-f576-4f00-93c2-1ea5291d9d68":{"name":"Valve","flowsInto":["29a85459-ddbe-484b-a1b5-7bd800e8be3a","64fb162e-2b48-4cf2-820e-f7aedef55606"],"deviceName":"null","deviceType":"Valve","volume":0.25},"29a85459-ddbe-484b-a1b5-7bd800e8be3a":{"name":"Collection point","flowsInto":null,"deviceName":"null","deviceType":"FlowTerminus","volume":0},"64fb162e-2b48-4cf2-820e-f7aedef55606":{"name":"Collection point","flowsInto":null,"deviceName":"null","deviceType":"FlowTerminus","volume":0}}

    """
    #jsonStringFromFlutter = """<insert JSON here>"""
    parser = ParseFlowpath(jsonStringFromFlutter)
    parser.parse()
    flow_path = parser.get_flow_path()
    
    # Print path details
    for segment in flow_path.segments:
        print(f"Component: {segment.name}, Inlet sets: {segment.inletSets}, Outlet sets: {segment.outletSets}")

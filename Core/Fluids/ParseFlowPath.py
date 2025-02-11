
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
{"aa762ff2-5017-446b-ab75-da692637a805":{"name":"Flowsyn Maxi 2","flowsInto":["74384fba-1087-4a4e-b32b-435dd58a4f74"],"deviceName":"flowsynmaxi1","deviceType":"FlowsynMaxi","volume":5},"72212b59-d382-49b0-98d8-5cfa831458f0":{"name":"R4 (HPLC)","flowsInto":["74384fba-1087-4a4e-b32b-435dd58a4f74"],"deviceName":"vapourtecR4P1700","deviceType":"vapourtecR4","volume":5},"8fcfa765-8cac-4b42-9dfb-38dcd4496b67":{"name":"Push","flowsInto":["93ad0331-6350-4abc-869e-d81d75fa2867"],"deviceName":"null","deviceType":"FlowOrigin","volume":0},"a8d79676-f2eb-4363-9a72-caec5be27cc4":{"name":"Stock","flowsInto":["93ad0331-6350-4abc-869e-d81d75fa2867"],"deviceName":"null","deviceType":"FlowOrigin","volume":0},"93ad0331-6350-4abc-869e-d81d75fa2867":{"name":"Valve","flowsInto":["aa762ff2-5017-446b-ab75-da692637a805"],"deviceName":"null","deviceType":"Valve","volume":0.25},"5a6d36e1-c2dc-4880-a1a8-1cc2dd3da3af":{"name":"Push","flowsInto":["72212b59-d382-49b0-98d8-5cfa831458f0"],"deviceName":"null","deviceType":"FlowOrigin","volume":0},"74384fba-1087-4a4e-b32b-435dd58a4f74":{"name":"Hotcoil (20 mL)","flowsInto":["7a418de5-4e6d-4606-90d5-719717ba57e9"],"deviceName":"hotcoil1","deviceType":"Coil","volume":20},"7a418de5-4e6d-4606-90d5-719717ba57e9":{"name":"BPR (5 Bar)","flowsInto":["0be456a5-cf6f-4058-b27d-0337da8c1e35"],"deviceName":"null","deviceType":"BPR","volume":0.1},"0be456a5-cf6f-4058-b27d-0337da8c1e35":{"name":"Valve","flowsInto":["4aba0242-4f23-4d01-8149-b67ebd15fa11","10b85d74-4bcf-49fb-b114-3c0d7f5cd358"],"deviceName":"null","deviceType":"Valve","volume":0.25},"4aba0242-4f23-4d01-8149-b67ebd15fa11":{"name":"Collection point","flowsInto":null,"deviceName":"null","deviceType":"FlowTerminus","volume":0},"c5afa68e-6c94-488e-a406-2a14b5f2b2ce":{"name":"Flowsyn Maxi 1","flowsInto":null,"deviceName":"flowsynmaxi2","deviceType":"FlowsynMaxi","volume":5},"10b85d74-4bcf-49fb-b114-3c0d7f5cd358":{"name":"Collection point","flowsInto":null,"deviceName":"null","deviceType":"FlowTerminus","volume":0}}

    """
    #jsonStringFromFlutter = """<insert JSON here>"""
    parser = ParseFlowpath(jsonStringFromFlutter)
    parser.parse()
    flow_path = parser.get_flow_path()
    
    # Print path details
    for segment in flow_path.segments:
        print(f"Component: {segment.name}, Inlet sets: {segment.inletSets}, Outlet sets: {segment.outletSets}")

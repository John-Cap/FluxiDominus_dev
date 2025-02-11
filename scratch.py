import json

from Config.devices.standard import StandardConfiguratedDevices
from Core.Fluids.FlowPath import FlowPath

class ParseFlowpath:
    def __init__(self, json_string):
        self.json_data = json.loads(json_string)
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
        {
        "9d84f9a9-8665-4883-a506-4aa07cee48ab": {
            "name": "Flowsyn Maxi 2",
            "flowsInto": [
            "7b51af7b-ccec-4a47-a13c-ba16eb65b973"
            ],
            "deviceName": "flowsynmaxi1",
            "deviceType": "Pump",
            "volume": 5
        },
        "6892d932-90df-447b-b1f8-77020f8ef4f5": {
            "name": "R4 (Peristaltic)",
            "flowsInto": [
            "7b51af7b-ccec-4a47-a13c-ba16eb65b973"
            ],
            "deviceName": "vapourtecR4P1700",
            "deviceType": "Pump",
            "volume": 5
        },
        "07e4e67d-88a5-486b-9919-83f41aadb926": {
            "name": "Valve",
            "flowsInto": [
            "6892d932-90df-447b-b1f8-77020f8ef4f5"
            ],
            "deviceName": null,
            "deviceType": "Valve",
            "volume": 0.25
        },
        "86f76937-a5a4-4821-947c-f3686d0593f8": {
            "name": "Push",
            "flowsInto": [
            "07e4e67d-88a5-486b-9919-83f41aadb926"
            ],
            "deviceName": null,
            "deviceType": "FlowOrigin",
            "volume": 0
        },
        "2a3dbe75-f252-4d84-a5bd-46abdac44883": {
            "name": "Stock",
            "flowsInto": [
            "07e4e67d-88a5-486b-9919-83f41aadb926"
            ],
            "deviceName": null,
            "deviceType": "FlowOrigin",
            "volume": 0
        },
        "701867bb-daa6-48e6-94b4-c52a11eb6626": {
            "name": "Stock",
            "flowsInto": [
            "9d84f9a9-8665-4883-a506-4aa07cee48ab"
            ],
            "deviceName": null,
            "deviceType": "FlowOrigin",
            "volume": 0
        },
        "7b51af7b-ccec-4a47-a13c-ba16eb65b973": {
            "name": "Hotcoil (10 mL)",
            "flowsInto": [
            "1b28500a-8bf6-4c89-8e09-2416f3e1cc5a"
            ],
            "deviceName": "hotcoil1",
            "deviceType": "Coil",
            "volume": 10
        },
        "1b28500a-8bf6-4c89-8e09-2416f3e1cc5a": {
            "name": "ReactIR 702L1",
            "flowsInto": [
            "96f1d6fd-1304-4e72-a124-8c31dd082e57"
            ],
            "deviceName": "reactIR702L1",
            "deviceType": "IR",
            "volume": 0.25
        },
        "96f1d6fd-1304-4e72-a124-8c31dd082e57": {
            "name": "BPR (8 Bar)",
            "flowsInto": [
            "d2222e10-c5e6-4cd7-add6-21da90dd72ae"
            ],
            "deviceName": null,
            "deviceType": "BPR",
            "volume": 0.1
        },
        "d2222e10-c5e6-4cd7-add6-21da90dd72ae": {
            "name": "Valve",
            "flowsInto": [
            "51dfd5fe-fa37-4dd3-8b26-a3ccb63a8a6f",
            "242b2435-c911-42d0-bfaf-a2e34d554edf"
            ],
            "deviceName": null,
            "deviceType": "Valve",
            "volume": 0.25
        },
        "242b2435-c911-42d0-bfaf-a2e34d554edf": {
            "name": "Collection point",
            "flowsInto": null,
            "deviceName": null,
            "deviceType": "FlowTerminus",
            "volume": 0
        },
        "51dfd5fe-fa37-4dd3-8b26-a3ccb63a8a6f": {
            "name": "Collection point",
            "flowsInto": null,
            "deviceName": null,
            "deviceType": "FlowTerminus",
            "volume": 0
        }
        }
    """
    #jsonStringFromFlutter = """<insert JSON here>"""
    parser = ParseFlowpath(jsonStringFromFlutter)
    parser.parse()
    flow_path = parser.get_flow_path()
    
    # Print path details
    for segment in flow_path.segments:
        print(f"Component: {segment.name}, Inlets: {segment.inlets}, Outlets: {segment.outlets}")

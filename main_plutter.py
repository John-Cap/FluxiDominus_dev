from opcua import Client

# OPC UA endpoint and node details
opcua_url = "opc.tcp://146.64.91.174:62552/iCOpcUaServer"
node_id = "ns=2;s=Local.iCIR.Probe1.SpectraTreated"

def read_opcua_array():
    # Create a client object to connect to the OPC UA server
    client = Client(opcua_url)
    
    try:
        # Connect to the OPC UA server
        client.connect()
        print(f"Connected to OPC UA server at {opcua_url}")
        
        # Get the node using the provided node ID
        node = client.get_node(node_id)
        
        # Read the array value from the node
        value = node.get_value()
        
        print(f"Value from node '{node_id}': {value}")
        
    except Exception as e:
        print(f"Error reading OPC UA node: {e}")
        
    finally:
        # Close the connection to the OPC UA server
        client.disconnect()
        print("Disconnected from OPC UA server")

if __name__ == "__main__":
    read_opcua_array()

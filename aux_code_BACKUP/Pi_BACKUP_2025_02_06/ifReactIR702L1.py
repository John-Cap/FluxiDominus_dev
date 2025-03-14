# -*- coding: utf-8 -*-ï¿½ # Use UTF-8 encoding for better compatibility
import paho.mqtt.client as mqtt
import time
import socket
import json
import threading
import opcua
import asyncio

from opcua import Client

# Constants
MQTT_TOPIC_CMND = "subflow/reactIR702L1/cmnd"
MQTT_TOPIC_TELE = "subflow/reactIR702L1/tele"
MQTT_BROKER_ADDRESS = "146.64.91.174"  # Replace with your broker address
MQTT_BROKER_PORT = 1883
DEVICE_IP_ADDRESS = "192.168.1.50"
DEVICE_PORT = 62552
DEVICE_RT_POLL_PERIOD = 5

# Global variables
# opc.tcp://192.168.1.50:62552/iCOpcUaServer
device_info = {
    "deviceName": "reactIR702L1",
    "deviceType": "IR",
    "inUse": False,
    "remoteEnabled": False,
    "connDetails":{
        "ipCom" : {
            "addr": DEVICE_IP_ADDRESS,
            "port": DEVICE_PORT,
        }
    },
    "tele": {
        "cmnd": "",
        "settings": {},
        "state": {"data": []},
        "timestamp": ""
    }
}

# Function to handle MQTT messages
def on_message(client, userdata, message):
    global device_info

    try:
        payload = message.payload.decode()
        data = json.loads(payload)

        if (data["deviceName"] == device_info["deviceName"]):
            if (data["settings"]["command"] == "SET"):
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                print("Command ...")

            elif data["settings"]["command"] == "REMOTEEN":
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "REMOTEEN"
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

            elif (data["settings"]["command"] == "REMOTEDIS") :
                device_info["inUse"] = False
                device_info["remoteEnabled"] = False
                device_info["tele"]["cmnd"] = "REMOTEDIS"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

            # print("Sent:{}".format(data))
            # print("Received:{}".format(received))
            # print("Global: {}".format(device_info))
    except Exception as e:
        print("Error On Msg:", e)
        print("Sent:{}".format(data))
        print("Global: {}".format(device_info))

# Function to start the periodic task for reading real-time data
def read_real_time_data():
    global device_info

    opcua_url = "opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) + ":" + str(device_info["connDetails"]["ipCom"]["port"]) + "/iCOpcUaServer"
    node_id = "ns=2;s=Local.iCIR.Probe1.SpectraTreated"

    if (device_info["inUse"] == True) :
        try:
            clientOPC = Client(opcua_url)
            clientOPC.connect()
            # Get the node using the provided node ID
            node = clientOPC.get_node(node_id)
            # Read the array value from the node
            value = node.get_value()
            # Convert the array to a JSON object
            #json_data = json.dumps(value)

            # print(f"Value from node '{node_id}': '{json_data}'")
            device_info["tele"]["state"]["data"] = value
            device_info["tele"]["cmnd"] = "POLL"
            # print("Global: {}".format(device_info))

            # Publish the updated device_info
            client.publish(MQTT_TOPIC_TELE, json.dumps(device_info))

        except Exception as e:
            print("Error reading real-time data:", e)
            print("Global: {}".format(device_info))

        finally:
            # Close the connection to the OPC UA server
            clientOPC.disconnect()
            # print("Disconnected from OPC UA server")

    threading.Timer(DEVICE_RT_POLL_PERIOD, read_real_time_data).start()

# Initialize MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT)
client.subscribe(MQTT_TOPIC_CMND)
print("MQTT Setup complete...")

# polling_thread = threading.Thread(target=read_real_time_data)
# polling_thread.start()
threading.Timer(DEVICE_RT_POLL_PERIOD, read_real_time_data).start()
print("Thread started complete...")

# Start the MQTT loop
print("MQTT Loop started complete...")
client.loop_forever()

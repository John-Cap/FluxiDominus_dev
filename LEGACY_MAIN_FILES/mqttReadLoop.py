import time
import paho.mqtt.client as mqtt
import json
from Core.Communication.Network import MQTTReader

print("Here")
_this=MQTTReader()
_this.readMQTTLoop()

# MQTT Broker Settings
broker_address = "146.64.91.174"
port = 1883

# Callback function to handle when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        pass
        #print("Connected to broker")
    else:
        print("Connection failed with error code " + str(rc))

# Create MQTT client instance
client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
# Assign on_connect callback to client
client.on_connect = on_connect
client.on_message = MQTTReader().on_message

# Connect to MQTT broker

client.connect(broker_address, port, 1)
client.loop_start()

#{"deviceName":"hotcoil1","deviceType":"Hotchip","cmnd":"POLL","settings":{"temp":29.5}, "state": {"temp": 14.5, "state":"ON"}}

client.subscribe("subflow/hotcoil1/tele")

while True:
    pass

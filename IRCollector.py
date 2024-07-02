
import paho.mqtt.client as mqtt
from Core.Communication.Network import MQTTReader
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder

from Core.Diagnostics.Logging import Diag_log

#Logging
diag_log=Diag_log()

# MQTT Broker Settings
broker_address = "192.168.1.2"
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

# Connect to MQTT broker

client.connect(broker_address, port, 1)
client.loop_start()

# Script listener

_MQTTReader=MQTTReader()
_MQTTReader.readMQTTLoop()

_fdpDecoder=FdpDecoder()

while True:
    pass
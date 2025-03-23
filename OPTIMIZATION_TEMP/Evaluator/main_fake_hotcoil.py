import json
from time import sleep
import paho.mqtt.client as mqtt

mqttClient=mqtt.Client()
mqttClient.connect(host="localhost")
mqttClient.loop_start()

"""
{"deviceName": "hotcoil1", "deviceType": "Hotchip", "inUse": True, "remoteEnabled": True, "ipAddr": "192.168.1.213", "port": 81, "tele": {"cmnd": "POLL", "settings": {"temp": 0.1}, "state": {"temp": 17.83, "state": "ON"}, "timestamp": ""}}
"""
evaluate=False
tempMin=0
tempMax=100
tempPerSec=1
temp=0
up=False
while True:
    if temp <= tempMin:
        temp += tempPerSec
        up=True
    elif temp >= tempMax:
        temp -= tempPerSec
        up=False
    elif up:
        temp += tempPerSec
    elif not up:
        temp -= tempPerSec
        
    payload={"deviceName": "hotcoil1", "deviceType": "Hotchip", "inUse": True, "remoteEnabled": True, "ipAddr": "192.168.1.213", "port": 81, "tele": {"cmnd": "POLL", "settings": {"temp": temp}, "state": {"temp": temp, "state": "ON"}, "timestamp": ""}}
    mqttClient.publish(topic="subflow/hotcoil1/tele",payload=json.dumps(payload))
    sleep(1)

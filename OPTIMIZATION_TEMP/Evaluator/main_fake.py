import json
import os
import random
from time import sleep
import time
import numpy as np
import pandas as pd

import paho.mqtt.client as mqtt

# Define the folder containing the CSV files
folder_path = ""  # Change if needed

# List of CSV files to load
csv_files = [
    "ir_yield_no_resample_averages.csv",
    "ir_yield_no_resample_unaveraged.csv",
    "ir_yield_no_resample_unmasked.csv",
    "ir_yield_training_data.csv",
]

# Dictionary to store the data from each file
data_dict = {}

for file in csv_files:
    file_path = os.path.join(folder_path, file)
    
    # Load the CSV while skipping the first row (header)
    df = pd.read_csv(file_path)
    
    # Remove the last column
    df = df.iloc[:, :-1]
    
    # Convert to list of arrays (one per line)
    data_dict[file] = [row.values for _, row in df.iterrows()]

mqttClient=mqtt.Client()
mqttClient.connect(host="172.30.243.138")
mqttClient.loop_start()

# Example access to data
allData=[]
for file, data in data_dict.items():
    allData = allData + data
    print(f"{file}: Loaded {len(data)} rows.")

"""
{"deviceName": "reactIR702L1", "deviceType": "IR", "inUse": true, "remoteEnabled": true, "ipAddr": "192.168.1.50", "port": 62552, "tele": {"cmnd": "POLL", "settings": {}, "state": {"data": "[-0.02064050707891766,...,1]"}, "timestamp": ""}}
"""
now=time.time() + 60
evaluate=False
temp=0
tempPerSec=2
evaluate=False
tempMin=0
tempMax=100
tempPerSec=1
temp=0
up=False

publishInt={}
publishInt["hotcoil1"] = 1
publishInt["reactIR702L1"] = 6

publishStamps={}
publishStamps["hotcoil1"] = time.time()
publishStamps["reactIR702L1"] = time.time()

while True:
    #Hotcoil
    if time.time() - publishStamps["hotcoil1"] > publishInt["hotcoil1"]:
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
        
        publishStamps["hotcoil1"] = time.time()        
        
    #ReactIR
    if time.time() - publishStamps["reactIR702L1"] > publishInt["reactIR702L1"]:
        _rand=random.choice(allData)
        
        payload={"deviceName": "reactIR702L1", "deviceType": "IR", "inUse": True, "remoteEnabled": True, "ipAddr": "192.168.1.50", "port": 62552, "tele": {"cmnd": "POLL", "settings": {}, "state": {"data": list(_rand)}, "timestamp": ""}}
        mqttClient.publish(topic="subflow/reactIR702L1/tele",payload=json.dumps(payload))
        
        publishStamps["reactIR702L1"] = time.time()        

    sleep(0.1)
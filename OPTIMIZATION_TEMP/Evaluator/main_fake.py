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
mqttClient.connect(host="localhost")
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
while True:
    _rand=random.choice(allData)
    '''
    if now - time.time() < 0:
        if not evaluate:
            evaluate=True
        else:
            evaluate=False
        now=time.time() + 60
            
    if evaluate:
        publishThis=json.dumps({"goEvaluator":True,"scan":list(_rand)})
    else:
        publishThis=json.dumps({"goEvaluator":False,"scan":list(_rand)})
    '''
    payload={"deviceName": "reactIR702L1", "deviceType": "IR", "inUse": True, "remoteEnabled": True, "ipAddr": "192.168.1.50", "port": 62552, "tele": {"cmnd": "POLL", "settings": {}, "state": {"data": list(_rand)}, "timestamp": ""}}
    mqttClient.publish(topic="subflow/reactIR702L1/tele",payload=json.dumps(payload))
    sleep(6)

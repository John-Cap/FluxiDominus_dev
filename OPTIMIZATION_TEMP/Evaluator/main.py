
import json
import os
import time
import numpy as np

from irmlp_trainer_fake import IRMLPTrainer  

# Load trained TensorFlow model
trainer = IRMLPTrainer(
    host="172.30.243.138",
    #host="localhost",
    csv_path="ir_yield_no_resample_averages.csv",
    csv_path_unaveraged="ir_yield_no_resample_unaveraged.csv",
    csv_path_unmasked="ir_yield_no_resample_unmasked.csv"
)
trainer.loadModel("ir_yield_mlp.keras")

print(f'Keras model {"ir_yield_mlp.keras"} loaded')

trainer.client.connect(host=trainer.host)
trainer.client.loop_start()

while not trainer.client.is_connected():
    time.sleep(1)
    
print(f'MQTT client "{trainer.client.username}" initialized')

trainer.client.publish(trainer.topicOut,json.dumps({"statReq":{"init":True}}))

while True:
    time.sleep(5)
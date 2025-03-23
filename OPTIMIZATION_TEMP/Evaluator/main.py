
import json
import os
import time
import numpy as np

from irmlp_trainer import IRMLPTrainer  

# Load trained TensorFlow model
trainer = IRMLPTrainer(
    csv_path="ir_yield_no_resample_averages.csv",
    csv_path_unaveraged="ir_yield_no_resample_unaveraged.csv",
    csv_path_unmasked="ir_yield_no_resample_unmasked.csv"
)
trainer.loadModel("ir_yield_mlp.keras")
trainer.trimLeft=200
trainer.trimRight=40
keyPrev=-1
yields=[]

evaluating=False
cont=False

trainer.client.connect(host=trainer.host)
trainer.client.loop_forever()
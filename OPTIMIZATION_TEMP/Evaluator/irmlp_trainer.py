import json
import os
import time
import numpy as np  

from main import IRMLPTrainer

SHARED_FOLDER = "../SharedData/"  # Set path to shared folder

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
yieldAvgs=[]

while True:
    #Open, check if new scan
    try:
        with open(os.path.join(SHARED_FOLDER, "latest_ir_scan.json"), "r") as f:
            data = json.load(f)
    except:
        time.sleep(4)
        continue
    
    keyStr=(list(data.keys()))[0]
    key=eval(keyStr)
    if key > keyPrev:
        keyPrev=key
        ir = trainer.trimDataSingle(data[keyStr])

        # Predict yield
        yield_score = trainer.estimateYield(ir)
        print(f"🔹 Evaluated yield: {yield_score*100}")
        # Write recommendation to SharedData/
        
        #Before writing, take the averages of IR scans until data["evaluate"] = False
        if not data["evaluate"]:
            with open(os.path.join(SHARED_FOLDER, "yield.json"), "w") as f:
                json.dump({"yield":float(yield_score)}, f)

    time.sleep(4)
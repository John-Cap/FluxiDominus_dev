
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
'''
while True:
    saidItOnce=False

    while not cont:
        """ Check if goEvaluator. """

        try:

            with open(trainer.evaluatorCmndPath, "r") as f:
                data = json.load(f)

            if data["goEvaluator"]:
                cont=True
            else:
                if not saidItOnce:
                    print("Waiting for goEvaluator")
                    saidItOnce=True
                continue
            
        except:
            pass

        time.sleep(1)
        
    saidItOnce=False
    print("Running evaluator")

    while cont:
        """ Check if goEvaluator. """
        try:
            with open(trainer.evaluatorCmndPath, "r") as f:
                data = json.load(f)

            if not data["goEvaluator"]:
                cont=False
                continue
        except:
            time.sleep(1)
            continue
        
        #Open, check if new scan
        try:
            with open(scanPath, "r") as f:
                data = json.load(f)
        except:
            time.sleep(4)
            continue
        
        keyStr=(list(data.keys()))[0] #TODO - careful!
        key=eval(keyStr)
        if key > keyPrev:
            keyPrev=key
            ir = trainer.trimDataSingle(data[keyStr])

            # Predict yield
            yield_score = trainer.estimateYield(ir)
            print(f"🔹 Evaluated yield: {yield_score*100}")
            # Write recommendation to SharedData/   
            
            if evaluating:
                yields.append(yield_score)
            
            #Before writing, take the averages of IR scans until data["evaluate"] = False
            if data["evaluate"]:
                if not evaluating:
                    evaluating=True
                    print(f"Yield evaluation started at IR scan index {key}")
            else:
                if evaluating:
                    #Take max yield
                    yield_score=max(yields)
                    yields.clear()
                    with open(os.path.join(SHARED_FOLDER, "yield.json"), "w") as f:
                        json.dump({"yield":float(yield_score),"toSummit":True}, f)
                    
                    evaluating=False
                    print(f"Yield evaluation stopped at IR scan index {key}, peak yield is {yield_score*100}")
                

        time.sleep(4)
'''
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

while True:
    try:
        # Generate a mock IR spectrum (replace with real data if available)
        ir_spectrum = np.random.rand(839)
        ir_spectrum = trainer.trimDataSingle(ir_spectrum)

        # Predict yield
        yield_score = trainer.estimateYield(ir_spectrum)
        print(f"🔹 Evaluated yield: {yield_score:.3f}")
        # Write recommendation to SharedData/
        
        with open(os.path.join(SHARED_FOLDER, "yield.json"), "w") as f:
            json.dump({"yield":float(yield_score)}, f)
        time.sleep(5)  # Wait before checking for a new recommendation

    except FileNotFoundError:
        print("🔺 Waiting for Summit recommendations...")
        time.sleep(5)

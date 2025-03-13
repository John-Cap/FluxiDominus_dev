import json
import time
import numpy as np
from main import IRMLPTrainer  # Ensure this file is accessible

# Load trained TensorFlow model
trainer = IRMLPTrainer(
    csv_path="ir_yield_no_resample_averages.csv",
    csv_path_unaveraged="ir_yield_no_resample_unaveraged.csv",
    csv_path_unmasked="ir_yield_no_resample_unmasked.csv"
)
trainer.loadModel("ir_yield_mlp.keras")

while True:
    try:
        # Load recommendation from Summit optimizer
        with open("recommendation.json", "r") as f:
            recommendation = json.load(f)

        temp = recommendation["temperature"]
        flowrate = recommendation["flowrate"]

        # Generate a mock IR spectrum (replace with real data if available)
        ir_spectrum = np.random.rand(839)

        # Predict yield
        yield_score = trainer.estimateYield(ir_spectrum)
        print(f"🔹 Evaluated yield: {yield_score:.3f} (Temp: {temp}, Flowrate: {flowrate})")

        # Save yield to file for Summit optimizer to read
        with open("yield.json", "w") as f:
            json.dump({"temperature": temp, "flowrate": flowrate, "yield": yield_score}, f)

        time.sleep(5)  # Wait before checking for a new recommendation

    except FileNotFoundError:
        print("🔺 Waiting for Summit recommendations...")
        time.sleep(5)

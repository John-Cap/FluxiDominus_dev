import json
import time
from summit.strategies import TPE
from summit.domain import Domain, ContinuousVariable

class SummitOptimizer:
    def __init__(self):
        self.domain = Domain()
        self.domain += ContinuousVariable(name="temperature", bounds=[25, 100])
        self.domain += ContinuousVariable(name="flowrate", bounds=[0.1, 5])
        self.strategy = TPE(self.domain)
        self.experiments = []

    def recommend(self):
        """ Generate the next recommendation. """
        next_experiment = self.strategy.suggest_experiments(1)
        recommendation = {
            "temperature": next_experiment["temperature"][0],
            "flowrate": next_experiment["flowrate"][0]
        }
        self.experiments.append(recommendation)

        # Save to file for TensorFlow evaluator to read
        with open("recommendation.json", "w") as f:
            json.dump(recommendation, f)

        print(f"🔹 Summit Optimizer recommended: {recommendation}")

    def update(self, temperature, flowrate, yield_score):
        """ Update Summit with the new yield score. """
        data = {"temperature": [temperature], "flowrate": [flowrate], "yield": [yield_score]}
        self.strategy.add_experiments(data)

# Run optimization loop
if __name__ == "__main__":
    optimizer = SummitOptimizer()
    
    while True:
        optimizer.recommend()
        time.sleep(5)  # Wait for the evaluator to process


from summit.strategies import TPE
from summit.domain import Domain, ContinuousVariable
import numpy as np

class SummitOptimizer:
    def __init__(self):
        # Define the optimization domain (temperature and flowrate)
        self.domain = Domain()
        self.domain += ContinuousVariable(name="temperature", bounds=[25, 100])  # Temp range
        self.domain += ContinuousVariable(name="flowrate", bounds=[0.1, 5])  # Flowrate range

        # Use Tree-structured Parzen Estimator (TPE) for optimization
        self.strategy = TPE(self.domain)

        # Store experiment history
        self.experiments = []

    def recommend(self, tweakables):
        """ Generate the next set of parameters to test. """
        # Ask Summit for the next suggestion
        next_experiment = self.strategy.suggest_experiments(1)

        # Extract values
        recommended_values = {
            "temperature": next_experiment["temperature"][0],
            "flowrate": next_experiment["flowrate"][0]
        }

        self.experiments.append(recommended_values)
        return recommended_values

    def update(self, temperature, flowrate, yield_score):
        """ Update Summit with the latest experiment results. """
        data = {"temperature": [temperature], "flowrate": [flowrate], "yield": [yield_score]}
        self.strategy.add_experiments(data)

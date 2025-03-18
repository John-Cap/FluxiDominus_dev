
import os
import summit
from summit.domain import Domain, ContinuousVariable
from summit.strategies import SOBO
import json
import pandas as pd
import numpy as np

SHARED_FOLDER = "../SharedData/"  # Set path to shared folder

class SummitOptimizer:
    def __init__(self):
        # Define the optimization domain
        self.domain = Domain()
        self.domain += ContinuousVariable(name="temperature", bounds=[25, 100], is_objective=False, description='temperature')
        self.domain += ContinuousVariable(name="flowrate", bounds=[0.1, 5], is_objective=False, description='temperature')
        self.domain += ContinuousVariable(name="yieldVal", bounds=[0, 1], is_objective=True, maximize=True, description='yieldVal')  # Yield is the objective

        self.randomInitialAssigned=False
        
        self.recommending=True

        # Use SOBO optimizer
        self.strategy = SOBO(self.domain)
        self.experiments = pd.DataFrame(columns=["temperature", "flowrate", "yieldVal"])  # Store experiments

        self.prevExp={}
        
        self.recommendationPath=(os.path.join(SHARED_FOLDER, "recommendation.json"))
        self.yieldPath=(os.path.join(SHARED_FOLDER, "yield.json"))

    def recommend(self):
        """ Generate the next recommendation. """
        if self.experiments.empty and not self.randomInitialAssigned:
            # Generate initial random experiments (needed for SOBO)
            temp = np.random.uniform(40, 100)
            flowrate = np.random.uniform(1, 3)
            recommendation = {"temperature": temp, "flowrate": flowrate}
            self.prevExp=recommendation
            print("🔹 First random experiment:", recommendation)
            self.randomInitialAssigned=True
        else:
            # Generate recommendation from SOBO
            next_experiment = self.strategy.suggest_experiments(1,summit.DataSet.from_df(self.experiments))

            if next_experiment.empty:
                print("⚠️ Summit returned an empty dataset! Ensure optimizer is correctly updated with past experiments.")
                return

            recommendation = {
                "temperature": next_experiment["temperature"].iloc[0],
                "flowrate": next_experiment["flowrate"].iloc[0]
            }
            self.prevExp=recommendation
            
        # Write recommendation to SharedData/
        with open(self.recommendationPath, "w") as f:
            json.dump(recommendation, f)
        
        self.recommending=False
        
        print(f"✅ Summit Optimizer recommended: {recommendation}")

    def update(self):
        """ Check for evaluated yield and update optimizer. """
        try:
            with open(self.yieldPath, "r") as f:
                data = json.load(f)

            if data["toSummit"]:
                yield_score = data["yield"]
                temp=self.prevExp["temperature"]
                flowrate=self.prevExp["flowrate"]
            else:
                return
            
            os.remove(self.yieldPath)

            # Add the new experiment result
            new_data = pd.DataFrame({"temperature": [temp], "flowrate": [flowrate], "yieldVal": [yield_score]})
            self.experiments = pd.concat([self.experiments, new_data], ignore_index=True)

            # Update SOBO strategy
            #self.strategy.add_experiments(self.experiments)
            print(f"✅ Updated Summit with yield: {yield_score:.3f}")
            
            self.recommending=True

        except FileNotFoundError:
            print("🔺 No evaluated yield found, waiting...")


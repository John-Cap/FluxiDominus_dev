import numpy as np
from typing import Callable, Dict, List

class Optimizer:
    def __init__(self, startParams: List[float], paramNames: List[str], 
                 brackets: Dict[str, tuple], model, objFunc: Callable, stopVal: float = 0.9):
        """
        Initialize the optimizer with starting parameters and bounds.

        Args:
            startParams (List[float]): Initial values of parameters.
            paramNames (List[str]): Names of parameters (e.g., ["temp", "fr", "equiv"]).
            brackets (Dict[str, tuple]): Bounds for each parameter, e.g., {"temp": (50, 100), "fr": (0.1, 1.0)}.
            model: Trained machine learning model for recommending parameter updates.
            objFunc (Callable): Objective function to evaluate the parameters.
            stopVal (float): Stop optimization when objective function value exceeds this threshold.
        """
        self.params = dict(zip(paramNames, startParams))
        self.brackets = brackets
        self.model = model
        self.objFunc = objFunc
        self.stopVal = stopVal
        
        # Logging and tracking
        self.attemptedParams = []
        self.objFuncVals = []
        self.cycleNumber = 0
        self.optimize = True

    def checkBounds(self, params: Dict[str, float]) -> bool:
        """Check if parameters are within the defined bounds."""
        for name, value in params.items():
            if not (self.brackets[name][0] <= value <= self.brackets[name][1]):
                return False
        return True

    def getNextParams(self) -> Dict[str, float]:
        """Use the model to predict the next set of parameters."""
        # Assuming model.predict takes current cycle as input and returns new params
        predictedParams = self.model.predict(self.cycleNumber)
        recommendedParams = dict(zip(self.params.keys(), predictedParams))
        
        # Check bounds and adjust if necessary
        for param, value in recommendedParams.items():
            minVal, maxVal = self.brackets[param]
            recommendedParams[param] = np.clip(value, minVal, maxVal)
        
        return recommendedParams

    def runCycle(self):
        """Run a single cycle of optimization."""
        # Step 1: Get recommended next parameters
        recommendedParams = self.getNextParams()
        
        # Step 2: Check if recommended parameters are within bounds
        if not self.checkBounds(recommendedParams):
            print("Recommended parameters out of bounds, skipping cycle.")
            return
        
        # Step 3: Attempt the new parameters
        self.attemptedParams.append(recommendedParams)
        self.params = recommendedParams
        
        # Step 4: Evaluate objective function
        objVal = self.objFunc(self.params)
        self.objFuncVals.append(objVal)
        
        # Step 5: Update cycle number and stop condition
        self.cycleNumber += 1
        if objVal >= self.stopVal:
            self.optimize = False

    def optimizeLoop(self):
        """Main optimization loop."""
        while self.optimize:
            self.runCycle()
        
        # Return the best set of parameters
        bestIndex = np.argmax(self.objFuncVals)
        return self.attemptedParams[bestIndex], self.objFuncVals[bestIndex]

# Dummy model and objective function for testing purposes
class DummyModel:
    def predict(self, cycleNumber):
        # This is just a placeholder function that returns some dummy predictions
        return [0.5, 0.8, 0.2]  # replace with actual predictions

def dummyObjFunc(params):
    # Placeholder objective function that could be based on the parameters
    return np.random.rand()  # replace with actual evaluation logic

# Example usage
startParams = [0.5, 0.8, 0.2]
paramNames = ["temp", "fr", "equiv"]
brackets = {"temp": (0.4, 1.0), "fr": (0.6, 1.0), "equiv": (0.1, 0.3)}
model = DummyModel()
stopVal = 0.9

optimizer = Optimizer(startParams=startParams, paramNames=paramNames, 
                      brackets=brackets, model=model, objFunc=dummyObjFunc, 
                      stopVal=stopVal)

bestParams, bestObjVal = optimizer.optimizeLoop()
print(f"Best parameters: {bestParams} with objective function value: {bestObjVal}")

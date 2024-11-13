import keras
import numpy as np
from typing import Callable, Dict, List

from ReactionSimulation.fakeReactionLookup import ReactionLookup

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
        
        self.objectiveFunc=ReactionLookup() #Nothing done with this yet, has method .get_yield that returns value between 0-1 from recommended x, y

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

class LSTMOptimizer:
    def __init__(self, startParams, paramNames, brackets, reaction_lookup, stopVal=0.99, sequence_length=5):
        self.params = dict(zip(paramNames, startParams))
        self.paramNames = paramNames
        self.brackets = brackets
        self.reaction_lookup = reaction_lookup
        self.stopVal = stopVal
        self.sequence_length = sequence_length
        self.cycleNumber = 0
        self.optimize = True

        # Data storage for LSTM training
        self.attemptedParams = []  # Stores past parameter sets
        self.yields = []  # Stores yields corresponding to each parameter set

        # Initialize LSTM model
        self.model = self.build_lstm_model((self.sequence_length, len(paramNames)))

    def build_lstm_model(self, input_shape):
        """Build the LSTM model."""
        model = keras.Sequential()
        model.add(keras.layers.LSTM(64, input_shape=input_shape))
        model.add(keras.layers.Dense(len(self.paramNames)))  # Output layer with units matching paramNames length
        model.compile(optimizer='adam', loss='mse')
        return model

    def checkBounds(self, params):
        """Check if parameters are within the defined bounds."""
        for name, value in params.items():
            if not (self.brackets[name][0] <= value <= self.brackets[name][1]):
                return False
        return True

    def getNextParams(self):
        """Predict the next parameters using the LSTM model."""
        if len(self.attemptedParams) < self.sequence_length:
            # Random initialization if not enough history for a full sequence
            return [np.random.uniform(self.brackets[name][0], self.brackets[name][1]) for name in self.paramNames]
        
        # Prepare the sequence data for the LSTM model
        recent_sequence = np.array(self.attemptedParams[-self.sequence_length:]).reshape(1, self.sequence_length, len(self.paramNames))
        predicted_params = self.model.predict(recent_sequence)[0]
        
        # Clip predictions to parameter bounds
        return [np.clip(predicted_params[i], self.brackets[self.paramNames[i]][0], self.brackets[self.paramNames[i]][1]) for i in range(len(self.paramNames))]

    def runCycle(self):
        """Run a single optimization cycle."""
        recommended_params = self.getNextParams()
        
        # Check bounds
        params_dict = dict(zip(self.paramNames, recommended_params))
        if not self.checkBounds(params_dict):
            print("Recommended parameters out of bounds, skipping cycle.")
            return
        
        # Get yield from the ReactionLookup function
        x, y = params_dict['temp'], params_dict['time']
        yield_val = self.reaction_lookup.get_yield(x, y)
        
        # Log data for training
        self.attemptedParams.append([x, y])
        self.yields.append(yield_val)
        
        # Check stop condition
        self.cycleNumber += 1
        if yield_val >= self.stopVal:
            self.optimize = False
            print("Target yield achieved.")
            return

        # Incrementally train the LSTM model with new data
        if len(self.attemptedParams) > self.sequence_length:
            self.trainLSTMModel()

    def trainLSTMModel(self):
        """Train the LSTM model on all recorded sequences."""
        # Prepare the training data
        X = np.array([self.attemptedParams[i:i+self.sequence_length] for i in range(len(self.attemptedParams) - self.sequence_length)])
        y = np.array(self.attemptedParams[self.sequence_length:])
        self.model.fit(X, y, epochs=1, verbose=0)

    def optimizeLoop(self):
        """Main optimization loop."""
        while self.optimize:
            self.runCycle()
        
        # Return the best set of parameters and corresponding yield
        best_index = np.argmax(self.yields)
        return self.attemptedParams[best_index], self.yields[best_index]

# Example usage
if __name__ == "__main__":
    # Define some dummy values for the parameters
    startParams = [25.0, 5.0]
    paramNames = ["temp", "time"]
    brackets = {"temp": (10, 50), "time": (1, 20)}
    
    # Create the optimizer instance
    reaction_lookup = ReactionLookup()
    optimizer = LSTMOptimizer(startParams=startParams, paramNames=paramNames, brackets=brackets, reaction_lookup=reaction_lookup, stopVal=0.99)
    
    # Run optimization
    bestParams, bestYield = optimizer.optimizeLoop()
    print(f"Best parameters: {bestParams} with yield: {bestYield}")

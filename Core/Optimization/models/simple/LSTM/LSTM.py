
import keras
import numpy as np

from ReactionSimulation.fakeReactionLookup import ReactionLookup

class LSTMOptimizer:
    def __init__(self, startParams, paramNames, brackets, reaction_lookup, stopVal=0.99, sequence_length=5, sequence_length_interval=5):
        self.params = dict(zip(paramNames, startParams))
        self.paramNames = paramNames
        self.brackets = brackets
        self.reaction_lookup = reaction_lookup
        self.stopVal = stopVal
        self.sequence_length = sequence_length
        self.sequence_length_interval = sequence_length_interval
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
        
        # Get yield from the ReactionLookup function (objective function)
        x, y = params_dict['temp'], params_dict['time']
        yield_val = self.reaction_lookup.get_yield(x, y)
        print('Predicted params for cycle ' + str(self.cycleNumber) + ': ' + str(recommended_params) + ', yield: ' + str(yield_val*100))        
        # Log data for training
        self.attemptedParams.append([x, y])
        self.yields.append(yield_val)
        
        # Check stop condition
        self.cycleNumber += 1
        if yield_val >= self.stopVal:
            self.optimize = False
            print("Target yield achieved.")
            return

        # Train the LSTM model with exploration data only if we have enough data points
        if len(self.attemptedParams) > self.sequence_length:
            self.trainLSTMModel()
            self.sequence_length+=self.sequence_length_interval

    def trainLSTMModel(self):
        """Train the LSTM model on all recorded sequences."""
        # Prepare the training data
        X = np.array([self.attemptedParams[i:i+self.sequence_length] for i in range(len(self.attemptedParams) - self.sequence_length)])
        y = np.array(self.attemptedParams[self.sequence_length:])
        self.model.fit(X, y, epochs=5, verbose=0)

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
    startParams = [5.0, 5.0]
    paramNames = ["temp", "time"]
    brackets = {"temp": (4, 100), "time": (1, 60)}
    
    # Create the optimizer instance
    reaction_lookup = ReactionLookup()
    optimizer = LSTMOptimizer(startParams=startParams, paramNames=paramNames, brackets=brackets, sequence_length=10, sequence_length_interval=10, reaction_lookup=reaction_lookup, stopVal=0.99)
    
    # Run optimization
    bestParams, bestYield = optimizer.optimizeLoop()
    print(f"Best parameters: {bestParams} with yield: {bestYield*100} obtained in {optimizer.cycleNumber} cycles!")

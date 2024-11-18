
from ast import List
import random
import uuid
import keras
import numpy as np
import tensorflow as tf

from ReactionSimulation.fakeReactionLookup import ReactionLookup

class LSTMOptimizer:
    def __init__(self, reaction_lookup, stopVal=0.95, sequence_length=5, sequence_length_interval=5):
        # self.params = dict(zip(paramNames, startParams))
        self.modelParams = {} #self.modelParams[str(model)]=dict(zip(paramNames, startParams))
        # self.paramNames = paramNames
        self.modelParamNames = {}
        
        self.modelAttemptedParams = {}
        self.modelYields = {}
        
        self.modelBrackets = {}
        self.reaction_lookup = reaction_lookup
        self.stopVal = stopVal
        self.sequence_length = sequence_length
        self.sequence_length_interval = sequence_length_interval
        self.cycleNumber = 0
        self.optimize = True
        
        self.training = False
        
        self.models={}
        
        self.strikes={}

        # Data storage for LSTM training
        # self.attemptedParams = []  # Stores past parameter sets
        # self.yields = []  # Stores yields corresponding to each parameter set

        # Initialize LSTM model
        # self.model = self.build_lstm_model((self.sequence_length, len(paramNames)))

    def build_lstm_model(self, input_shape, startParams, paramNames, bracket, name=""):
        """Build the LSTM model."""
        model = keras.Sequential()
        if name == "":
            model.name=str(uuid.uuid4())
        else:
            model.name=name
        # model.name=str(model)
        self.models[model.name]=model
        self.modelParams[model.name]=dict(zip(paramNames, startParams))
        self.modelParamNames[model.name]=paramNames
        self.modelBrackets[model.name]=bracket
        self.modelAttemptedParams[model.name]=[]
        self.modelYields[model.name]=[]
        model.add(keras.layers.LSTM(64, input_shape=input_shape))
        model.add(keras.layers.Dense(len(paramNames)))  # Output layer with units matching paramNames length
        model.compile(optimizer='adam', loss=tf.keras.losses.Huber(1))
        print(model.name)
        return model

    def checkBounds(self, model, params):
        # model.name=str(model)
        # params=self.modelParams[model.name]
        bracket=self.modelBrackets[model.name]
        """Check if parameters are within the defined bounds."""
        for name, value in params.items():
            if not (bracket[name][0] <= value <= bracket[name][1]):
                return False
        return True

    def getNextParams(self,model):
        """Predict the next parameters using the LSTM model."""
        # _mdlStr=str(model)
        attemptedParams = self.modelAttemptedParams[model.name]
        paramNames = self.modelParamNames[model.name]
        bracket = self.modelBrackets[model.name]
        # print(self.modelBrackets)
        if len(attemptedParams) < 100:
            # Random initialization if not enough history for a full sequence
            init=[np.random.uniform(bracket[name][0], bracket[name][1]) for name in paramNames]
            return init
        
        # Prepare the sequence data for the LSTM model
        recent_sequence = np.array(attemptedParams[-self.sequence_length:]).reshape(1, self.sequence_length, len(paramNames))
        
        predicted_params = model.predict(recent_sequence)[0]
        print('WJ - ' + str(predicted_params))
        # print(predicted_params)
        # Clip predictions to parameter bounds
        return [np.clip(predicted_params[i], bracket[paramNames[i]][0], bracket[paramNames[i]][1]) for i in range(len(paramNames))]

    def scaleToBracket(self,model,val):
        brackets = self.modelBrackets[model.name]
        _i=0
        for x in brackets.values():
            val[_i] = x[0]

    def scaleDownFromBracket(self,model,val):
        brackets = self.modelBrackets[model.name]
        _i=0
        for x in brackets.values():
            val[_i] = x[0]

    def runMultiModelCycle(self,models=None):
        """Run a single optimization cycle for each model."""

        if (not models and len(self.models) != 0):
            models=self.models
        else:
            print('WJ - No available models!')
            return None
        
        for model in list(models.values()):
            # _mdlStr=str(model)
            paramNames=self.modelParamNames[model.name]
            # attemptedParams=self.modelAttemptedParams[model.name]
            # yields=self.modelYields[model.name]
            recommended_params = self.getNextParams(model)
            print('Recommended params: ' + str(recommended_params))
            # Check bounds
            params_dict = dict(zip(paramNames, recommended_params))
            if not self.checkBounds(model,params_dict):
                print("Recommended parameters out of bounds, skipping cycle.")
                return
            
            # Get yield from the ReactionLookup function (objective function)
            x, y, predictedYield = params_dict['temp'], params_dict['time'], params_dict['yieldPrev']
            if len(self.modelAttemptedParams[model.name]) < 100:
                yield_val=(self.reaction_lookup.get_yield(x, y))
                predictedYield=yield_val
            else:
                self.training=True
                yield_val = (self.reaction_lookup.get_yield(x, y))
            print('Predicted yield for cycle ' + str(self.cycleNumber) + ': ' + str(predictedYield*100) + ', true yield: ' + str(yield_val*100))        
            # Log data for training
            
            if not self.training:
                self.modelAttemptedParams[model.name].append([x, y, yield_val])
                self.modelYields[model.name].append(yield_val)                
            elif abs(predictedYield - yield_val) < 0.05:
                self.modelAttemptedParams[model.name].append([x, y, yield_val])
                self.modelYields[model.name].append(yield_val)
            else:
                pass
            
            # Check stop condition
            if yield_val >= self.stopVal and self.training:
                self.optimize = False
                print(f"Target yield of at least {self.stopVal} achieved by + {model.name} , predicted params: {[x, y, predictedYield]}")
                break

            # Train the LSTM model with exploration data only if we have enough data points (first check if data is useful)
            if len(self.modelAttemptedParams[model.name]) > self.sequence_length and self.training:
                self.trainLSTMModel(model=model,attemptedParams=self.modelAttemptedParams[model.name])
                self.sequence_length+=self.sequence_length_interval
        if self.training:
            self.cycleNumber += 1

    def trainLSTMModel(self, model, attemptedParams):
        """Train the LSTM model on all recorded sequences."""
        # Prepare the training data
        X = np.array([attemptedParams[i:i+self.sequence_length] for i in range(len(attemptedParams) - self.sequence_length)])
        y = np.array(attemptedParams[self.sequence_length:])
        model.fit(X, y, epochs=5, verbose=0)

    def optimizeLoop(self):
        """Main optimization loop."""
        while self.optimize:
            self.runMultiModelCycle()
        
        # for model in list(self.models.values()):
        #     # Return the best set of parameters and corresponding yield
        #     best_index = np.argmax(self.modelYields[model.name])
        # return self.modelAttemptedParams[model.name][best_index], self.modelYields[model.name][best_index]

# Example usage
if __name__ == "__main__":
    # Define some dummy values for the parameters
    startParams_1 = [35.0, 55.0, 0]
    paramNames_1 = ["temp", "time", "yieldPrev"]
    brackets_1 = {"temp": (4, 100), "time": (5, 60), "yieldPrev": (0,1)}
    info_1=(startParams_1,paramNames_1,brackets_1)

    startParams_2 = [45.0, 45.0, 0]
    paramNames_2 = ["temp", "time", "yieldPrev"]
    brackets_2 = {"temp": (4, 100), "time": (5, 60), "yieldPrev": (0,1)}
    info_2=(startParams_2,paramNames_2,brackets_2)

    startParams_3 = [5.0, 5.0, 0]
    paramNames_3 = ["temp", "time", "yieldPrev"]
    brackets_3 = {"temp": (4, 100), "time": (5, 60), "yieldPrev": (0,1)}
    info_3=(startParams_3,paramNames_3,brackets_3)
    
    allInfo=[info_1,info_2,info_3]
    names=["Bob","Sam","Oprah"]
    
    # Create the optimizer instance
    reaction_lookup = ReactionLookup()
    optimizer = LSTMOptimizer(sequence_length=100, sequence_length_interval=10, reaction_lookup=reaction_lookup)
    
    _i=0
    for info in allInfo:
        optimizer.build_lstm_model(input_shape=(optimizer.sequence_length, len(info[1])),startParams=info[0],bracket=info[2],paramNames=info[1],name=names[_i])
        _i+=1
    # Run optimization
    bestParams, bestYield = optimizer.optimizeLoop()
    print(f"Best parameters: {bestParams} with yield: {bestYield*100} obtained in {optimizer.cycleNumber} cycles!")

from ast import List
import random
from time import sleep
import uuid
import keras
import numpy as np
import tensorflow as tf

from Core.Utils import Utils
from ReactionSimulation.fakeReactionLookup import ReactionLookup

class LSTMOptimizer:
    def __init__(self, reactionLookup, stopVal=0.95, sequenceLengthGlobal=5, sequenceLengthIntervalGlobal=5):
        self.modelParams = {}
        self.modelParamNames = {}
        self.modelAttemptedParams = {}
        self.modelYields = {}
        self.initialTraining = False
        self.modelBrackets = {}
        self.reactionLookup = reactionLookup
        self.stopVal = stopVal
        self.sequenceLengthGlobal = sequenceLengthGlobal
        self.sequenceLengthIntervalGlobal = sequenceLengthIntervalGlobal
        self.cycleNumber = 0
        self.optimize = True
        self.modelBrackets = {}
        self.modelSequenceLengths = {}
        self.training = False
        self.models = {}
        self.strikes = {}

    def buildLstmModel(self, inputShape, startParams, paramNames, bracket, name="", sequenceLength=None):
        """Build the LSTM model."""
        model = keras.Sequential()
        model.name = str(uuid.uuid4()) if name == "" else name
        self.models[model.name] = model
        self.modelParams[model.name] = dict(zip(paramNames, startParams))
        self.modelParamNames[model.name] = paramNames
        self.modelAttemptedParams[model.name] = []
        self.modelYields[model.name] = []
        sequenceLength = sequenceLength or self.sequenceLengthGlobal
        self.modelSequenceLengths[model.name] = sequenceLength
        self.modelBrackets[model.name] = bracket
        self.modelBrackets[model.name] = {
            key: Utils.Bracket(minValue=bracket[key][0], maxValue=bracket[key][1])
            for key in bracket.keys()
        }
        
        model.add(keras.layers.LSTM(64, input_shape=inputShape))
        model.add(keras.layers.Dense(len(paramNames), activation="relu"))
        model.compile(optimizer="adam", loss=tf.keras.losses.Huber(1))
        print(f"Model '{model.name}' initialized!")
        return model

    def checkBounds(self, model, params):
        """Check if parameters are within the defined bounds."""
        bracket = self.modelBrackets[model.name]
        bracketer = self.modelBrackets[model.name]
        for name, value in params.items():
            if not (bracket[name][0] <= bracketer[name].toBracket(value) <= bracket[name][1]):
                return False
        return True

    def getNextParams(self, model):
        """Predict the next parameters using the LSTM model."""
        attemptedParams = self.modelAttemptedParams[model.name]
        paramNames = self.modelParamNames[model.name]

        if len(attemptedParams) < 100:
            return np.array([np.random.uniform(0, 1) for name in paramNames])

        recent_sequence = np.array(attemptedParams[-self.modelSequenceLengths[model.name]:])
        recent_sequence = recent_sequence.reshape(1, self.modelSequenceLengths[model.name], len(paramNames))
        return model.predict(recent_sequence)[0]

    def runMultiModelCycle(self, models=None):
        """Run a single optimization cycle for each model."""
        if not models and len(self.models) != 0:
            models = self.models
        else:
            print("No available models!")
            return None

        for model in list(models.values()):
            paramNames = self.modelParamNames[model.name]
            recommendedParams = self.getNextParams(model)
            paramsDict = dict(zip(paramNames, recommendedParams))

            if not self.checkBounds(model, paramsDict):
                print("Recommended parameters out of bounds, skipping cycle.")
                return
            
            x, y, predictedYield = paramsDict["temp"], paramsDict["time"], paramsDict["yieldPrev"]
            xProc = self.modelBrackets[model.name]["temp"].toBracket(x)
            yProc = self.modelBrackets[model.name]["time"].toBracket(y)

            if len(self.modelAttemptedParams[model.name]) < self.sequenceLengthGlobal:
                yieldVal = self.reactionLookup.getYield(xProc, yProc)
                predictedYield = yieldVal
            else:
                self.training = True
                yieldVal = predictedYield

            print(f"Cycle {self.cycleNumber}: Predicted {predictedYield:.2f}, True Yield {yieldVal:.2f}")

            if len(self.modelAttemptedParams[model.name]) < self.sequenceLengthGlobal:
                self.modelAttemptedParams[model.name].append([x, y, predictedYield])
                self.modelYields[model.name].append(yieldVal)
            elif not self.initialTraining:
                self.modelAttemptedParams[model.name].append([x, y, predictedYield])
                self.modelYields[model.name].append(yieldVal)
                self.initialTraining = True
            else:
                self.modelAttemptedParams[model.name].append([x, y, predictedYield])
                self.modelYields[model.name].append(yieldVal)

            if yieldVal >= self.stopVal and self.training:
                self.optimize = False
                print(f"Target yield achieved by {model.name}: {yieldVal:.2f}")
                break

            if self.initialTraining and len(self.modelAttemptedParams[model.name]) >= self.modelSequenceLengths[model.name]:
                print(f"Training {model.name} with {len(self.modelAttemptedParams[model.name])} data points.")
                self.trainLSTMModel(model, self.modelAttemptedParams[model.name], epochs=30)

        if self.training:
            self.cycleNumber += 1

    def trainLSTMModel(self, model, attemptedParams, epochs=25):
        """Train the LSTM model on all recorded sequences."""
        sequence_length = min(self.modelSequenceLengths[model.name], len(attemptedParams))
        if len(attemptedParams) < sequence_length:
            print(f"Not enough data to train {model.name}. Skipping training.")
            return

        X = np.array([attemptedParams[i:i+sequence_length] for i in range(len(attemptedParams) - sequence_length)])
        y = np.array(attemptedParams[sequence_length:])
        print(f"Training {model.name}: X shape {X.shape}, y shape {y.shape}")
        model.fit(X, y, epochs=epochs, verbose=0)

    def optimizeLoop(self):
        """Main optimization loop."""
        while self.optimize:
            self.runMultiModelCycle()

# Example usage
if __name__ == "__main__":
    # Define some dummy values for the parameters
    startParams_1 = [15.0, 10.0, 0]
    paramNames_1 = ["temp", "time", "yieldPrev"]
    brackets_1 = {"temp": (4, 25), "time": (5, 15), "yieldPrev": (0,1)}
    info_1=(startParams_1,paramNames_1,brackets_1)

    startParams_2 = [25.0, 40.0, 0]
    paramNames_2 = ["temp", "time", "yieldPrev"]
    brackets_2 = {"temp": (25, 75), "time": (15, 45), "yieldPrev": (0,1)}
    info_2=(startParams_2,paramNames_2,brackets_2)

    startParams_3 = [80, 50.0, 0]
    paramNames_3 = ["temp", "time", "yieldPrev"]
    brackets_3 = {"temp": (75, 100), "time": (45, 60), "yieldPrev": (0,1)}
    info_3=(startParams_3,paramNames_3,brackets_3)
    
    allInfo=[info_1]#,info_2,info_3]
    names=["Bob","Sam","Oprah"]
    
    # Create the optimizer instance
    reactionLookup = ReactionLookup()
    optimizer = LSTMOptimizer(stopVal=0.5,sequenceLengthGlobal=100, sequenceLengthIntervalGlobal=10, reactionLookup=reactionLookup)
    
    _i=0
    for info in allInfo:
        optimizer.buildLstmModel(inputShape=(optimizer.sequenceLengthGlobal, len(info[1])),startParams=info[0],bracket=info[2],paramNames=info[1],name=names[_i],sequenceLength=100)
        _i+=1
    # Run optimization
    bestParams, bestYield = optimizer.optimizeLoop()
    print(f"Best parameters: {bestParams} with yield: {bestYield*100} obtained in {optimizer.cycleNumber} cycles!")

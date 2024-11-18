
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
        # self.params = dict(zip(paramNames, startParams))
        self.modelParams = {} #self.modelParams[str(model)]=dict(zip(paramNames, startParams))
        # self.paramNames = paramNames
        self.modelParamNames = {}
        
        self.modelAttemptedParams = {}
        self.modelYields = {}
        
        self.modelBrackets = {}
        self.reactionLookup = reactionLookup
        self.stopVal = stopVal
        self.sequenceLengthGlobal= sequenceLengthGlobal
        self.sequenceLengthIntervalGlobal = sequenceLengthIntervalGlobal
        self.cycleNumber = 0
        self.optimize = True
        
        self.modelBracketers = {}
        
        self.modelSequenceLenghts = {}
        
        self.training = False
        
        self.models={}
        
        self.strikes={}

        # Data storage for LSTM training
        # self.attemptedParams = []  # Stores past parameter sets
        # self.yields = []  # Stores yields corresponding to each parameter set

        # Initialize LSTM model
        # self.model = self.build_lstm_model((self.sequenceLength, len(paramNames)))

    def buildLstmModel(self, inputShape, startParams, paramNames, bracket, name="", sequenceLength=None):
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
        self.modelAttemptedParams[model.name]=[]
        self.modelYields[model.name]=[]
        if sequenceLength is None:
            sequenceLength=self.sequenceLengthGlobal
        self.modelSequenceLenghts[model.name]=sequenceLength
        
        self.modelBrackets[model.name]=bracket
        self.modelBracketers[model.name]={}
        for key in self.modelBrackets[model.name].keys():
            self.modelBracketers[model.name][key]=Utils.Bracketer(minValue=bracket[key][0],maxValue=bracket[key][1])
        
        model.add(keras.layers.LSTM(64, input_shape=inputShape))
        model.add(keras.layers.Dense(len(paramNames),activation='relu'))  # Output layer with units matching paramNames length
        model.compile(optimizer='adam', loss='mse')
        #model.compile(optimizer='adam', loss=tf.keras.losses.Huber(1))
        print(f"Model '{model.name}' initialized!")
        return model

    def checkBounds(self, model, params):
        # model.name=str(model)
        # params=self.modelParams[model.name]
        bracket=self.modelBrackets[model.name]
        bracketer=self.modelBracketers[model.name]
        """Check if parameters are within the defined bounds."""
        for name, value in params.items():
            print(f'BJ - {[bracket[name][0],bracketer[name].toBracket(value),bracket[name][1],(bracket[name][0] <= bracketer[name].toBracket(value) <= bracket[name][1])]}')
            if not (bracket[name][0] <= bracketer[name].toBracket(value) <= bracket[name][1]):
                return False
        return True

    def getNextParams(self,model):
        """Predict the next parameters using the LSTM model."""
        # _mdlStr=str(model)
        attemptedParams = self.modelAttemptedParams[model.name]
        paramNames = self.modelParamNames[model.name]
        bracket = self.modelBrackets[model.name]
        #print(f'WJ - {bracket}')
        # print(self.modelBrackets)
        if len(attemptedParams) < 100:
            # # Random initialization if not enough history for a full sequence
            # init=[np.random.uniform(0, 1) for name in paramNames]
            # _i=0
            # # print(f'WJ - {init}')
            # for key in bracket:
            #     init[_i]=self.modelBracketers[model.name][key].toBracket(init[_i])
            #     _i+=1
            # #print(f'WJ - {init}')
            return np.array([np.random.uniform(0, 1) for name in paramNames])
        
        # Prepare the sequence data for the LSTM model
        recent_sequence = np.array(attemptedParams[-self.modelSequenceLenghts[model.name]:])
        recent_sequence = recent_sequence.reshape(1, self.modelSequenceLenghts[model.name], len(paramNames))
        return model.predict(recent_sequence)[0]

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
            recommendedParams = self.getNextParams(model)
            print('Recommended params: ' + str(recommendedParams))
            # Check bounds
            paramsDict = dict(zip(paramNames, recommendedParams))
            if not self.checkBounds(model,paramsDict):
                print("Recommended parameters out of bounds, skipping cycle.")
                return
            
            # Get yield from the ReactionLookup function (objective function)
            x, y, predictedYield = paramsDict['temp'], paramsDict['time'], paramsDict['yieldPrev']
            xProc=self.modelBracketers[model.name]['temp'].toBracket(x)
            yProc=self.modelBracketers[model.name]['time'].toBracket(y)
            if len(self.modelAttemptedParams[model.name]) < self.sequenceLengthGlobal:
                yieldVal=(self.reactionLookup.getYield(xProc, yProc))
                predictedYield=yieldVal
            else:
                self.training=True
                yieldVal = (self.reactionLookup.getYield(xProc, yProc))
            print(f'Predicted yield for cycle {self.cycleNumber} with params {round(xProc,2)} degrees and {round(yProc,2)} min: {round(predictedYield*100,2)}%, true yield: {round(yieldVal*100,2)}%')        
            # Log data for training
            
            if len(self.modelAttemptedParams[model.name]) < self.sequenceLengthGlobal:
                self.modelAttemptedParams[model.name].append([x, y, self.modelBracketers[model.name]['yieldPrev'].fromBracket(yieldVal)])
                self.modelYields[model.name].append(yieldVal)
            elif abs(predictedYield - yieldVal) < 0.05:
                exit()
                del self.modelAttemptedParams[model.name][0]
                self.modelAttemptedParams[model.name].append([x, y, self.modelBracketers[model.name]['yieldPrev'].fromBracket(yieldVal)])
                self.modelYields[model.name].append(yieldVal)
            else:
                print('We here')
                del self.modelAttemptedParams[model.name][0]
                self.modelAttemptedParams[model.name].append([x, y, self.modelBracketers[model.name]['yieldPrev'].fromBracket(yieldVal)])
                self.modelYields[model.name].append(yieldVal)
            
            # Check stop condition
            if yieldVal >= self.stopVal and self.training:
                self.optimize = False
                print(f"Target yield of at least {self.stopVal} achieved by + {model.name} , predicted params: {[x, y, predictedYield]}")
                break

            # Train the LSTM model with exploration data only if we have enough data points (first check if data is useful)
            if len(self.modelAttemptedParams[model.name]) > self.modelSequenceLenghts[model.name] and self.training:
                
                print("\n")
                print(f'Training time for {model.name}!')
                print("\n")
                sleep(1)
                self.trainLSTMModel(model=model,attemptedParams=self.modelAttemptedParams[model.name])
                self.modelSequenceLenghts[model.name]+=self.sequenceLengthIntervalGlobal
                print('Taining done!')
                print("\n")
                sleep(3)
                
        if self.training:
            self.cycleNumber += 1

    def trainLSTMModel(self, model, attemptedParams):
        """Train the LSTM model on all recorded sequences."""
        # Prepare the training data
        X = np.array([attemptedParams[i:i+self.modelSequenceLenghts[model.name]] for i in range(len(attemptedParams) - self.modelSequenceLenghts[model.name])])
        y = np.array(attemptedParams[self.modelSequenceLenghts[model.name]:])
        print(f'Shape - {X.shape}, {y.shape}')
        model.fit(X, y, epochs=25, verbose=1)

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
    reactionLookup = ReactionLookup()
    optimizer = LSTMOptimizer(sequenceLengthGlobal=100, sequenceLengthIntervalGlobal=10, reactionLookup=reactionLookup)
    
    _i=0
    for info in allInfo:
        optimizer.buildLstmModel(inputShape=(optimizer.sequenceLengthGlobal, len(info[1])),startParams=info[0],bracket=info[2],paramNames=info[1],name=names[_i],sequenceLength=100)
        _i+=1
    # Run optimization
    bestParams, bestYield = optimizer.optimizeLoop()
    print(f"Best parameters: {bestParams} with yield: {bestYield*100} obtained in {optimizer.cycleNumber} cycles!")

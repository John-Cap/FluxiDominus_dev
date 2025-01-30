import threading
import random
import time

from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.parametres.reaction_parametres import Flowrate, ReactionParametres, Temp

class OptimizationRig:
    def __init__(self, mqttService):
        self.automation = FlowChemAutomation()  # Handles command parsing
        self.reactionParametres = ReactionParametres()  # Holds different parameters that can be optimized
        self.availableParams = {}  # Reaction parameters that can be tweaked, per device
        self.availableCommands = {}  # Links a tweakable parameter to a specific device command name
        self.availableDeviceCommands = {}  # Links device to commands
        self.currentRecommendation = {}
        self.recommendationHistory = []
        self._rigThread = None
        self.optimizer = None
        self.optimizing = False
        self.objectiveEvaluator = None  # Function handle for evaluation
        self.objectiveEvaluationKwargs = {}  # Additional args for evaluation
        self.objectiveScore = None  # Score between 0 and 1
        self.targetScore = None
        self.mqttService = mqttService
        
    def registerDevice(self, device):
        """ Registers a device and its available commands. """
        if device in self.automation.commandTemplatesNested:
            self.availableDeviceCommands[device] = self.automation.commandTemplatesNested[device]
        else:
            print(f"Warning: Unknown device {device}!")

    def registerTweakableParam(self, device, parameter):
        """ Registers a tweakable parameter for a specific device. """
        self.reactionParametres.addTweakable(parameter)
        if device in self.availableParams:
            self.availableParams[device].append(parameter)
        else:
            self.availableParams[device] = [parameter]
            
    def generateRecommendation(self):
        """ Generates recommendations using the optimizer. """
        if self.optimizer is None:
            print("Warning: No optimizer set. Cannot generate recommendations.")
            return

        recommendedValues = self.optimizer.recommend(self.reactionParametres.getAllTweakables())

        if not recommendedValues:
            print("Warning: Optimizer returned empty recommendations.")
            return

        self.currentRecommendation = {}

        for param, value in recommendedValues.items():
            for device, params in self.availableParams.items():
                if param in params:
                    if device not in self.currentRecommendation:
                        self.currentRecommendation[device] = {}
                    self.currentRecommendation[device][param.id] = value

        self.recommendationHistory.append(self.currentRecommendation)

        print("\nGenerated Recommendation:")
        for device, params in self.currentRecommendation.items():
            print(f"  Device: {device}")
            for paramId, val in params.items():
                print(f"    {paramId}: {val:.3f}")
                
    def evaluateRecommendation(self):
        """ Evaluates the latest recommendation using the provided objective function. """
        if self.objectiveEvaluator is None:
            print("Warning: No objective evaluator function set.")
            self.objectiveScore = None
            return

        print("\nEvaluating recommendation with objective function:")
        print(self.currentRecommendation)  # Debugging print

        try:
            self.objectiveScore = self.objectiveEvaluator(self.currentRecommendation, **self.objectiveEvaluationKwargs)

            if not (0 <= self.objectiveScore <= 1):
                raise ValueError(f"Invalid objective score: {self.objectiveScore}. Must be between 0 and 1.")

        except Exception as e:
            print(f"Error in objective evaluation: {e}")
            self.objectiveScore = None

    def executeRecommendation(self):
        """ Converts recommendation into commands, resets automation, and sends the script to MQTT. """
        # First, clear current automation
        self.automation.reset()

        for device, params in self.currentRecommendation.items():
            for paramId, value in params.items():
                # Find the parameter by ID
                for param in self.reactionParametres.getAllTweakables():
                    if param.id == paramId:
                        command = param.associatedCommand
                        self.automation.addBlockElement(param.name, device, command, value)
                        break

        # Convert to script and send to MQTT
        self.automation.parseToScript()
        self.mqttService.script = self.automation.output

    def start(self):
        """ Starts a background thread to continuously optimize until the target score is reached. """
        if not self.optimizing:
            self.optimizing = True
            self._rigThread = threading.Thread(target=self._optimizationLoop)
            self._rigThread.start()
            
    def _optimizationLoop(self):
        """ Runs the optimization loop in the background until the target score is reached. """
        print("\n--- Starting Optimization Loop ---")
        while self.optimizing:
            self.generateRecommendation()
            self.evaluateRecommendation()
            print(f"Current Objective Score: {self.objectiveScore:.3f}")

            if self.objectiveScore and self.objectiveScore >= self.targetScore:
                print("\n🎯 Target Score Reached! Stopping optimization. 🎯")
                self.optimizing = False
                break  # Stop loop

            time.sleep(1)  # Prevents excessive CPU usage
            
if __name__ == "__main__":

    class MockMQTTService:
        """ Mock service to emulate MQTT script execution. """
        def __init__(self):
            self.script = None

        def execute(self):
            print("\n--- Executing Script ---")
            print(self.script)
            print("------------------------\n")

    class MockOptimizer:
        """ Mock optimizer that generates random values within the tweakable range. """
        def recommend(self, tweakables):
            recommendations = {}
            for param in tweakables:
                if param.getRanges():
                    lower, upper = param.getRanges()[0]  # Use the first range
                    recommendations[param] = random.uniform(lower, upper)
            return recommendations
        
    def mockObjectiveEvaluator(recommendation, targetTemp=50, targetFlowrate=2.5):
        """ Objective function that evaluates recommendation accuracy based on target values. """
        totalScore = 0
        numParams = 0

        print("\nObjective Evaluator Received:")
        print(recommendation)  # Debugging print

        for device, params in recommendation.items():
            for paramId, value in params.items():
                if "hotcoil1" in device:
                    score = max(0, 1 - abs(value - targetTemp) / 50)
                    print(f"  Temp {paramId}: {value:.2f} → Score: {score:.3f}")
                    totalScore += score
                elif "flowsynmaxi2" in device:
                    score = max(0, 1 - abs(value - targetFlowrate) / 5)
                    print(f"  Flowrate {paramId}: {value:.2f} → Score: {score:.3f}")
                    totalScore += score
                numParams += 1

        return totalScore / numParams if numParams else 0

    print("Initializing Optimization Rig...")

    # Create mock MQTT service and optimization rig
    mqttService = MockMQTTService()
    rig = OptimizationRig(mqttService)

    # Create mock devices and parameters
    device1 = "hotcoil1"
    device2 = "flowsynmaxi2"

    tempParam = Temp("ReactionTemp", associatedCommand="temp", ranges=[[25, 100]])
    flowrateParam1 = Flowrate("FlowRatePumpA", associatedCommand="pafr", ranges=[[0.1, 5]])
    flowrateParam2 = Flowrate("FlowRatePumpB", associatedCommand="pbfr", ranges=[[0.5, 7]])

    # Register devices
    rig.registerDevice(device1)
    rig.registerDevice(device2)

    # Register tweakable parameters to the devices
    rig.registerTweakableParam(device1, tempParam)
    rig.registerTweakableParam(device2, flowrateParam1)
    rig.registerTweakableParam(device2, flowrateParam2)

    # Set a mock optimizer and evaluator
    rig.optimizer = MockOptimizer()
    rig.objectiveEvaluator = mockObjectiveEvaluator
    rig.objectiveEvaluationKwargs = {"targetTemp": 50, "targetFlowrate": 2.5}

    # Set a target score for stopping the loop
    rig.targetScore = 0.80

    # Start background optimization loop
    print("\n🚀 Starting Optimization Process 🚀")
    rig.start()

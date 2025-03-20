import json
import os
import threading
import random
import time

import numpy as np

from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.parametres.reaction_parametres import Flowrate, ReactionParametres, Temp

class OptimizationRig:
    def __init__(self, mqttService, recommendationPath=r"OPTIMIZATION_TEMP\SharedData\recommendation.json", yieldPath=r"OPTIMIZATION_TEMP\SharedData\yield.json"):
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
        self.objectiveScore = 0  # Score between 0 and 1
        self.targetScore = None
        self.mqttService = mqttService
        
        self.evalYielded=False
        self.recommYielded=False
        
        self.awaitYield=False
        
        self.lastRecommendedVal={}
        
        self.startScanAt=0
        self.endScanAt=0
        
        self.zeroTime=0
        
        self.scanning=False
        
        self.generateRecommendation_TEMPsaidItOnce=False
        self.evaluateRecommendation_TEMPsaidItOnce=False
        
        self.recommendationPath=recommendationPath
        self.yieldPath=yieldPath
        
        self.summitCmndPath=r'OPTIMIZATION_TEMP\SharedData\summitCmnd.json'
        self.evaluatorCmndPath=r'OPTIMIZATION_TEMP\SharedData\evaluatorCmnd.json'
        
        # self.lastIR = self.lastMsgFromTopic[topic]
        
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
                
    def generateRecommendation_TEMP(self):
        """ Reads recommendation from Summit JSON and applies flowrate adjustment. """

        try:
            with open(self.recommendationPath, "r") as f:
                recommendedValues = json.load(f)  # Load recommendation from Summit
            
            if not recommendedValues:
                print("⚠️ Warning: Summit Optimizer returned empty recommendations.")
                return
            
            self.lastRecommendedVal=recommendedValues

            self.currentRecommendation = {}

            # Iterate over all tweakable parameters to match with recommendation
            print(f"Current tweakables: {self.reactionParametres.getAllTweakables()}")
            for param in self.reactionParametres.getAllTweakables():
                if param.name == "temperature" and "temperature" in recommendedValues:
                    if "hotcoil1" not in self.currentRecommendation:
                        self.currentRecommendation["hotcoil1"] = {}
                    self.currentRecommendation["hotcoil1"][param.id] = recommendedValues["temperature"]

                elif param.name == "flowrateA" and "flowrate" in recommendedValues:
                    adjusted_flowrate = recommendedValues["flowrate"] / 2  # ✅ Divide flowrate for two pumps
                    
                    # Assign flowrates to the correct device
                    if "vapourtecR4P1700" not in self.currentRecommendation:
                        self.currentRecommendation["vapourtecR4P1700"] = {}

                    if param.associatedCommand == "pafr":
                        self.currentRecommendation["vapourtecR4P1700"][param.id] = adjusted_flowrate
                    elif param.associatedCommand == "pbfr":
                        self.currentRecommendation["vapourtecR4P1700"][param.id] = adjusted_flowrate

                elif param.name == "flowrateB" and "flowrate" in recommendedValues:
                    adjusted_flowrate = recommendedValues["flowrate"] / 2  # ✅ Divide flowrate for two pumps
                    
                    # Assign flowrates to the correct device
                    if "vapourtecR4P1700" not in self.currentRecommendation:
                        self.currentRecommendation["vapourtecR4P1700"] = {}

                    if param.associatedCommand == "pafr":
                        self.currentRecommendation["vapourtecR4P1700"][param.id] = adjusted_flowrate
                    elif param.associatedCommand == "pbfr":
                        self.currentRecommendation["vapourtecR4P1700"][param.id] = adjusted_flowrate

            self.recommendationHistory.append(self.currentRecommendation)

            # Remove the recommendation file to prevent duplicate reads
            os.remove(self.recommendationPath)
            
            self.recommYielded=True
            self.generateRecommendation_TEMPsaidItOnce=False
            print("\n✅ Generated Recommendation:")
            for device, params in self.currentRecommendation.items():
                print(f"  Device: {device}")
                for paramId, val in params.items():
                    print(f"    {paramId}: {val:.3f}")
                    
            self.executeRecommendation_TEMP()

        except FileNotFoundError:
            # if self.recommYielded:
            #     self.recommYielded=False
            if not self.generateRecommendation_TEMPsaidItOnce:
                self.generateRecommendation_TEMPsaidItOnce=True
            else:
                return
            print("⚠️ No recommendation file found, waiting for Summit...")

    def evaluateRecommendation(self):
        """ Evaluates the latest recommendation using the provided objective function. """
        if self.objectiveEvaluator is None:
            print("Warning: No objective evaluator function set.")
            self.objectiveScore = 0
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
            
    def evaluateRecommendation_TEMP(self):
        """ Sends recommendation to Evaluator, waits for yield, and updates Summit. """
        # recommendation_path = os.path.join(SHARED_FOLDER, "recommendation.json")

        if not self.currentRecommendation:
            print("⚠️ Warning: No recommendation available for evaluation.")
            self.evalYielded=False
            return

        try:
            # Write recommendation for Evaluator to process
            # with open(recommendation_path, "w") as f:
            #     json.dump(str(self.currentRecommendation), f)

            print("\n🚀 Sent recommendation to Evaluator, waiting for yield...")

            # Wait for Evaluator to generate a yield score
            while not os.path.exists(self.yieldPath):
                time.sleep(2)  # Check every 2 seconds

            # Read the yield from Evaluator
            with open(self.yieldPath, "r") as f:
                yield_data = json.load(f)

            self.objectiveScore = yield_data.get("yield", None)

            if self.objectiveScore is None or not (0 <= self.objectiveScore <= 1):
                raise ValueError(f"Invalid objective score: {self.objectiveScore}")

            self.evaluateRecommendation_TEMPsaidItOnce=False

            print(f"✅ Received Estimated Yield: {self.objectiveScore:.3f}")

            self.evalYielded=True

            # Remove the yield file to prevent duplicate reads
            os.remove(self.yieldPath)

        except FileNotFoundError:
            if self.evalYielded:
                self.evalYielded=False
            if not self.evaluateRecommendation_TEMPsaidItOnce:
                self.evaluateRecommendation_TEMPsaidItOnce=True
            else:
                return
            print("⚠️ Evaluator has not provided yield yet, waiting...")

        except Exception as e:
            print(f"❌ Error in yield evaluation: {e}")
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
                        self.automation.addBlockElement("recommendation", device, command, value)
                        break

        # Convert to script and send to MQTT
        self.automation.parseToScript()
        self.mqttService.script = self.automation.output
        print(f"Automization output: {self.automation.output}")
                        
    def executeRecommendation_TEMP(self):
        """ Converts recommendation into commands, resets automation, and sends the script to MQTT. """
        # First, clear current automation
        self.automation.reset()
        
        #Switch to reagents
        self.automation.addBlockElement("resetAndStart","vapourtecR4P1700","svasr",True)
        self.automation.addBlockElement("resetAndStart","vapourtecR4P1700","svbsr",True)

        for device, params in self.currentRecommendation.items():
            for paramId, value in params.items():
                # Find the parameter by ID
                for param in self.reactionParametres.getAllTweakables():
                    if param.id == paramId:
                        command = param.associatedCommand
                        self.automation.addBlockElement("recommendation", device, command, value)
                        break                

        #Calculate and add delay
        volToDispense=2
        
        vol=15 #wat was dit nou weer??
        timeToPump=(volToDispense/(self.lastRecommendedVal["flowrate"]))*60

        self.automation.addBlockElement("waitAndSwitch","Delay","sleepTime",timeToPump)

        #Switch to back to solvent
        self.automation.addBlockElement("waitAndSwitch","vapourtecR4P1700","svasr",False)
        self.automation.addBlockElement("waitAndSwitch","vapourtecR4P1700","svbsr",False)
        
        timeToReachExit=((vol/(self.lastRecommendedVal["flowrate"]))*60)
        delayRemaining=timeToReachExit - timeToPump #TODO - maak seker
        delayRemaining=delayRemaining - delayRemaining*0.05 #Start scanning a bit earlier to compensate for forwards dispersion
        
        #Wait until reaction stream theoretically reaches IR
        self.automation.addBlockElement("waitAndSwitch","Delay","sleepTime",delayRemaining)
        
        #Scan for a while
        timeToScan=timeToPump + timeToPump*0.15 #Scan a little longer to compensate for rearwards dispersion
        self.automation.addBlockElement("scanning","Delay","sleepTime",timeToScan)
                        
        # Convert to script and send to MQTT
        self.automation.parseToScript()
        self.mqttService.script = self.automation.output
        
        #zero
        self.zeroTime=time.time()
        #Delays
        self.startScanAt=timeToReachExit + self.zeroTime
        self.endScanAt=timeToScan + self.zeroTime
        
        self.awaitYield=True
        print(f"Automization output: {self.automation.output}")
        
    def setGoSummit(self,run):
        if run:
            with open(self.summitCmndPath, "w") as f:
                json.dump({"goSummit":run}, f)
        else:
            with open(self.summitCmndPath, "w") as f:
                json.dump({"goSummit":run}, f)            
        
    def setGoEvaluator(self,run):
        if run:
            with open(self.evaluatorCmndPath, "w") as f:
                json.dump({"goEvaluator":run}, f)
        else:
            with open(self.evaluatorCmndPath, "w") as f:
                json.dump({"goEvaluator":run}, f)            

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
            if self.recommYielded:
                self.generateRecommendation_TEMP()
            elif self.evalYielded:
                self.evaluateRecommendation_TEMP()

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

    print("\n🔹 Initializing Optimization Rig...")

    # Create mock MQTT service and optimization rig
    mqttService = MockMQTTService()
    rig = OptimizationRig(mqttService)

    # Define devices
    device1 = "hotcoil1"
    device2 = "vapourtecR4P1700"

    # Define tweakable parameters
    tempParam = Temp("temperature", associatedCommand="temp", ranges=[[25, 100]])
    flowrateParam1 = Flowrate("flowrate", associatedCommand="pafr", ranges=[[0.1, 2]])
    flowrateParam2 = Flowrate("flowrate", associatedCommand="pbfr", ranges=[[0.1, 2]])

    # Register devices
    rig.registerDevice(device1)
    rig.registerDevice(device2)

    # Register tweakable parameters to the devices
    rig.registerTweakableParam(device1, tempParam)
    rig.registerTweakableParam(device2, flowrateParam1)
    rig.registerTweakableParam(device2, flowrateParam2)

    print("\n✅ Rig Initialized!\n")

    # --- MANUAL INPUT SECTION ---
    print("\n🔹 Copy-Paste this into 'SharedData/recommendation.json':")
    print(json.dumps({
        "temperature": 75.0,
        "flowrate": 3.0  # Summit recommends total flowrate (before division)
    }, indent=4))
    
    input("\nPress Enter after pasting into 'SharedData/recommendation.json'...")

    # --- TEST 1: Read and Process Recommendation ---
    print("\n🚀 Running generateRecommendation_TEMP()...")
    rig.generateRecommendation()

    # --- MANUAL INPUT SECTION ---
    print("\n🔹 Copy-Paste this into 'SharedData/yield.json':")
    print(json.dumps({
        "temperature": 75.0,
        "flowrate": 3.0,
        "yield": 0.87  # Simulated yield from Evaluator
    }, indent=4))

    input("\nPress Enter after pasting into 'SharedData/yield.json'...")

    # --- TEST 2: Read Evaluated Yield ---
    print("\n🚀 Running evaluateRecommendation_TEMP()...")
    rig.evaluateRecommendation()

    # --- TEST 3: Execute Recommendation ---
    print("\n🚀 Running executeRecommendation()...")
    rig.executeRecommendation()

    print("\n✅ Test Cycle Complete!")

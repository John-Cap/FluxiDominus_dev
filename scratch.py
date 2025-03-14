import json
import os
import threading
import random
import time

import numpy as np

from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.Optimization.optimization_rig import OptimizationRig
from Core.parametres.reaction_parametres import Flowrate, ReactionParametres, Temp

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
    flowrateParam1 = Flowrate("flowrateA", associatedCommand="pafr", ranges=[[0.1, 2]])
    flowrateParam2 = Flowrate("flowrateB", associatedCommand="pbfr", ranges=[[0.1, 2]])

    # Register devices
    rig.registerDevice(device1)
    rig.registerDevice(device2)

    # Register tweakable parameters to the devices
    rig.registerTweakableParam(device1, tempParam)
    rig.registerTweakableParam(device2, flowrateParam1)
    rig.registerTweakableParam(device2, flowrateParam2)

    print("\n✅ Rig Initialized!\n")

    while True:
        # --- MANUAL INPUT SECTION ---
        print("\n🔹 Copy-Paste this into 'SharedData/recommendation.json':")
        print(json.dumps({
            "temperature": 75.0,
            "flowrate": 3.0  # Summit recommends total flowrate (before division)
        }, indent=4))
        
        input("\nPress Enter after pasting into 'SharedData/recommendation.json'...")

        # --- TEST 1: Read and Process Recommendation ---
        print("\n🚀 Running generateRecommendation_TEMP()...")
        rig.generateRecommendation_TEMP()
        rig.executeRecommendation_TEMP()

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
        rig.evaluateRecommendation_TEMP()

        print("\n✅ Test Cycle Complete!")

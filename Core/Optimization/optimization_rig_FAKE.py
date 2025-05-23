import ast
import json
import os
import threading
import random
import time
import paho.mqtt.client as mqtt

import numpy as np

from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.UI.brokers_and_topics import MqttTopics
from Core.parametres.reaction_parametres import Flowrate, ReactionParametres, Temp
from ReactionSimulation.fakeReactionLookup import ReactionLookup

class OptimizationRig:
    def __init__(self, mqttService, host="localhost"):
        self.automation = FlowChemAutomation()  # Handles command parsing
        self.reactionParametres = ReactionParametres()  # Holds different parameters that can be optimized
        self.availableParams = {}  # Reaction parameters that can be tweaked, per device
        self.availableCommands = {}  # Links a tweakable parameter to a specific device command name
        self.availableDeviceCommands = {}  # Links device to commands
        self.currentRecommendation = {}
        self.recommendationHistory = []
        self._rigThread = None
        self.optimizer = None
        self.terminate = False
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
        
        self.optimizerInit=False
        self.evaluatorInit=False
        
        self.summitCmndPath=r'OPTIMIZATION_TEMP\SharedData\summitCmnd.json'
        self.evaluatorCmndPath=r'OPTIMIZATION_TEMP\SharedData\evaluatorCmnd.json'
        
        self.topicOptOut="opt/out"
        self.topicOptIn="opt/in"
        self.topicEvalOut="eval/out"
        self.topicEvalIn="eval/in"
        
        self.lastPingEvaluator=0
        self.lastPingOptimizer=0
        
        self.client = mqtt.Client(client_id="OptimizerRig", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
        self.client.on_message=self.onMessage
        self.client.on_connect=self.onConnect
        self.client.on_disconnect=self.onDisconnect
        
        self.host=host
        
        self.connected=False
        
        self.objTarget=0
        self.optimized=False
        
        self.virtualYieldLookup = ReactionLookup()
        
        self.resTime=0
        
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
        pass
    
    def pingOptimizer(self):
        self.client.publish(self.topicOptOut,json.dumps({"statReq":{"ping":{}}})) #additional params can be sent to request specific information and not just ping
    def pingEvaluator(self):
        self.client.publish(self.topicEvalOut,json.dumps({"statReq":{"ping":{}}}))
        
    def onMessage(self, client, userdata, msg):
        topic=msg.topic
        msg = msg.payload.decode()
        msg = msg.replace("true", "True").replace("false", "False")
        msg = msg.replace("null","None")
        msg = ast.literal_eval(msg)
        
        if topic == self.topicEvalIn:
            if "statReq" in msg:
                #Init?
                if "init" in msg["statReq"]:
                    if msg["statReq"]["init"] != self.evaluatorInit:
                        self.evaluatorInit=msg["statReq"]["init"]
                        if self.evaluatorInit:
                            print("Evaluator initialized!")
                        self.lastPingEvaluator=time.time()
                return
                            
            self.evaluateRecommendation_TEMP(msg)
        elif topic == self.topicOptIn:
            if "statReq" in msg:
                #Init?
                if "init" in msg["statReq"]:
                    if msg["statReq"]["init"] != self.optimizerInit:
                        self.optimizerInit=msg["statReq"]["init"]
                        if self.optimizerInit:
                            print("Optimizer initialized!")
                        self.lastPingOptimizer=time.time()
                return
                            
            self.generateRecommendation_TEMP(msg)
            print(f"Received message from optimizer! -> {msg}")

    def onConnect(self, client, userdata, flags, rc):
        #if self.connected:
            #return
        if rc == 0:
            self.client.subscribe(topic=self.topicEvalIn)
            self.client.subscribe(topic=self.topicOptIn)
            time.sleep(1)
            print(f"WJ - Connected with rc {rc}!")
            self.connected=True
    def onDisconnect(self, client, userdata, rc):
        print(f"Optimization rig has disconnected! Reason code: {rc}")
    
    def generateRecommendation_TEMP(self, msg):
        """ Check for evaluated yield and update optimizer. """
        
        recommendedValues=msg["recomm"]
        
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
        
        self.recommYielded=True
        self.generateRecommendation_TEMPsaidItOnce=False
        
        print("\n✅ Generated Recommendation:")
        for device, params in self.currentRecommendation.items():
            print(f"  Device: {device}")
            for paramId, val in params.items():
                print(f"    {paramId}: {val:.3f}")

        evalInfo={
            "recommendedParams":{
                "Temperature":float(self.lastRecommendedVal["temperature"]),
                "Flowrate":float(self.lastRecommendedVal["flowrate"])
            }
        }
        self.mqttService.publish(MqttTopics.getUiTopic("optOut"),json.dumps({"optInfo":evalInfo}))
        self.executeRecommendation_TEMP()

    def evaluateRecommendation(self):
        pass
    
    def evaluateRecommendation_TEMP(self, msg):
        """ Sends recommendation to Evaluator, waits for yield, and updates Summit. """
        if "maxYield" in msg:
            #self.objectiveScore=msg["maxYield"]
            self.objectiveScore=self.virtualYieldLookup.getYield(self.lastRecommendedVal["temperature"],self.resTime)
            print(f"Recommendation {self.lastRecommendedVal} delivered conversion of {self.objectiveScore}")
            
            # if self.objectiveScore is None or not (0 <= self.objectiveScore <= 1):
            #     raise ValueError(f"Invalid objective score: {self.objectiveScore}")
            evalInfo={
                "eval":{
                    "yield":self.objectiveScore
                }
            }
            msgOut={"goSummit":True,"instruct":evalInfo}
            print(f"✅ Received Estimated Yield: {self.objectiveScore:.3f}")
            self.client.publish(self.topicOptOut,json.dumps(msgOut))
            evalInfo={
                "recommendationResult":{
                    "Temperature":self.lastRecommendedVal["temperature"],
                    "Flowrate":self.lastRecommendedVal["flowrate"],
                    "yield":self.objectiveScore
                }
            }
            self.mqttService.publish(MqttTopics.getUiTopic("optOut"),json.dumps({"optInfo":evalInfo}))
            if self.objectiveScore >= self.objTarget:
                self.terminate=True
                self.optimizing=False
                self.setGoSummit(False)
                self.setGoEvaluator(False)
                evalInfo={
                    "eval":{
                        "maxYield":self.objectiveScore
                    }
                }
                self.mqttService.publish(MqttTopics.getUiTopic("optOut"),json.dumps({"optInfo":evalInfo}))
                print(f"Target conversion of {self.objTarget} reached with max conversion {self.objectiveScore}!")
                return
            

            self.optimizing = False
            self.evalYielded=True
            

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
        volToDispense=1
        
        vol=5 #wat was dit nou weer??
        timeToPump=(volToDispense/(self.lastRecommendedVal["flowrate"]))*60

        self.automation.addBlockElement("waitAndSwitch","Delay","sleepTime",timeToPump)

        #Switch to back to solvent
        self.automation.addBlockElement("waitAndSwitch","vapourtecR4P1700","svasr",False)
        self.automation.addBlockElement("waitAndSwitch","vapourtecR4P1700","svbsr",False)
        
        self.resTime=(vol/(self.lastRecommendedVal["flowrate"]))
        timeToReachExit=(self.resTime)*60
        delayRemaining=timeToReachExit - timeToPump #TODO - maak seker
        delayRemaining=delayRemaining - delayRemaining*0.05 #Start scanning a bit earlier to compensate for forwards dispersion
        
        #Wait until reaction stream theoretically reaches IR
        self.automation.addBlockElement("waitAndSwitch","Delay","sleepTime",delayRemaining)
        
        #Scan for a while
        timeToScan=timeToPump + timeToPump*0.15 #Scan a little longer to compensate for rearwards dispersion
        self.automation.addBlockElement("scanning","Delay","sleepTime",timeToScan)
                        
        # Convert to script and send to MQTT
        self.automation.parseToScript()
        self.optimizing = True
        self.mqttService.script = self.automation.output
        
        #zero
        self.zeroTime=time.time()
        #Delays
        self.startScanAt=timeToReachExit + self.zeroTime
        self.endScanAt=timeToScan + self.startScanAt

        self.awaitYield=True
        
        print(f"IR scanning will commence in {timeToReachExit/60} minutes. Scanning will take {timeToScan} seconds.")

    def readYieldFromSurface(self,temp,res):
        return self.virtualYieldLookup.getYield(temp,res)

    def setGoSummit(self,run):
        if run:
            brackets={}
            self.client.publish(topic=self.topicOptOut,payload=json.dumps(
                {"goSummit":True,"instruct":{"start":"","init":{
                    "initVal":{ #TODO - Temp
                        "temperature":[10,60],
                        "flowrate":[0.25,3]
                    }
                }}}
            ))
        else:
            self.client.publish(topic=self.topicOptOut,payload=json.dumps({
                "goSummit":False
            }))
            
    def setGoEvaluator(self,run):
        if run:
            self.client.publish(topic=self.topicEvalOut,payload=json.dumps({
                "goEvaluator":True
            }))
        else:
            self.client.publish(topic=self.topicEvalOut,payload=json.dumps({
                "goEvaluator":False
            }))        

    def resetEvaluator(self):
        self.client.publish(topic=self.topicEvalOut,payload=json.dumps({
            "goEvaluator":False,
            "reset":True
        }))

    def initRig(self):
        self.client.connect(host=self.host)
        self.client.loop_start()

    def optimise(self,objTarget=0.9):
        """ Starts a background thread to continuously optimize until the target score is reached. """
        self.objTarget=objTarget
        
        if not self.connected:
            print("Not connected to MQTT!")
            return
            
        if not (self.evaluatorInit and self.optimizerInit):
            print("Not all optimizers and/or evaluators initialized")
            return
            
        if not self.optimizing:
            self.optimizing = True
        self.setGoSummit(True)
        self.resetEvaluator()

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

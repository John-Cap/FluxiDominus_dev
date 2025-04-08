
import ast
import os
import summit
from summit.domain import Domain, ContinuousVariable
from summit.strategies import SOBO
import json
import pandas as pd
import numpy as np
import paho.mqtt.client as mqtt

SHARED_FOLDER = "../SharedData/"  # Set path to shared folder

class SummitOptimizer:
    def __init__(self,client=None,host="localhost"):
        # Define the optimization domain
        self.domain = Domain()
        self.randomInitialAssigned=False

        self.started=False

        # Use SOBO optimizer
        self.strategy = None
        self.experiments = pd.DataFrame(columns=["temperature", "flowrate", "yieldVal"])  # Store experiments

        self.prevExp={}
        
        self.updateSaidItOnce=False
        
        self.client = client if client else (mqtt.Client(client_id="SummitOptimizer", clean_session=True, userdata=None, protocol=mqtt.MQTTv311))
        self.host=host
        self.topicIn="opt/out"
        self.topicOut="opt/in"
        
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage

    def recommend(self):
        """ Generate the next recommendation. """
        if self.experiments.empty and not self.randomInitialAssigned:
            # Generate initial random experiments (needed for SOBO)
            temp = np.random.uniform(10, 50)
            flowrate = np.random.uniform(0.25, 2)
            recommendation = {"recomm":{"temperature": temp, "flowrate": flowrate}}
            # recommendation = {"recomm":{"temperature": float(30), "flowrate": float(0.5)}}
            self.prevExp=recommendation["recomm"]
            print("First random experiment:", recommendation)
            self.randomInitialAssigned=True
        else:
            # Generate recommendation from SOBO
            print(f"Previous experiments: {self.experiments}")
            next_experiment = self.strategy.suggest_experiments(1,summit.DataSet.from_df(self.experiments))

            if next_experiment.empty:
                print("Summit returned an empty dataset! Ensure optimizer is correctly updated with past experiments.")
                return

            recommendation = {
                "recomm":{
                    "temperature": next_experiment["temperature"].iloc[0],
                    "flowrate": next_experiment["flowrate"].iloc[0]
                }
            }
            self.prevExp=recommendation["recomm"]
            
        # Write recommendation
        self.client.publish(self.topicOut,json.dumps(recommendation))
        
        print(f"Summit Optimizer recommended: {recommendation}")

    def update(self, data):
        """ Check for evaluated yield and update optimizer. """
        if not self.started:
            if "goSummit" in data:
                if data["goSummit"]:
                    self.recommend()
                    self.started=True
                    return
                else:
                    #reset
                    self.prevExp={}
                    self.strategy=None
                    self.experiments = pd.DataFrame(columns=["temperature", "flowrate", "yieldVal"])
                    self.domain = Domain()
                    self.started=False
                    print("Summit was reset!")
                    return
                    
        else:
            if "goSummit" in data:
                if not data["goSummit"]:
                    #reset
                    self.strategy=None
                    self.prevExp={}
                    self.experiments = pd.DataFrame(columns=["temperature", "flowrate", "yieldVal"])
                    self.domain = Domain()
                    self.started=False
                    print("Summit was reset!")
                    return
        
        yieldScore = data["yield"]
        print(f"Summit received yield score: {yieldScore}")
        temp=self.prevExp["temperature"]
        flowrate=self.prevExp["flowrate"]
        
        # Add the new experiment result
        newData = pd.DataFrame({"temperature": [temp], "flowrate": [flowrate], "yieldVal": [yieldScore]})
        self.experiments = pd.concat([self.experiments, newData], ignore_index=True)

        print(f"Updated Summit with yield: {yieldScore:.3f}")
        
        self.recommend()

    def pingOptRig(self):
        self.client.publish(self.topicOut,json.dumps({"statReq":{"init":True}}))
        
    def onMessage(self, client, userdata, msg):
        data = msg.payload.decode()
        data = data.replace("true", "True").replace("false", "False")
        data=data.replace("null","None")
        data = ast.literal_eval(data)
        
        if "goSummit" in data:
            if not data["goSummit"]:
                self.update({"goSummit":False})
        
        if "statReq" in data:
            if "ping" in data["statReq"]:
                self.pingOptRig()
            
        if "instruct" in data:
            if "init" in data["instruct"]:
                if "initVal" in data["instruct"]["init"]:
                    print(f'initVal: {data["instruct"]["init"]}')
                    self.domain += ContinuousVariable(name="temperature",bounds=[0,50], is_objective=False, description='temperature')
                    self.domain += ContinuousVariable(name="flowrate", bounds=[0.1,3], is_objective=False, description='flowrate')
                    self.domain += ContinuousVariable(name="yieldVal", bounds=[0, 1], is_objective=True, maximize=True, description='yieldVal')  # Yield is the objective
                    if not self.strategy:
                        self.strategy=SOBO(self.domain)
            if "start" in data["instruct"]:
                self.update({"goSummit":True})
                return
            if "eval" in data["instruct"]: #Only route for now, will automatically recommend
                print(f"Evaluation result data: {data}")
                self.update(
                    {
                        "goSummit":data["goSummit"],
                        "yield":data["instruct"]["eval"]["yield"]
                    }
                )

    def onConnect(self, client, userdata, flags, rc):
        #if self.connected:
            #return
        if rc == 0:
            self.client.subscribe(topic=self.topicIn)
            print(f"WJ - Connected with rc {rc}!")
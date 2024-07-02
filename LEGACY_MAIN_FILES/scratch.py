import copy
import threading
import time
from time import sleep
from datetime import datetime

import numpy as np
from Core.Communication.Network import MQTTReader
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder
from Core.Control.Commands import BaselineDetected, BlueDetected, ColourChanged, Condition, Configuration, Delay, IRCategorizer, IrSwitch, Procedure, RedDetected, WaitUntil
import json
import paho.mqtt.client as mqtt

from Core.Control.IR import IRScanner
from Core.Diagnostics.Logging import Diag_log
from Core.Fluids.FlowPath import IR, Chip, Coil, FlowAddress, FlowOrigin, FlowPath, FlowTerminus, Pump, Slugs, TPiece, Tubing, Valve

#Logging
diag_log=Diag_log()

# MQTT Broker Settings
broker_address = "192.168.1.2"
port = 1883

# Callback function to handle when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        pass
    else:
        print("Connection failed with error code " + str(rc))

# Create MQTT client instance
global client
client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
# Assign on_connect callback to client
client.on_connect = on_connect

# Connect to MQTT broker
client.connect(broker_address, port, 1)
client.loop_start()

# Script listener
global ThisMQTTReader
ThisMQTTReader=MQTTReader()
ThisMQTTReader.readMQTTLoop()

_fdpDecoder=FdpDecoder();

######################################################################
#Flow trackerscript
_path=FlowPath()

#Stocks + pumps up to t piece
_maxiColourStock=FlowOrigin(volume=0,name="MAXI_COLOUR",flowrateIn=0)
_maxiSolv=FlowOrigin(volume=0,name="MAXI_SOLV",flowrateIn=1/60)
_SF10ColourStock=FlowOrigin(volume=0,name="SF10_COLOUR",flowrateIn=0)
_SF10Solv=FlowOrigin(volume=0,name="SF10_SOLV",flowrateIn=0)
#Pumps
_maxiB=Pump(volume=0.5,name="PUMP_MAXI_B",flowrateIn=0)
_SF10=Pump(volume=0.5,name="PUMP_SF10",flowrateIn=0)
#Valves
_maxiValve=(Valve(volume=0.005,name="MAXI_VALVE"))
_SF10Valve=(Valve(volume=0.005,name="SF10_VALVE"))
_collectValve=(Valve(volume=0.005,name="COLL_VALVE"))
#Mixing chip
_chip=Chip(volume=2,name="MIXING_CHIP",flowrateIn=0)
#Coil
_coil=Coil(volume=25,name="COIL",flowrateIn=0)
#IR
_IR=(IR(volume=0.025,name="IR"))
#Tubing
_tubingToSF10=(Tubing(volume=0.22,name="TUBING_TO_SF10"))
_tubingFromSF10=(Tubing(volume=0.22,name="TUBING_FROM_SF10"))
_tubingToMaxi=(Tubing(volume=0.22,name="TUBING_TO_MAXI"))
_tubingFromMaxi=(Tubing(volume=0.22,name="TUBING_FROM_MAXI"))
_tubingToWC=(Tubing(volume=0.4712,name="TUBING_TO_WC"))
#Terminus
_waste=FlowTerminus(volume=0,name="WASTE")
_collect=FlowTerminus(volume=0,name="COLLECT")

_collectWaste=FlowAddress('TO_WASTE',[],[[_collectValve,"WASTE"]])
_collectColour=FlowAddress('TO_BLUE',[],[[_collectValve,"COLLECT"]])

###################
#Connect components
_maxiColourStock.flowInto(_maxiValve,setNameIn="COLOUR")
_maxiSolv.flowInto(_maxiValve,setNameIn="PUSH")
_SF10ColourStock.flowInto(_SF10Valve,setNameIn="COLOUR")
_SF10Solv.flowInto(_SF10Valve,setNameIn="PUSH")

_maxiValve.flowInto(_tubingToMaxi)
_SF10Valve.flowInto(_tubingToSF10)

_tubingToMaxi.flowInto(_maxiB)
_tubingToSF10.flowInto(_SF10)

_maxiB.flowInto(_tubingFromMaxi)
_SF10.flowInto(_tubingFromSF10)

_tubingFromMaxi.flowInto(_chip)
_tubingFromSF10.flowInto(_chip)

_chip.flowInto(_coil)
_coil.flowInto(_IR)

_IR.flowInto(_tubingToWC)

_tubingToWC.flowInto(_collectValve)

_collectValve.flowInto(_waste,setNameOut="WASTE")
_collectValve.flowInto(_collect,setNameOut="WASTE")

#Create paths
_path.addPath(
    [
        _maxiColourStock,
        _maxiSolv,
        _SF10ColourStock,
        _SF10Solv,
        _tubingToMaxi,
        _tubingToSF10,

        _maxiValve,
        _SF10Valve,

        _maxiB,
        _SF10,

        _tubingFromMaxi,
        _tubingFromSF10,

        _chip,
        _coil,
        _IR,

        _tubingToWC,

        _collectValve,
        _collect,
        _waste
    ]
)

_path.selectPath()
_maxiColourStock.associatedFlowPath=_path
_maxiSolv.associatedFlowPath=_path
_SF10ColourStock.associatedFlowPath=_path
_SF10Solv.associatedFlowPath=_path
'''
for _x in _path.segments:
    print("*********")
    print(_x.name)
    print(_x.inletSets)
    print(_x.outletSets)
    print(_x.inlets)
    print(_x.outlets)
'''
global _currOrigin
_currOrigin=_maxiColourStock
global _currTerminus
_currTerminus=_waste

# Flag variable to indicate whether the thread should continue running
running=True
allSlugs=Slugs()

_intervalStamp=time.perf_counter()

def flowTracker():
    global _intervalStamp
    global _IR
    global running
    global allSlugs
    global _currTerminus
    while running:
        _slug=_currOrigin.dispense()
        allSlugs.slugs.append(_slug)
        print(str(_slug.slugVolume()) + " mL")

        _path.updateFlowrates()
        for _x in _path.segments:
            print(_x.flowrateOut)

        _switched=False
        _now=time.perf_counter()
        _path.timePrev=time.perf_counter()
        while not (_slug.tailHost is _currTerminus):
            _path.advanceSlugs()
            _vol=_slug.slugVolume()
            if _slug.frontHost is _IR and not _switched:
                _currOrigin.terminateDispensing()
                _switched=True
                _stamp=datetime.now()
                print(_stamp.strftime("%H:%M:%S") + "->Flow tracker predicts slug has reached IR!")
            if time.perf_counter()-_intervalStamp>10:
                _intervalStamp=time.perf_counter()
                print("Time: " + str(round(time.perf_counter() - _now, 0)) + " seconds, Fro h/pos: " + str(
                    _slug.frontHost.name) + ", " + str(round(_slug.frontHostPos, 2)) + "/" + str(
                    _slug.frontHost.volume) + " mL, tail h/pos: " + str(_slug.tailHost.name) + ", " + str(
                    round(_slug.tailHostPos, 2)) + "/" + str(_slug.tailHost.volume) + " mL, fr: " + str(
                    round(_slug.frontHost.flowrateOut*60, 2)) + " mL.min-1, slug vol: " + str(
                    round(_vol, 2)) + " mL, vol collected: " + str(round(_slug.collectedVol, 2)) + " mL")

        print("************")
        print(str(time.perf_counter() - _now) + " seconds")
        print("Collected slug volumes")
        for _x in _path.collectedSlugs:
            print(_x.collectedVol)
        print("Slug took " + str(round(time.perf_counter() - _now, 0)) + " seconds to reach terminus")
        print("************")

######################################################################
#IR script
_IRScanner=IRScanner();
_IRScanner.parseIrData();
red_data=np.array(_IRScanner.arrays_list_red);  # Example time series data for compound 1
red_data=np.mean(red_data, axis=0);
blue_data=np.array(_IRScanner.arrays_list_blue);  # Example time series data for compound 1
blue_data=np.mean(blue_data, axis=0);
ThisIrCategorizer=IRCategorizer(red_data,blue_data);
global ThisIrSwitch;
ThisIrSwitch=IrSwitch();
ThisIrSwitch.makeSures=1
ThisIrSwitch.makeSuresOrig=1
_redDetected=RedDetected(ThisIrSwitch);
_blueDetected=BlueDetected(ThisIrSwitch);
_baselineDetected=BaselineDetected(ThisIrSwitch);
_colourChanged=ColourChanged();
global currentScan;
currentScan=[];
currentColour="Baseline";
global IrTopic;
IrTopic="subflow/reactIR702L1/tele";

global IrInterrupt
IrInterrupt=False

def randomSolvReagSwitch():
    pass

def scanIR():
    global running
    global currentColour
    global ThisIrSwitch
    global IrInterrupt
    print("Welcome to 'scanIR()', current colour: " + ThisIrSwitch.currentLock)
    _saidItOnce=False
    while running:
        currentScan=copy.deepcopy(ThisMQTTReader.currentIrScan)
        if len(currentScan)!=0:
            
            del currentScan[750:]
            del currentScan[410:540]

            colour=ThisIrCategorizer.categorize(np.array(currentScan))
            if ThisIrSwitch.statusChanged(colour):
                print("New colour: " + colour)

        time.sleep(1)
        if ThisIrSwitch.currentLock!="Baseline" and _saidItOnce:
            _saidItOnce=False
            IrInterrupt=True

        elif ThisIrSwitch.currentLock=="Baseline" and not _saidItOnce:
            IrInterrupt=False
            _saidItOnce=True

    
    print("IR loop done")
# Create a thread for running the code
time.sleep(2)
thread=threading.Thread(None,scanIR,"IR_Thread")

# Start the thread
thread.start()

######################################################################
#Waste sequence
clearToWaste=[
    {
        "deviceName": "flowsynmaxi2",
        "inUse":True,
        "settings": {
            "subDevice": "PumpBFlowRate",
            "command": "SET",
            "value": 0
        },
        "topic":"subflow/flowsynmax2/cmnd",
        "client":"client"
    },
    {
        "deviceName":"flowsynmaxi2", 
        "inUse" : True,
        "settings":{
            "subDevice": "FlowSynValveB",
            "command":"SET",
            "value": False
        },
        "topic":"subflow/flowsynmax2/cmnd",
        "client":"client"
    },
    {"deviceName":"flowsynmaxi2", "inUse":True, "settings":{"command":"SET", "subDevice":"FlowCWValve", "value": False},"topic":"subflow/flowsynmax2/cmnd","client":"client"},
    {"Delay":{"initTimestamp":None,"sleepTime":1}},
    {
        "deviceName":"sf10Vapourtec1",
        "inUse":True,
        "settings":{"command":"SET","mode":"FLOW","flowrate":4},
        "topic":"subflow/sf10vapourtec1/cmnd",
        "client":"client"
    },
    {"Delay":{"initTimestamp":None,"sleepTime":30}},
    {
        "deviceName":"sf10Vapourtec1",
        "inUse":True,
        "settings":{"command":"SET","mode":"FLOW","flowrate":0},
        "topic":"subflow/sf10vapourtec1/cmnd",
        "client":"client"
    }
]

if not isinstance(clearToWaste,str):
    clearToWaste=str(clearToWaste)
clearToWaste=clearToWaste.replace("'",'"')
clearToWaste=clearToWaste.replace("True",'true')
clearToWaste=clearToWaste.replace("False",'false')
clearToWaste=clearToWaste.replace("None",'null')
clearToWaste=_fdpDecoder.readAndReturn(clearToWaste)

for _x in clearToWaste:
    if isinstance(_x,dict):
        _x["client"]=client

######################################################################

_time=time.time()
_updateTime=10

while True:

    print("Waiting for script")

    while len(ThisMQTTReader.currentScript) == 0:
        pass

    print("Script received")

    nodeScript=eval(ThisMQTTReader.currentScript)
    if not isinstance(nodeScript,str):
        nodeScript=str(nodeScript)
    nodeScript=nodeScript.replace("'",'"')
    nodeScript=nodeScript.replace("True",'true')
    nodeScript=nodeScript.replace("False",'false')
    nodeScript=nodeScript.replace("None",'null')
    nodeScript=_fdpDecoder.readAndReturn(nodeScript)

    for _x in nodeScript:
        if isinstance(_x,dict):
            _x["client"]=client

    _starter="Issuing go command"
    _starter=json.dumps(_starter)
    _started=client.publish("test/status/",_starter)
    _started.wait_for_publish(10)
    _go=_started.is_published()
    if _go:
        print("Go command published")
    else:
        print("Go command not delivered!")

    _procedure=Procedure(sequence=[
        Configuration(
            nodeScript,
            "->nodeScript 1 complete"
        )    
    ])
    _procedureOrig=Procedure(sequence=[
        Configuration(
            nodeScript,
            "->nodeScript 1 complete"
        )    
    ])
    _clearToWaste=Procedure(sequence=[
        Configuration(
            clearToWaste,
            "->clear to waste complete"
        ) 
    ])
    _currentConfigurator=_procedure.currConfiguration()

    #_currentConfigurator.sendMQTT()
    itemsQueued=True
    _result=None
    _starter="Running procedure"
    _starter=json.dumps(_starter)
    _started=client.publish("test/status/",_starter)
    ThisMQTTReader.runTest=True
    time.sleep(2);
    print("Entering itemsQueued loop: " + str(ThisMQTTReader.runTest))

    _saidItOnce=False

    #Start IR tracker
    #thread_IR=threading.Thread(target=flowTracker)

# Start the thread
    #thread_IR.start()
    #################

    _reachedTime=time.perf_counter()

    while itemsQueued and ThisMQTTReader.runTest:

        ###################################
        #IR interrupt
        if IrInterrupt and not _saidItOnce:
            continue

            _starter="Colour detected! Flushing flowpath"
            _starter=json.dumps(_starter)
            _started=client.publish("test/status/",_starter)
            #_procedure=_clearToWaste
            _currentConfigurator=_clearToWaste.currConfiguration()
            _saidItOnce=True
            print(datetime.now().strftime("%H:%M:%S")+"->Colour detected! CW set to waste")
            print(str(time.perf_counter()-_reachedTime) + " seconds from Maxi valve to IR")
        elif not IrInterrupt and _saidItOnce:
            continue
            _starter="Collecting clear solvent"
            _starter=json.dumps(_starter)
            _started=client.publish("test/status/",_starter)
            #_procedure=copy.copy(_procedureOrig)
            #_currentConfigurator=_procedure.currConfiguration()
            _saidItOnce=False
            print(datetime.now().strftime("%H:%M:%S")+"->No colour detected. CW set to collect")
        ###################################
            
        if itemsQueued:
            if len(_currentConfigurator.commands)==0:
                print(_currentConfigurator.setMessage)
                _procedure.next()
                _currentConfigurator=_procedure.currConfiguration()
                if _currentConfigurator is None:
                    itemsQueued=False
            elif len(_currentConfigurator.commands)!=0:
                _result = _currentConfigurator.sendMQTT()
                #print(_result)            
        elif not (_procedure.currConfiguration() is None):
                itemsQueued=True
        else:
            pass
    
    time.sleep(2)

    print("Run test: " + str(ThisMQTTReader.runTest))
    _starter={'running':False,'status':'Procedure complete'}    
    _starter=json.dumps(_starter)
    _started=client.publish("test/status/",_starter) 

    ThisMQTTReader.currentScript=[]

'''
import copy
import datetime
import time

import numpy as np
from Core.Communication.Network import MQTTReader
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import BaselineDetected, BlueDetected, ColourChanged, Condition, Configuration, Delay, IRCategorizer, IrSwitch, Procedure, RedDetected, WaitUntil
import json
import paho.mqtt.client as mqtt
import threading
import time
from Core.Control.IR import IRScanner
from Core.Diagnostics.Logging import Diag_log
from Core.Fluids.FlowPath import IR, FlowAddress, FlowOrigin, FlowPath, FlowTerminus, Pump, Slugs, TPiece, Tubing, Valve

from Core.Fluids.FlowPath import FlowPathAdjustment
from Core.Utils.Utils import Utils

#Logging
diag_log=Diag_log()

# MQTT Broker Settings
broker_address = "192.168.1.2"
port = 1883

# Callback function to handle when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        pass
        #print("Connected to broker")
    else:
        print("Connection failed with error code " + str(rc))

# Create MQTT client instance
client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
# Assign on_connect callback to client
client.on_connect = on_connect

# Connect to MQTT broker

client.connect(broker_address, port, 1)
client.loop_start()

# Script listener

_MQTTReader=MQTTReader()
_MQTTReader.readMQTTLoop()


###############################################################
#IR
_IRScanner=IRScanner().parseIrData()
red_data=np.array(_IRScanner.arrays_list_red)  # Example time series data for compound 1
red_data=np.mean(red_data, axis=0)
blue_data=np.array(_IRScanner.arrays_list_blue)  # Example time series data for compound 1
blue_data=np.mean(blue_data, axis=0)
_IrCategorizer=IRCategorizer(red_data,blue_data)
_IrSwitch=IrSwitch()
_redDetected=RedDetected(_IrSwitch)
_blueDetected=BlueDetected(_IrSwitch)
_baselineDetected=BaselineDetected(_IrSwitch)
_colourChanged=ColourChanged()
_flowPathAdjuster=FlowPathAdjustment()

_path=FlowPath()

###############################################################
# Fluid tracker + flow line
#Stocks + pumps up to t piece
_redStock=FlowOrigin(volume=0,name="RED_STOCK_LINE",flowrateIn=1.0)
_blueStock=FlowOrigin(volume=0,name="BLUE_STOCK_LINE",flowrateIn=1.0)
_pumplineSolv=FlowOrigin(volume=0,name="PUSH_SOLV_LINE",flowrateIn=1.0)
#Pump lines
_pumpline_1=Pump(volume=1.5,name="PUMP_1_LINE")
#Valves
_stocksValve=(Valve(volume=0,name="STOCKS_VALVE"))
_collectValve=(Valve(volume=0,name="COLL_VALVE"))
_RBValve=(Valve(volume=0,name="RB_VALVE"))
#IR
_IR=(IR(volume=0.05,name="IR"))
#TPiece
_Tpiece=(TPiece(volume=0.05,name="T_PIECE"))
#Tubing
_tubingToIR=(Tubing(volume=0.2513,name="TUBING_TO_IR"))
_tubingToWC=(Tubing(volume=0.4712,name="TUBING_TO_WC"))
_tubingToRBC=(Tubing(volume=0.2513,name="TUBING_TO_RBC"))
#Terminus
_waste=FlowTerminus(volume=0,name="WASTE")
_blueCollect=FlowTerminus(volume=0,name="BLUE_COLLECT")
_redCollect=FlowTerminus(volume=0,name="RED_COLLECT")

_collectWaste=FlowAddress('TO_WASTE',[],[[_collectValve,"WASTE"]])
_collectBlue=FlowAddress('TO_BLUE',[],[[_collectValve,"COLLECT"],[_RBValve,"BLUE"]])
_collectRed=FlowAddress('TO_RED',[],[[_collectValve,"COLLECT"],[_RBValve,"RED"]])
###################
#Connect components

#Stock solutions
_redStock.flowInto(_stocksValve,setNameIn="RED",setNameOut="VALVE")
_blueStock.flowInto(_stocksValve,setNameIn="BLUE",setNameOut="VALVE")
_stocksValve.flowInto(_pumpline_1)
_stocksValve.switchToInlets("RED")
#Pumplines
_pumpline_1.flowInto(_Tpiece)
_pumplineSolv.flowInto(_Tpiece)
#Tubing etc to WC
_Tpiece.flowInto(_tubingToIR)
_tubingToIR.flowInto(_IR)
_IR.flowInto(_tubingToWC)
_tubingToWC.flowInto(_collectValve)
_collectValve.flowInto(_waste,setNameOut="WASTE")
_collectValve.flowInto(_tubingToRBC,setNameOut="COLLECT")
_collectValve.switchToOutlets("WASTE")
#R/B collect
_tubingToRBC.flowInto(_RBValve)
_RBValve.flowInto(_blueCollect,setNameOut="BLUE")
_RBValve.flowInto(_redCollect,setNameOut="RED")

#Create paths

_path.addPath(
    [
        _redStock,
        _blueStock,
        _stocksValve,

        _pumpline_1,
        _pumplineSolv,
        _Tpiece,

        _tubingToIR,
        _IR,

        _tubingToWC,
        _collectValve,
        _waste,

        _tubingToRBC,
        _RBValve,
        _blueCollect,
        _redCollect
    ]
)

#_path.addPath([_redStock,_blueStock,_stocksValve,_pumpline_1])
_path.selectPath()
_redStock.associatedFlowPath=_path
_blueStock.associatedFlowPath=_path
_pumplineSolv.associatedFlowPath=_path

for _x in _path.segments:
    print("*********")
    print(_x.name)
    print(_x.inletSets)
    print(_x.outletSets)
    print(_x.inlets)
    print(_x.outlets)

_currOrigin=_redStock
_currTerminus=_waste

# Flag variable to indicate whether the thread should continue running
running=True
trackingCycleComplete=True
allSlugs=Slugs()

_slugVol=1

def run_code():
    global running
    global allSlugs
    global trackingCycleComplete
    while running:
        while trackingCycleComplete:
            pass

        _slug=_stocksValve.inlets[0].dispense()
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
            print("Time: " + str(round(time.perf_counter() - _now, 0)) + " seconds, Fro h/pos: " + str(
                _slug.frontHost.name) + ", " + str(round(_slug.frontHostPos, 2)) + "/" + str(
                _slug.frontHost.volume) + " mL, tail h/pos: " + str(_slug.tailHost.name) + ", " + str(
                round(_slug.tailHostPos, 2)) + "/" + str(_slug.tailHost.volume) + " mL, fr: " + str(
                round(_slug.frontHost.flowrateOut*60, 2)) + " mL.min-1, slug vol: " + str(
                round(_vol, 2)) + " mL, vol collected: " + str(round(_slug.collectedVol, 2)) + " mL")
            if not _switched and _vol > _slugVol:
                _stocksValve.inlets[0].dispensing=False
                _switched=True
        print("************")
        print(str(time.perf_counter() - _now) + " seconds")
        print("Collected slug volumes")
        for _x in _path.collectedSlugs:
            print(_x.collectedVol)
        print("Slug took " + str(_now-_slug.reachedTerminusAt) + " seconds to reach terminus")
        print("************")

        trackingCycleComplete=True

# Create a thread for running the code
thread=threading.Thread(target=run_code)

# Start the thread
thread.start()

kwarguments={
    "path":_path,
    "setAddress":_path.setAddress,
    "addCollectWaste":_collectWaste,
    "addCollectRed":_collectRed,
    "addCollectBlue":_collectBlue,
    "currOrigin":_currOrigin,
    "currTerminus":_currTerminus,
    "None":None
}

kwarguments={};
###############################################################
#Main
while True:

    print("Awaiting go command");

    while len(_MQTTReader.currentScript) == 0:
        time.sleep(0.05)

    nodeScript=_MQTTReader.currentScript
    #nodeScript=Utils().removeComments(nodeScript)
    #Clear script
    _MQTTReader.clearScript()
    
    parser = ScriptParser(nodeScript,client)
    _procedure = parser.createProcedure(FdpDecoder())

    _currentConfigurator=_procedure.currConfiguration()
   
    #####

    _starter={'running':True,'status':"Issuing go command"}
    #_starter="Issuing go command"
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
    

    #_currentConfigurator.sendMQTT()
    itemsQueued=True
    _result=None
    _starter={'running':True,'status':"Running"}
    _starter=json.dumps(_starter)
    _started=client.publish("test/status/",_starter)

    time.sleep(2)
    while itemsQueued and _MQTTReader.runTest:
        if itemsQueued:
            if len(_currentConfigurator.commands)==0:
                print(_currentConfigurator.setMessage)
                _procedure.next()
                _currentConfigurator=_procedure.currConfiguration()
                if _currentConfigurator is None:
                    itemsQueued=False
            else:
                _result = _currentConfigurator.sendMQTT(waitForDelivery=True)
                #print(_result)            
        elif not (_procedure.currConfiguration() is None):
                itemsQueued=True
        else:
            pass
        time.sleep(0.01)

    #_starter="Procedure complete"
    if _MQTTReader.runTest:
        _starter={'running':False,'status':'Procedure complete'}
        _starter=json.dumps(_starter)
        _started=client.publish("test/status/",_starter)

# Example usage
from Core.UI.plutter import CommandHandler


def calculate_flow_rate(reaction_setup):
    flow_rate = sum(reaction_setup.values()) / len(reaction_setup)
    return flow_rate

handler = CommandHandler()
handler.register_command('calculate_flow_rate', calculate_flow_rate)
handler.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    handler.stop()
'''
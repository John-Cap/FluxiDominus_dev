
from datetime import datetime
import json
import os
import time

from pytz import utc

from Config.Data.hardcoded_tele_templates import HardcodedTeleKeys
from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.Optimization.optimization_rig import OptimizationRig
from Core.parametres.reaction_parametres import Flowrate, Temp
from OPTIMIZATION_TEMP.Plutter_TEMP.plutter import MqttService

# Create an instance of MQTTTemperatureUpdater#
updater = MqttService(broker_address="localhost")
updater.connectDb=False
# updater = MqttService(broker_address="146.64.91.174")
thread = updater.start()
time.sleep(2)

# updater.disarm()

###########################################################
#Package for MongoDB
#Host details
#host = "localhost"
host = "146.64.91.174"
port = 27017
database_name = "Pharma"
collection_name = "pharma-data"
metadata={"location": "Room 101", "type": "Demo_Data"}

#Start
#tsDb = TimeSeriesDatabaseMongo(host, port, database_name, collection_name)
#tsDb.start()
#tsDb.pause()

###########################################################

client = updater.client

fdpDecoder = updater.fdpDecoder
automation = FlowChemAutomation()

_reportSleep=5
_reportDelay=Delay(_reportSleep)

parser=None
procedure=None

#Ping database delay
mySqlPngDelay=30;
lstPngTime=time.time();
runOptimization=False
noTestDetails=True

########################################################################
#Optimizer rig
#rig=OptimizationRig(updater,host="146.64.91.174")
rig=OptimizationRig(updater,host="localhost")
rig.initRig()
while not rig.client.is_connected():
    time.sleep(2)
#Wait until both evaluator and optimizer initialized:
print('Waiting for optimizers to initialize')
while not (rig.evaluatorInit and rig.optimizerInit):
    if not rig.evaluatorInit:
        rig.pingEvaluator()
    if not rig.optimizerInit:
        rig.pingOptimizer()
    time.sleep(5)

# Define devices
device1 = "hotcoil1"
device2 = "vapourtecR4P1700"

# Define tweakable parameters
tempParam = Temp("temperature", associatedCommand="temp", ranges=[[35, 55]])
flowrateParam1 = Flowrate("flowrateA", associatedCommand="pafr", ranges=[[1, 2]])
flowrateParam2 = Flowrate("flowrateB", associatedCommand="pbfr", ranges=[[1, 2]])

# Register devices
rig.registerDevice(device1)
rig.registerDevice(device2)

# Register tweakable parameters to the devices
rig.registerTweakableParam(device1, tempParam)
rig.registerTweakableParam(device2, flowrateParam1)
rig.registerTweakableParam(device2, flowrateParam2)

for _x in rig.reactionParametres.getAllTweakables():
    print([_x.name,_x.getRanges()[0]])

########################################################################

#TODO - Smarter way to manage this:
updater.currTestlistId=None
updater.currTestrunId=None

print("WJ - Waiting for script")
updater.dataQueue.dataPoints=[] #Pasop!
updater.abort=False

# updater.databaseOperations.mongoDb.currZeroTime=None

# Main loop!
rig.optimise(objTarget=0.8)
goTime=time.time()
while True:

    scanDone=False #TODO - temp
    rig.resetEvaluator()
    time.sleep(1.5)
    
    while updater.script=="" and not rig.terminate:
        # dbConnection ping
        if updater.connectDb:
            if time.time() - lstPngTime > mySqlPngDelay:
                if updater.databaseOperations.mySqlDb.connection.is_connected():
                    lstPngTime=time.time();
                    #print('mySQL db pinged!');
                else:
                    print('mySQL db ping not answered!');
                    updater.databaseOperations.mySqlDb.connect();
                    time.sleep(0.5);
        #
        time.sleep(0.1)
    
    if rig.terminate:
        print(f"Optimisation terminated with objective score {rig.objectiveScore}! Optimisation took {(time.time() - goTime)/60} minutes.")
        exit()
        
    if updater.abort:
        print('WJ - Testrun aborted!')
        if updater.runTest:
            updater.runTest=False
        updater.abort=False
        continue
    
    try:

        parser = ScriptParser(updater.script, client)
        procedure = parser.createProcedure(updater.fdpDecoder)

        print('#######')
        print('WJ - Parsed script is: '+updater.script)
        print('#######')
        
        updater.script=""
        
        runOptimization=True

    except:
        print("Script parsing error!")
        rig.setGoSummit(False)
        rig.setGoEvaluator(False)
        runOptimization=False
        updater.script=""
        continue
    
    ###############################################################################
    #TODO - wait for coil to heat up/cool down
    start=time.time()
    temp=rig.lastRecommendedVal["temperature"]
    while not "subflow/hotcoil1/tele" in updater.lastMsgFromTopic:
        time.sleep(0.25)
    currTemp=HardcodedTeleKeys.getTeleVal(updater.lastMsgFromTopic["subflow/hotcoil1/tele"],"temp")
    updater.client.publish("subflow/hotcoil1/cmnd",json.dumps({"deviceName":"hotcoil1","inUse":True, "connDetails":{"ipCom" : {"addr": "192.168.1.213", "port": 81}}, "settings": {"command":"SET","temp":temp}}))
    #Push through cooling solvent?
    if currTemp > temp:
        print(f"Cooling hotcoil from {currTemp} deg to {temp} deg! Pushing through cooling solvent.")
        updater.client.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({'deviceName': 'vapourtecR4P1700', 'inUse': True, 'connDetails': {'ipCom': {'addr': '192.168.1.51', 'port': 43344}}, 'settings': {'command': 'SET', 'subDevice': 'PumpAFlowRate', 'value': 2}}))
        updater.client.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({'deviceName': 'vapourtecR4P1700', 'inUse': True, 'connDetails': {'ipCom': {'addr': '192.168.1.51', 'port': 43344}}, 'settings': {'command': 'SET', 'subDevice': 'PumpBFlowRate', 'value': 2}}))
        updater.client.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({'deviceName': 'vapourtecR4P1700', 'inUse': True, 'connDetails': {'ipCom': {'addr': '192.168.1.51', 'port': 43344}}, 'settings': {'command': 'SET', 'subDevice': 'valveASR', 'value': False}}))
        updater.client.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({'deviceName': 'vapourtecR4P1700', 'inUse': True, 'connDetails': {'ipCom': {'addr': '192.168.1.51', 'port': 43344}}, 'settings': {'command': 'SET', 'subDevice': 'valveBSR', 'value': False}}))
    else:
        print(f"Hotcoil heating up from {currTemp} deg to {temp} deg.")
    wait=True
    tempReportDelay=time.time()
    while wait:
        if time.time() - tempReportDelay > 15:
            tempReportDelay=time.time()
            print(f"Curr hotcoil temp: {currTemp}")
        if abs(temp - currTemp) < 3.5:
            print("Target temperature reached!")
            wait=False
        else:
            time.sleep(1)
            currTemp=HardcodedTeleKeys.getTeleVal(updater.lastMsgFromTopic["subflow/hotcoil1/tele"],"temp")
    #Adjust scan time!!!
    shift=time.time() - start
    rig.startScanAt=rig.startScanAt + shift
    rig.endScanAt=rig.endScanAt + shift
    ########################################################################################################
    
    while runOptimization and rig.optimizing:
        ##################################  
        #Recommendation phase
        
        #dbConnection ping
        if updater.connectDb:
            if time.time() - lstPngTime > mySqlPngDelay:
                if updater.databaseOperations.mySqlDb.connection.is_connected():
                    lstPngTime=time.time();
                    #print('mySQL db pinged!');
                else:
                    print('mySQL db ping not answered!');
                    updater.databaseOperations.mySqlDb.connect();
                    time.sleep(0.5);
                    
        if not procedure.currConfig is None:
            if len(procedure.currConfig.commands) == 0:
                procedure.next()
                if procedure.currConfig is None:
                    print("Procedure complete")
                    #updater.abort = True
                else:
                    print("Next procedure!")
            else:
                procedure.currConfig.sendMQTT(waitForDelivery=True)
            
        if not scanDone:
            if not rig.scanning and rig.startScanAt < time.time():
                rig.scanning=True
                print("Yield evaluation starting!")
            elif rig.scanning and rig.endScanAt < time.time():
                rig.scanning=False
                scanDone=True
                print("Yield evaluation ended!")
            
        if updater.irAvailable:
            updater.irAvailable=False
            if rig.scanning:
                rig.client.publish(
                    rig.topicEvalOut,
                    json.dumps(
                    {
                        "goEvaluator":True,
                        "scan":updater.IR
                    }
                    )
                )
            else:
                rig.client.publish(
                    rig.topicEvalOut,
                    json.dumps(
                    {
                        "goEvaluator":False,
                        "scan":updater.IR
                    }
                    )
                )
                    
        
        if updater.connectDb:
            if (_reportDelay.elapsed() and updater.logData) and not noTestDetails:
                if len(updater.dataQueue.dataPoints) != 0:
                    updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
                    updater.dataQueue.dataPoints=[]
                _reportDelay=Delay(_reportSleep)

        time.sleep(0.15)

        ##################################
        #Evaluation phase
                
    # #TODO - in own thread
    
    if updater.connectDb:
        if updater.logData and not noTestDetails:
            if len(updater.dataQueue.dataPoints) != 0:
                updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
                updater.dataQueue.dataPoints=[]
            updater.databaseOperations.setStopTime(updater.currTestrunId)

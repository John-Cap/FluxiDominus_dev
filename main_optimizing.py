
from datetime import datetime
import json
import os
import time

from pytz import utc

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.Optimization.optimization_rig import OptimizationRig
from Core.parametres.reaction_parametres import Flowrate, Temp
from OPTIMIZATION_TEMP.Plutter_TEMP.plutter import MqttService

# Create an instance of MQTTTemperatureUpdater#
updater = MqttService(broker_address="localhost")
# updater = MqttService(broker_address="146.64.91.174")
thread = updater.start()
time.sleep(2)

updater.disarm()

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
rig=OptimizationRig(updater)

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

rig.recommYielded=True

rig.start()
########################################################################

#TODO - Smarter way to manage this:
updater.currTestlistId=None
updater.currTestrunId=None

print("WJ - Waiting for script")
updater.dataQueue.dataPoints=[] #Pasop!
updater.abort=False

#And notify backend
updater.runTest=False
updater.registeredTeleDevices={}
updater.script=""
updater.databaseOperations.mongoDb.currZeroTime=None

##############################
#OPtimization specific var
SHARED_FOLDER=r'OPTIMIZATION_TEMP\SharedData'
irCntr=0

# rig.setGoSummit(True)
# rig.setGoEvaluator(True)

# Main loop!
while True:
    
    while updater.script=="":
        #dbConnection ping
        if time.time() - lstPngTime > mySqlPngDelay:
            if updater.databaseOperations.mySqlDb.connection.is_connected():
                lstPngTime=time.time();
                print('mySQL db pinged!');
            else:
                print('mySQL db ping not answered!');
                updater.databaseOperations.mySqlDb.connect();
                time.sleep(0.5);
        #
        time.sleep(0.1)

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
    
    while runOptimization and rig.optimizing:
        ##################################  
        #Recommendation phase
        
        #dbConnection ping
        if time.time() - lstPngTime > mySqlPngDelay:
            if updater.databaseOperations.mySqlDb.connection.is_connected():
                lstPngTime=time.time();
                print('mySQL db pinged!');
            else:
                print('mySQL db ping not answered!');
                updater.databaseOperations.mySqlDb.connect();
                time.sleep(0.5);
        if len(procedure.currConfig.commands) == 0:
            procedure.next()
            if procedure.currConfig is None:
                print("Procedure complete")
                updater.abort = True
            else:
                print("Next procedure!")
        else:
            procedure.currConfig.sendMQTT(waitForDelivery=True)
            
        if rig.startScanAt < time.time() and not rig.scanning:
            rig.scanning=True
            
        elif rig.endScanAt < time.time() and rig.scanning:
            rig.scanning=False
            
        if updater.irAvailable:
            updater.irAvailable=False
            if rig.scanning:
                rig.client.publish(
                    rig.topicEvalOut,
                    {
                        "goEvaluator":True,
                        "scan":updater.IR
                    }
                )
            else:
                rig.client.publish(
                    rig.topicEvalOut,
                    {
                        "goEvaluator":False,
                        "scan":updater.IR
                    }
                )
                    
            
        if (_reportDelay.elapsed() and updater.logData) and not noTestDetails:
            if len(updater.dataQueue.dataPoints) != 0:
                updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
                updater.dataQueue.dataPoints=[]
            _reportDelay=Delay(_reportSleep)

        time.sleep(0.15)

        ##################################
        #Evaluation phase
                
    # #TODO - in own thread
    # if updater.logData and not noTestDetails:
    #     if len(updater.dataQueue.dataPoints) != 0:
    #         updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
    #         updater.dataQueue.dataPoints=[]
    #     updater.databaseOperations.setStopTime(updater.currTestrunId)

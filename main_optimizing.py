
from datetime import datetime
import json
import time

from pytz import utc

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.UI.plutter import MqttService

# Create an instance of MQTTTemperatureUpdater#
updater = MqttService(broker_address="localhost")
#updater = MqttService(broker_address="146.64.91.174")
thread = updater.start()
time.sleep(2)

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
# Main loop!
while True:
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
    
    while updater.script=="" and not updater.abort:
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
        
        runOptimization=True

    except:
        print("Script parsing error!")
        runOptimization=False
        #updater.script=""
        continue
    
    while runOptimization:
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
        if len(procedure.currConfig.commands) == 0:
            procedure.next()
            if procedure.currConfig is None:
                print("Procedure complete")
                updater.abort = True
            else:
                print("Next procedure!")
        else:
            procedure.currConfig.sendMQTT(waitForDelivery=True)
            
        if (_reportDelay.elapsed() and updater.logData) and not noTestDetails:
            if len(updater.dataQueue.dataPoints) != 0:
                updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
                updater.dataQueue.dataPoints=[]
            _reportDelay=Delay(_reportSleep)

        time.sleep(0.1)
        
    #TODO - in own thread
    if updater.logData and not noTestDetails:
        if len(updater.dataQueue.dataPoints) != 0:
            updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
            updater.dataQueue.dataPoints=[]
        updater.databaseOperations.setStopTime(updater.currTestrunId)


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

temps = [60, 70, 80, 90, 95, 0.5]
sequenceComplete=False
targetIndex = 0
maxIndex = len(temps)-1
targetTemp = temps[targetIndex]

hitBracket=2 #abs distance from target temp to be considered reached

def checkTempFunc(value):
    global targetIndex, targetTemp, sequenceComplete
    if sequenceComplete:
        return True
    _b = hitBracket >= abs(value-targetTemp)
    if _b:
        print("Target temperature "+str(targetTemp)+" reached!")
        targetIndex += 1
        if targetIndex > maxIndex:
            print("All temperatures reached!")
            sequenceComplete=True
            return True
        targetTemp = temps[targetIndex]
    return _b

def pullTemp():
    return updater.getTemp()

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

################################ 1.70 - 3.00 A/B -> 11:15
#Signed in?
print("WJ - Awaiting sign-in")
updater.authenticator.mqttService=updater
updater.authenticator.user.orgId="309930"
'''
while not updater.authenticator.signedIn:
    time.sleep(0.2)
print("Signed in!")
'''
################################
#Database flags
noTestDetails=False

#Ping database delay
mySqlPngDelay=30;
lstPngTime=time.time();
# Main loop!
while True:
    #TODO - Smarter way to manage this:
    updater.currTestlistId=None
    updater.currTestrunId=None
    #Send back test not started confirmation
    updater.publish("ui/dbCmnd/ret",json.dumps({"runTest":False}))

    ##########################################################
    #Wake everything up 1
    updater.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({"deviceName":"vapourtecR4P1700","inUse":True,"connDetails":{"ipCom":{"addr":"192.168.1.51","port":43344}},"settings":{"command":"REMOTEEN"}}))
    updater.publish("subflow/flowsynmaxi2/cmnd",json.dumps({
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "connDetails": {
            "ipCom": {
            "addr": "192.168.1.201",
            "port": 80
            }
        },
        "settings": {
            "command": "REMOTEEN"
        }
    }))
    updater.publish("subflow/hotcoil1/cmnd",json.dumps({"deviceName":"hotcoil1","inUse":True,"connDetails":{"ipCom":{"addr":"192.168.1.213","port":81}},"settings":{"command":"REMOTEEN"}}))

    time.sleep(1)

    ##########################################################
    #Set setup to safe state
    updater.publish("subflow/flowsynmaxi2/cmnd",json.dumps({
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "connDetails": {
            "ipCom": {
            "addr": "192.168.1.201",
            "port": 80
            }
        },
        "settings": {
            "command": "SET",
            "subDevice": "PumpAFlowRate",
            "value": 0
        }
    }))
    updater.publish("subflow/flowsynmaxi2/cmnd",json.dumps({
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "connDetails": {
            "ipCom": {
            "addr": "192.168.1.201",
            "port": 80
            }
        },
        "settings": {
            "command": "SET",
            "subDevice": "PumpBFlowRate",
            "value": 0
        }
    }))

    updater.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({
        "deviceName": "vapourtecR4P1700",
        "inUse": True,
        "connDetails": {
            "ipCom": {
            "addr": "192.168.1.51",
            "port": 80
            }
        },
        "settings": {
            "command": "SET",
            "subDevice": "PumpAFlowRate",
            "value": 0.05
        }
    }))
    updater.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({
        "deviceName": "vapourtecR4P1700",
        "inUse": True,
        "connDetails": {
            "ipCom": {
            "addr": "192.168.1.51",
            "port": 80
            }
        },
        "settings": {
            "command": "SET",
            "subDevice": "PumpBFlowRate",
            "value": 0.05
        }
    }))
    updater.publish("subflow/hotcoil1/cmnd",json.dumps({"deviceName":"hotcoil1","inUse":True,"connDetails":{"ipCom":{"addr":"192.168.1.213","port":81}},"settings":{"command":"SET","temp":0.0}}))
    updater.publish("subflow/sf10Vapourtec1/cmnd",json.dumps({
        "deviceName": "sf10Vapourtec1",
        "inUse": True,
        "connDetails": {
            "serialCom": {
            "port": "/dev/ttyUSB0",
            "baud": 9600,
            "dataLength": 8,
            "parity": "N",
            "stopbits": 1
            }
        },
        "settings": {
            "command": "SET",
            "mode": "FLOW",
            "flowrate": 0
        }
        }))
    #Script posted?
    #
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
        print('WJ - Script parsed successfully.')
        print('#######')

    except:
        print("Script parsing error!")
        #updater.script=""
        continue
    
    #Wait for go
    print('WJ - Waiting for go command')
    while (not updater.runTest) and (not updater.abort):
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

    if updater.currTestlistId != None  and updater.currTestrunId != None:
        print('WJ - currTestlistId and currTestrunId')
        noTestDetails=False
        updater.zeroTime=datetime.now(utc) #Start experiment time
        updater.databaseOperations.mongoDb.currZeroTime=None #Start experiment time
        updater.databaseOperations.setZeroTime(updater.currTestrunId)
        print(f"WJ - Set zerotime for testrun entry {updater.currTestrunId}!")
    else:
        noTestDetails=True
        print('WJ - No test details!')
        
    print('WJ - Here we go!')

    ##########################################################
    #Wake everything up 2
    updater.publish("subflow/vapourtecR4P1700/cmnd",json.dumps({"deviceName":"vapourtecR4P1700","inUse":True,"connDetails":{"ipCom":{"addr":"192.168.1.51","port":43344}},"settings":{"command":"REMOTEEN"}}))
    updater.publish("subflow/flowsynmaxi2/cmnd",json.dumps({
        "deviceName": "flowsynmaxi2",
        "inUse": True,
        "connDetails": {
            "ipCom": {
            "addr": "192.168.1.201",
            "port": 80
            }
        },
        "settings": {
            "command": "REMOTEEN"
        }
    }))
    updater.publish("subflow/hotcoil1/cmnd",json.dumps({"deviceName":"hotcoil1","inUse":True,"connDetails":{"ipCom":{"addr":"192.168.1.213","port":81}},"settings":{"command":"REMOTEEN"}}))
    updater.publish("subflow/reactIR702L1/cmnd",json.dumps({"deviceName":"reactIR702L1","inUse":True, "connDetails":{"ipCom" : {"addr": "192.168.1.50", "port": 62552}},"settings": {"command":"REMOTEEN"}}))
    time.sleep(1)

    #
    #Inform UI of test start and provide zerotime
    #
    _zt=updater.databaseOperations.mongoDb.currZeroTime
    updater.publish("ui/dbCmnd/ret",json.dumps(
        {
            "runTest":True,
            "datetime":_zt
        })
    )
    #TODO - Hardcoded streaming example
    if not noTestDetails:
        _thisRef=updater.databaseOperations.mySqlDb.fetchColumnValById(tableName='testruns',columnName='labNotebookBaseRef',id=updater.currTestrunId)
        _thisTstrn=updater.databaseOperations.mySqlDb.fetchColumnValById(tableName='testruns',columnName='runNr',id=updater.currTestrunId)
        updater.publish(
            topic="ui/dbCmnd/in",payload=json.dumps({
                "instructions":{
                    "function":"handleStreamRequest",
                    "params":{
                        "id":"hotcoil1_temp",
                        "labNotebookBaseRef":_thisRef,
                        "runNr":_thisTstrn,
                        "timeWindow":10000,
                        "deviceName":"hotcoil1",
                        "setting":"temp"
                    }
                }
            }))
        updater.publish(
            topic="ui/dbCmnd/in",payload=json.dumps({
                "instructions":{
                    "function":"handleStreamRequest",
                    "params":{
                        "id":"flowsynmaxi2_pressA",
                        "labNotebookBaseRef":_thisRef,
                        "runNr":_thisTstrn,
                        "timeWindow":10000,
                        "deviceName":"flowsynmaxi2",
                        "setting":"pressA"
                    }
                }
            }))
        updater.publish(
            topic="ui/dbCmnd/in",payload=json.dumps({
                "instructions":{
                    "function":"handleStreamRequest",
                    "params":{
                        "id":"flowsynmaxi2_pressB",
                        "labNotebookBaseRef":_thisRef,
                        "runNr":_thisTstrn,
                        "timeWindow":10000,
                        "deviceName":"flowsynmaxi2",
                        "setting":"pressB"
                    }
                }
            }))
        updater.publish(
            topic="ui/dbCmnd/in",payload=json.dumps({
                "instructions":{
                    "function":"handleStreamRequest",
                    "params":{
                        "id":"flowsynmaxi2_pressSystem",
                        "labNotebookBaseRef":_thisRef,
                        "runNr":_thisTstrn,
                        "timeWindow":10000,
                        "deviceName":"flowsynmaxi2",
                        "setting":"pressSys"
                    }
                }
        }))
        updater.publish(
            topic="ui/dbCmnd/in",payload=json.dumps({
                "instructions":{
                    "function":"handleStreamRequest",
                    "params":{
                        "id":"vapourtecR4P1700_pressA",
                        "labNotebookBaseRef":_thisRef,
                        "runNr":_thisTstrn,
                        "timeWindow":10000,
                        "deviceName":"vapourtecR4P1700",
                        "setting":"pressA"
                    }
                }
        }))
        updater.publish(
            topic="ui/dbCmnd/in",payload=json.dumps({
                "instructions":{
                    "function":"handleStreamRequest",
                    "params":{
                        "id":"vapourtecR4P1700_pressB",
                        "labNotebookBaseRef":_thisRef,
                        "runNr":_thisTstrn,
                        "timeWindow":10000,
                        "deviceName":"vapourtecR4P1700",
                        "setting":"pressB"
                    }
                }
        }))
        updater.publish(
            topic="ui/dbCmnd/in",payload=json.dumps({
                "instructions":{
                    "function":"handleStreamRequest",
                    "params":{
                        "id":"vapourtecR4P1700_pressSystem",
                        "labNotebookBaseRef":_thisRef,
                        "runNr":_thisTstrn,
                        "timeWindow":10000,
                        "deviceName":"vapourtecR4P1700",
                        "setting":"pressSys"
                    }
                }
        }))
    
    while (not updater.abort):
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

        time.sleep(0.15)
        
    #TODO - in own thread
    if updater.logData and not noTestDetails:
        if len(updater.dataQueue.dataPoints) != 0:
            updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
            updater.dataQueue.dataPoints=[]
        updater.databaseOperations.setStopTime(updater.currTestrunId)

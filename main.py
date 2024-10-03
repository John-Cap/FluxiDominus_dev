
from datetime import datetime
import time

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
from Core.UI.plutter import MqttService

# Create an instance of MQTTTemperatureUpdater
#updater = MqttService(broker_address="localhost")
updater = MqttService(broker_address="146.64.91.174")
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

decoder_kwargs = {
    "conditionFunc": checkTempFunc,
    "conditionParam": pullTemp
}

fdpDecoder = FdpDecoder(currKwargs=decoder_kwargs)
automation = FlowChemAutomation()

_reportSleep=5
_reportDelay=Delay(_reportSleep)

parser=None
procedure=None

################################
#Signed in?
print("WJ - Awaiting sign-in")
updater.authenticator.mqttService=updater
updater.authenticator.user.orgId="50403"
'''
while not updater.authenticator.signedIn:
    time.sleep(0.2)
print("Signed in!")
'''
################################
#Database flags
noTestDetails=False
# Main loop!
while True:
    #Script posted?
    
    print("WJ - Waiting for script")
    updater.dataQueue.dataPoints=[] #Pasop!
    updater.abort=False
    updater.runTest=False
    updater.registeredTeleDevices={}
    
    while updater.script=="":
        time.sleep(0.1)

    try:

        parser = ScriptParser(updater.script, client)
        procedure = parser.createProcedure(fdpDecoder)

        print('#######')
        print('WJ - Parsed script is: '+updater.script)
        print('#######')

    except:
        print("Script parsing error!")
        updater.script=""
        continue
        
    updater.script=""
    
    #Wait for go
    print('WJ - Waiting for go command')
    while (not updater.runTest) and (not updater.abort):
        time.sleep(0.1)

    if updater.abort:
        print('WJ - Testrun aborted!')
        if updater.runTest:
            updater.runTest=False
            updater.abort=False
        continue
    
    if updater.currTestlistId and updater.currTestrunId:
        noTestDetails=False
        updater.zeroTime=datetime.now() #Start experiment time
        updater.databaseOperations.mongoDb.currZeroTime=updater.zeroTime #Start experiment time
        updater.databaseOperations.setZeroTime(updater.currTestrunId)
        print(f"WJ - Set zerotime for testrun entry {updater.currTestrunId}!")
    else:
        noTestDetails=True
        
    print('WJ - Here we go!')
    
    while (not updater.abort):

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

        time.sleep(0.05)
                        
    #TODO - in own thread
    if updater.abort and not noTestDetails:
        if len(updater.dataQueue.dataPoints) != 0:
            updater.databaseOperations.mongoDb.insertDataPoints(updater.dataQueue.toDict())
            updater.dataQueue.dataPoints=[]
        _reportDelay=Delay(_reportSleep)
    if (_reportDelay.elapsed() and updater.logData) and not noTestDetails:
        updater.databaseOperations.setStopTime(updater.currTestrunId)
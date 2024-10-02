
from datetime import datetime
import time

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
from Core.UI.plutter import MqttService

# Create an instance of MQTTTemperatureUpdater
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
doIt=True

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

# Main loop!
while True:
    #Script posted?
    
    print("WJ - Waiting for script")
    updater.dataQueue.dataPoints=[] #Pasop!
    updater.abort=False
    
    while updater.script=="":
        time.sleep(0.5)

    try:

        parser = ScriptParser(updater.script, client)
        procedure = parser.createProcedure(fdpDecoder)

        print('#######')
        print('WJ - Parsed script is: '+updater.script)
        print('#######')

    except:
        print("Script parsing error!")
        updater.script=""
        updater.abort=True
        
    updater.script=""
    updater.logData=True #TODO - moet stel via UI
    
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
    
    updater.zeroTime=datetime.now() #Start experiment time
    updater.databaseOperations.mongoDb.currZeroTime=updater.zeroTime #Start experiment time
    updater.databaseOperations.setZeroTime(updater.currTestrunId)
    
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

        if _reportDelay.elapsed() and updater.logData:
            if len(updater.dataQueue.dataPoints) != 0:
                for _x in updater.dataQueue.toDict(): #TODO - sit liewers almal op 'n slag in
                    updater.databaseOperations.mongoDb.insertDataPoint(_x)
                    
                updater.dataQueue=[]
            _reportDelay=Delay(_reportSleep)
                        
        #TODO - might be better in own thread            
        if _reportDelay.elapsed() or updater.abort:
            if len(updater.dataQueue.dataPoints) != 0:
                for _x in updater.dataQueue.toDict(): #TODO - sit liewers almal op 'n slag in
                    updater.databaseOperations.mongoDb.insertDataPoint(_x)
                    
                updater.dataQueue.dataPoints=[]
            _reportDelay=Delay(_reportSleep)
            
        time.sleep(0.05)
    updater.databaseOperations.setStopTime(updater.currTestrunId)
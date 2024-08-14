
import time

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
from Core.Data.data import DataPointFDE
from Core.Data.database import TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService
from Core.Utils.Utils import DataLogger, TimestampGenerator

# Create an instance of MQTTTemperatureUpdater
updater = MqttService(broker_address="localhost")
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
tsDb = TimeSeriesDatabaseMongo(host, port, database_name, collection_name,[])
tsDb.start()
tsDb.pause()

###########################################################

client = updater.client

decoder_kwargs = {
    "conditionFunc": checkTempFunc,
    "conditionParam": pullTemp
}

fdpDecoder = FdpDecoder(currKwargs=decoder_kwargs)
automation = FlowChemAutomation()

doIt = True
_reportSleep=5
_reportDelay=Delay(_reportSleep)
#logger = DataLogger('time_degrees_IR_1.txt')
#logger.logData(-1,[-1])

parser=None
procedure=None
doIt=True

################################
#Signed in?
while updater.user == "" or not updater.signedIn:
    time.sleep(0.2)
################################

# Main loop!
while True:
    #Script posted?
    
    print("WJ - Waiting for script")
    updater.dataQueue=[]
    tsDb.purgeAndPause()
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
        doIt=False
        #exit()

    updater.script=""
    updater.logData=True
    tsDb.start()
    while doIt:
        if _reportDelay.elapsed():
            #print(updater.dataQueue)
            _reportDelay=Delay(_reportSleep)
            if len(updater.dataQueue)!=0:
                tsDb.dataPoints=tsDb.dataPoints+updater.dataQueue
                updater.dataQueue=[]
            #logger.logData(updater.getTemp(),updater.getIR())
        if len(procedure.currConfig.commands) == 0:
            procedure.next()
            if procedure.currConfig is None:
                print("Procedure complete")
                doIt = False
            else:
                print("Next procedure!")
        else:
            procedure.currConfig.sendMQTT(waitForDelivery=True)
        time.sleep(0.2)
    doIt=True
thread.join()
exit()
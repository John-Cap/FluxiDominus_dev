
import time

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
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

# Main loop!
while True:
    #Script posted?
    
    print("WJ - Waiting for script")
    while updater.script=="":
        time.sleep(0.5)
    try:
        '''
        print('#######')
        print('WJ - Parsed script is: '+updater.script)
        print('#######')
        '''
        parser = ScriptParser(updater.script, client)
        procedure = parser.createProcedure(fdpDecoder)
        
    except:
        print("Script parsing error!")
        exit()
        
    updater.script=""
    doIt=True
    while doIt:
        if _reportDelay.elapsed():
            _reportDelay=Delay(_reportSleep)
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
thread.join()
exit()
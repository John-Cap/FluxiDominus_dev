from datetime import datetime
import time
import paho.mqtt.client as mqtt

from Core.Communication.ParseFluxidominusProcedure import FdpDecoder, ScriptParser
from Core.Control.Commands import Delay
from Core.Control.ScriptGenerator_tempMethod import FlowChemAutomation
from Core.Utils.Utils import DataLogger, TimestampGenerator
from Core.Communication.MqttDataLogger import MqttDataLogger

# Create an instance of MQTTTemperatureUpdater
updater = MqttDataLogger()
thread = updater.start()
time.sleep(2)

temps = [60, 70, 80, 90, 95, 0.5]
sequenceComplete=False
targetIndex = 0
maxIndex = len(temps)-1
targetTemp = temps[targetIndex]

hitBracket=2 #abs distance from target temp to be considered reached

def checkTempFunc(value):
    #print(value)
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

# Example script, parser and decoder setup
#
#{'deviceName': 'hotcoil1', 'command': 'SET', 'temperatureSet': 25}

# Set up MQTT client
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()



# Data logger


# Create script parser and decoder
# Assuming ScriptParser and FdpDecoder are defined elsewhere

decoder_kwargs = {
    "conditionFunc": checkTempFunc,
    "conditionParam": pullTemp
}

fdpDecoder = FdpDecoder(currKwargs=decoder_kwargs)
automation = FlowChemAutomation()

doIt = True
_reportSleep=5
_reportDelay=Delay(_reportSleep)
logger = DataLogger('time_degrees_IR_1.txt')
logger.logData(-1,[-1])

parser=None
procedure=None

# Main loop!
while True:
    #Script posted?
    
    print("WJ - Waiting for script")
    while (not "test/settings" in updater.lastMsgFromTopic) or updater.script=="":
        time.sleep(0.5)
        
    try:
        print('WJ - Received script: '+updater.script)
        parser = ScriptParser(updater.script, client)
        procedure = parser.createProcedure(fdpDecoder)
        updater.script=""
        print("WJ - Script received!")
    except:
        print("Script parsing error!")
        exit()
    
    doIt=True
    while doIt:
        if _reportDelay.elapsed():
            _reportDelay=Delay(_reportSleep)
            logger.logData(updater.getTemp(),updater.getIR())
        if len(procedure.currConfig.commands) == 0:
            procedure.next()
            if procedure.currConfig is None:
                print("Procedure complete")
                doIt = False
            else:
                print("Next procedure!")
        else:
            procedure.currConfig.sendMQTT(waitForDelivery=True)
        time.sleep(0.1)
thread.join()
exit()
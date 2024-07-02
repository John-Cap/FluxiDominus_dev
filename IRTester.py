import copy
import time
import numpy as np
from Core.Communication.Network import MQTTReader
from Core.Control.Commands import BaselineDetected, BlueDetected, ColourChanged, IRCategorizer, IrSwitch, RedDetected
from Core.Control.IR import IRScanner

# Script listener

_MQTTReader=MQTTReader()
_MQTTReader.readMQTTLoop()
_IRScanner=IRScanner()
_IRScanner.parseIrData()
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
_currentScan=[]

while True:
    _currentScan=copy.deepcopy(_MQTTReader.currentIrScan)
    if len(_currentScan)!=0:
        
        del _currentScan[750:]
        del _currentScan[410:540]

        colour=_IrCategorizer.categorize(np.array(_currentScan))
        if _IrSwitch.statusChanged(colour):
            print("New colour: " + colour)

    time.sleep(1)
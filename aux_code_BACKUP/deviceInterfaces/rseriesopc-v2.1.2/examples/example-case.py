# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 12:00:32 2021

@author: lechuzin
"""

import rseriesopc as rs
import time

client = rs.RSeriesClient("opc.tcp://localhost:43344")

try:
    "Connect the client with the server"
    isConnected = client.connect()

    "Get the manual control node in RSeries node"
    manualControl = client.getRSeries().getManualControl()

    "Get the r2s"
    r2Primary = manualControl.getR2Primary()
    r2Secondary = manualControl.getR2Secondary()

    "Setting r2 primary"
    "Pumps"
    "Setting the flow rates"
    priPump = r2Primary.getPumps()
    priPump["A"].setFlowRate(1000)
    priPump["B"].setFlowRate(2000)

    "Valves"
    "Valve IL = True:  Inject -> Load"
    "         = False: Load -> Inject"
    "Valve SR = True:  Reagent -> Solvent"
    "         = False: Solvent -> Reagent"

    valveAIL = priPump.get("A").getValveIL()  # another valid syntax for dict()'s
    valveAIL.setValveState(False)
    valveASR = priPump["A"].getValveSR()
    if valveASR.getValveState():
        valveASR.setValveState(False)

    valveBIL = priPump["B"].getValveIL()  # another valid syntax for dict()'s
    if not valveBIL.getValveState():
        valveBIL.setValveState(True)
    valveBSR = priPump["B"].getValveSR()  # another valid syntax for dict()'s
    valveBSR.setValveState(True)

    "Setting r2 secondary"
    "Pumps"
    secPump = r2Secondary.getPumps()
    for pump in secPump.values():
        pump.setFlowRate(150)

    "Valves"
    valveCIL = secPump["A"].getValveIL()
    valveCSR = secPump["A"].getValveSR()
    valveDIL = secPump["B"].getValveIL()
    valveDSR = secPump["B"].getValveSR()

    valveCIL.setValveState(False)
    valveCSR.setValveState(True)
    valveDIL.setValveState(True)
    valveDSR.setValveState(False)

    "start system"
    manualControl.startManualControl()

    time.sleep(20)
    manualControl.stopAll()

    "Turning pumps off"
    for pump in priPump.values():
        pump.setFlowRate(0)

    for pump in secPump.values():
        pump.setFlowRate(0)

    "Settings for reactors"
    r4i = manualControl.getR4I()

    "Temperatures"
    reactor = r4i.getReactors()
    r1 = reactor.get("1")
    r2 = reactor.get("2")

    temp = r1.getTemperature()
    temp.setTemperature(15)
    temp = r2.getTemperature()
    temp.setTemperature(45)

    manualControl.startManualControl()

    time.sleep(8)

    "Change settings"
    r2.getTemperature().setTemperature(20)
    r1.getTemperature().setTemperature(80)

    valveASR.setValveState(True)
    priPump["A"].setFlowRate(1000)

    time.sleep(10)

    manualControl.stopAll()
    priPump["A"].setFlowRate(0)

    "Return to beginning"
    r2.getTemperature().setTemperature(25)
    r1.getTemperature().setTemperature(25)

    valveAIL.setValveState(False)
    valveASR.setValveState(False)
    valveBIL.setValveState(False)
    valveBSR.setValveState(False)

    valveCIL.setValveState(False)
    valveCSR.setValveState(False)
    valveDIL.setValveState(False)
    valveDSR.setValveState(False)

finally:
    if isConnected:
        client.disconnect()

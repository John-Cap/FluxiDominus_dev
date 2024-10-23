# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 19:19:14 2021

This is a demonstration about the manual control in python
through OPC UA.

@author: Edwin Barragan for Emtech S.A.
"""

import rseriesopc as rs
import time


class Valve:
    def __init__(self, stateSetter) -> None:
        self.setter = stateSetter

    def setValveState(self, state):
        self.setter(state)


def square(valve: Valve, period: int, clk: int):
    """
    This function opens and close a given valve in a period of time when it is
    called repetitvle in a loop.

    Parameters
    ----------
    valve : rseriesopc.ValveType
        This is the valve which state will be set.
    period : integer
        It is a period of time while the valve will be closed or opened.
    clk : integer
        It is the seconds of a running clock.

    Returns
    -------
    None.

    """
    valve.setValveState(int(clk / period) % 2 == 0)


def sawtooth(pump, amp, period, clk):
    """
    This function take a pump and sets its flowrate.
    While the clock clk runs, and this function is called, the flow rate of the
    pump will be growing as a ramp to reach the maximum amplitud in a desired
    period of time.
    Then the flow rate will be set to 0 and start to growing up again.

    Parameters
    ----------
    pump : rseriesopc.PumpType
        This is the pump that its flow rate will be set.
    amp : intenger
        This is the maximu amplitud that the flow rate will reach.
    period : integer
        This is the time in seconds between the flow rate is 0 and this reach
        the maximum amplitud.
    clk : integer
        This is the running clock. Its units are in seconds.

    Returns
    -------
    None.

    """
    mod = clk % period
    amp = int(amp * mod / period)
    pump.setFlowRate(amp)


"Client instantiation. It needs the server's URL"
client = rs.RSeriesClient("opc.tcp://localhost:43344")

try:
    "Setup"
    "Connecting to the server"
    isConnected = client.connect()

    "Getting the objects of interest in server."
    manualControl = client.getRSeries().getManualControl()

    "Getting valveWC"
    valveWC = Valve(manualControl.setWCValveState)
    "R2 Primary"
    primary = manualControl.getModule(0)
    "Getting pump A"
    pumpA = primary.getPumps().get("A")
    "Getting pumpA vavles"
    valveASR = Valve(pumpA.setSRValveState)
    valveAIL = Valve(pumpA.setILValveState)
    "Getting pump B"
    pumpB = primary.getPumpB()
    "getting pumpB valves"
    valveBSR = Valve(pumpB.setSRValveState)
    valveBIL = Valve(pumpB.setILValveState)

    "R2 Secondary"
    secondary = manualControl.getModule(1)

    "Getting pump A"
    pumpC = secondary.getPumpA()
    "Getting pumpA vavles"
    valveCSR = Valve(pumpC.setSRValveState)
    valveCIL = Valve(pumpC.setILValveState)
    "Getting pump B"
    pumpD = secondary.getPumps()["B"]
    "getting pumpB valves"
    valveDSR = Valve(pumpD.setSRValveState)
    valveDIL = Valve(pumpD.setILValveState)

    "Getting a R4 Reactor"
    r4 = manualControl.getR4I()
    reactor = r4.getReactors()["1"]

    "Main loop"
    manualControl.stopAll()
    manualControl.startManualControl()
    minutes = 0
    seconds = 0
    temp = 20.1
    tempPer = 0
    start_time = time.time()
    while minutes < 5:
        print(seconds)
        # pumpA.setFlowRate(5000)
        sawtooth(pumpA, 1000, 40, seconds)
        sawtooth(pumpB, 1500, 60, seconds)
        sawtooth(pumpC, 1200, 50, seconds)
        sawtooth(pumpD, 8000, 30, seconds)

        # reactor.getTemperature().setTemperature(50)
        if tempPer >= 20:
            tempPer = 0
            temp = temp + 15
            reactor.setTemperature(temp)

        # valveWC.setValveState(True);
        square(valveASR, 15, seconds)
        square(valveBSR, 20, seconds)
        square(valveCSR, 25, seconds)
        square(valveDSR, 30, seconds)

        square(valveAIL, 40, seconds)
        square(valveBIL, 45, seconds)
        square(valveCIL, 50, seconds)
        square(valveDIL, 35, seconds)

        square(valveWC, 35, seconds)

        time.sleep(1)
        cur_time = time.time()
        minutes, seconds = divmod(cur_time - start_time, 60)
        seconds = int(seconds + minutes * 60)
        tempPer = tempPer + 1


finally:
    "Turn the pumps off"
    for pump in primary.getPumps().values():
        pump.setFlowRate(0)
    for pump in secondary.getPumps().values():
        pump.setFlowRate(0)
    "Close all valves"
    valveAIL.setValveState(False)
    valveASR.setValveState(False)
    valveBIL.setValveState(False)
    valveBSR.setValveState(False)
    valveCIL.setValveState(False)
    valveCSR.setValveState(False)
    valveDIL.setValveState(False)
    valveDSR.setValveState(False)
    valveWC.setValveState(False)

    "Reset reactor temperature"
    reactor.setTemperature(20.1)
    "stop manual control"
    manualControl.stopAll()
    "disconnect the server"
    if isConnected:
        client.disconnect()

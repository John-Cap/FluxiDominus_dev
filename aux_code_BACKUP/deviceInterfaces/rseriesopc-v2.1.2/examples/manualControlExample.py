# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 12:34:10 2021

Example 1: Manual Control

This example is a python script of an automated reaction but using manual 
control. This performs the following tasks: 
- Running a reactor and ramping flow rate from rampInitFlowrate value to 
    rampStopFlowrate over a time given by rampTime.
- Constant temperature at tempSetpoint. This includes pre-heating flow rate 
    and time period
- Polling for target temperature and final clean/cooling as manual steps.

For running this script all the modules has to be set as R2 types
@author: Edwin Barragán for Emtech S.A.
"""

import rseriesopc as rs
import time

tempSetpoint = 60  # in degrees
coolingStep = 5  # in degrees
coolSetpoint = 35  # in degrees

coolStepTime = 30  # in seconds
rampTime = 120  # in seconds

heatingFlowrate = 500  # in ul/min
rampStopCondition = 10000  # in ul/min
rampInitFlowrate = 1000  # in ul/min
coolingFlowrate = 500  # in ul/min


class TempSubsHandler:
    def datachange_notification(self, node, val, data):
        print("The temperature of the reactor is ", val, " degrees")


def rampFlowRate(pump, fromValue, toValue, period, clk):
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
    fromValue : intenger
        This is the offset flow rate for the ramp.
    toValue : integer
        This is the final flow rate for the ramp. This value will be get at
        the end of the period
    period : integer
        This is the time in seconds between the flow rate goes fromValue to
        get toValue.
    clk : integer
        This is the running clock. Its units are in seconds.

    Returns
    -------
    None.

    """
    amp = int(fromValue + (toValue * clk / period))
    pump.setFlowRate(amp)


client = rs.RSeriesClient("opc.tcp://localhost:43344")

try:
    "Connection and Getting address space"
    conState = client.connect()
    rseries = client.getRSeries()
    manualControl = rseries.getManualControl()
    reactor = manualControl.getR4I().getReactors()["3"]
    pump = manualControl.getModule(0).getPumpA()

    # temperature = reactor.getTemperature()

    "Setup the initial values"
    "turn off every pump"
    for module in manualControl.getAllModules():
        for p in module.getPumps().values():
            p.setFlowRate(0)

    "set the desired pump setpoint"
    pump.setFlowRate(1000)
    reactor.setTemperature(20)

    "node to suscribe the temperature"
    tempNode = reactor.getTemperatureNode()

    "subscribe the temperature variable"
    handler = TempSubsHandler()
    subscriptionInterval = 1000  # in millisec
    subs = client.create_subscription(subscriptionInterval, handler)
    handle = subs.subscribe_data_change(tempNode)

    "set a timer for changing the flowrate every 2 minutes"

    "starting manual control"
    manualControl.startManualControl()

    "wait for flowrate reach the stop condition"
    minutes = 0
    seconds = 0
    start_time = time.time()

    "pre heating loop"
    pump.setFlowRate(heatingFlowrate)
    reactor.setTemperature(tempSetpoint)
    while reactor.getTemperature() < tempSetpoint:
        time.sleep(1)
        cur_time = time.time()
        minutes, seconds = divmod(cur_time - start_time, 60)
        seconds = int(seconds + minutes * 60)
        pass

    "main loop"
    print("Ramping flow rate")
    print("The loop will be when flow rate reachs ", rampStopCondition / 1000, "ml/min")
    minutes = 0
    seconds = 0
    start_time = time.time()
    while pump.getFlowRate() < rampStopCondition:
        rampFlowRate(pump, rampInitFlowrate, rampStopCondition, rampTime, seconds)
        time.sleep(1)
        cur_time = time.time()
        minutes, seconds = divmod(cur_time - start_time, 60)
        seconds = int(seconds + minutes * 60)

    "cleaning and cooling"
    actualTemp = reactor.getTemperature()
    start_time = time.time()
    seconds = 0
    while actualTemp > coolSetpoint:
        pump.setFlowRate(coolingFlowrate)
        if seconds >= coolStepTime:
            newTemp = actualTemp - coolingStep
            reactor.setTemperature(newTemp)
            start_time = time.time()
        time.sleep(1)
        cur_time = time.time()
        minutes, seconds = divmod(cur_time - start_time, 60)
        seconds = int(seconds + minutes * 60)
        actualTemp = reactor.getTemperature()

finally:
    "stopping manual control"
    manualControl.stopAll()
    "turn off pump and reactor"
    pump.setFlowRate(0)
    reactor.setTemperature(25)

    if conState:
        client.disconnect()

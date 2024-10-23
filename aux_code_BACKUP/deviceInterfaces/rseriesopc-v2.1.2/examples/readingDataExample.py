# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 18:39:52 2021

Example 2: Reading data from sensors

This example shows how to subscribe a variable and how to poll variables.

For subscribing a variable, a handler class has to be declared. This class must
have a function called datachange_notification.
Then, the variable change could be subscribed in the way shown below.

To set and poll variables, just use the getters and setters provided in the
API.

@author: Edwin Barragán for Emtech S.A.
"""

import rseriesopc as rs
import time

client = rs.RSeriesClient("opc.tcp://localhost:43344")


class SubscriptionHadlerExample:
    def datachange_notification(self, node, value, data):
        print("Value of the node subscribed is: ", value)


class PressuresHandler:
    def datachange_notification(self, node, value, data):
        print("The pressures has changed. The new pressure are:")
        print("System pressure --> ", value[0])
        print("Pump A pressure --> ", value[1])
        print("Pump B pressure --> ", value[2])


try:
    "setup"
    conn = client.connect()

    manualControl = client.getRSeries().getManualControl()
    reactor4 = manualControl.getR4I().getReactors().get("4")
    r2prim = manualControl.getModule(0)

    "Monitoring Variables"
    "subscribe the pressures variable to monitoring"
    pressuresInfo = r2prim.getPumpsPressures()
    pumpsPressures = r2prim.getPumpsPressuresNode()

    handler = PressuresHandler()
    subs = client.create_subscription(1000, handler)
    handle = subs.subscribe_data_change(pumpsPressures)

    "Setting and polling Parameters"
    tempObject = reactor4.getTemperature()
    print(tempObject)
    reactor4.setTemperature(60)
    while reactor4.getTemperature() < 60:
        time.sleep(1)

    reactor4.setTemperature(30)
    while reactor4.getTemperature() > 30:
        time.sleep(1)

finally:
    "unsubscribe the monitored variable"
    subs.unsubscribe(handle)
    if conn:
        client.disconnect()

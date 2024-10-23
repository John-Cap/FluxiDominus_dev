# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 09:20:55 2021

@brief This is a demonstration about the Reaction Manager methods walk-through.

@details Before run this script, the RSeries Controller has to be running and 
at least one reaction needs to be added to the Reaction List. 
(Experiment -> Edit Reactions). Also, the name of the reaction to demo
must be given on reactionName parameter

In addition, the OPC Server feature has to be present in the R-Series 
Controller.

@author: Edwin Barragán
"""

import rseriesopc as rs
from rseriesopc import Reaction

reactionName = "reaction0"


class SubscriptionHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change", node, val)

    def event_notification(self, event):
        print("Python: New event", event)


class ExperimentStateHandler(SubscriptionHandler):
    oldVal = 0
    waitForReactionEnd = True

    def datachange_notification(self, node, val, data):
        print("ExperimentState = ", val)
        if self.oldVal >= 13 and val == 3:
            self.waitForReactionEnd = False
        self.oldVal = val

    pass


client = rs.RSeriesClient("opc.tcp://localhost:43344")

try:
    "Setting up"
    "Connect the client"
    isConnected = client.connect()
    "Get the Reaction Manager OPC Node address"
    rseries = client.getRSeries()
    experiment = rseries.getExperiment()
    reactionManager = experiment.getReactionManager()
    "Get a shortcut for the stopAll method"
    stop = rseries.getManualControl().stopAll

    "Work with Reaction Manager methods:"

    "Getting the current Reaction List Parameters"
    reactionParameters = reactionManager.getReactionParameters()

    "Reaction Parameters is a String in a JSON format"
    "JSON could be easily converted to dictionary"
    import json

    rj = json.loads(reactionParameters)
    "reactionParameters has the fields delimiters and the decimal point delimiter."
    "we will be used this parameter for CSV strings coding and decoding."
    stringDelimiter = rj["CSVStringSeparator"]
    decimalDelimiter = rj["CSVDecimalPoint"]

    "Getting the current Reaction List"
    reactionList = reactionManager.getReactionList()

    "Reaction List is a String in a CSV format"
    "reactionList could be converted to a list"
    import csv

    "rows is a list which each element is a row of the reaction list."
    rows = reactionList.split("\n")
    "discard the last one because it is empty"
    rows.pop()

    "parsing the csv"
    rl = list(csv.reader(rows, delimiter=stringDelimiter))
    "changing the decimal point delimiter."
    rl = [[sel.replace(decimalDelimiter, ".") for sel in el] for el in rl]

    "Extract the reactions of reactionList"
    "reaction will be a reaction list"
    reaction = list()
    for data in rl[1:]:
        r = Reaction()
        r.load(data)
        reaction.append(r)

    "Expand some attribute of the reactions"
    newReactions = reaction[0].flowrateStepper(
        pumpIndex="B", fromValue=1.8, toValue=5, step=0.3
    )

    "Add new reactions after the reaction[0]"
    newReactions.reverse()
    for r in newReactions:
        reaction.insert(1, r)

    newReactions = reaction[-1].tempStepper(1, 5, 80, 15)
    reaction.extend(newReactions)

    "RUN1: send a reactionList to RSeries Controller:"
    "Convert the reaction table into a CSV String"
    newReactionList = ""
    for r in reaction:
        newReactionList += r.makeCSVRow(stringDelimiter, decimalDelimiter)
        newReactionList += "\n"

    "Add the header"
    newReactionList = rows[0] + "\n" + newReactionList
    "Send the ReactionList to the RSeries Controller"
    reactionManager.loadReactionList(newReactionList)

    print(" -- New reactions added! --")
    print(" -- Check at the controller interface --")
    input("Press ENTER to continue...")
    "END RUN1"

    # "RUN2: send reactions one by one"
    # 'Another way to load reactions to list'
    # reactionManager.resetReactionList()
    # print (" -- Reactions erased --")
    # print (" -- Check at the controller interface --")
    # input ("Press ENTER to continue...")

    # for r in reaction:
    #     if r.name == 'r2':
    #         reactionManager.addReationToList(r.makeCSVRow(stringDelimiter,
    #                                                       decimalDelimiter))
    # print(" -- Only reactions called 'r2' was added --")
    # print (" -- Check at the controller interface --")
    # input ("Press ENTER to continue...")
    # "END RUN2"

    # reactionManager.addReationToList(react1)
    # reactionManager.addReationToList(react2)
    # reactionManager.addReationToList(react3)

    idx = 0
    for r in reaction:
        if r.name == reactionName:
            if idx % 2:
                reactionManager.enableReaction(idx)
            else:
                reactionManager.disableReaction(idx)
            idx += 1

    print(" -- Reactions in odd position are enabled --")
    print(" -- Check the controller interface --")
    input("Press ENTER to continue...")

    # TODO: wait for reaction ends
    # 'Suscribe the ExperimentStatus variable for monitoring reactions execution'
    # experimentState = rseries.getNotification().getExperimentState()
    # handler = ExperimentStateHandler()
    # subscription = client.create_subscription(500, handler)
    # handle = subscription.subscribe_data_change(experimentState)

    # reactionManager.startReaction()

    # while handler.waitForReactionEnd:
    #     pass

    # subscription.unsubscribe(handle)

    print(" -- Experiment was started --")
    print(" -- Check the controller interface --")
    input("Press ENTER to stop the experiment")

    reactionManager.stopReaction()

    input("Press ENTER to continue...")

    rseries.getManualControl().stopAll()

finally:
    "Restore the old Reaction List"
    if reactionList:
        reactionManager.resetReactionList()
        reactionManager.loadReactionList(reactionList)

    if isConnected:
        client.disconnect()

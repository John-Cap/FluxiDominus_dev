# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 12:51:36 2021

Example 4b: Modifying Reaction

This example replace a reaction in a reaction list by other with new 
parameters.
In order to replace the reaction, the new reaction must be created, loaded into
the ReactionList. Then the old one has to be removed and the new one must to
be set in the desired place.

For running the example, the experiment example4 must to be loaded in R-Series 
Controller and the OPC server must be enabled. The example will change the
reaction list so making a backup of the example folder is recommended.

@author: Edwin Barragán for Emtech S.A.
"""

import rseriesopc as rs
from rseriesopc import Reaction

# import copy

import json
import csv

newReactionTemperature = 70
reactionIndex = 1  # from 0 to number of reaction in list
reactorIndex = 1  # from 1 to 4

client = rs.RSeriesClient("opc.tcp://localhost:43344")

try:
    "Setting up the connection and getting address space."
    conn = client.connect()
    rseries = client.getRSeries()
    reactionManager = rseries.getExperiment().getReactionManager()

    "Getting delimiters for decoding CSV data"
    reactionParameters = reactionManager.getReactionParameters()
    rP = json.loads(reactionParameters)
    strDel = rP["CSVStringSeparator"]
    decPntDel = rP["CSVDecimalPoint"]

    "Getting the reaction list. This is a CSV string."
    "It needs to be decoded."
    reactionList = reactionManager.getReactionList()
    csvRows = str(reactionList).split("\n")
    csvRows.pop()
    rL = csv.reader(csvRows, delimiter=strDel)
    rL = list(rL)
    rL = [[sub.replace(decPntDel, ".") for sub in elem] for elem in rL]

    "Extrancting the reactions. The first line is the header."
    reaction = list()
    for data in rL[1:]:
        auxReact = Reaction()
        auxReact.load(data)
        reaction.append(auxReact)

    "Working with reactions."
    reactionOfInterest = reaction[reactionIndex]
    reactorOfInterest = reactionOfInterest.reactor[reactorIndex]
    reactorOfInterest.temperature = newReactionTemperature
    "Add the new reaction"
    reactionManager.addReactionToList(
        reaction[reactionIndex].makeCSVRow(strDel, decPntDel)
    )
    "Delete the old reaction"
    reactionManager.deleteReaction(reactionIndex)
    "Move the new reaction at the old reaction position"
    reactionManager.setReactionPosition(len(reaction) - 1, reactionIndex)

finally:
    "Closing the connection."
    if conn:
        client.disconnect()

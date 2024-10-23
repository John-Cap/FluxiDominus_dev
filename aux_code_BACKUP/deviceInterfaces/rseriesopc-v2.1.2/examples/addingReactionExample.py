# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 12:51:36 2021

Example 4a: Adding a Reaction

This example reads a data set, modifies one parameter of a reaction and 
add the resultant reaction to the reaction list.

In order to make a new reaction, a reaction is copied of the ReactionList.
Then the reaction is modified and append to the ReactionList.

For running this example the expmeriment "example4" must to be loaded to the
R-Series Controller.
This script modifies the Reaction List so making a backup of the example4
folder is recommended.

@author: Edwin Barragán for Emtech S.A.
"""

import rseriesopc as rs
from rseriesopc.model import Reaction

import json
import csv

newReactionTemperature = 100

client = rs.RSeriesClient("opc.tcp://localhost:43344")

try:
    "Setting up the connection."
    conn = client.connect()
    rseries = client.getRSeries()
    reactionManager = rseries.getExperiment().getReactionManager()

    "Getting the CSV delimiters for decoding reaction list."
    reactionParameters = reactionManager.getReactionParameters()
    rP = json.loads(reactionParameters)
    strDel = rP["CSVStringSeparator"]
    decPntDel = rP["CSVDecimalPoint"]

    "Getting the reaction list. It is a CSV string."
    "It needs to be decoded."
    reactionList = reactionManager.getReactionList()
    csvRows = str(reactionList).split("\n")
    csvRows.pop()
    rL = csv.reader(csvRows, delimiter=strDel)
    rL = list(rL)
    rL = [[sub.replace(decPntDel, ".") for sub in elem] for elem in rL]

    "Extracting the reactions. The first line is the header."
    reaction = list()
    for data in rL[1:]:
        auxReact = Reaction()
        auxReact.load(data)
        reaction.append(auxReact)

    "Woring with a reaction."
    reaction[0].reactor[1].temperature = newReactionTemperature
    reactionToSend = reaction[0].makeCSVRow(strDel, decPntDel)
    print("Sending reaction.....:", end=" ")
    if reactionManager.addReactionToList(reactionToSend):
        print("Ok")
    else:
        print("Fail")

finally:
    "Closing the connection."
    if conn:
        client.disconnect()

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 09:21:05 2021

Example 3: Reaction Parameters 

Python example to show how to retrieve reaction parameters with the JSON file.
This example script displays the CSV delimiters and enumerates all the parameters
of the desired reaction with its data. This reaction index should be less or equal
to the amount of reactions in the current ReactionList in the R-Series Controller.

@author: Edwin Barragán for Emtech S.A.
"""
import rseriesopc as rs
import json

reactionToShow = 2
client = rs.RSeriesClient("opc.tcp://localhost:43344")

try:
    "Setting up the connection"
    conn = client.connect()
    rseries = client.getRSeries()
    experiment = rseries.getExperiment()
    reactionManager = experiment.getReactionManager()

    "Extraction reactions parameters in a JSON object"
    reactionParameters = json.loads(
        reactionManager.getReactionParameters(reactionToShow - 1)
    )

    print("CSV exporter parameters:")
    print("  StringDelimiter: ", reactionParameters["CSVStringSeparator"])
    print("  DecimalPoint Delimiter: ", reactionParameters["CSVDecimalPoint"])

    reaction = reactionParameters[chr(reactionToShow - 1)]
    for key in reaction:
        if not isinstance(reaction[key], dict):
            print("{0}:\t{1}".format(key, reaction[key]))
        else:
            for k in reaction[key]:
                print("\t{0}:\t{1}".format(k, reaction[key][k]))

finally:
    if conn:
        client.disconnect()

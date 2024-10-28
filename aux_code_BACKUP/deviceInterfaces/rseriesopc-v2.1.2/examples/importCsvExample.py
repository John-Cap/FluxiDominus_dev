# -*- coding: utf-8 -*-
"""



Author: Josh Ridgway 
"""

import rseriesopc as rs
from rseriesopc import Reaction
import csv
import json

" Enter the ip address of your Touch panel or PC that is using the R Series SW "
IPAdress = "localhost"
client = rs.RSeriesClient("opc.tcp://" + IPAdress + ":43344")

'Enter path to import csv, "./test.csv" will locate a CSV file contained inside the directory of the script'
pathToLoad = "./files/test.csv"

"If false the the script will append to the current reaction list "
"if true the reaction list will be overwritten"
overwrite = False

try:
    "Setting up"
    "Connect the client"
    isConnected = client.connect()
    "Get the Reaction Manager OPC Node address"
    rseries = client.getRSeries()
    experiment = rseries.getExperiment()
    reactionManager = experiment.getReactionManager()

    "Getting the CSV delimiters for decoding reaction list."
    reactionParameters = reactionManager.getReactionParameters()
    rP = json.loads(reactionParameters)
    strDel = rP["CSVStringSeparator"]
    decPntDel = rP["CSVDecimalPoint"]

    "opens the CSV file of reactions"
    with open(pathToLoad) as bits:
        rL = csv.reader(bits, delimiter=",")
        rL = list(rL)
        rL = [[sub.replace(decPntDel, ".") for sub in elem] for elem in rL]

    "Converting CSV into a List of Reaction() objects"
    reactions = list()
    for data in rL[1:]:
        auxReact = Reaction()
        auxReact.load(data)
        reactions.append(auxReact)
    if overwrite:
        reactionManager.resetReactionList()

    "importing List o Reaction objects into the opc ua server"
    count = 0
    print("Sending reaction list")
    for reaction in reactions:
        reactionToSend = reaction.makeCSVRow(strDel, decPntDel)
        if reactionToSend != "":
            print("{0}-> Reaction Name: ".format(count), end="")
            print(reaction.name + ", ", end="")
            if reactionManager.addReactionToList(reactionToSend):
                print("Ok")
            else:
                print("Fail")
            count += 1
    print("Reaction List sent.")

finally:
    if isConnected:
        client.disconnect()

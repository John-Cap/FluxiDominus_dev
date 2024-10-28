"""
Created on Wed Sep 15 12:34:10 2021

Example 6: Get and load Experiments to R-Series

This example is a python script of automated saving and loading files through
OPC communication. This performs the following tasks: 
- Read the current experiment loaded on the R-Series device connected on
    a given address and port.
- Save the readed experiment on a given path.
- Load an experiment stored on a given path.

@author: Edwin Barragán for Emtech S.A.
"""
import rseriesopc as rs
import json

deviceIPAddress = "localhost"
devicePort = "43344"
pathToSave = "./tmpFiles"
pathToLoad = "./files/example6/"

url = "opc.tcp://" + deviceIPAddress + ":" + devicePort
cli = rs.RSeriesClient(url)
if cli.connect():
    try:
        rseries = cli.getRSeries()
        experiment = rseries.getExperiment()
        setup = experiment.getExperimentSetup()
        readingFromRSeries = setup.getExperiment(pathToSave)
        print(json.loads(readingFromRSeries).keys())
        print(setup.loadExperiment(pathToLoad))

    finally:
        cli.disconnect()

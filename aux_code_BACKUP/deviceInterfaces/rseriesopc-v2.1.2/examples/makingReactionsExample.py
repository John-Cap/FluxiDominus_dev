# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 09:20:55 2021

Example 5: 

This example reads a reaction from the Reaction List, then create a set of
reaction that increase the themperature by 10 C between each reaction.
Then, the new reaction list is loaded into the R-Series Controller.

For running the example, the experiment example5 must to be loaded in R-Series 
Controller and the OPC server must be enabled. The example will change the
reaction list so making a backup of the example folder is recommended.

@author: Edwin Barragán
"""

import rseriesopc as rs
from rseriesopc.model import Reaction
import json
import csv


class ExperimentStateHandler:
    """
    This class is a handler for register data changes.
    """

    oldVal = 0
    waitForReactionEnd = True

    def datachange_notification(self, node, val, data):
        print("ExperimentState = ", val)
        if self.oldVal != 0 and val == 0:
            self.waitForReactionEnd = False
        self.oldVal = val

    pass


# class Reaction():
#     """
#     This class represents a Reaction in a Reaction List.
#     Allows the user to load a Reaction and make copies with different
#     configurations.
#     """

#     def __init__(self):
#         self.name = None
#         self.residenceTime = None
#         self.reactor = {1: self.Reactor(), #1
#                         2: self.Reactor(), #2
#                         3: self.UVReactor(), #3
#                         4: self.Reactor(), #4
#                         5: self.Reactor(), #5
#                         6: self.UVReactor(), #6
#                         7: self.Reactor(), #7
#                         8: self.Reactor(), #8
#                         }
#         self.pump = {'A': self.Pump(), #A
#                      'B': self.Pump(), #B
#                      'C': self.Pump(), #C
#                      'D': self.Pump(), #D
#                      'E': self.Pump(), #E
#                      'F': self.Pump(), #F
#                      'G': self.Pump(), #G
#                      'H': self.Pump(), #H
#                       }
#         self.wash = {"pre": self.Wash(),
#                       "post": self.Wash(),
#                       }
#         self.collection = self.Collection()
#         self.autosampler = self.Autosampler()

#     def makeCSVRow(self, strDel, decDel):
#         accum = ''
#         accum += self.name + strDel
#         accum += str(self.residenceTime).replace('.',decDel) + strDel
#         for reactor in self.reactor.values():
#             accum += str(reactor.temperature).replace('.',decDel) + strDel
#             accum += str(reactor.residenceTime).upper() + strDel
#             if isinstance(reactor, Reaction.UVReactor):
#                 accum += str(reactor.power).replace('.',decDel) + strDel
#         for pump in self.pump.values():
#             accum += str(pump.flowRate).replace('.',decDel) + strDel
#             accum += str(pump.volumeRatio).replace('.',decDel) + strDel
#             accum += str(pump.concentrationRatio).replace('.',decDel) + strDel
#             accum += str(pump.quantity).replace('.',decDel) + strDel
#             accum += str(pump.advanceRetard).replace('.',decDel) + strDel
#             accum += str(pump.reagentConcentration).replace('.',decDel) + strDel
#         for wash in self.wash.values():
#             accum += str(wash.volume).replace('.',decDel) + strDel
#             accum += str(wash.flowRate).replace('.',decDel) + strDel
#         accum += self.collection.state.upper() + strDel
#         accum += str(self.collection.diverterTime).replace('.',decDel) + strDel
#         accum += str(self.collection.collectionTime).replace('.',decDel) + strDel
#         accum += str(self.collection.totalVolume).replace('.',decDel) + strDel
#         accum += str(self.collection.vialVolume).replace('.',decDel) + strDel
#         accum += str(self.collection.vials).replace('.',decDel) + strDel
#         if(self.autosampler.manual):
#             accum += 'MANUAL'
#         else:
#             accum += 'AUTOSAMPLER'
#         accum += strDel
#         for sample in self.autosampler.sample.values():
#             accum += str(sample.site).replace('.', decDel) + strDel
#             if sample.description:
#                 accum += sample.description + strDel
#             accum += str(not sample.fill).upper() + strDel
#             accum += str(sample.clean).upper() + strDel
#         return accum[:-1]

#     def load(self, reaction):
#         data = list(reaction).copy()
#         self.name = data.pop(0)
#         self.residenceTime = bool(data.pop(0))
#         for reactor in self.reactor.values():
#             reactor.load(data)
#         for pump in self.pump.values():
#             pump.load(data)
#         for wash in self.wash.values():
#             wash.load(data)
#         self.collection.load(data)
#         self.autosampler.load(data)

#     def tempStepper(self, reactorIndex, fromValue, toValue, step = 10):
#         if not isinstance(self.reactor[reactorIndex], self.Reactor):
#             return
#         reactions = list()
#         while fromValue <= toValue:
#             reaction = copy.deepcopy(self)
#             reaction.reactor[reactorIndex].setTemperature(fromValue)
#             reactions.append(reaction)
#             fromValue += step
#         return reactions

#     def uvPowerStepper(self, reactorIndex, fromValue, toValue, step = 10):
#         if not isinstance(self.reactor[reactorIndex], self.Reactor()):
#             return
#         reactions = list()
#         while fromValue <= toValue:
#             reaction = copy.deepcopy(self)
#             reaction.reactor[reactorIndex].setPower(fromValue)
#             reactions.append(reaction)
#             fromValue += step
#         return reactions

#     def flowrateStepper(self, pumpIndex, fromValue, toValue, step = 0.5):
#         if not isinstance(self.pump[pumpIndex], self.Pump):
#             return
#         reactions = list()
#         while fromValue <= toValue:
#             reaction = copy.deepcopy(self)
#             reaction.pump[pumpIndex].setFlowRate(fromValue)
#             reactions.append(reaction)
#             fromValue += step
#         return reactions

#     def volumeRatioStepper(self, pumpIndex, fromValue, toValue, step=0.1):
#         if not isinstance(self.pump[pumpIndex], self.Pump):
#             return
#         reactions = list()
#         while fromValue <= toValue:
#             reaction = copy.deepcopy(self)
#             reaction.pump[pumpIndex].setVolumeRatio(fromValue)
#             reactions.append(reaction)
#             fromValue += step
#         return reactions

#     def advanceRetardStepper(self, pumpIndex, fromValue, toValue, step):
#         if not isinstance(self.pump[pumpIndex], self.Pump):
#             return
#         reactions = list()
#         while fromValue <= toValue:
#             reaction = copy.deepcopy(self)
#             reaction.pump[pumpIndex].setAdvanceRetard(fromValue)
#             reactions.append(reaction)
#             fromValue += step
#         return reactions

#     def reagentConcentrationStepper(self, pumpIndex, fromValue, toValue, step):
#         if not isinstance(self.pump[pumpIndex], self.Pump):
#             return
#         reactions = list()
#         while fromValue <= toValue:
#             reaction = copy.deepcopy(self)
#             reaction.pump[pumpIndex].setReagentConcentration(fromValue)
#             reactions.append(reaction)
#             fromValue += step
#         return reactions

#     class Reactor():
#         """
#         A reactor has a tempreature and a residence time.
#         Each Reaction has 8 reactors, numbered from 1 to 8.
#         """
#         def __init__(self):
#             self.temperature  = 0
#             self.residenceTime = False
#             pass

#         def load(self, reaction):
#             self.temperature = reaction.pop(0)
#             self.residenceTime = reaction.pop(0)

#         def setTemperature(self, temp):
#             self.temperature = temp

#         def setResidenceTime(self, rt):
#             self.residenceTime = rt

#     class UVReactor(Reactor):
#         """
#         An UVReactor is a kind of Reactor which has an extra UV power.
#         """
#         def __init__(self):
#             super().__init__()
#             self.power = 0
#             pass

#         def load(self, reaction):
#             super().load(reaction)
#             self.power = reaction.pop(0)

#         def setPower(self, power):
#             self.power = power

#     class Pump():
#         """
#         A Pump has Flowrate, Volume Ratio, Concentration Ratio, Quantity,
#         Advance Retard and Regent Concentration.
#         It depends of the kind of Pump the experiment has, the valid changes
#         of Volume or Conentration Ratio.
#         The time which the pump is working is a function of flowrate and
#         quantity selected.
#         A Reacctor has 8 Pumps, stored in a list numbered from 1 to 8.
#         """
#         def __init__(self):
#             self.flowRate = 0
#             self.volumeRatio = 0
#             self.concentrationRatio = 0
#             self.quantity = 0
#             self.advanceRetard = 0
#             self.reagentConcentration = 0
#             pass

#         def load(self, reaction):
#             self.flowRate = reaction.pop(0)
#             self.volumeRatio = reaction.pop(0)
#             self.concentrationRatio = reaction.pop(0)
#             self.quantity = reaction.pop(0)
#             self.advanceRetard = reaction.pop(0)
#             self.reagentConcentration = reaction.pop(0)

#         def setFlowRate(self, fr):
#             self.flowRate = fr

#         def setVolumeRatio(self, vr):
#             self.volumeRatio = vr

#         def setConcentrationRatio(self, cr):
#             self.concentrationRatio = cr

#         def setAdvanceRetard(self, ar):
#             self.advanceRetard = ar

#         def setReagentConcentration(self, rc):
#             self.reagentConcentration = rc

#     class Wash():
#         """
#         A wash is a time where a Pump is cleaning its system.
#         A wash has a flowrate and a volume, which defines the wash time.
#         A Reaction has two different times for wash before and after the
#         Reaction is run.
#         """
#         def __init__(self):
#             self.flowRate = 0
#             self.volume = 0

#         def load(self, reaction):
#             self.volume = reaction.pop(0)
#             self.flowRate = reaction.pop(0)

#     class Collection():
#         """
#         A collection is the way how reaction stores the final produt.
#         It has an state, a diverterTime, a collectionTime, a number of vials,
#         a total volume and a volume for each vial.
#         A Reaction has information of one Collection.
#         """
#         def __init__(self):
#             self.state = None
#             self.diverterTime = 0
#             self.collectionTime = 0
#             self.vials = 0
#             self.totalVolume = 0
#             self.vialVolume = 0

#         def load(self, reaction):
#             self.state = reaction.pop(0)
#             self.diverterTime = reaction.pop(0)
#             self.collectionTime = reaction.pop(0)
#             self.totalVolume = reaction.pop(0)
#             self.vialVolume = reaction.pop(0)
#             self.vials = reaction.pop(0)

#         def setCollecionTime(self, ct):
#             self.collectionTime = ct

#         def setVials(self, v):
#             self.vials = v

#     class Autosampler():
#         def __init__(self):
#             self.manual = False
#             self.sample = {'A': self.Sample(),
#                            'B': self.Sample(),
#                            'C': self.Sample(),
#                            'D': self.Sample(),
#                            'E': self.Sample(),
#                            'F': self.Sample(),
#                            'G': self.Sample(),
#                            'H': self.Sample()}

#         def load(self, reaction):
#             if reaction.pop(0) == 'AUTOSAMPLER' :
#                 self.manual = False
#             else:
#                 self.manual = True
#             for sample in self.sample.values():
#                 sample.load(reaction)

#         class Sample():
#             def __init__(self):
#                 self.site = 0
#                 self.description = ""
#                 self.fill = True,
#                 self.clean = True

#             def load(self, reaction):
#                 self.site = reaction.pop(0)
#                 aux = reaction.pop(0)
#                 if 'TRUE' in aux or 'FALSE' in aux:
#                     self.description = None
#                     self.fill = aux
#                 else:
#                     self.description = aux
#                     self.fill = not reaction.pop(0)
#                 self.clean = reaction.pop(0)


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
    rj = json.loads(reactionParameters)
    stringDelimiter = rj["CSVStringSeparator"]
    decimalDelimiter = rj["CSVDecimalPoint"]

    reactionList = reactionManager.getReactionList()

    rows = reactionList.split("\n")
    rows.pop()
    rl = list(csv.reader(rows, delimiter=stringDelimiter))
    rl = [[sel.replace(decimalDelimiter, ".") for sel in el] for el in rl]

    reaction = list()
    for data in rl[1:]:
        r = Reaction()
        r.load(data)
        reaction.append(r)

    newReactions = reaction[-1].tempStepper(1, 30, 80, 10)
    "Convert the reaction table into a CSV String"
    name = "Reaction"
    counter = 0
    newReactionList = ""
    for reaction in newReactions:
        reaction.name = name + str(counter)
        counter += 1
        newReactionList += reaction.makeCSVRow(stringDelimiter, decimalDelimiter)
        newReactionList += "\n"

    "Add the header"
    newReactionList = rows[0] + "\n" + newReactionList

    "Send the ReactionList to the RSeries Controller"
    reactionManager.loadReactionList(newReactionList)

    # TODO: wait for reaction ends
    "Suscribe the ExperimentStatus variable for monitoring reactions execution"
    experimentState = reactionManager.getReactionStatusNode()
    handler = ExperimentStateHandler()
    subscription = client.create_subscription(500, handler)
    handle = subscription.subscribe_data_change(experimentState)

    reactionManager.startReaction()

#     while handler.waitForReactionEnd:
#         pass

#     subscription.unsubscribe(handle)

finally:
    #     'Restore the old Reaction List'
    #     rseries.getManualControl().stopAll()
    #     if reactionList:
    #         reactionManager.resetReactionList()
    #         reactionManager.loadReactionList(reactionList)

    if isConnected:
        client.disconnect()

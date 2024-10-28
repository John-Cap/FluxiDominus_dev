# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 17:09:01 2021

This is the implementation of the architecture for OPC UA communication
from Vapourtec R-Series Flow Chemistry machines modelling. 

This package contains the FlowChemistryType, its components, the class
definition of that components and the Reaction class with its components.

@author: Edwin Barragán for Emtech S.A
"""
from rseriesopc.model.devices import *
from rseriesopc.model.notification import *
from rseriesopc.model.identification import *
from rseriesopc.model.experiment import *
from rseriesopc.model.monitoring import *
from rseriesopc.model.reaction import Reaction

# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 14:18:43 2021

This module is for the high level opc client configuration.
It contains the connection and disconnection methods to the server.

@author: Edwin Barragan by Emtech S.A.
"""
import logging
import sys

from opcua import Client

from rseriesopc.model import FlowChemistryType


log = logging.getLogger("rseriesclient")
log.setLevel(logging.WARNING)
# log.setLevel(logging.DEBUG)

fh = logging.FileHandler("rseries.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(
    fmt=logging.Formatter("[%(asctime)s:%(levelname)s:%(name)s:]:%(message)s")
)
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(fmt=logging.Formatter("[%(module)s]:%(message)s"))
sh.setLevel(logging.WARNING)
# sh.setLevel(logging.DEBUG)

log.addHandler(fh)
log.addHandler(sh)


class RSeriesClient(Client):
    """
    The RSeries Client class contructs a OPC client object for RSeries OPC
    server.

    This class inherits opcua.Client class. This allows to use all of the
    funtions provided by it. Further information about this class and its use
    cases could be found in https://python-opcua.readthedocs.io/en/latest/

    This is a High Level Class that instantiates all the needed components
    to connect the R-Series Controller through OPC-UA communication

    Parameters
    ----------
    url : String
        It is the RSeries Controller OPC Server address.

    Attributes
    ----------
    rSeries : FlowChemistryType
        It represents the R-Series machine. This has all the methods to
        communicate to the controller.
    isConnected : bool
        It is true when the client is connected to the R-Series Controller.
        Otherwise, this is false.

    Methods
    -------
    connect()
        It connects the client with RSeries OPC Server.
    disconnect()
        It disconnects the client with the R-Series Controller OPC UA Server.
    getRSeries()
        It returns the RSeries machine
    """

    def __init__(self, url):
        super().__init__(url, timeout=60)
        # self.client = Client(url, timeout = 10)
        self._clientConfig()
        self.rSeries = None
        self.isConnected = False

    def _clientConfig(self):
        self.name = "OPC-UA R-Series Client"
        self.description = "Default R-Series Client for UPC UA Communication"
        self.application_uri = "opc:vapourtec"
        self.product_uri = "opc:vapurtec:rseries"
        self.secure_channel_timeout = 600000

    def _setUsername(self, usr):
        self.set_user(usr)

    def _setPassword(self, pwd):
        self.set_password(pwd)

    def connect(self):
        """
        It connects the client with RSeries OPC Server.

        Returns
        -------
        bool
            It returns true if the connections was successful.
            Else, it returns false.

        """
        try:
            super().connect()
            log.debug("R-Series machine is connected to server.")
            self.load_type_definitions()
            self.isConnected = True
            return True
        except:
            log.error("R-Series machine was unable connecting to server.")
            return False

    def disconnect(self):
        """
        It disconnects the client with the R-Series Controller OPC UA Server.

        Returns
        -------
        None.

        """
        if self.isConnected:
            super().disconnect()
            self.isConnected = False
            log.debug("R-Series machine disconnected")

    def loadRSeries(self):
        """
        This function look up in the server and construct the RSeries
        object of interest.

        Returns
        -------
        bool
            It is True when an RSeries machine was loaded.
            Else, it is False.

        """
        obj = self.get_objects_node()
        if obj is not None:
            try:
                self.rSeries = FlowChemistryType(obj)
                return True
            except:
                log.error("Client: RSeries machine could not be loaded.")
        else:
            log.error("Object node not found.")
        return False

    def getRSeries(self):
        """
        It returns the RSeries machine

        Returns
        -------
        FlowChemistryType
            It is the R-Series machine.

        """
        if self.rSeries is None:
            if not self.loadRSeries():
                return None
        return self.rSeries

    pass

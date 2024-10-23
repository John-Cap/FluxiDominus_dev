from opcua import Node

import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class VBFRType(BaseNode):
    """
    A VBFRType Object contains all the variables and methods to know the
    measurements and information about the Variable Bed Flow Reactor

    Parameters
    ----------
    root : opcua.Node
        It is the id of the VBFR object in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the VBFR object in the OPC UA Address Space.
    position : opcua.Node
        It is the id of the VBFR Piston Position variable in the OPC UA
        Address Space.
    dPress : opcua.Node
        It is the id of the VBFR Differential Pressure variable in the OPC UA
        Address Space.
    volume : opcua.Node
        It is the id of the VBFR Volume variable in the OPC UA Address Space.
    """

    position: Node
    dPress: Node
    volume: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("position", "VBFRPosition", None),
            NodeInfo("dPress", "DiffPressure", None),
            NodeInfo("volume", "Volume", None),
        ]

        log.debug("{0} : hydrating variables".format(__class__.__name__))
        for item in variables:
            node, browse_names = self._get_interest_ua_node(
                item.name, item.prototype, browse_names
            )
            setattr(self, item.variable, node)

        for browse_name in browse_names:
            log.warning(
                "{0}: {1} was not caught".format(__class__.__name__, browse_name)
            )

    def getPosition(self):
        """
        It gives the Piston Position in mm.

        Returns
        -------
        float
            It is the position of the piston.

        """
        return self.position.get_value()

    def getPositionNode(self):
        """
        This method returns the id of the VBFR Piston Position variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the VBFR Piston Position variable in the OPC UA
            Address Space.

        """
        return self.position

    def getDifferentialPressure(self):
        """
        It gives the value of the VBFR differential pressure in mBar.

        Returns
        -------
        integer
            This is the differential pressure.

        """
        return self.dPress.get_value()

    def getDifferentialPressureNode(self):
        """
        This method returns the id of the VBFR Diffetential Pressur variable.
        This id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the VBFR Diferential Pressure variable in the
            OPC UA Address Space.

        """
        return self.dPress

    def getVolume(self):
        """
        It gives the inyected or loaded volume from the VBFR in mm^3

        Returns
        -------
        float
            It is the VBFR volume.

        """
        return self.volume.get_value()

    def getVolumeNode(self):
        """
        This method returns the id of the VBFR Volume variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the VBFR Volume variable in the OPC UA Address
            Space.

        """
        return self.volume

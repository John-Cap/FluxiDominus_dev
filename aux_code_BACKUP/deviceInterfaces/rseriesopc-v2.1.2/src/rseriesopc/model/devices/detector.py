from opcua import Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class DetectorType(BaseNode):
    """
    A DetectorType object contains the variables with the measurements and
    information about the UV50D detector

    Parameters
    ----------
    root : opcua.Node
        It is the id of this object in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the detector in the OPC UA Address Space.
    lampState : opcua.Node
        It is the id of the lamp state variable in the OPC UA Address Space.
    Wavelengths : opcua.Node
        It is the id of the measuring values in the OPC UA Address Space.

    """

    lampState: Node
    wavelengths: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in self.root.get_children()
        }

        variables = [
            NodeInfo("lampState", "LampState", None),
            NodeInfo("wavelengths", "Wavelengths", None),
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

    def getLampState(self):
        """
        It gives the lamp status. It could be: \n

        OFF = 0\n
        HEATING = 1\n
        ON = 2

        Returns
        -------
        integer
            It is the lamp status.

        """
        return self.lampState.get_value()

    def getLampStateNode(self):
        """
        This method returns the id of the UV50D Lamp status variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the UV50D Lamp Status variable in the OPC UA
            Address Space.

        """
        return self.lampState

    def getWavelengthAt(self, index):
        """
        It gives a measuremnt of the desired wavelength detector.

        Parameters
        ----------
        index : integer
            It is the index of the detector to measure.

        Returns
        -------
        float
            It is the detector measurement.

        """
        return self.wavelengths.get_value()[index]

    def getWavelengths(self):
        """
        It gives an array with all of detetors measurements.

        Returns
        -------
        list of float
            These are the measurements.

        """
        return self.wavelengths.get_value()

    def getWavelengthNode(self):
        """
        This method returns the id of the UV50D measurements variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the UV50D measurements variable in the OPC UA
            Address Space.

        """
        return self.wavelengths

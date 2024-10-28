from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class IONType(BaseNode):
    """
    The IONType class implements the low level functions for
    controlling the components of the R-Series Machine.

    This class allows the user to control the electrical control functions
    for the Vapourtec ION Electrochemial Reactor.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        This is the parent node in the OPC UA Address Space.
    voltage : opcua.Node
        This is the id of the voltage variable in the OPC UA Address Space.
    current : opcua.Node
        It is the id of the current variable in the OPC UA Address Space.

    """

    current: Node
    voltage: Node
    _start: Node
    _stop: Node

    def __init__(self, root: Node):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("current", "Current", None),
            NodeInfo("voltage", "Voltage", None),
            NodeInfo("_start", "Start", None),
            NodeInfo("_stop", "Stop", None),
        ]

        for item in variables:
            node, browse_names = self._get_interest_ua_node(
                item.name, item.prototype, browse_names
            )
            setattr(self, item.variable, node)

        for browse_name in browse_names:
            log.warning(
                "{0}: {1} was not caught".format(__class__.__name__, browse_name)
            )

    def start(self):
        """
        It starts the electrochemical control functions of the reactor.

        """
        self.root.call_method(self._start)

    def stop(self):
        """
        It stops the electrochemical control functions of the reactor.

        """
        self.root.call_method(self._stop)

    def setCurrent(self, newCurrentInA: float):
        """
        It sets a new target for the ION Reactor's current.

        Parameters
        ----------
        index : float
            It is the new current target in Amperes.

        Returns
        -------
        bool
            It returns a boolean. It it is true, means the value was set.
            Otherwise, it is false

        """
        try:
            self.current.set_value(
                ua.Variant(newCurrentInA, ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getCurrent(self):
        """
        It gives a measuremnt of the ION Reactor's current.

        Returns
        -------
        float
            It is the reactor's current measurement.

        """
        return self.current.get_value()

    def getCurrentNode(self):
        """
        This method returns the id of the ION Reactor's current variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the reactor's current variable in the OPC UA
            Address Space.

        """
        return self.current

    def setVoltage(self, newVoltageInV):
        """
        It sets a new target for the ION Reactor's voltage.

        Parameters
        ----------
        index : float
            It is the new voltage target in Volt.

        Returns
        -------
        bool
            It returns a boolean. It it is true, means the new value was set.
            Otherwise, it is false

        """
        self.voltage.set_value(ua.Variant(newVoltageInV, ua.uatypes.VariantType.Float))

    def getVoltage(self):
        """
        It gives a measuremnt of the ION Reactor's voltage.

        Returns
        -------
        float
            It is the reactor's voltage measurement.

        """
        return self.voltage.get_value()

    def getVoltageNode(self):
        """
        This method returns the id of the ION Reactor's voltage variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the reactor's voltage variable in the OPC UA
            Address Space.

        """
        return self.voltage

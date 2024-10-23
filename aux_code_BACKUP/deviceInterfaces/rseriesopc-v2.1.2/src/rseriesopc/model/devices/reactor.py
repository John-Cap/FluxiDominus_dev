from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class ReactorType(BaseNode):
    """
    This ReactorType class represent each reactor that has present in the
    R-Series Controller.
    This contains all the methods and variables with information about
    one reactor.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the Reactor in the OPC UA Address Space.
    temperature : opcua.Node
        This is the id of the temperature measurement in the OPC UA Address
        Space.
    power : opcua.Node
        This is the id of the power variable in the OPC UA Address Space.
    reactorType : opcua.Node
        It is the id of the reactor type variable in the OPC UA Address Space.

    """

    _setTemperature: Node
    _getTemperatureLimits: Node
    _getTemperature: Node
    temperatureLimits: Node
    temperature: Node
    _getPower: Node
    power: Node
    _getReactorType: Node
    reactorType: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_setTemperature", "SetTemperature", None),
            NodeInfo("_getTemperatureLimits", "GetTemperatureLimits", None),
            NodeInfo("_getTemperature", "GetTemperature", None),
            NodeInfo("temperatureLimits", "TemperatureLimits", None),
            NodeInfo("temperature", "Temperature", None),
            NodeInfo("_getPower", "GetPower", None),
            NodeInfo("power", "Power", None),
            NodeInfo("_getReactorType", "GetReactorType", None),
            NodeInfo("reactorType", "ReactorType", None),
            # TODO interface not implemented
            NodeInfo("overTripCutOff", "OverTripCutOff", None),
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

        for child in self.root.get_children():
            name = child.get_browse_name().to_string()

    def setTemperature(self, temp):
        """
        It sets the temperature set point. This temperature will be reached
        when the StartManualControl method is run.

        The temperature will be set into the limits. If a lower or higher
        target temperature is send, the closer limit will be set

        Parameters
        ----------
        temp : integer
            This is the new temperature set point.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.temperature.set_value(ua.Variant(temp, ua.uatypes.VariantType.Float))
            return True
        except:
            return False

    # getters
    def getTemperature(self):
        """
        It gets the last temperature measuremt of the reactor.

        Returns
        -------
        float
            This is the measured temperature. A -1000 value means the
            reactor is turned off.

        """
        return self.temperature.get_value()

    def getTemperatureLimits(self):
        """
        It returns the temperature limits for the set point.

        Returns
        -------
        list
            It is a list that contains the low and high limits.

        """
        return self.temperatureLimits.get_value()

    def getTemperatureNode(self):
        """
        This method returns the id of the Temperature variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the Temperature variable in the OPC UA Address
            Space.

        """
        return self.temperature

    def getTemperatureLimitsNode(self):
        """
        This method returns the id of the tempearture limits. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the Temperature Limits variable in the OPC UA
            Address Space.

        """
        return self.temperatureLimits

    def getPower(self):
        """
        It returns the power of the Reactor.

        Returns
        -------
        float
            The reactor power.

        """
        return self.power.get_value()

    def getPowerNode(self):
        """
        This method returns the id of the reactor's power. This id allows the user
        to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py


        Returns
        -------
        opcua.Node
            This is the id of the power variable in the OPC UA Address Space.

        """
        return self.power

    def getReactorType(self):
        """
        It returns the Reactor Type in an integer.
        This is defined by self.ReactorTypeEnum

        Returns
        -------
        ReactorTypeEnum
            It is the reactor type.

        """
        return self.reactorType.get_value()

    def getReactorTypeNode(self):
        """
        This method returns the id of the Reactor Type variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the reactor type variable in the OPC UA Address
            Space.

        """
        return self.reactorType

    class ReactorTypeEnum:
        """
        The posible types of reactor founded
        HEATED_NOR
        COOLED_TUBE
        COOLED_COLUMN
        MIDRANGE_TUBE
        UV150
        NIK_BATCH
        CHIP_REACTOR
        EC_REACTOR

        """

        HEATED_NOR = (0,)
        COOLED_TUBE = (1,)
        COOLED_COLUMN = (2,)
        MIDRANGE_TUBE = (3,)
        UV150 = (4,)
        NIK_BATCH = (5,)
        CHIP_REACTOR = (6,)
        EC_REACTOR = (7,)

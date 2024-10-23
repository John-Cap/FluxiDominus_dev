from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class ChillerType(BaseNode):
    """
    A ChillerType Object contains all the variables and methods to know the
    measurements and information about the Chillers.

    Parameters
    ----------
    root : opcua.Node
        It is the id of a Chiller object in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the Chiller object in the OPC UA Address Space.
    errorState : opcua.Node
        It is the id of the error state variable for the Chiller in the OPC UA
        Address Space.
    setTemperature : opcua.Node
        It is the id of the Chiller Temperature Set Point variable in the OPC UA
        Address Space.
    temperature : opcua.Node
        It is the id of the Chiller Temperature measurement variable in the OPC
        UA Address Space.
    chillerType : opcua.Node
        It is the id of the type of Chiller variable in the OPC UA Address Space.
    leaveRunning : opcua.Node
        It is the id of the Chiller's leaveRunning variable in the OPC UA Address
        Space.
    sensorType : opcua.Node
        It is the id of the sensor Type of the Chiller variable in the OPC UA Address
        Space.
    """

    errorState: Node
    setTemperature: Node
    temperature: Node
    chillerType: Node
    leaveRunning: Node
    sensorType: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("errorState", "ChillerErrorState", None),
            NodeInfo("setTemperature", "SetTemperature", None),
            NodeInfo("temperature", "Temperature", None),
            NodeInfo("chillerType", "ChillerType", None),
            NodeInfo("leaveRunning", "LeaveRunning", None),
            NodeInfo("sensorType", "SensorType", None),
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

    def getChillerType(self):
        """
        It gives the chiller type target.

        Returns
        -------
        integer
            It is the chiller type.
            0 means Julabo Chiller.
            1 means Huber Chiller.

        """
        return self.chillerType.get_value()

    def getChillerTypeNode(self):
        """
        This method returns the id of the Chiller Type variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the Chiller Type variable in the OPC UA
            Address Space.

        """
        return self.chillerType

    def getErrorState(self):
        """
        It reports if there are an error in the chiller.

        Returns
        -------
        bool
            It is True when an error occurs. Otherwise, it is False.

        """
        return self.errorState.get_value()

    def getErrorStateNode(self):
        """
        This method returns the id of the Chiller's error state variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the ErrorState Chiller's variable in the OPC UA
            Address Space.

        """
        return self.errorState

    def getLeaveRunning(self):
        """
        It gives if the chiller will be left running after reaction list excecution.

        Returns
        -------
        bool
            If it is True, the chiller will not be turned off at the end of the
            reaction lsit excecution.

        """
        return self.leaveRunning.get_value()

    def getLeaveRunningNode(self):
        """
        This method returns the id of the Chiller's Leave Running variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the LeaveRunning variable in the OPC UA
            Address Space.

        """
        return self.leaveRunning

    def getSensorType(self):
        """
        It gives the sensor type present on the device.

        Returns
        -------
        integer
            It is kind of control for the chiller.
            0 means the control is made with the interal sensor.
            1 means the control is made with an external sensor.

        """
        return self.sensorType.get_value()

    def getSensorTypeNode(self):
        """
        This method returns the id of the Chiller's Sensor Type variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the Sensor Type variable in the OPC UA
            Address Space.

        """
        return self.sensorType

    def getTemperature(self):
        """
        It gives the temperature measurement.

        Returns
        -------
        float
            It is the temperature in the chiller.

        """
        return self.temperature.get_value()

    def getTemperatureNode(self):
        """
        This method returns the id of the Chiller's temperature variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the Temperature variable in the OPC UA
            Address Space.

        """
        return self.temperature

    def getSetTemperature(self):
        """
        It gives the temperature target.

        Returns
        -------
        float
            It is the temperature target for the chiller.

        """
        return self.setTemperature.get_value()

    def getSetTemperatureNode(self):
        """
        This method returns the id of the Chiller's temperature target
        variable. This id allows the user to subscribe the variable to a
        handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SetTemperature variable in the OPC UA
            Address Space.

        """
        return self.temperature

    def setChillerType(self, chiller):
        """
        It set the chiller controller. Each brand needs an specific controller.

        Parameters
        ----------
        chiller : integer.
            This is the chiller type.
            0 is for Julabo Chiller.
            1 is for Huber Chiller.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.chillerType.set_value(ua.Variant(chiller, ua.uatypes.VariantType.Byte))
            return True
        except:
            return False

    def setLeaveRunning(self, state):
        """
        It set the leave running parameter.

        When Leave Running is True, the chiller will not be turned off at the end
        of the reaction list excecution.

        Parameters
        ----------
        state : bool.
            This is the new leave running state for the chiller.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.leaveRunning.set_value(
                ua.Variant(state, ua.uatypes.uatypes.VariantType.Boolean)
            )
            return True
        except:
            return False

    def setSensorType(self, sensor):
        """
        It set the temperature target.

        Parameters
        ----------
        sensor : int.
            This is the new sensorType for the chiller.
            0 means internal sensor.
            1 menas external sensor.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.sensorType.set_value(ua.Variant(sensor, ua.uatypes.VariantType.Byte))
            return True
        except:
            return False

    def setTemperature(self, temperature):
        """
        It set the temperature target.

        Parameters
        ----------
        temperature : float.
            This is the new temperature target for the chiller.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.setTemperature.set_value(
                ua.Variant(temperature, ua.uatypes.VariantType.Double)
            )
            return True
        except:
            return False

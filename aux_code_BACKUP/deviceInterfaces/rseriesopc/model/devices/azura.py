from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.devices.module import ModuleType
from rseriesopc.model.base import NodeInfo


class AzuraPumpType(ModuleType):
    """
    An AzuraPumpType object contains all of the methods and object to monitor and
    control a Azura Pump Module in the R-Series Controller.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the R2 object id in the OPC UA Address Space.
    erroState : opcua.Node
        It is the ErrorState variable id in the OPC UA Address Space.
    maxPressureLimit : opcua.Node
        It is the MaxPressureLimit variable id in the OPC UA Address Space.
    pressureLimit : opcua.Node
        It is the PressureLimit variable id in the OPC UA Address Space.
    flowRate : opcua.Node
        It is the FlowRate variable id in te OPC UA Address Space.
    """

    errorState: Node
    _getMaxPressureLimit: Node
    maxPressureLimit: Node
    _setPressureLimit: Node
    pressureLimit: Node
    _getPumpPressure: Node
    pumpPressure: Node
    _getFlowRate: Node
    _setFlowRate: Node
    flowRate: Node

    def __init__(self, root):
        super().__init__(root)
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }
        variables = [
            NodeInfo("errorState", "AzuraErrorState", None),
            NodeInfo("_getMaxPressureLimit", "GetMaxPressureLimit", None),
            NodeInfo("maxPressureLimit", "MaxPressureLimit", None),
            NodeInfo("_setPressureLimit", "SetMaxPressureLimit", None),
            NodeInfo("pressureLimit", "PressureLimit", None),
            NodeInfo("_getPumpPressure", "GetPumpPressure", None),
            NodeInfo("pumpPressure", "PumpPressure", None),
            NodeInfo("_getFlowRate", "GetFlowRate", None),
            NodeInfo("_setFlowRate", "SetFlowRate", None),
            NodeInfo("flowRate", "FlowRate", None),
        ]

        log.debug("{0} : hydrating variables".format(__class__.__name__))
        for item in variables:
            node, browse_names = self._get_interest_ua_node(
                item.name, item.prototype, browse_names
            )
            setattr(self, item.variable, node)

        self.pumps.update({"A": self})

        for browse_name in browse_names:
            log.warning(
                "{0}: {1} was not caught".format(__class__.__name__, browse_name)
            )

    def getErrorState(self):
        """It reports if there was an error with the module.

        Returns
        -------
        bool
            It is True if there was an error. Otherwise, it si False.
        """
        return self.errorState.get_value()

    def getErrorStateNode(self):
        """
        This method returns the id of the ErrorState variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the ErrorState variable in the OPC UA Address Space.
        """
        return self.errorState

    def setMaxPressureLimit(self, newMaxPressureLimit):
        """It sets a new maximum pressure limit.

        Parameters
        ----------
        newMaxPressureLimit : float
            It is the new maximum pressure limit.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.maxPressureLimit.set_value(
                ua.Variant(newMaxPressureLimit, ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getMaxPressureLimit(self):
        """It gives the actual maximum pressure limit.

        Returns
        -------
        float
            It is the actual maximum pressure limit.
        """
        return self.maxPressureLimit.get_value()

    def getMaxPressureLimitNode(self):
        """
        This method returns the id of the SF10 MaxPressureLimit variable.
        This id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SF10 MaxPressureLimit variable in the OPC UA
            Address Space.

        """
        return self.maxPressureLimit

    def setFlowRate(self, flowRate):
        """
        It sets the flow rate to the pump.
        When flow rate is setted in 0, the pump is turned off.
        If the pump is setted in other value than 0, the pump is immediatly
        turned on.
        The flow rate must be set in a suitable value for the connected
        pump in R2. In other case, the flow rate will not be setted in the
        machine.

        Parameters
        ----------
        flowRate : integer
            It is the pump flow rate in ul/min.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.flowRate.set_value(
                ua.Variant(float(flowRate), ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getFlowRate(self):
        """
        This function gives the current pump flow rate.

        Returns
        -------
        integer
            It is the pump flow rate in ul/min.

        """
        return int(self.flowRate.get_value())

    def getFlowRateNode(self):
        """
        This method returns the id of the flow rate variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the flowRate variable in the OPC UA Address Space.

        """
        return self.flowRate

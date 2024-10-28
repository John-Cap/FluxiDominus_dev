from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.devices.module import ModuleType
from rseriesopc.model.base import NodeInfo


class MFCType(ModuleType):
    """
    A MFCType object contains all of the methods and object to monitor and
    control a MFC Module in the R-Series Controller.

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
    gasType : opcua.Node
        It is the GasType variable id in the OPC UA Address Space.
    flowRate : opcua.Node
        It is the FlowRate variable id in the OPC UA Address Space.

    """

    errorState: None
    _getGasType: None
    gasType: None
    _getFlowRate: None
    _setFlowRate: None
    flowRate: None

    def __init__(self, root: Node):
        super().__init__(root)
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("errorState", "MFCErrorState", None),
            NodeInfo("_getGasType", "GetGasType", None),
            NodeInfo("gasType", "GasType", None),
            NodeInfo("_getFlowRate", "GetFlowRate", None),
            NodeInfo("_setFlowRate", "SetFlowRate", None),
            NodeInfo("flowRate", "GasFlowRate", None),
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

    def getGasType(self):
        """It gives the gas type MFC has set.

        Returns
        -------
        integer
            This is the code for the gas type.
        """
        return self.gasType.get_value()

    def getGasTypeNode(self):
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
        return self.gasType

    def setFlowRate(self, flowRate):
        """
        It sets the flow rate to the pump.
        When flow rate is setted in 0, the pump is turned off.
        If the pump is setted in other value than 0, the pump is immediatly
        turned on.
        The flow rate must be set in a suitable value for the connected
        pump in MFC. In other case, the flow rate will not be setted in the
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

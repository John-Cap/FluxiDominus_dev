from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.devices.module import ModuleType
from rseriesopc.model.base import NodeInfo


class SyringePumpType(ModuleType):
    """
    SyringePumpType class is an object to monitor and control external
    syringe pumps.

    Parameters
    ----------
    root : opcua.Node
        It is the id of this node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the OPC UA Address Space information about this object.
    valveState: opcua.Node
        It is the id of the ValveState variable in the OPC UA Address
        Space.
    position: opcua.Node
        It is the id of the Position variable in the OPC UA Address
        Space.
    flowRate: opcua.Node
        It is the id of the FlowRate variable in the OPC UA Address
        Space.

    """

    errorState: Node
    _getValveState: Node
    _setValveState: Node
    valveState: Node
    _setPosition: Node
    position: Node
    _getFlowRate: Node
    _selfFlowRate: Node
    flowRate: Node

    def __init__(self, root):
        super().__init__(root)
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("errorState", "SyringeErrorState", None),
            NodeInfo("_getValveState", "GetSRValveState", None),
            NodeInfo("_setValveState", "SetSRValveState", None),
            NodeInfo("valveState", "SRValveState", None),
            NodeInfo("_setPosition", "SetPosition", None),
            NodeInfo("position", "Position", None),
            NodeInfo("_getFlowRate", "GetFlowRate", None),
            NodeInfo("_selfFlowRate", "SetFlowRate", None),
            NodeInfo("flowRate", "FlowRate", None),
            # TODO variables catched but interface was not implemented
            NodeInfo("pressureLimit", "PressureLimit", None),
            NodeInfo("_setMaxPressureLimit", "SetMaxPressureLimit", None),
            NodeInfo("maxPressureLimit", "MaxPressureLimit", None),
            NodeInfo("gasType", "GasType", None),
            NodeInfo("_getPumpPressure", "GetPumpPressure", None),
            NodeInfo("pumpPressure", "PumpPressure", None),
            NodeInfo("_getMaxPressureLimit", "GetMaxPressureLimit", None),
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
        """
        It reports if there was an error with the module.

        Returns
        -------
        bool
            It is True if there was an error. Otherwise, it is False.

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

    def setValveState(self, state):
        """
        It sets the state of the valve.

        Parameters
        ----------
        state : bool
            Depends on which is the valve, true means fluid from
            Reagent to Solvent,
            Collect to Waste or
            Inject to Load.
            Else, the fluid moves in the another way.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.valveState.set_value(ua.Variant(state, ua.uatypes.VariantType.Boolean))
            return True
        except:
            return False

    def getValveState(self):
        """
        This gives the state of the valve

        Returns
        -------
        bool
            Depends on which is teh valve, true means liquid from
            Reagent to Solvent,
            Collect to Waste or
            Inject to Load.
            Else, the liquid moves in the another way.

        """
        return self.valveState.get_value()

    def getValveStateNode(self):
        """
        This method returns the id of the valve state variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the ValveState variable in the OPC UA Address
            Space.

        """
        return self.valveState

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

    def setPosition(self, newPosition):
        """
        It sets a new position for the syringe

        Parameters
        ----------
        newPosition : integer
            It is hte new position to set.

        """
        self.position.set_value(ua.Variant(newPosition, ua.uatypes.VariantType.Boolean))

    def getPosition(self):
        """
        It gives the syringe position

        Returns
        -------
        integer
            It is the syringe position

        """
        return self.position.get_value()

    def getPositionNode(self):
        """
        This method returns the id of the Position variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the Position variable in the OPC UA Address Space.

        """
        return self.position

from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class PumpType(BaseNode):
    """
    A PumpType object contains all of the methods and variables to control and
    monitor a pump inside an R2Module.

    This object can set and get the values of their attributes members but
    cannot subscribe them. In order to subscribe, the variable id must to be
    getted from inside the member object.

    In example, to subscribe the flow rate, the variable id has to be getted
    from :

    \tPumpType.flowRate.getFlowRateNode().

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the pump object in the OPC UA Address Space.
    flowRate: opcua.Node
        It is the id of flow rate variable in the OPC UA Address Space.
    srValveState : opcua.Node
        It is the id of the state of the valve in the OPC UA Address Space.
    ilValveState : opcua.Node
        It is the id of the state of the valve in the OPC UA Address Space.

    """

    _setFlowRate: Node
    _getFlowRate: Node
    flowRate: Node
    _setSRValveState: Node
    _getSRValveState: Node
    srValveState: Node
    _setILValveState: Node
    _getILValveState: Node
    ilValveState: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_setFlowRate", "SetFlowRate", None),
            NodeInfo("_getFlowRate", "GetFlowRate", None),
            NodeInfo("flowRate", "FlowRate", None),
            NodeInfo("_setSRValveState", "SetSRValveState", None),
            NodeInfo("_getSRValveState", "GetSRValveState", None),
            NodeInfo("srValveState", "SRValveState", None),
            NodeInfo("_setILValveState", "SetILValveState", None),
            NodeInfo("_getILValveState", "GetILValveState", None),
            NodeInfo("ilValveState", "ILValveState", None),
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

    def setILValveState(self, state):
        """
        It sets the state of the inject or load selection valve.

        Parameters
        ----------
        state : bool
            Depends on which is the valve, true means fluid from
            Inject to Load.
            Else, the fluid moves in the another way.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.ilValveState.set_value(
                ua.Variant(state, ua.uatypes.VariantType.Boolean)
            )
            return True
        except:
            return False

    def getILValveState(self):
        """
        This gives the state of the inject or load selection valve.

        Returns
        -------
        bool
            Depends on which is teh valve, true means liquid from
            Inject to Load.
            Else, the liquid moves in the another way.

        """
        return self.ilValveState.get_value()

    def getILValveStateNode(self):
        """
        This method returns the id of the ILValveState variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the ILValveState variable in the OPC UA Address
            Space.

        """
        return self.ilValveState

    def setSRValveState(self, state):
        """
        It sets the state of the Solvent or Reagent selection valve.

        Parameters
        ----------
        state : bool
            Depends on which is the valve, true means fluid from
            Reagent to Solvent
            Else, the fluid moves in the another way.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.srValveState.set_value(
                ua.Variant(state, ua.uatypes.VariantType.Boolean)
            )
            return True
        except:
            return False

    def getSRValveState(self):
        """
        This gives the state of the Solvent or Reagent selection valve

        Returns
        -------
        bool
            True means liquid from
            Reagent
            Else, the liquid moves in the another way.

        """
        return self.srValveState.get_value()

    def getSRValveStateNode(self):
        """
        This method returns the id of the SRValveState variable. This id allows
        the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the SRValveState variable in the OPC UA Address
            Space.

        """
        return self.srValveState

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

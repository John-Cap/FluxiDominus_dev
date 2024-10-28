from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.devices.module import ModuleType
from rseriesopc.model.base import NodeInfo


class SFType(ModuleType):
    """
    The SF10Type class implements the low level functions for
    controlling the components of the R-Series Machine.

    This class allows the user to write and run scripts for custom
    automation routines.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        This is the parent node in the OPC UA Address Space.
    maxPressureLimit :
        This is the MaxPressureLimit node in the OPC UA Address
        Space.
    pressureLimit :
        This is the PressureLimit node in the OPC UA Address Space.
    bprRegulationPressure :
        This is the BPRRegulationPression node in the OPC UA Address
        Space.
    pumpPressure :
        This is the PumpPressure node in the OPC UA Address Space.
    gasFlowRate :
        This is the GasFlowRate node in the OPC UA Address Space.
    flowrate :
        This is the FlowRate node in the OPC UA Address Space.
    srValveState :
        This is the SRValveState node in the OPC UA Address Space.

    """

    _setMaxPressureLimit: Node
    _getMaxPressureLimit: Node
    maxPressureLimit: Node
    pressureLimit: Node
    _getOscillation: Node
    _setOscillation: Node
    bprRegulationPression: Node
    _getPumpPressure: Node
    pumpPressure: Node
    _getOperationMode: Node
    _setOperationMode: Node
    gasFlowRate: Node
    _getFlowRate: Node
    _setFlowRate: Node
    flowrate: Node
    _setSRValveState: Node
    _getSRValveState: Node
    srValveState: Node

    def __init__(self, root):
        super().__init__(root)
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_setMaxPressureLimit", "SetMaxPressureLimit", None),
            NodeInfo("_getMaxPressureLimit", "GetMaxPressureLimit", None),
            NodeInfo("maxPressureLimit", "MaxPressureLimit", None),
            NodeInfo("pressureLimit", "PressureLimit", None),
            NodeInfo("_getOscillation", "GetOscillation", None),
            NodeInfo("_setOscillation", "SetOscillation", None),
            NodeInfo("bprRegulationPression", "BPRRegulationPression", None),
            NodeInfo("_getPumpPressure", "GetPumpPressure", None),
            NodeInfo("pumpPressure", "PumpPressure", None),
            NodeInfo("_getOperationMode", "GetOperationMode", None),
            NodeInfo("_setOperationMode", "SetOperationMode", None),
            NodeInfo("gasFlowRate", "GasFlowRate", None),
            NodeInfo("flowrate", "FlowRate", None),
            NodeInfo("_getFlowRate", "GetFlowRate", None),
            NodeInfo("_setFlowRate", "SetFlowRate", None),
            NodeInfo("srValveState", "SRValveState", None),
            NodeInfo("_getSRValveState", "GetSRValveState", None),
            NodeInfo("_setSRValveState", "SetSRValveState", None),
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

    def setPressureLimit(self, newPressureLimit):
        """It sets the pressure limit for SF10 operation.

        Parameters
        ----------
        newPressureLimit : float
            It is the new pressure limit

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.pressureLimit.set_value(
                ua.Variant(newPressureLimit, ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getPressureLimit(self):
        """It gives the current pressure limit set on the device.

        Returns
        -------
        float
            It is the current pressure limit
        """
        return self.pressureLimit.get_value()

    def getPressureLimitNode(self):
        """
        This method returns the id of the SF10 PressureLimit variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SF10 PressureLimit variable in the OPC UA
            Address Space.

        """
        return self.pressureLimit

    def setOscillation(self, speedul, displacement):
        """
        It configures the oscillation parameters for SF10 scillation
        mode operation.

        Parameters
        ----------
        speedul : integer
            It is the speed at which the pump oscillates
        displacement : integer
            It is the amount of volume that is oscillated back and forth

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._setOscillation,
                ua.Variant(speedul, ua.uatypes.VariantType.Int16),
                ua.Variant(displacement, ua.uatypes.VariantType.Int16),
            )
            return True
        except:
            return False

    def getOscillation(self):
        """
        It gives the parameters set for the SF10 Oscillation mode.

        Returns
        -------
        list
            It returns a list with the speedul and displacement parameters.
        """
        return self.root.call_method(self._getOscillation)

    def setBPRRegulationPressure(self, newPressure):
        """It sets the pressure for the Back Pressure Regulation
        mode.

        Parameters
        ----------
        newPressure : float
            It is the new pressure for the regulator.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.bprRegulationPression.set_value(
                ua.Variant(newPressure, ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getBPRRegulationPressure(self):
        """It gives the current pressure set for Back Pressure Regulation mode.

        Returns
        -------
        float
            It is the current pressure set.
        """
        return self.bprRegulationPression.get_value()

    def getBPRRegulationPressionNode(self):
        """
        This method returns the id of the SF10 BPRRegulationPression variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SF10 BPRRegulationPression variable in the OPC UA
            Address Space.

        """
        return self.bprRegulationPression

    def getPumpPressure(self):
        """It gives the current pressure on the pump

        Returns
        -------
        float
            It is the pump pressure
        """
        return self.pumpPressure.get_value()

    def getPumpPressureNode(self):
        """
        This method returns the id of the SF10 Pumppressure variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SF10 PumpPressure variable in the OPC UA
            Address Space.

        """
        return self.pumpPressure

    def setOperationMode(self, newMode):
        """It sets the Pump Mode to Pressure Regulation.
        You can switch between Flow, Pressure Regulation (REG), DOSE, RAMP, GAS.

        Parameters
        ----------
        newMode : integer
            It is the new operation mode.
            0 means Constant flow rate mode
            1 means Pressure Regulation mode
            2 means volume dose regulation mode
            3 means ramp flowrate mode
            4 means gas mode
            5 means Oscillation Mode

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._setOperationMode, ua.Variant(newMode, ua.uatypes.VariantType.Byte)
            )
            return True
        except:
            return False

    def getOperationMode(self):
        """It gives the current operation mode set on SF10 pump.

        Returns
        -------
        integer
            It is the current operation mode
            0 means Constant flow rate mode
            1 means Pressure Regulation mode
            2 means volume dose regulation mode
            3 means ramp flowrate mode
            4 means gas mode
            5 means Oscillation Mode

        """
        return self.root.call_method(self._getOperationMode)

    def setGasFlowRate(self, newFlowRate):
        """It sets the flow rate for gas mode operation

        Parameters
        ----------
        newFlowRate : float
            It is the new flow rate

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.gasFlowRate.set_value(
                ua.Variant(newFlowRate, ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getGasFlowRate(self):
        """It gives the current flow rate for gas operation mode

        Returns
        -------
        float
            It is the current flow rate.
        """
        return self.gasFlowRate.get_value()

    def getGasFlowRateNode(self):
        """
        This method returns the id of the SF10 GasFlowRate variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SF10 GasFlowRate variable in the OPC UA
            Address Space.

        """
        return self.gasFlowRate

    def setFlowRate(self, newFlowRate):
        """It sets the flow rate for constant flow rate mode.

        Parameters
        ----------
        newFlowRate : float
            It is the new flow rate.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.flowrate.set_value(
                ua.Variant(newFlowRate, ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getFlowRate(self):
        """
        It gives the current flow rate for constant flow rate operation
        mode.

        Returns
        -------
        float
            It is the current flow rate.
        """
        return self.flowrate.get_value()

    def getFlowRateNode(self):
        """
        This method returns the id of the FlowRate variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SF10 FlowRate variable in the OPC UA
            Address Space.

        """
        return self.flowrate

    def setSRValveState(self, newState):
        """It sets the state of the solvent or reagent selection valve.

        Parameters
        ----------
        newState : bool
            This is the new valve state.
            True means the pump will deliver reagent.
            False means the pump will deliver solvent.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.srValveState.set_value(
                ua.Variant(newState, ua.uatypes.VariantType.Boolean)
            )
            return True
        except:
            return False

    def getSRValveState(self):
        """It gives the current state for the solvent-reagent selection valve.

        Returns
        -------
        bool
            This is the current valve state.
            True means the pump delivers reagent.
            False means the pump delivers solvent.

        """
        return self.srValveState.get_value()

    def getSRValveStateNode(self):
        """
        This method returns the id of the SRValveState variable. This
        id allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the SF10 SRValveState variable in the OPC UA
            Address Space.

        """
        return self.srValveState

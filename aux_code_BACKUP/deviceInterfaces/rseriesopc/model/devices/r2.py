from opcua import ua, Node
import logging

from rseriesopc.model.devices.pump import PumpType
from rseriesopc.model.devices.module import ModuleType
from rseriesopc.model.base import NodeInfo

log = logging.getLogger("rseriesclient." + __name__)


class R2Type(ModuleType):
    """
    A R2Type object contains all of the methods and object to monitor and
    control a R2 Module in the R-Series Controller.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the R2 object id in the OPC UA Address Space.
    maxPressureLimit : opcua.Node
        It is the id of the maxPressureLimit variable in the OPC UA Address
        Space. This contains information about the maximum pressure limit
        allowed for the pump.
    pressureLimit : opcua.Node
        It is the pressureLimit variable id in the OPC UA Address Space. This
        is the current pressure limit set point in system.
    pumpsPressure : opcua.Node
        It is the measured pumpsPressure variable id in the OPC UA Address
        Space.
    pumpsPerformance : opcua.Node
        It is the id of PumpsPerformance variable in the OPC UA Address Space.
    pump : dict of PumpType
        It is a dictionary of pumps. Each dictionary entry contains the
        methods, object and variable necesary to control and monitor a pump.
        The pumps are alphabetic labeled, so the key of the dict are
        ['A', 'B'].

    """

    _getPressureLimit: Node
    _getPumpPerformance: Node
    _getPumpPressures: Node
    maxPressureLimit: Node
    pressureLimit: Node
    pumpsPerformance: Node
    pumpsPressures: Node
    _setPressureLimit: Node

    def __init__(self, root):
        super().__init__(root)
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_getPressureLimit", "GetMaxPressureLimit", None),
            NodeInfo("_getPumpPerformance", "GetPumpsPerformance", None),
            NodeInfo("_getPumpPressures", "GetPumpsPressures", None),
            NodeInfo("maxPressureLimit", "MaxPressureLimit", None),
            NodeInfo("pressureLimit", "PressureLimit", None),
            NodeInfo("pumpsPerformance", "PumpsPerformance", None),
            NodeInfo("pumpsPressures", "PumpsPressures", None),
            NodeInfo("_setPressureLimit", "SetMaxPressureLimit", None),
        ]

        log.debug("{0} : hydrating variables".format(__class__.__name__))
        for item in variables:
            node, browse_names = self._get_interest_ua_node(
                item.name, item.prototype, browse_names
            )
            setattr(self, item.variable, node)

        pattern, prototype = "Pump", PumpType
        self.pumps, browse_names = self._make_dictionaries(
            pattern, prototype, browse_names
        )

        for browse_name in browse_names:
            log.warning(
                "{0}: {1} was not caught".format(__class__.__name__, browse_name)
            )

    def setMaxPressureLimit(self, pressure):
        """
        Sets the maximum pressure admited in the pumps by the system

        Parameters
        ----------
        pressure : float
            It is the new maximum pressure limit for all of the pumps.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._setPressureLimit,
                ua.Variant(pressure, ua.uatypes.VariantType.Float),
            )
            return True
        except:
            return False

    # getters
    def _getPump(self, idx):
        if idx in self.pumps:
            return self.pumps.get(idx)
        else:
            print("Pump{} is not found".format(idx))
            return None

    def getPumpA(self):
        """
        It returns the pump A object.

        Returns
        -------
        PumpType
            It is the the object that contains the methods, objects and
            variables to control and monitor the Pump A.

        """
        return self._getPump("A")

    def getPumpB(self):
        """
        It gives the pump B object.

        Returns
        -------
        PumpType
            It is the object that contains the methods, objects and
            variables to control and monitor the Pump B.

        """
        return self._getPump("B")

    # def getPumps(self):
    #     """
    #     It gives the pumps dictionary.

    #     Returns
    #     -------
    #     dict of PumpType
    #         It is the list of pumps.

    #     """
    #     return self.pump

    def getMaxPressureLimit(self):
        """
        It gives the maximum pressure limit setted in the module.

        Returns
        -------
        float
            It is the pressute limit in mbar.

        """
        return self.root.call_method(self._getPressureLimit)

    def getPumpsPressures(self):
        """
        It returns the pressures of the pumps and the R2 Module.

        Returns
        -------
        list
            It is a list with the pressure each pump and the system.
            list()[0] is the module Pressure
            list()[1] is the pumpA pressure
            list()[2] is the pumpB pressure

        """
        res = self.pumpsPressures.get_value()
        res.reverse()
        return res

    def getPumpsPressuresNode(self):
        """
        This method returns the id of the pumps pressures variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the PumpsPressures variable in the OPC UA Address
            Space.

        """
        return self.pumpsPressures

    def getPressureLimit(self):
        """
        It gives the pressure limit value.

        Returns
        -------
        float
            It is the actual pressure limit.
        """
        return self.pressureLimit.get_value()

    def setPressureLimit(self, pressure):
        """It sets the pressure limit value.

        Parameters
        ----------
        pressure : float
            It is the new pressure to set.

        Returns
        -------
        bool
            It is true if the value set was successfully aplied.
        """
        try:
            self.pressureLimit.set_value(
                ua.Variant(pressure, ua.uatypes.VariantType.Float)
            )
            return True
        except:
            return False

    def getPressureLimitNode(self):
        """
        This method returns the id of the pressure limit variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the pressureLimit variable in the OPC UA Address
            Space.

        """
        return self.pressureLimit

    def getMaxPressureLimitNode(self):
        """
        This method returns the id of the max pressure limit variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the maxPressureLimit variable in the OPC UA
            Address Space.

        """
        return self.maxPressureLimit

    def getPumpsPerformance(self):
        """
        It returns the performance of all of the pumps.

        Returns
        -------
        list
            It is a list with the performance of each pump.
            [0] is the pumpA performance
            [1] is the pumpB performance

        """
        res = self.pumpsPerformance.get_value()
        res.reverse()
        return res

    def getPumpsPerformanceNode(self):
        """
        This method returns the id of the pumps performance variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of PumpsPerformance variable in the OPC UA Address
            Space.

        """
        return self.pumpsPreformance

from opcua import ua, Node
import logging

from rseriesopc.model.devices.r4 import R4Type
from rseriesopc.model.devices.uv150 import UV150Type
from rseriesopc.model.devices.vbfr import VBFRType
from rseriesopc.model.devices.detector import DetectorType
from rseriesopc.model.devices.autosampler import AutoSamplerType
from rseriesopc.model.devices.chiller import ChillerType
from rseriesopc.model.devices.factories import ModuleTypeFactory
from rseriesopc.model.devices.ion import IONType
from rseriesopc.model.base import BaseNode, NodeInfo

log = logging.getLogger("rseriesclient." + __name__)


class ManualControlType(BaseNode):
    """
    The ManualControlType class implements the low level functions for
    controlling the components of the R-Series Machine.

    This class allows the user to write and run scripts for custom automation
    routines.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        This is the parent node in the OPC UA Address Space.
    module : list of a reagent source type
        It is a collection of ModuleType objects. Those objects contains the
        reagent source modules and the methods related to control the pumps.
    r4 : dict of R4Type
        It is a collection of R4Type objects. Those objects contains the R4
        modules and the methods related to set the power and temperatures of
        the reactors.
    uv150 : UV150Type
        This is an object to control UV150 reactors.
    autoSampler : AutoSamplerType
        It is an object that implements the methods to control the AutoSampler
        module
    wcValveState : opcua.Node
        It is an the WCValveState variable in the OPC UA address space. It can
        control the Waste/Collect valve.
    chiller : dict of ChillerType
        It is a collection of ChillerType bbjects. Those objects contains the
        chiller modules and the methods related to control and monitoring them.

    """

    autoSampler: AutoSamplerType
    uvDet: DetectorType
    _getWCValveState: Node
    ion: IONType
    _setWCValveState: Node
    _startManualControl: Node
    _stopManualControl: Node
    uv150: UV150Type
    vbfr: VBFRType
    wcValveState: Node

    def __init__(self, root: Node):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("autoSampler", "AutoSampler", AutoSamplerType),
            NodeInfo("uvDet", "Detector", DetectorType),
            NodeInfo("_getWCValveState", "GetWCValveState", None),
            NodeInfo("ion", "ION", IONType),
            NodeInfo("_setWCValveState", "SetWCValveState", None),
            NodeInfo("_startManualControl", "StartManualControl", None),
            NodeInfo("_stopManualControl", "StopAll", None),
            NodeInfo("uv150", "UV150", UV150Type),
            NodeInfo("vbfr", "VBFR", VBFRType),
            NodeInfo("wcValveState", "WCValveState", None),
        ]

        log.debug("{0} : hydrating variables".format(__class__.__name__))
        for item in variables:
            node, browse_names = self._get_interest_ua_node(
                item.name, item.prototype, browse_names
            )
            setattr(self, item.variable, node)

        self.modules = list()
        pattern, prototype = ["M", "_"], ModuleTypeFactory.makeReagentSourceType
        for name in list(
            filter(
                lambda module: all(tag in module for tag in pattern),
                browse_names.keys(),
            )
        ):
            item, browse_names = self._get_interest_ua_node(
                name, prototype, browse_names
            )
            self.modules.append(item)

        pattern, prototype = "Chiller", ChillerType
        self.chillers, browse_names = self._make_dictionaries(
            pattern, prototype, browse_names
        )
        pattern, prototype = "R4", R4Type
        self.r4, browse_names = self._make_dictionaries(
            pattern, prototype, browse_names
        )

        for browse_name in browse_names:
            log.warning(
                "{0}: {1} was not caught".format(__class__.__name__, browse_name)
            )

    def setWCValveState(self, state):
        """
        It sets the state of the valve.

        Parameters
        ----------
        state : bool
            True means fluid from Collect to Waste.
            Else, the fluid moves in the another way.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.wcValveState.set_value(
                ua.Variant(state, ua.uatypes.VariantType.Boolean)
            )
            return True
        except:
            return False

    def getWCValveState(self):
        """
        This gives the state of the valve

        Returns
        -------
        bool
            True means liquid from Collect to Waste
            Else, the liquid moves in the another way.

        """
        return self.wcValveState.get_value()

    def getWCValveStateNode(self):
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
        return self.wcValveState

    def startManualControl(self):
        """
        This function allows the user to reach the control of the machine from
        this Python Client.
        It starts the manual control when the machine gives back a
        confirmation.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._startManualControl)
            return True
        except:
            return False

    def stopAll(self):
        """
        This function stops the manual control of the Vapourtec R-Series Flow
        Chemistry Machine.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._stopManualControl)
            return True
        except:
            return False

    # getters
    def getR4(self):
        """
        It returns a dictionary with all R4 modules.

        Returns
        -------
        dict
            These are all of the R4 modules.

        """
        return self.r4

    def getR4I(self):
        """
        If there is a R4 Module, this gives that node.

        Returns
        -------
        R4Type or None
            If R4Module is in RSeries, it is returned.
            Else, None is returned

        """
        return self._getR4Value("I")

    def getR4II(self):
        """
        If there is a second R4 Module, this gives that node.

        Returns
        -------
        R4Type or None
            If a second R4Module is in RSeries, it is returned.
            Else, None is returned

        """
        return self._getR4Value("II")

    def _getR4Value(self, key):
        """
        It looks for a R4 Module in R4 Modules dictionary and returns that.

        Parameters
        ----------
        key : string
            It is the name of the R4 Module to look up.

        Returns
        -------
        res : R4Type or None
            If the R4 Module is in the r4 Modules dictionary, it is returned.
            Else, None is returned.
        """
        res = self._getDictValue(self.r4, key)
        if res is None:
            log.info("R4" + key + " is not found")
            print("R4" + key + " is not found")
            print("Check R4 module connection and load manual control again.")
        return res

    def getUV150(self):
        """
        If there is a UV150 module, this gives that node.

        Returns
        -------
        UV150Type or None
            If a UV150module is in RSeries, it is returned.

        """
        return self.uv150

    def getAutoSampler(self):
        """
        If there is an AutoSampler module, this gives that node.

        Returns
        -------
        AutoSamplerType or None
            If the AutoSmapler is in RSeries, it is returned.

        """
        return self.autoSampler

    def _getDictValue(self, dic, key):
        """
        Safety function to look up a particular key in a dictionary

        Parameters
        ----------
        dic : dict
            It is the dictionary where the key is looked up.
        key : string
            It is the key to look up.

        Returns
        -------
            If dic has the key, it returns the value of the dictionary in key.
            Else, it returns None.

        """
        try:
            return dic[key]
        except KeyError:
            return None

    def getDetector(self):
        """
        It returns an external detector object.

        Returns
        -------
        DetectorType
            It is the detector.

        """
        return self.uvDet

    def getVBFR(self):
        """
        It gives the Variable Bed Flow Reactor object.

        Returns
        -------
        VBFRType
            It is the VBFR.

        """
        return self.vbfr

    def getChillers(self):
        """
        It returns a dictionary with all Chillers modules.

        Returns
        -------
        dict
            These are all of the Chillers modules.

        """
        self.chillers

    def getChiller1(self):
        """
        If there is a Chiller, this gives that node.

        Returns
        -------
        ChillerType or None
            If Chiller is in RSeries, it is returned.
            Else, None is returned

        """
        return self._getChillerValue("1")

    def getChiller2(self):
        """
        If there is a Chiller, this gives that node.

        Returns
        -------
        ChillerType or None
            If Chiller is in RSeries, it is returned.
            Else, None is returned

        """
        return self._getChillerValue("2")

    def _getChillerValue(self, key):
        """
        It looks for a R4 Module in R4 Modules dictionary and returns that.

        Parameters
        ----------
        key : string
            It is the name of the R4 Module to look up.

        Returns
        -------
        res : ChillerType or None
            If the Chiller is in the chiller dictionary, it is returned.
            Else, None is returned.
        """
        res = self._getDictValue(self.chillers, key)
        if res is None:
            log.info("Chiller" + key + " is not found")
            print("Chiller" + key + " is not found")
            print("Check Chiller module connection and load manual control again.")
        return res

    def getAllModules(self):
        return self.modules

    def getModule(self, index):
        if index >= len(self.modules):
            return None
        return self.modules[index]

from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class AutoSamplerType(BaseNode):
    """
    The AutoSamplerType class instantiates Autosampler objects.
    This objects allows a high level communication to send orders to the
    GX271 system, connected to the R-Series Controller.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root: opcua.Node
        This contains the id of the Autosampler in the OPC UA Address Space.
    collectionValveState: opcua.Node
        It is the id of the collection valve variable in the OPC UA Address
        Space.

    """

    _goHome: None
    _primeSampleLoop: None
    _lowerSyringePump: None
    _riseSyringePump: None
    _switchValveToCollect: None
    _cleansSampleLoops: None
    _autoSampleGoToPortA: None
    _lowerNeedleOverPortA: None
    _lowerNeedleIntoPortA: None
    _loadLoopVolumeFromVial: None
    _goToVialForCollection: None
    _cleanLoop: None
    _cleanNeedle: None
    _stopRoutines: None
    collectionValveState: None

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }
        variables = [
            NodeInfo("_goHome", "GoHome", None),
            NodeInfo("_primeSampleLoop", "PrimeSampleLoop", None),
            NodeInfo("_lowerSyringePump", "LowerSyringePump", None),
            NodeInfo("_riseSyringePump", "RiseSyringePump", None),
            NodeInfo("_switchValveToCollect", "SwitchValveToCollect", None),
            NodeInfo("_cleansSampleLoops", "CleansSampleLoops", None),
            NodeInfo("_autoSampleGoToPortA", "GoToPortA", None),
            NodeInfo("_lowerNeedleOverPortA", "LowerNeedleOverPortA", None),
            NodeInfo("_lowerNeedleIntoPortA", "LowerNeedleIntoPortA", None),
            NodeInfo("_loadLoopVolumeFromVial", "LoadLoopVolumeFromVial", None),
            NodeInfo("_goToVialForCollection", "GoToVialForCollection", None),
            NodeInfo("_cleanLoop", "CleanLoop", None),
            NodeInfo("_cleanNeedle", "CleanNeedle", None),
            NodeInfo("_stopRoutines", "StopRoutines", None),
            NodeInfo("collectionValveState", "CollectionValveState", None),
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

    def getCollectionValveState(self):
        """
        It gives if the valve is in collection or waste direction.

        Returns
        -------
        Bool
            This is the valve position. If it is true, the valve is in collect
            position.
            Else, the valve is in waste position.

        """
        return self.collectionValveState.get_value()

    def setCollectionValveState(self, state):
        """
        It sets the autosampler valve in collection or waste position.

        Parameters
        ----------
        state : Bool
            This is the postion of the valve. When it is true, the valve will
            be set on collect position. Otherwise it will be set on waste
            position.

        Returns
        -------
        None.

        """
        self.collectionValveState.set_value(
            ua.Variant(state, ua.uatypes.VariantType.Boolean)
        )

    def getCollectionValveStateNode(self):
        """
        This method returns the id of the colection valve variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py


        Returns
        -------
        opcua.Node
            This is the id of the collection valve variable in the OPC UA
            Address Space.

        """
        return self.collectionValveState

    def goHome(self):
        """
        It moves the Autosampler arm to home position.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._goHome)
            return True
        except:
            return False

    def primeSampleLoop(self):
        """
        It fills the syringe tube with solvent. The Syringe must be primed
        before running the first reaction and when the solvent needs to be
        changed.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._primeSampleLoop)
            return True
        except:
            return False

    def lowerSyringePump(self):
        """
        Use this function when you need to replace the syringe.
        Refer to section 4.11 Syringe pump installation.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._lowerSyringePump)
            return True
        except:
            return False

    def riseSyringePump(self):
        """
        Use this function when you need to install the syringe.
        Refer to section 4.11 Syringe pump installation.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._riseSyringePump)
            return True
        except:
            return False

    def switchValveToCollect(self):
        """
        It switches the Waste/Collect to Collect and a few seconds later, the
        valve comes back to waste in an autmatic way.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._switchValveToCollect)
            return True
        except:
            return False

    def cleansSampleLoops(self):
        """
        The probe will inject the solvent from the reservoir and flush the
        sample loops with the solvent.
        Depend on the setup, it will activate the number of sample loops as
        per the experiment setup in R-series controller.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._cleansSampleLoops)
            return True
        except:
            return False

    def goToPortA(self):
        """
        It moves the autosampler arm to port A.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._autoSampleGoToPortA)
            return True
        except:
            return False

    def lowerNeedleOverPortA(self):
        """
        It moves the needle down over Port A.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._lowerNeedleOverPortA)
            return True
        except:
            return False

    def lowerNeedleIntoPortA(self):
        """
        It moves the needle down into Port A.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._lowerNeedleIntoPortA)
            return True
        except:
            return False

    def loadLoopVolumeFromVial(self, channel, position, volume):
        """
        It moves the arm to a given position and dispenses product.

        Parameters
        ----------
        channel : integer
            This is the rack index.
        position : integer
            It is the position in the rack where the product will be
            dispensed.
        volume : integer
            It is the amount of liquid in ml to dispense into the loop.

        Returns
        -------
        bool
            It is false when the position is bigger than allowed.
            Otherwise, it is true.

        """
        try:
            self.root.call_method(
                self._loadLoopVolumeFromVial,
                ua.Variant(channel, ua.uatypes.VariantType.Int16),
                ua.Variant(position, ua.uatypes.VariantType.Int16),
                ua.Variant(volume, ua.uatypes.VariantType.Int16),
            )
            return True
        except:
            return False

    def goToVialForCollection(self, site, time):
        """
        It moves the autosampler arm to the especified and take a sample
        during a given time.

        Parameters
        ----------
        site : integer
            It is the position where the autosampler collect from.
        time : float
            It is the time to collect in seconds.

        Returns
        -------
        bool
            It is false when the site is bigger than allowed.
            Otherwise, this is true.

        """
        try:
            self.root.call_method(
                self._goToVialForCollection,
                ua.Variant(site, ua.uatypes.VariantType.Int16),
                ua.Variant(time, ua.uatypes.VariantType.Float),
            )
            return True
        except:
            return False

    def cleanLoop(self, channel):
        """
        It cleans the channel loop

        Parameters
        ----------
        channel : integer
            This is the channel that will be cleaned.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._cleanLoop, ua.Variant(channel, ua.uatypes.VariantType.Int16)
            )
            return True
        except:
            return False

    def cleanNeedle(self):
        """
        It rinses the needle.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._cleanNeedle)
            return True
        except:
            return False

    def stopRoutines(self):
        """
        This method stops any routine execution.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._stopRoutines)
            return True
        except:
            return False

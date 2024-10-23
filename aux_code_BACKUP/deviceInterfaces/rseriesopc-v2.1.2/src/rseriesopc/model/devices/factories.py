from rseriesopc.model.devices.r2 import R2Type
from rseriesopc.model.devices.sf import SFType
from rseriesopc.model.devices.mfc import MFCType
from rseriesopc.model.devices.azura import AzuraPumpType
from rseriesopc.model.devices.syringe import SyringePumpType

import logging

log = logging.getLogger("rseriesclient." + __name__)


class ModuleTypeFactory:
    """
    It is a factory that returns the right type of reagent source class
    when makeReagentSourceType is called.
    The ModuleType class has any members.
    """

    def isAReagentSourceModule(node):
        """It reports if the selected node is a module that can be
        created by this object or not.

        Parameters
        ----------
        node : opcua.Node
            It is the node that wants to be readed from OPC UA address space.

        Returns
        -------
        bool
            It is True when the node is a reagent source object.
            Otherwise, it is False.
        """
        name = node.get_display_name().Text
        if all(tag in name for tag in ["M", "_"]):
            return True
        return False

    def makeReagentSourceType(node):
        """It returns an object of one of the reagent source types.

        Parameters
        ----------
        node : opcua.Node
            It is the node to be readed from OPC UA address space.

        Returns
        -------
        R2Type, SF10Type, MFCType, AzuraPumpType, SyringePumpType or None
            It is the reagent source type object
        """
        name = node.get_display_name().Text
        if "R2" in name:
            return R2Type(node)
        if "SF10" in name:
            return SFType(node)
        if "MFC" in name:
            return MFCType(node)
        if "Azura" in name:
            return AzuraPumpType(node)
        if "Syringe" in name:
            return SyringePumpType(node)

        log.info("ReagentTypeFactory: {0} was not caught".format(name))
        return None

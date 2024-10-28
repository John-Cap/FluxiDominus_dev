from opcua import Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class EquipmentIdentificationType(BaseNode):
    """
    An EquipmentIdentificationType object has the hardware identification
    information.

    Parameters
    ----------
    root : opcua.Node
        It is the id of this node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the OPC-UA Address Space of this object
    harwareRevision : opcua.Node
        It is a OPC-UA variable.
        It has the hardware revision data in a String value.
    equipmentIdentifier : opcua.Node
        It is a OPC-UA variable.
        It has the equipment identifier data in a String value.
    equipmentManufacturer : opcua.Node
        It is a OPC-UA variable.
        It contains the equpiment manufacturer data in a String value.

    """

    _hardwareRevision: Node
    _equipmentIdentifier: Node
    _equipmentManufacturer: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_hardwareRevision", "HardwareRevision", None),
            NodeInfo("_equipmentIdentifier", "EquipmentIdentifier", None),
            NodeInfo("_equipmentManufacturer", "EquipmentManufacturer", None),
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

    def hardwareRevision(self):
        """
        This gives the hardware version.

        Returns
        -------
        String
            This is the hardware version.
            The format of the harware revision is vXX.YY.ZZ, where :

            * v is an arbitrary character
            * XX is a major change
            * YY is a minor change
            * ZZ is a patch

        """
        return self._hardwareRevision.get_value()

    def equipmentIdentifier(self):
        """
        This gives the name of the machine.

        Returns
        -------
        String
            This machine is an RSeries Flow Chemistry.

        """
        return self._equipmentIdentifier.get_value()

    def equipmentManufacturer(self):
        """
        This function returns Vapourtec.
        This is the buider company of the machine.

        Returns
        -------
        String
            Vapourtec design and made the RSeries machine.

        """
        return self._equipmentManufacturer.get_value()

import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.identification.softwareIdentification import (
    SoftwareIdentificationType,
)
from rseriesopc.model.identification.equipmentIdentification import (
    EquipmentIdentificationType,
)
from rseriesopc.model.base import BaseNode, NodeInfo


class IdentificationType(BaseNode):
    """
    IdentificationType is an object that gives the machine information.
    It has a opc Node that contains its opc address.
    Also has two components that gives the software and hardware information.
    The data could be accesed by itself, by calling this class methods or
    by calling each component methods.

    Parameters
    ----------
    root : opcua.Node
        It is the id of this node in the OPC UA Address Space.

    Attributes
    ----------
    root: opcua.Node
        This has the OPC-UA information.
    equipmentIdentification: EquipmentIdentificationType
        It contains the hardware information.
    softwareIdentification: SoftwareIdentificationType
        It has the software data.
    """

    equipmentIdentification: EquipmentIdentificationType
    machineSoftware: SoftwareIdentificationType

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo(
                "equipmentIdentification",
                "EquipmentIdentification",
                EquipmentIdentificationType,
            ),
            NodeInfo(
                "machineSoftware", "SoftwareIdentification", SoftwareIdentificationType
            ),
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

    def getSoftwareVersion(self):
        """
        This function gives the version of the software at the controller.

        Returns
        -------
        String
            This is the software version.
            The format of the software version is vXX.YY.ZZ, where:

            * v is an arbitrary identifier
            * XX is a major change.
            * YY is a minor change.
            * ZZ is a patch.

        """
        return self.machineSoftware.softwareVersion()

    def getSoftwareIdentifier(self):
        """
        This function gives the human readable name of the software at the
        controller.

        Returns
        -------
        String
            This is the software name identifier.

        """
        return self.machineSoftware.softwareIdentifier()

    def getSoftwareDeveloper(self):
        """
        This function gives the name of the software developer company.

        Returns
        -------
        String
            The controller's software was masde by Emtech.

        """
        return self.machineSoftware.softwareDeveloper()

    def getHardwareRevision(self):
        """
        This funtion gives the hardware version.

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
        return self.equipmentIdentification.hardwareRevision()

    def getEquipmentManufacturer(self):
        """
        This function returns Vapourtec.
        This is the buider company of the machine.

        Returns
        -------
        String
            Vapourtec design and made the RSeries machine.

        """
        return self.equipmentIdentification.equipmentManufacturer()

    def getEquipmentIdentifier(self):
        """
        This function gives the name of the machine.

        Returns
        -------
        String
            This machine is an RSeries Flow Chemistry.

        """
        return self.equipmentIdentification.equipmentIdentifier()

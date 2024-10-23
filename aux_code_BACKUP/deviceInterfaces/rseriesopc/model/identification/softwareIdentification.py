from opcua import Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class SoftwareIdentificationType(BaseNode):
    """
    The SoftwareIdentificationType class contains information
    about the software development.

    Parameters
    ----------
    root : opcua.Node
        It is the id of this node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the OPC-UA Address Space information
    softwareRevision : opcua.Node
        It is a OPC-UA variable. This contains the software revision
        version in a String value.
    softwareIdentifier : opcua.Node
        It is a OPC-UA varialbe.
        This variable contains the software identifier in a String value.
    softwareDeveloper : opcua.Node
        It is a OPC-UA variable.
        It contains the software developer in a String value.

    """

    _softwareRevision: Node
    _softwareIdentifier: Node
    _softwareDeveloper: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_softwareRevision", "SoftwareVersion", None),
            NodeInfo("_softwareIdentifier", "SoftwareIdentifier", None),
            NodeInfo("_softwareDeveloper", "SoftwareDeveloper", None),
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

    def softwareVersion(self):
        """
        This gives the version of the software at the controller.

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
        return self._softwareRevision.get_value()

    def softwareIdentifier(self):
        """
        This gives a human readable name of the software at the
        controller.

        Returns
        -------
        String
            This is the software name identifier.

        """
        return self._softwareIdentifier.get_value()

    def softwareDeveloper(self):
        """
        This gives the name of the software developer company.

        Returns
        -------
        String
            The controller's software was masde by Emtech.

        """
        return self._softwareDeveloper.get_value()

    pass

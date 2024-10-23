from opcua import Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class MonitoringType(BaseNode):
    """
    MonitoringType class is an object to get information about the
    system status.

    Parameters
    ----------
    root : opcua.Node
        It is the id of this node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the OPC-UA Address Space information about this object.
    rSeriesStaus : StatusType
        It is an object to get the status of the R-Series machine.
    """

    activeExperiment: Node
    _getConnectionStatus: Node
    _getLoopStatus: Node
    _getEnableReactionStatus: Node
    _getAllVariablesStatus: Node
    _getCollectionStatus: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("activeExperiment", "ActiveExperiment", None),
            NodeInfo("_getConnectionStatus", "GetConnectionStatus", None),
            NodeInfo("_getLoopStatus", "GetLoopStatus", None),
            NodeInfo("_getEnableReactionStatus", "GetEnableReactionStatus", None),
            NodeInfo("_getAllVariablesStatus", "GetAllVariablesStatus", None),
            NodeInfo("_getCollectionStatus", "GetCollectionStatus", None),
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

    # TODO make monitoring methods

    def getRSeriesStatus(self):
        """
        It gives the RSeries status object in this machine.

        Returns
        -------
        StatusType
            It is the status node.
            This node will give access to call methods in StatusType.

        """
        return self.rSeriesStatus

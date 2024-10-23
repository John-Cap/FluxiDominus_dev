from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class ExperimentStatisticType(BaseNode):
    """
    An ExperimentStatisticsType object contains the methods to obtain the
    statistics information about the loaded experiment.

    Parameters
    ----------
    root : opcua.Node
        It is the id of the ExperimentStatistics in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the ExperimentStatistics in the OPC UA Address Space.

    """

    _getReactionStatistics: Node
    _getExperimentGraphs: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in self.root.get_children()
        }

        variables = [
            NodeInfo("_getReactionStatistics", "GetReactionStatistics", None),
            NodeInfo("_getExperimentGraphs", "GetExperimentGraphs", None),
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

    def getReactionStatistics(self, reaction):
        """
        It gives the temporal statistic of a given reaction.

        Parameters
        ----------
        reaction: integer
            It is the index of the reacction in ReactionList

        Returns
        -------
        JSON or None.
            These are the statistics of the selected reaction.
            If the reaction is not in the RactionList, it returns None.

        """
        return self.root.call_method(
            self._getReactionStatistics,
            ua.Variant(reaction, ua.uatypes.VariantType.UInt16),
        )

    def getExperimentGraphs(self, filename=None):
        """
        It gives the graphs from the R-Series Controller. This graph could
        be stored in a file or could be returned as a list.

        Parameters
        ----------
        filename : string, optional
            It is the path where the file will be stored. The default is None.

        Returns
        -------
        rspList : list of list of string or None.
            It is the list with all graphs.\n
            If a filename is given, the response of this method is None and
            the graphs will be stored in a file.

        """
        rspList = []
        stopLoop = False
        while stopLoop == False:
            rsp = self.root.call_method(self._getExperimentGraphs)
            rsp = rsp.split(",")
            if "Time" in rsp:
                stopLoop = True
                rspList.insert(0, rsp)
            else:
                rspList.append(rsp)

        if filename:
            with open(filename, "w") as f:
                f.write(rspList)
            return None
        else:
            return rspList

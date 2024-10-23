import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo
from rseriesopc.model.experiment.experimentSetup import ExperimentSetupType
from rseriesopc.model.experiment.reactionManager import ReactionManagerType
from rseriesopc.model.experiment.experimentStatistics import ExperimentStatisticType


class ExperimentType(BaseNode):
    """
    ExperimentType class is an object that contains the high level commands to
    work with the R-Series machine.

    It has the experiment settings information and the reaction manager
    methods to command the list of reactions that are running in the system.

    Also, it gives statistics about the experiments.

    Parameters
    ----------
    root : opcua.Node
        It is the id of this node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the experiment object in the OPC UA Address Space.
    experimentSetup : ExperimentSetupType
        It is the id of the experiment setup object in the OPC UA Address
        Space.
    reactionManager : ReactionManagerType
        It is the id of the reaction manager object in the OPC UA Address
        Space.
    statistics : ExperimentStatisticType
        It is the id of the experiment statistics in the OPC UA Address Space.

    """

    experimentSetup: ExperimentSetupType
    reactionManager: ReactionManagerType
    statistics: ExperimentStatisticType

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("experimentSetup", "ExperimentSetup", ExperimentSetupType),
            NodeInfo("reactionManager", "ReactionManager", ReactionManagerType),
            NodeInfo("statistics", "Statistics", ExperimentStatisticType),
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

    # getters
    def getExperimentSetup(self):
        """
        It returns the experiment setup object.

        Returns
        -------
        ExperimentSetupType
            It is the setup object.

        """
        return self.experimentSetup

    def getReactionManager(self):
        """
        It gives the Reaction Manager object.

        Returns
        -------
        ReactionManagerType
            It is the Reaction Manager object.

        """
        return self.reactionManager

    def getStatistics(self):
        """
        It gives the Experiment Statistics object

        Returns
        -------
        ExperimentStatisticsType
            It is the Statistics object.

        """
        return self.statistics

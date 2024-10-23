import logging

from rseriesopc.utils import get_interest_child
from rseriesopc.model.identification import IdentificationType
from rseriesopc.model.monitoring import MonitoringType
from rseriesopc.model.experiment.experiment import ExperimentType
from rseriesopc.model.notification import NotificationType
from rseriesopc.model.devices.manualControl import ManualControlType

from rseriesopc.model.base import BaseNode, NodeInfo

log = logging.getLogger("rseriesclient." + __name__)


class FlowChemistryType(BaseNode):
    """
    The FlowChemistry class is the representation of the whole Vapourtec
    R-Series Flow Chemistry machines.

    This OPC UA Client is based on the freeopcua. The Python OPC-UA
    documentation could be found at python-opcua.readthedocs.io.

    Parameters
    ----------
    parentNode : opcua.Node
        This is the root object of the R-Series OPC UA Server. From there, all
        of the relative information about the R-Series Flow Chemistry Machine
        will be read on connection.

    Attributes
    ----------
    root : opcua.Node
        It is the address of the R-Series machine in the OPC-UA Address Space.
    identification: IdentificationType
        It is an object to get the machine identification information.
    monitoring: MonitoringType
        It is an object that has the methods to get the data to monitor the
        R-Series status.
    experiment: ExperimentType
        It cointains the experiment settings and the reactions information.
    notification: NotificationType
        This object has address from variables for subscribe to data changes.
    manualControl: ManualControlType
        It contains all the methods for low level controlling of the R-Series
        subsystems.

    """

    identification: IdentificationType
    monitoring: MonitoringType
    experiment: ExperimentType
    notification: NotificationType
    manualControl: ManualControlType

    def __init__(self, parentNode):
        self.root = get_interest_child(parentNode, "RSeries")
        if self.root is None:
            log.warning("FlowChemistryType: RSeries Machine was not loaded")
            return

        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in self.root.get_children()
        }

        variables = [
            NodeInfo("identification", "Identification", IdentificationType),
            NodeInfo("monitoring", "Monitoring", MonitoringType),
            NodeInfo("experiment", "Experiment", ExperimentType),
            NodeInfo("notification", "Notification", NotificationType),
            NodeInfo("manualControl", "ManualControl", ManualControlType),
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

    def getIdentification(self):
        """
        It is a getter to gain easier access to the identification
        information.

        Returns
        -------
        IdentificationType
            It is the identification information of the Vapourtec RSeries Flow
            Chemistry Machine.

        """
        return self.identification

    def getMonitoring(self):
        """
        It is a getter to gain easier access to the monitoring information.

        Returns
        -------
        MonitoringType
            It is the node that contains the machine status information.

        """
        return self.monitoring

    def getExperiment(self):
        """
        It is a getter to gain easier access to the experiment information.

        Returns
        -------
        ExperimentType
            It is the node that allows the user managing the experiment
            setup and data.

        """
        return self.experiment

    def getNotification(self):
        """
        It is a getter to gain easier access to alerts.

        Returns
        -------
        NotificationType
            It is the node that emits alerts.

        """
        return self.notification

    def getManualControl(self):
        """
        It is a getter to gain easier access to manual control methods.

        Returns
        -------
        ManualControlType
            It is the manual control object.

        """
        return self.manualControl

from opcua import Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import NodeInfo, BaseNode


class NotificationType(BaseNode):
    """
    A NotificationType Object contains variables and methods related to
    equipment alerts.

    Parameters
    ----------
    root : opcua.Node
        It is the NotificationType's id in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of this object in the OPC UA Address Space.

    """

    _getEquipmentAlerts: Node
    _equipmentAlerts: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_getEquipmentAlerts", "GetEquipmentAlerts", None),
            NodeInfo("_equipmentAlerts", "EquipmentAlerts", None),
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

    def getEquipmentAlerts(self):
        """
        It gives the equipment status.

        The status could be one of the followings:

        SYS_OK                    = 0\n
        SYS_OVERPRESSURE_TRIP     = 1\n
        PUMPA_OVERPRESSURE_TRIP   = 2\n
        PUMPB_OVERPRESSURE_TRIP   = 3\n
        UNDERPRESSURE_TRIP        = 4\n
        PUMPA_UNDERPRESSURE_TRIP  = 5\n
        PUMPB_UNDERPRESSURE_TRIP  = 6\n
        PUMPA_LOGIC_ERROR         = 7\n
        PUMPB_LOGIC_ERROR         = 8\n
        PUMPC_OVERPRESSURE_TRIP   = 9\n
        PUMPD_OVERPRESSURE_TRIP   = 10\n
        PUMPC_UNDERPRESSURE_TRIP  = 11\n
        PUMPD_UNDERPRESSURE_TRIP  = 12\n
        PUMPC_LOGIC_ERROR         = 13\n
        PUMPD_LOGIC_ERROR         = 14

        Returns
        -------
        integer
            It is the sttatus of the equipment

        """
        return self._equipmentAlerts.get_value()

    def getEquipmentAlertsNode(self):
        """
        This method returns the id of the equipment alerts variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            It is the id of the flowRate variable in the OPC UA Address Space.

        """
        return self._equipmentAlerts

from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class UV150Type(BaseNode):
    """
    The UV150Type class instantiates UV150 objects.
    This objects allows the user to turn the UV lamp on and modify its power.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        This is the id of the UV150 in the OPC UA Address Space.
    lampPower : opcua.Node
        This is the id of the lamp power in the OPC UA Address Space.
    """

    _setLampPower: Node
    lampPower: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_setLampPower", "SetLampPower", None),
            NodeInfo("lampPower", "LampPower", None),
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

    def setLampPower(self, power):
        """
        It sets the UV150 lamp power

        Parameters
        ----------
        power : integer.
            This is the new lamp power.
            The lamp power is a percentage number, but only can be between 50
            and 100.
            To turn the lamp off, power needs to be 0.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._setLampPower, ua.Variant(power, ua.uatypes.VariantType.Byte)
            )
            return True
        except:
            return False

    def getLampPower(self):
        """
        It gets the UV150 lamp power

        Returns
        -------
        integer
            This returns an integer that is lamp power. The lamp power is a
            percentage number.

        """
        return self.lampPower.get_value()

    def getLampPowerNode(self):
        """
        This method returns the id of the Lamp Power. This id allows the user
        to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py


        Returns
        -------
        opcua.Node
            This is the id of the Lamp Power in the OPC UA Address Space.
            This id allows to subscribe the variable to monitor it.

        """
        return self.lampPower

from opcua import Node
import logging

log = logging.getLogger("rseriesclient." + __name__)


class NodeFactory:
    """
    The NodeFactory is a class of object that is provides the client the right
    type of member of a device class

    """

    node: None
    prototype: None

    def getNode(self, node: Node, prototype: object = None):
        """
        The getNode method gives an object of proto instantiated with the node argument.

        If proto is None, the node is returned.

        Parameters
        ----------
        node : Node
            This is the parameter of the prototype given.
        prototype : object, optional
            This is the prototype to instantiate a new object, by default None

        Returns
        -------
        object | Node
            This is the instantiated object of prototype.
            If prototype is None, the node will be returned.

        """

        if prototype is None:
            return node
        return prototype(node)

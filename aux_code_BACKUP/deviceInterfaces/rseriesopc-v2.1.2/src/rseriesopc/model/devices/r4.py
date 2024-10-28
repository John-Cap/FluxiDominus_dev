import logging

from rseriesopc.model.devices.reactor import ReactorType

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode


class R4Type(BaseNode):
    """
    The R4Type is an object that contains all the methods, variables and
    objects that contains the information to control and monitor the R4Modules.

    Parameters
    ----------
    root : opcua.Node
        It is the parent node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the R4 object in the OPC UA Address Space.
    reactor : dict of ReactorType
        It is a dictionary that contains all of the reactors.
        Each R4 has 4 reactors. The key of each reactor is a number from 1 to
        4.

    """

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        pattern, prototype = "Reactor", ReactorType
        self.reactor, browse_names = self._make_dictionaries(
            pattern, prototype, browse_names
        )

        for browse_name in browse_names:
            log.warning(
                "{0}: {1} was not caught".format(__class__.__name__, browse_name)
            )

    def getReactors(self):
        """
        It return a dictionary with all the reactors in R4 module.

        Returns
        -------
        dict
            This has all the reactors.

        """
        return self.reactor

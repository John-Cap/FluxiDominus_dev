import logging

from rseriesopc.model.base import BaseNode

log = logging.getLogger("rseriesclient." + __name__)


class ModuleType(BaseNode):
    """

    This is a base class for class of objects that delivers some type of
    reagent and/or solvent.

    """

    pumps: dict

    def __init__(self, root) -> None:
        self.root = root
        self.pumps = dict()
        pass

    def getPumps(self):
        """
        It gives the pumps dictionary.

        Returns
        -------
        dict of PumpType
            It is the list of pumps.

        """
        return self.pumps

    pass

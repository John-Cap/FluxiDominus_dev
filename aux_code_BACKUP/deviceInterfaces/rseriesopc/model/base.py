import logging

from rseriesopc.model.factories import NodeFactory

log = logging.getLogger("rseriesclient." + __name__)


class BaseNode:
    """
    The BaseNode class has the common methods with the tasks that every device
    has to perform in order to get the right nodes on the server side.

    """

    def _get_interest_ua_node(self, name, prototype, browse_names):
        browse_name = browse_names.pop(name, None)
        if browse_name is None:
            log.debug(
                "{0}: {1} was not found on server".format(__class__.__name__, name)
            )
            return None, browse_names
        node = self.root.get_child(browse_name)
        retVal = NodeFactory().getNode(node, prototype)
        log.debug("{0}: {1} object {2}".format(__class__.__name__, name, retVal))
        return retVal, browse_names

    def _make_dictionaries(self, pattern, prototype, browse_names):
        dictionary = dict()
        for name in list(filter(lambda tag: pattern in tag, browse_names.keys())):
            item, browse_names = self._get_interest_ua_node(
                name, prototype, browse_names
            )
            name = name.removeprefix(pattern)
            dictionary.update({name: item})
        return dictionary, browse_names


class NodeInfo:
    """
    This is an auxiliar class that allows groups variables on a standard python container.

    """

    variable: str
    name: str
    prototype: str

    def __init__(self, variableName, TagName, prototypeClass) -> None:
        self.variable = variableName
        self.name = TagName
        self.prototype = prototypeClass

from opcua import ua
import logging

log = logging.getLogger("rseriesclient." + __name__)


class StatusType:
    """
    StatusType class is an object to get the R-Series status information.

    Parameters
    ----------
    root : opcua.Node
        It is the id of this node in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the OPC UA Address Space information about this object.
    activeExperiment: opcua.Node
        It is the id of the active experiment variable in the OPC UA Address
        Space.

    """

    def __init__(self, root):
        self.root = root
        for child in self.root.get_children():
            name = child.get_browse_name().to_string()
            if "ConnectionStatus" in name:
                self._connectionStatus = child
            elif "AllVariablesStatus" in name:
                self._allVariablesStatus = child
            elif "ReactionStatus" in name:
                self._reactionStatus = child
            elif "CollectionStatus" in name:
                self._collectionStatus = child
            elif "LoopStatus" in name:
                self._loopStatus = child
            elif "ActiveExperiment" in name:
                self.activeExperiment = child
            else:
                log.info("StatusType: {0} was not caught".format(name))

    def getActiveExperiment(self):
        """
        This gives the name of the current active experiment

        Returns
        -------
        String
            This is the active experiment.

        """
        return self.activeExperiment.get_value()

    def getActiveExperimentNode(self):
        """
        This method returns the id of the active experiment variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the active variable in the OPC UA
            Address Space.

        """
        return self.activeExperiment

    def getConnectionStatus(self):
        """
        It returns the status of all possible components of the machine.

        Returns
        -------
        JSON
            It is the status of all components.

        """
        # TODO: parsing the JSON. Maybe in top level
        # status = self.root.call_method(self.connectionStatus)
        # retVal = json.loads(status)
        # 'this is a dict... to document'
        # return retVal
        return self.root.call_method(self._connectionStatus)

    def getAllVariablesStatus(self):
        """
        It gives the status of all the variables present in the OPC UA Server.

        Returns
        -------
        JSON
            It is the variables status.

        """
        # TODO: parse the JSON
        return self.root.call_method(self._allVariablesStatus)

    def getReactionStatus(self, reaction):
        """
        This method gives whether the reaction in an index is enabled or not.

        Parameters
        ----------
        reaction : integer
            It is the index of the reaction in the reaction list.

        Returns
        -------
        bool
            It is true if the reaction is.

        """
        return self.root.call_method(
            self._reactionStatus, ua.Variant(reaction, ua.uatypes.VariantType.Byte)
        )

    def getCollectionStatus(self):
        """
        This method gives the state of the Waste/Collect valve.

        Returns
        -------
        string
            It is "WASTE" if the valve is on Waste state.
            It is "COLLECT" if the valve is on Collect state.

        """
        return self.root.call_method(self._collectionStatus)

    def getLoopStatus(self):
        """
        It gives the INJECT/LOAD valve state of all of the pumps whether having
        sample loop or not.

        Returns
        -------
        JSON
            It is the valves status.

        """
        # TODO: parse?
        return self.root.call_method(self._loopStatus)

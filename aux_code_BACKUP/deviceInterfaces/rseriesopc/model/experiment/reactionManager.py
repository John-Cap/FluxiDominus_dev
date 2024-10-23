from opcua import ua, Node
import logging

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class ReactionManagerType(BaseNode):
    """
    The Reaction Manager class allows the user manage the Reaction List.

    Reactions can be added, deleted or desabled from the Reaction List. Then,
    this list could be started or stoped with the methods provides from an
    object of this class.

    Parameters
    ----------
    root : opcua.Node
        It is the Reaction Manager's id in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the Reaction Manager's id in the OPC UA Address Space.
    reactionStatus : opcua.Node
        It is the ReactionStatus variable id in the OPC UA Address Space.

    """

    _getReactionList: Node
    _loadReactionList: Node
    _addReactionToList: Node
    _resetReactionList: Node
    _getReactionParameters: Node
    _deleteReaction: Node
    _getEnableReactionStatus: Node
    _enableReaction: Node
    _disableReaction: Node
    _startReaction: Node
    _stopReaction: Node
    _setReactionPosition: Node
    reactionStatus: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in root.get_children()
        }

        variables = [
            NodeInfo("_getReactionList", "GetReactionList", None),
            NodeInfo("_loadReactionList", "LoadReactionList", None),
            NodeInfo("_addReactionToList", "AddReactionToList", None),
            NodeInfo("_resetReactionList", "ResetReactionList", None),
            NodeInfo("_getReactionParameters", "GetReactionParameters", None),
            NodeInfo("_deleteReaction", "DeleteReaction", None),
            NodeInfo("_getEnableReactionStatus", "GetEnableReactionStatus", None),
            NodeInfo("_enableReaction", "EnableReaction", None),
            NodeInfo("_disableReaction", "DisableReaction", None),
            NodeInfo("_startReaction", "StartReaction", None),
            NodeInfo("_stopReaction", "StopReaction", None),
            NodeInfo("_setReactionPosition", "SetReactionPosition", None),
            NodeInfo("reactionStatus", "ReactionStatus", None),
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

    def getEnableReactionStatus(self, index):
        """It reports if a given reaction is enabled to be automatically excecuted or not.

        Parameters
        ----------
        index : integer
            It is the 0-based position of the desired reaction in the reaction list

        Returns
        -------
        bool
            It is True when the reaction is enabled.
        """
        return self.root.call_method(
            self._getEnableReactionStatus,
            ua.Variant(index, ua.uatypes.VariantType.Byte),
        )

    def getReactionList(self):
        # TODO parse and add to the docs?
        """
        It gives the reaction list of the actual experiment file loaded.
        It needs to be an experiment set and loaded a reaction list or created
        before to be meaningful.
        The reaction list is in CSV Format.
        It is received the string separator and the decimal point.

        Returns
        -------
        String
            It is the reaction list in CSV format.
            The first line is the table's header.
            The following lines are the fields.
            The lines are delimited by '\\n'.

        """
        # list[Reaction]
        #     It's the reaction list.
        #     Each element in the list is a Reaction objct which has all
        #     the reaction parameters.
        # if self.strSep is None:
        #     self.getReactionParameters()
        msg = self.root.call_method(self._getReactionList)
        # # TODO uncomment
        # csvRows = str(msg).split('\n')
        # 'The last one line is empty'
        # csvRows.pop()
        # # rL = list(csv.reader(csvRows, delimiter=self.strDel))
        # rL = list(csv.reader(csvRows, delimiter=','))
        # msg = list()
        # for r in rL:
        #     if len(r):
        #         msg.append(Reaction().load(r))
        return msg

    def loadReactionList(self, reactionList):
        """
        loadReactionList replaces the actual reaction list with a new one.
        This method needs an experiment set before its execution.

        Parameters
        ----------
        reactionList : String
            It is a CSV format string with the reaction list to load.
            It has to be a valid Vapourtec RSeries reaction table.

        Returns
        -------
        None.

        """
        decod = str(reactionList).split("\n")
        decod.pop(0)
        count = 0
        print("Sending reaction list")
        for reaction in decod:
            if reaction != "":
                print("-> R{0}: ".format(count), end="")
                if self.addReactionToList(reaction):
                    print("Ok")
                else:
                    print("Fail")
                count += 1
        print("Reaction List sent.")

    def addReactionToList(self, reaction):
        """
        This method add one reaction to the current Reaction List.

        Parameters
        ----------
        reaction : String
            This is the reaction to add.
            The reaction must be the followings field, in a CSV format.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._addReactionToList, reaction)
            return True
        except:
            return False

    def resetReactionList(self):
        """
        This method deletes all of the reactions in the current Reaction List.

        Returns
        -------
        None.

        """
        self.root.call_method(self._resetReactionList)
        pass

    def getReactionParameters(self, position=0):
        # TODO add to the docs
        # It likely needs a new description i guess
        """
        It returns all the parameteres of a given reaction in the Reaction List.

        Parameters
        ----------
        position : integer
            It is the index of the reaction in the reaciton list

        Returns
        -------
        String
            These are the reaction list parameters, including CSV string
            separators, CSV deciman point, the information about all of
            the pumps and reactors of each reaction in the Reaction List and
            the amount of reactions.
            It could be direct loaded to a JSON object.

        """

        msg = self.root.call_method(
            self._getReactionParameters,
            ua.Variant(position, ua.uatypes.VariantType.UInt16),
        )
        return msg

    def deleteReaction(self, reaction):
        """
        It deletes a given reaction.

        Parameters
        ----------
        reaction : integer
            This is the index of the reaction to be removed of the Reaction
            List.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._deleteReaction,
                ua.Variant(reaction, ua.uatypes.VariantType.UInt16),
            )
            return True
        except:
            return False

    def enableReaction(self, reaction):
        """
        This method enables a given reaction.
        When a reaction is enabled, it will be runned when startReaction is
        called.

        Parameters
        ----------
        reaction : integer
            This is the index of the reaction to be enabled in the Reaction
            List.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._enableReaction,
                ua.Variant(reaction, ua.uatypes.VariantType.UInt16),
            )
            return True
        except:
            return False

    def disableReaction(self, reaction):
        """
        This method disables a given reaction.
        When a reaction is disabled, it will not be runned when startReaction
        is called.

        Parameters
        ----------
        reaction : integer
            This is the index of the reaction to be disabled in the Reaction
            List.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._disableReaction,
                ua.Variant(reaction, ua.uatypes.VariantType.UInt16),
            )
            return True
        except:
            return False

    def startReaction(self):
        """
        startReaction sends a command to run all of the enabled reactions in
        the current Reaction List

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._startReaction)
            return True
        except:
            return False

    def stopReaction(self):
        """
        stopReaction sends a command to stop the current reaction execution.

        Returns
        -------
        None.

        """
        self.root.call_method(self._stopReaction)

    def setReactionPosition(self, curPos, newPos):
        """
        setReactionPosition changes the position of a Reaction in the Reaction
        List.

        Parameters
        ----------
        curPos : integer
            This is the current position of the reaction.
        newPos : integer
            This is the position where the reaction will be placed.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(
                self._setReactionPosition,
                ua.Variant(newPos, ua.uatypes.VariantType.UInt16),
                ua.Variant(curPos, ua.uatypes.VariantType.UInt16),
            )
            return True
        except:
            return False

    def getCurrentReactionIndex(self):
        """
        It returns the position of the current reaction in the reaction list.

        Returns
        -------
        integer
            It is the index of the reaction.

        """
        return self.reactionStatus.get_value()[0]

    def getCurrentReactionStatus(self):
        """
        It gives the status of the current reaction. It could be one of the
        following states:\n

            IDLE                    = 0 \n
            NOT_RUNNING             = 1\n
            WAIT_RACK_CHANGE        = 2\n
            SET_PREHEATING          = 3\n
            HEATING                 = 4\n
            WAIT4PRE_WASH           = 5\n
            PUMP_DEAD_VOLUME        = 6\n
            WAIT4DEAD_VOLUME        = 7\n
            WAIT4SAMPLE_LOOP_LOADS  = 8\n
            START_REACTION          = 9\n
            RUNNING_REACTION        = 10\n
            WAIT4COLLECTION         = 11\n
            POST_WASHING,           = 12\n
            WAIT4POST_WASH,         = 13\n
            FINAL_COLLECTION,       = 14\n
            WAIT4FINAL_COLLECTION,  = 15\n
            CHECK4REACTIONS,        = 16\n
            CLEANING,               = 17\n
            WAIT4CLEANING,          = 18\n
            COOLING,                = 19\n
            WAIT4COOLING,           = 20\n
            STOP_REACTION           = 21

        Returns
        -------
        integer
            It is the current reaction status.

        """
        return self.reactionStatus.get_value()[1]

    def getReactionStatusNode(self):
        """
        This method returns the id of the reaction status variable. This id
        allows the user to subscribe the variable to a handler object.

        To subscribe a variable, the handler class has to be defined and
        implement a datachange_notification(self, node, value, data) function.
        This give the user the capability of monitoring the variable and
        makes a custom control of it.

        Example of this will be found in readingDataExample.py

        Returns
        -------
        opcua.Node
            This is the id of the reaction status variable in the OPC UA
            Address Space.

        """
        return self.reactionStatus

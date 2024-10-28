from opcua import Node
import logging
import json
import os

log = logging.getLogger("rseriesclient." + __name__)

from rseriesopc.model.base import BaseNode, NodeInfo


class ExperimentSetupType(BaseNode):
    """
    The ExperimentSetupType class contain the methods that allow the user to
    save and restore the System settings.

    Parameters
    ----------
    root : opcua.Node
        It is the experiment setup object id in the OPC UA Address Space.

    Attributes
    ----------
    root : opcua.Node
        It is the id of the experimentSetup object in the OPC UA Address Space.

    """

    _getSystemSettings: Node
    _loadSystemSettings: Node
    _getExperiment: Node
    _loadExperiment: Node

    def __init__(self, root):
        self.root = root
        browse_names = {
            child.get_browse_name().Name: child.get_browse_name()
            for child in self.root.get_children()
        }

        variables = [
            NodeInfo("_getSystemSettings", "GetSystemSettings", None),
            NodeInfo("_loadSystemSettings", "LoadSystemSettings", None),
            NodeInfo("_getExperiment", "GetExperiment", None),
            NodeInfo("_loadExperiment", "LoadExperiment", None),
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

        self.pathSep = self._getPathSeparator()

    def _getPathSeparator(self):
        pathSep = "/"
        if os.name == "nt":
            pathSep = "\\"
        return pathSep

    def getSystemSettings(self):
        """
        It returns the settings of all the components presetns in the loaded
        experiment on the R-Series Controller.

        Returns
        -------
        JSON
            These are the system settings.

        """
        # TODO: parse?
        return self.root.call_method(self._getSystemSettings)

    def loadSystemSettings(self, settings):
        """
        It loads all the system settings in the current experiment on the
        R-Series Controller.

        Parameters
        ----------
        settings : JSON
            It is the system settings.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        try:
            self.root.call_method(self._loadSystemSettings, settings)
            return True
        except:
            return False

    def getExperiment(self, pathToSave=None):
        """
        It gives the experiment data. The data returned could be saved in a
        file and then it could be send by loadExperiment.

        Returns
        -------
        JSON
            This is the experiment data.

        """
        experiment = self.root.call_method(self._getExperiment)
        if pathToSave is not None:
            self._saveExperiment(experiment, pathToSave)
        return experiment

    def _saveExperiment(self, experiment, path: str):
        data = json.loads(experiment)
        fileName = data["name"]
        path = self._makeFolder(path, self.pathSep, fileName)
        filePath = path + self.pathSep + fileName
        self._writeFile(filePath, "rs", data["nodes"])
        if "cfg" in data.keys():
            self._writeFile(filePath, "rscfg", data["cfg"])
        if "rl" in data.keys():
            self._writeFile(filePath, "rsrl", data["rl"])

    def _writeFile(self, fileName, extension, content):
        with open(fileName + "." + extension, "w") as file:
            json.dump(obj=content, fp=file, indent=4, separators=[",", ": "])

    def _makeFolder(self, path, pathSep, fileName):
        if not path.endswith(pathSep):
            path += pathSep
        path += fileName
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def loadExperiment(self, experiment):
        """
        It loads an experiment into the system. The experiment data to send is
        getted by getExperiment method.

        Parameters
        ----------
        experiment : JSON
            It is the experiment to load.

        Returns
        -------
        bool
            It is true when the method was applied successfully to the system.
            Otherwise, it is false.

        """
        fileName = self._getFileName(experiment)
        if os.path.exists(fileName + ".rs"):
            experiment = {"name": fileName.split(self.pathSep)[-1]}
            reading = self._readFile(fileName, "rs")
            if reading == "":
                print("Error: Fail reading file")
                return False
            experiment["nodes"] = reading
            reading = self._readFile(fileName, "rscfg")
            if reading != "":
                experiment["cfg"] = reading
            reading = self._readFile(fileName, "rsrl")
            if reading != "":
                experiment["rl"] = reading
        try:
            self.root.call_method(self._loadExperiment, json.dumps(experiment))
            return True
        except:
            return False

    def _readFile(self, fileName, extension):
        content = ""
        fullPath = fileName + "." + extension
        if not os.path.exists(fullPath):
            return content
        with open(fullPath, "r") as file:
            content = file.read()
        return json.loads(content)

    def _getFileName(self, experiment):
        experimentWithoutEndSep = experiment
        if experimentWithoutEndSep.endswith(self.pathSep):
            experimentWithoutEndSep = experimentWithoutEndSep[:-1]
        fileName = experimentWithoutEndSep.split(self.pathSep)[-1]
        fileName = experimentWithoutEndSep + self.pathSep + fileName
        return fileName

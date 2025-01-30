
#rig for monitoring optimizations, generating recommended parameters, and executing the commands

from Config.Data.hardcoded_command_templates import HardcodedCommandTemplates
from Core.Control.ScriptGenerator import FlowChemAutomation
"""
automation.addBlockElement("block_2","sf10vapourtec2","fr",1.0)
"""

class OptimizationRig:
    def __init__(self):
        self.automation = FlowChemAutomation() #handles command parsing
        self.availableParams={} #Reaction parameters that can be tweaked
        self.availableCmnds={} #Links a tweakable parameter to a specific device command
        self.availableDeviceCmnds={} #Links cmnd to device
        self._rigThread=None
        self.optimizer=None
        self.objectiveEvaluator=None
        self.cmndTemplates=HardcodedCommandTemplates.commandTemplatesNested
    
    def registerDevice(self,device):
        if device in self.cmndTemplates:
            self.availableDeviceCmnds=self.cmndTemplates[device]
        else:
            print(f'WJ - Unknown device {device}!')
    def generateRecommendation(self):
        """
        outputs a recommended parameter dict, linked to specific device
        """
        pass
    
    def executeRecommendation(self):
        """
        executes recommended parameter dict, publishes mqtt
        """
        pass
    
    def start(self):
        """
        start thread
        """
        pass
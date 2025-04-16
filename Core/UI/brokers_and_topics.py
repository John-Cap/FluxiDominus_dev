#Note - topics in/out are relative to backend

class MqttTopics:
    topicsCnmd = {
        #"sf10vapourtec1": "subflow/sf10vapourtec1/cmnd",
        "flowsynmaxi2": "subflow/flowsynmaxi2/cmnd",
        #"hotchip1": "subflow/hotchip1/cmnd",
        #"hotchip2": "subflow/hotchip2/cmnd",
        "hotcoil1": "subflow/hotcoil1/cmnd",
        #"hotcoil2": "subflow/hotcoil2/cmnd",
        "reactIR702L1": "subflow/reactIR702L1/cmnd",
        "vapourtecR4P1700": "subflow/vapourtecR4P1700/cmnd"
    }

    topicsTele = {
        #"sf10vapourtec1": "subflow/sf10vapourtec1/tele",
        "flowsynmaxi2": "subflow/flowsynmaxi2/tele",
        #"hotchip1": "subflow/hotchip1/tele",
        #"hotchip2": "subflow/hotchip2/tele",
        "hotcoil1": "subflow/hotcoil1/tele",
        #"hotcoil2": "subflow/hotcoil2/tele",
        "reactIR702L1": "subflow/reactIR702L1/tele",
        "vapourtecR4P1700": "subflow/vapourtecR4P1700/tele"
    }

    topicsUI = {
        "optOut":"ui/opt/out",
        "optIn":"ui/opt/in",
        "FlowSketcher": "ui/FlowSketcher",
        "FlowTrackerOut": "ui/FlowSketcher/flowtracking/out",
        "FlowTrackerIn": "ui/FlowSketcher/flowtracking/in",
        "ScriptGeneratorWidget": "chemistry/cmnd",
        #"TestListWidget":"ui/TestListWidget",
        "FormPanelWidget":"ui/FormPanelWidget",
        "LoginPageWidget": "ui/LoginPageWidget",
        #"dbStreamingOut":"ui/dbStreaming/out",
        "dbCmndIn":"ui/dbCmnd/in", #Ui posts here
        "uiInfoOut":"ui/info/out",
        "uiInfoIn":"ui/info/in"
    }

    topicsOptimization = {
        "optimizerIn":"opt/in",
        "optimizerOut":"opt/out",
        "evaluatorIn":"eval/in",
        "evaluatorOut":"eval/out"
    }

    topicsTests={
        "testSettings":"test/settings"
    }

    topicsQos={
        "ui/dbCmnd/in":2
    }

    allTopics=[topicsCnmd,topicsTele,topicsUI,topicsTests]

    @staticmethod
    def getTopicQos(topic):
        if (topic in MqttTopics.topicsQos):
            return MqttTopics.topicsQos[topic]
        else:
            return 0

    @staticmethod
    def getUiTopic(type):
        if type not in MqttTopics.topicsUI:
            raise Exception(f"UI topic not found: {type}")
        return MqttTopics.topicsUI[type]

    @staticmethod
    def getCmndTopic(device):
        if device not in MqttTopics.topicsCnmd:
            raise Exception(f"Device not found: {device}")
        return MqttTopics.topicsCnmd[device]

    @staticmethod
    def getCmndTopics():
        return MqttTopics.topicsCnmd

    @staticmethod
    def getTeleTopic(device):
        if device not in MqttTopics.topicsTele:
            raise Exception(f"Device not found: {device}")
        return MqttTopics.topicsTele[device]

    @staticmethod
    def getTeleTopics():
        return MqttTopics.topicsTele

    @staticmethod
    def getUiTopics():
        return MqttTopics.topicsUI

    @staticmethod
    def getOptimizationTopics():
        return MqttTopics.topicsOptimization

    @staticmethod
    def getAllTopicSets():
        return MqttTopics.allTopics

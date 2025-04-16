
from Core.UI.brokers_and_topics import MqttTopics


class LoggingBase:
    def __init__(self) -> None:
        self.destination = r"Debug\General_Log.txt"

class Logging(LoggingBase):
    def __init__(self) -> None:
        super().__init__()

class Diag_log(Logging):
    def __init__(self) -> None:
        super().__init__()
    
    def toLog(self,logThis):
        with open(self.destination, 'a') as f:
            f.write((logThis) + "\n")

    def toLogIP(): #log elke ip as 'n 'object'
        pass

class UiInform:
    def __init__(self):
        self.uiInfoOut=MqttTopics.getUiTopic("uiInfoOut")
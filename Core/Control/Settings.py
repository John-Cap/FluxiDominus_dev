
class SettingsBase:
    def __init__(self) -> None:
        pass

class Settings(SettingsBase):
    def __init__(self) -> None:
        super().__init__()

class SettingsSF10(Settings):
    def __init__(self,mode="FLOW",flowrate=0) -> None:
        super().__init__()

        self.mode = mode
        self.flowrate = flowrate

'''{
  "payload": "sf10Vapourtec1",
  "_msgid": "e1a209f60ff86b96",
  "settings": {
    "mode": "FLOW",
    "flowrate": 0.3
  },
  "state": "STOP",
  "valve": "A",
  "myymd": "2023-12-08",
  "mytimes": "11:56:11",
  "myepoch": "1702029371610",
  "myrawdate": "2023-12-08T09:56:11.610Z",
  "timestamp": "1702029371610"
}'''
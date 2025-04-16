//Note - topics in/out are relative to backend

abstract class MqttTopics {
  static final Map<String, String> topicsCnmd = {
    "sf10vapourtec1": "subflow/sf10vapourtec1/cmnd",
    "flowsynmaxi2": "subflow/flowsynmaxi2/cmnd",
    //"flowsynmaxi1": "subflow/flowsynmaxi1/cmnd",
    //"hotchip1": "subflow/hotchip1/cmnd",
    //"hotchip2": "subflow/hotchip2/cmnd",
    "hotcoil1": "subflow/hotcoil1/cmnd",
    "vapourtecR4P1700": "subflow/vapourtecR4P1700/cmnd",
    //"hotcoil2": "subflow/hotcoil2/cmnd",
    //"reactIR702L1": "subflow/reactIR702L1/cmnd"
  };

  static final Map<String, String> topicsTele = {
    "sf10vapourtec1": "subflow/sf10vapourtec1/tele",
    "flowsynmaxi2": "subflow/flowsynmaxi2/tele",
    //"flowsynmaxi1": "subflow/flowsynmaxi1/tele",
    //"hotchip1": "subflow/hotchip1/tele",
    //"hotchip2": "subflow/hotchip2/tele",
    "hotcoil1": "subflow/hotcoil1/tele",
    "vapourtecR4P1700": "subflow/vapourtecR4P1700/tele",
    //"hotcoil2": "subflow/hotcoil2/tele",
    "reactIR702L1": "subflow/reactIR702L1/tele",
  };

  static final Map<String, String> topicsUI = {
    //"optOut": "ui/opt/in",
    "optIn": "ui/opt/out",
    "FlowSketcher": 'ui/FlowSketcher',
    "FlowTrackerIn": "ui/FlowSketcher/flowtracking/out",
    "FlowTrackerOut": "ui/FlowSketcher/flowtracking/in",
    "ScriptGeneratorWidget": 'chemistry/cmnd',
    "FormPanelWidget": 'ui/FormPanelWidget',
    "LoginPageWidget": 'ui/LoginPageWidget',
    "GraphWidgets": 'ui/GraphWidgets',
    "dbStreaming": "ui/dbStreaming/out", //TODO...'out' is relative to Python
    //"dbCmndIn": "ui/dbCmnd/in",
    "dbCmndRet": "ui/dbCmnd/ret"
  };

  static String getUITopic(String type) {
    if (!topicsUI.containsKey(type)) {
      throw Exception("UI topic not found: $type");
    }
    return topicsUI[type]!;
  }

  static String getCmndTopic(String device) {
    if (!topicsCnmd.containsKey(device)) {
      throw Exception("Device not found: $device");
    }
    return topicsCnmd[device]!;
  }

  static Map<String, String> getCmndTopics() {
    return topicsCnmd;
  }

  static String getTeleTopic(String device) {
    if (!topicsTele.containsKey(device)) {
      throw Exception("Device not found: $device");
    }
    return topicsTele[device]!;
  }

  static Map<String, String> getTeleTopics() {
    return topicsTele;
  }

  static Map<String, String> getUITopics() {
    return topicsUI;
  }
}

void main() {
  print(MqttTopics.topicsUI);
  print(MqttTopics.getUITopic("FlowSketcher"));
}

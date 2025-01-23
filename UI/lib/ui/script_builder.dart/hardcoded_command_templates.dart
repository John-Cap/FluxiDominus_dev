//import 'dart:convert';

import 'dart:convert';

class HardcodedCommands {
  final Map<dynamic, List<dynamic>> devicesAndTheirSettings = {
    'sf10vapourtec1': ['fr'],
    'sf10vapourtec2': ['fr'],
    'hotcoil1': ['temp'],
    'hotcoil2': ['temp'],
    'hotchip1': ['temp'],
    'hotchip2': ['temp'],
    'flowsynmaxi1': ['pafr', 'pbfr', 'sva', 'svb', 'svcw', 'svia', 'svib'],
    'flowsynmaxi2': ['pafr', 'pbfr', 'sva', 'svb', 'svcw', 'svia', 'svib'],
    'vapourtecR4P1700': [
      'pafr',
      'pbfr',
      'svasr',
      'svbsr',
      'svail',
      'svbil',
      'svcw',
      'r1temp',
      'r2temp',
      'r3temp',
      'r4temp'
    ],
  };
  Map<String, Map<String, dynamic>> hardcodedDeviceTemplates = {
    'flowsynmaxi1': {
      'pafr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 80}
          },
          'settings': {
            'subDevice': 'PumpAFlowRate',
            'command': 'SET',
            'value': 0.0
          }
        }
      },
      'pbfr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 80}
          },
          'settings': {
            'subDevice': 'PumpBFlowRate',
            'command': 'SET',
            'value': 0.0
          }
        }
      },
      'sva': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 80}
          },
          'settings': {
            'subDevice': 'FlowSynValveA',
            'command': 'SET',
            'value': false
          }
        }
      },
      'svb': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 80}
          },
          'settings': {
            'subDevice': 'FlowSynValveB',
            'command': 'SET',
            'value': false
          }
        }
      },
      'svcw': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 80}
          },
          'settings': {
            'subDevice': 'FlowCWValve',
            'command': 'SET',
            'value': false
          }
        }
      },
      'svia': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 80}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'FlowSynInjValveA',
            'value': false
          },
        }
      },
      'svib': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 80}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'FlowSynInjValveB',
            'value': false
          },
        }
      },
    },
    'flowsynmaxi2': {
      'pafr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.201', 'port': 80}
          },
          'settings': {
            'subDevice': 'PumpAFlowRate',
            'command': 'SET',
            'value': 0.0
          }
        }
      },
      'pbfr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.201', 'port': 80}
          },
          'settings': {
            'subDevice': 'PumpBFlowRate',
            'command': 'SET',
            'value': 0.0
          }
        }
      },
      'sva': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.201', 'port': 80}
          },
          'settings': {
            'subDevice': 'FlowSynValveA',
            'command': 'SET',
            'value': false
          }
        }
      },
      'svb': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.201', 'port': 80}
          },
          'settings': {
            'subDevice': 'FlowSynValveB',
            'command': 'SET',
            'value': false
          }
        }
      },
      'svcw': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.201', 'port': 80}
          },
          'settings': {
            'subDevice': 'FlowCWValve',
            'command': 'SET',
            'value': false
          }
        }
      },
      'svia': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.201', 'port': 80}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'FlowSynInjValveA',
            'value': false
          },
        }
      },
      'svib': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'flowsynmaxi2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.201', 'port': 80}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'FlowSynInjValveB',
            'value': false
          },
        }
      },
    },
    'hotcoil1': {
      'temp': {
        'address': ['settings', 'temp'],
        'cmnd': {
          'deviceName': 'hotcoil1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.213', 'port': 81}
          },
          'settings': {'command': 'SET', 'temp': 0.5},
        }
      },
    },
    'hotcoil2': {
      'temp': {
        'address': ['settings', 'temp'],
        'cmnd': {
          'deviceName': 'hotcoil2',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 81} //TODO - > fix ip
          },
          'settings': {'command': 'SET', 'temp': 0.0},
        }
      },
    },
    'hotchip1': {
      'temp': {
        'address': ['settings', 'temp'],
        'cmnd': {
          'deviceName': 'hotchip1',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.202', 'port': 81}
          },
          'command': 'SET',
          'temperatureSet': 0.0
        }
      },
    },
    'hotchip2': {
      'temp': {
        'address': ['settings', 'temp'],
        'cmnd': {
          'deviceName': 'hotchip2',
          'inUse': true,
          'command': 'SET',
          'temperatureSet': 0.0
        }
      },
    },
    'sf10vapourtec1': {
      'fr': {
        'address': ['settings', 'flowrate'],
        'cmnd': {
          'deviceName': 'sf10Vapourtec1',
          'inUse': true,
          'connDetails': {
            'serialCom': {
              'port': '/dev/ttyUSB0',
              'baud': 9600,
              'dataLength': 8,
              'parity': 'N',
              'stopbits': 1
            }
          },
          'settings': {'command': 'SET', 'mode': 'FLOW', 'flowrate': 0.0}
        }
      },
    },
    'sf10vapourtec2': {
      'fr': {
        'address': ['settings', 'flowrate'],
        'cmnd': {
          'deviceName': 'sf10Vapourtec2',
          'inUse': true,
          'connDetails': {
            'serialCom': {
              'port': '/dev/ttyUSB0',
              'baud': 9600,
              'dataLength': 8,
              'parity': 'N',
              'stopbits': 1
            }
          },
          'settings': {'command': 'SET', 'mode': 'FLOW', 'flowrate': 0.0}
        }
      },
    },

    //Vapourtec R4s
    'vapourtecR4P1700': {
      'pafr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'PumpAFlowRate',
            'value': 0
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'pbfr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'PumpBFlowRate',
            'value': 0
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'svasr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'valveASR',
            'value': false
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'svbsr': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'valveBSR',
            'value': false
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'svcw': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'subDevice': 'valveCW',
            'command': 'SET',
            'value': false
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'svail': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'valveAIL',
            'value': false
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'svbil': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'valveBIL',
            'value': false
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'r1temp': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'Reactor1Temp',
            'value': 0
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'r2temp': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'Reactor2Temp',
            'value': 0
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'r3temp': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'Reactor3Temp',
            'value': 0
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      },
      'r4temp': {
        'address': ['settings', 'value'],
        'cmnd': {
          'deviceName': 'vapourtecR4P1700',
          'inUse': true,
          'connDetails': {
            'ipCom': {'addr': '192.168.1.51', 'port': 43344}
          },
          'settings': {
            'command': 'SET',
            'subDevice': 'Reactor4Temp',
            'value': 0
          },
          'topic': 'subflow/vapourtecR4P1700/cmnd',
          'client': 'client'
        }
      }
    }
  };

  String? injectVal(String device, String cmnd, dynamic val) {
    // Retrieve the template based on device and command.
    Map<String, dynamic>? template = hardcodedDeviceTemplates[device]?[cmnd];

    // If the template is null, return an error or null.
    if (template == null) {
      return null; // or throw an exception if needed.
    }

    // Get the address list.
    List<dynamic> address = template['address'];

    // Start from the 'cmnd' map.
    Map<String, dynamic> cmndMap = template['cmnd'];

    // Navigate through the map using the address, stopping before the last key.
    for (int i = 0; i < address.length - 1; i++) {
      cmndMap = cmndMap[address[i]] as Map<String, dynamic>;
    }

    // Set the value at the last key in the address.
    cmndMap[address.last] = val;

    // Return the modified 'cmnd' map.
    return jsonEncode(template['cmnd']);
  }
}

//Example

void main() {
  print(HardcodedCommands().injectVal('vapourtecR4P1700', 'pafr', 2));
  print(HardcodedCommands().injectVal('vapourtecR4P1700', 'svail', true));
  print(HardcodedCommands().injectVal('vapourtecR4P1700', 'svcw', false));
}

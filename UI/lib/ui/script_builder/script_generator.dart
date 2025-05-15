import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ScriptGeneratorWidget extends StatefulWidget {
  final MqttService mqttService;
  static const String _blocksStorageKey = 'script_generator_blocks';

  const ScriptGeneratorWidget({required super.key, required this.mqttService});
  @override
  ScriptGeneratorWidgetState createState() => ScriptGeneratorWidgetState();
}

class ScriptGeneratorWidgetState extends State<ScriptGeneratorWidget>
    with AutomaticKeepAliveClientMixin<ScriptGeneratorWidget> {
  final Map<String, List<String>> devicesAndTheirSettings = {
    'sf10vapourtec1': ['fr'],
    'sf10vapourtec2': ['fr'],
    'hotcoil1': ['temp'],
    'hotcoil2': ['temp'],
    'hotchip1': ['temp'],
    'hotchip2': ['temp'],
    'flowsynmaxi1': ['pafr', 'pbfr', 'sva', 'svb', 'svcw'],
    'flowsynmaxi2': ['pafr', 'pbfr', 'sva', 'svb', 'svcw'],
    'vapourtecR4P1700': [
      'pafr',
      'pbfr',
      'svasr',
      'svbsr',
      'svcw',
      'svail',
      'svbil',
      'r1temp',
      'r2temp',
      'r3temp',
      'r4temp'
    ],
    'Delay': ['sleepTime'],
    'WaitUntil': ['timeout']
  };
  // Map of device keys to display names
  static const Map<String, String> displayNames = {
    "flowsynmaxi1": "Flowsyn Maxi 1",
    "flowsynmaxi2": "Flowsyn Maxi 2",
    "sf10vapourtec1": "SF10 Vapourtec 1",
    "sf10vapourtec2": "SF10 Vapourtec 2",
    "hotcoil1": "Hotcoil 1",
    "hotcoil2": "Hotcoil 2",
    "hotchip1": "Hotchip 1",
    "hotchip2": "Hotchip 2",
    "vapourtecR4P1700": "R4 P1700",
    "Delay": "Delay",
    "WaitUntil": "Wait Until"
  };

  // Map of command keys to display names
  static const Map<String, String> commandDisplayNames = {
    "pafr": "FR A",
    "pbfr": "FR B",
    "sva": "Valve A",
    "svb": "Valve B",
    "svcw": "Valve Collect/Waste",
    "svasr": "Valve S/R A",
    "svbsr": "Valve S/R B",
    "svail": "Inj/Load A",
    "svbil": "Inj/Load B",
    "r1temp": "Reactor 1 Temp",
    "r2temp": "Reactor 2 Temp",
    "r3temp": "Reactor 3 Temp",
    "r4temp": "Reactor 4 Temp",
    "temp": "Temperature",
    "fr": "FR",
    "sleepTime": "Time",
    "timeout": "Timeout"
  };
// Map containing unit names for each command setting
  static const Map<String, String> units = {
    "fr": "mL/min",
    "temp": "°C",
    "pafr": "mL/min",
    "pbfr": "mL/min",
    "sva": "", // No unit, handled as boolean
    "svb": "", // No unit, handled as boolean
    "svcw": "", // No unit, handled as boolean
    "svasr": "", // No unit, handled as boolean
    "svbsr": "", // No unit, handled as boolean
    "svail": "", // No unit, handled as boolean
    "svbil": "", // No unit, handled as boolean
    "r1temp": "°C",
    "r2temp": "°C",
    "r3temp": "°C",
    "r4temp": "°C",
    "sleepTime": "Sec",
    "timeout": "Sec"
  };
  @override
  void initState() {
    super.initState();
    _loadBlocksLocally();
  }

  void _saveBlocksLocally() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = jsonEncode(_blocks);
    await prefs.setString(ScriptGeneratorWidget._blocksStorageKey, jsonString);
    debugPrint("Script blocks saved locally.");
  }

  void _loadBlocksLocally() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = prefs.getString(ScriptGeneratorWidget._blocksStorageKey);

    if (jsonString != null && jsonString.trim().isNotEmpty) {
      try {
        final decoded = jsonDecode(jsonString) as Map<String, dynamic>;
        setState(() {
          _blocks = decoded.map((key, value) {
            return MapEntry(key, List<Map<String, dynamic>>.from(value));
          });
        });
        debugPrint("Script blocks loaded from local storage.");
      } catch (e) {
        debugPrint("Failed to parse saved script blocks: $e");
      }
    } else {
      debugPrint("No saved script blocks found.");
    }
  }

  static String getFullDisplayName(
      String deviceKey, String commandKey, dynamic val) {
    // Retrieve the device and command display names
    String deviceDisplayName = getDeviceDisplayName(deviceKey);
    String commandDisplayName = getCommandDisplayName(commandKey);

    // Handle boolean values with custom display
    if (val is bool) {
      if (commandKey == 'sva' ||
          commandKey == 'svb' ||
          commandKey == 'svasr' ||
          commandKey == 'svbsr') {
        return "$deviceDisplayName: $commandDisplayName -> ${val ? 'Reag' : 'Solv'}";
      } else if (commandKey == 'svcw') {
        return "$deviceDisplayName: $commandDisplayName -> ${val ? 'Collect' : 'Waste'}";
      } else if (commandKey == 'svail' || commandKey == 'svbil') {
        return "$deviceDisplayName: $commandDisplayName -> ${val ? 'Load' : 'Inject'}";
      }
    }

    // For non-boolean values, append unit if available
    String unit = units[commandKey] ?? "";
    return "$deviceDisplayName: $commandDisplayName -> $val${unit.isNotEmpty ? ' $unit' : ''}";
  }

  // Method to get only the device display name
  static String getDeviceDisplayName(String deviceKey) {
    return displayNames[deviceKey] ?? "Unknown Device";
  }

  // Method to get only the command display name
  static String getCommandDisplayName(String commandKey) {
    return commandDisplayNames[commandKey] ?? "Unknown Command";
  }

  String _selectedDevice = '';
  String _selectedSetting = '';
  String _blockName = '';
  Map<String, List<Map<String, dynamic>>> _blocks = {};

  final TextEditingController _valueController = TextEditingController();
  final TextEditingController _blockNameController = TextEditingController();

  void updateScriptBlocks(String newBlocks) {
    Map<String, dynamic> decodedBlocks = jsonDecode(newBlocks);
    setState(() {
      _blocks = decodedBlocks.map((key, value) {
        return MapEntry(key, List<Map<String, dynamic>>.from(value));
      });
      print('WJ - $_blocks');
    });
  }

  void _addCommand() {
    final String setting = _selectedSetting;
    final String value = _valueController.text;

    if (_blockName.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a block name')),
      );
      return;
    }

    if (_selectedDevice.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a device')),
      );
      return;
    }

    if (_selectedSetting.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a setting')),
      );
      return;
    }

    if (value.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a value')),
      );
      return;
    }

    final dynamic parsedValue = _parseValue(value);
    final command = {
      'device': _selectedDevice,
      'setting': setting,
      'value': parsedValue
    };

    setState(() {
      if (_blocks[_blockName] == null) {
        _blocks[_blockName] = [];
      }
      _blocks[_blockName]!.add(command);
      widget.mqttService.currTestScriptBlocks = _blocks;
    });
    _saveBlocksLocally();
    _valueController.clear();
  }

  void _deleteBlock(String blockName) {
    setState(() {
      _blocks.remove(blockName);
      widget.mqttService.currTestScriptBlocks = _blocks;
    });
    _saveBlocksLocally();
  }

  void _moveBlockUp(String blockName) {
    setState(() {
      final blockNames = _blocks.keys.toList();
      final int index = blockNames.indexOf(blockName);

      if (index > 0) {
        // Swap the positions of the block names in the list
        final String prevBlock = blockNames[index - 1];
        blockNames[index - 1] = blockName;
        blockNames[index] = prevBlock;

        // Rebuild the _blocks map with the new order
        _blocks = {for (var name in blockNames) name: _blocks[name]!};
      }
      _saveBlocksLocally();
    });
  }

  void _moveBlockDown(String blockName) {
    setState(() {
      final blockNames = _blocks.keys.toList();
      final int index = blockNames.indexOf(blockName);

      if (index < blockNames.length - 1) {
        // Swap the positions of the block names in the list
        final String nextBlock = blockNames[index + 1];
        blockNames[index + 1] = blockName;
        blockNames[index] = nextBlock;

        // Rebuild the _blocks map with the new order
        _blocks = {for (var name in blockNames) name: _blocks[name]!};
      }
      _saveBlocksLocally();
    });
  }

  void _saveBlocks() {
    final String jsonPayload = jsonEncode({"script": _blocks});
    widget.mqttService.publish('test/settings', jsonPayload);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Procedure set!')),
    );
    _saveBlocksLocally();
  }

  void _enableLogging() {
    final Map<String, Map<String, dynamic>> request = {
      "instructions": {
        "params": {"logData": true},
        "function": "enableLogging"
      }
    };
    widget.mqttService.publish('ui/dbCmnd/in', jsonEncode(request));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Telemetry recording enabled")),
    );
  }

  void _disableLogging() {
    final Map<String, Map<String, dynamic>> request = {
      "instructions": {
        "params": {"logData": false},
        "function": "disableLogging"
      }
    };
    widget.mqttService.publish('ui/dbCmnd/in', jsonEncode(request));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Telemetry recording disabled")),
    );
  }

  void _runTest() {
    final Map<String, Map<String, dynamic>> request = {
      "instructions": {
        "params": {"runTest": true},
        "function": "goCommand"
      }
    };
    widget.mqttService.publish('ui/dbCmnd/in', jsonEncode(request));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Let's go!")),
    );
    //widget.mqttService.runTest = true;
    //widget.mqttService.timeBracketMax = 500;
    //widget.mqttService.timeBracketMin = 0;
    //widget.mqttService.teleDataNotifiers.clear();
    //widget.mqttService.testRunning.value = true;
  }

  void _abort() {
    final Map<String, Map<String, dynamic>> request = {
      "instructions": {
        "params": {"abort": true},
        "function": "abort"
      }
    };
    widget.mqttService.publish('ui/dbCmnd/in', jsonEncode(request));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Aborting run!")),
    );
    //widget.mqttService.runTest = false;
    //widget.mqttService.timeBracketMax = 500;
    //widget.mqttService.timeBracketMin = 0;
    //widget.mqttService.epochDelta.reset();
    //widget.mqttService.teleDataNotifiers.clear();
    //widget.mqttService.testRunning.value = false;
  }

  dynamic _parseValue(String value) {
    if (value.toLowerCase() == 'true' || value.toLowerCase() == 'false') {
      return value.toLowerCase() == 'true';
    } else if (double.tryParse(value) != null) {
      return double.parse(value);
    }
    return value;
  }

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context); // Required for AutomaticKeepAliveClientMixin

    final List<String> availableSettings =
        devicesAndTheirSettings[_selectedDevice] ?? [];

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: _blockNameController,
              decoration: const InputDecoration(labelText: 'Block Name'),
              onChanged: (value) {
                setState(() {
                  _blockName = value;
                });
              },
            ),
            DropdownButton<String>(
              icon: const Text(
                '↓',
                textScaler: TextScaler.linear(1.5),
              ),
              hint: const Text('Select Device'),
              value: _selectedDevice.isEmpty ? null : _selectedDevice,
              items: widget.mqttService.availableDevices.map((String device) {
                return DropdownMenuItem<String>(
                  value: device,
                  child: Text(getDeviceDisplayName(device)),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  _selectedDevice = newValue ?? '';
                  _selectedSetting = ''; // Reset setting when device changes
                });
              },
            ),
            if (_selectedDevice.isNotEmpty)
              DropdownButton<String>(
                icon: const Text(
                  '↓',
                  textScaler: TextScaler.linear(1.5),
                ),
                hint: const Text('Select Setting'),
                value: _selectedSetting.isEmpty ? null : _selectedSetting,
                items: availableSettings.map((String setting) {
                  return DropdownMenuItem<String>(
                    value: setting,
                    child: Text(getCommandDisplayName(setting)),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedSetting = newValue ?? '';
                  });
                },
              ),
            TextField(
              controller: _valueController,
              decoration: const InputDecoration(labelText: 'Value'),
            ),
            ElevatedButton(
              onPressed: _addCommand,
              child: const Text('Submit Command'),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: _blocks.length,
                itemBuilder: (context, index) {
                  final blockName = _blocks.keys.elementAt(index);
                  final commands = _blocks[blockName]!;

                  return Card(
                    margin: const EdgeInsets.symmetric(vertical: 8.0),
                    child: ListTile(
                      title: Text('Block: $blockName'),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: commands.map((command) {
                          return Text(getFullDisplayName(command['device'],
                              command['setting'], command['value']));
                        }).toList(),
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: Text(
                              '^',
                              textScaler: TextScaler.linear(1.5),
                            ),
                            onPressed: () => _moveBlockUp(blockName),
                          ),
                          IconButton(
                            icon: const Text('v'),
                            onPressed: () => _moveBlockDown(blockName),
                          ),
                          IconButton(
                            icon: const Text('X'),
                            onPressed: () => _deleteBlock(blockName),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
            Wrap(
              spacing: 8.0, // Space between buttons
              runSpacing:
                  8.0, // Space between rows of buttons (if wrapped to a new line)
              children: [
                ElevatedButton(
                  onPressed: _runTest,
                  child: const Text(
                    'Run',
                    textScaleFactor: 0.75,
                  ),
                ),
                ElevatedButton(
                  onPressed: _saveBlocks,
                  child: const Text(
                    'Save',
                    textScaleFactor: 0.75,
                  ),
                ),
                ElevatedButton(
                  onPressed: _enableLogging,
                  child: const Text(
                    'Record telemetry',
                    textScaleFactor: 0.75,
                  ),
                ),
                ElevatedButton(
                  onPressed: _disableLogging,
                  child: const Text(
                    'Stop recording',
                    textScaleFactor: 0.75,
                  ),
                ),
                ElevatedButton(
                  onPressed: _abort,
                  child: const Text(
                    'ABORT',
                    textScaleFactor: 0.75,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

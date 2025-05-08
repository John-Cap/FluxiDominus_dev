import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/config/UI/brokers_and_topics.dart';
import 'package:flutter_flow_chart/config/UI/component_sketcher_setters.dart';
import 'package:flutter_flow_chart/includes/components.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/dashboard.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/connection_params.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/flow_element.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/flow_chart.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/ui/draw_arrow.dart';
import 'package:flutter_flow_chart/ui/script_builder/hardcoded_command_templates.dart';
import 'package:star_menu/star_menu.dart';
import 'src/ui/element_settings_menu.dart';
import 'src/ui/text_menu.dart';

// ignore: must_be_immutable
class FlowSketcher extends StatefulWidget {
  FlowSketcher({
    super.key,
    required this.mqttService,
    required this.topic,
    required this.dashboard,
  });
  final MqttService mqttService;
  final String topic;
  StarMenuController outerMenuController = StarMenuController();
  StarMenuController innerMenuController = StarMenuController();
  Map<String, Map<String, dynamic>> updatedReport = {};
  Dashboard dashboard;

  @override
  State<FlowSketcher> createState() => FlowSketcherState();
}

class FlowSketcherState extends State<FlowSketcher>
    with AutomaticKeepAliveClientMixin {
  ConnectionMqttReport mqttReport = ConnectionMqttReport();

  @override
  Widget build(BuildContext context) {
    super.build(context); // Ensure this line is added to keep the state alive
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Text('FlowSketcher'),
            ElevatedButton(
              onPressed: _save,
              child: Text('Set'),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () {
              widget.dashboard.setZoomFactor(1.5 * widget.dashboard.zoomFactor);
            },
            icon: const Text(
              '+',
              textScaler: TextScaler.linear(1.5),
            ),
          ),
          IconButton(
            onPressed: () {
              widget.dashboard.setZoomFactor(widget.dashboard.zoomFactor / 1.5);
            },
            icon: const Text(
              '-',
              textAlign: TextAlign.center,
              textScaler: TextScaler.linear(2),
            ),
          ),
        ],
      ),
      backgroundColor: Colors.black12,
      body: Container(
        constraints: const BoxConstraints.expand(),
        child: FlowChart(
          dashboard: widget.dashboard,
          onDashboardTapped: ((context, position) {
            debugPrint('Dashboard tapped $position');
            //debugPrint('WJ - ${dashboard.elements[0].next[0].destElementId}');
            _displayDashboardMenu(context, position);
          }),
          onScaleUpdate: (newScale) {
            debugPrint('Scale updated. new scale: $newScale');
          },
          onDashboardSecondaryTapped: (context, position) {
            debugPrint('Dashboard right clicked $position');
            _displayDashboardMenu(context, position);
          },
          onDashboardLongTapped: ((context, position) {
            debugPrint('Dashboard long tapped $position');
          }),
          onDashboardSecondaryLongTapped: ((context, position) {
            debugPrint(
                'Dashboard long tapped with mouse right click $position');
          }),
          onElementLongPressed: (context, position, element) {
            debugPrint('Element with "${element.text}" text long pressed');
          },
          onElementSecondaryLongTapped: (context, position, element) {
            debugPrint(
                'Element with "${element.text}" text long tapped with mouse right click');
          },
          onElementPressed: (context, position, element) {
            debugPrint('Element with "${element.text}" text pressed');
            _displayElementMenu(context, position, element);
          },
          onElementSecondaryTapped: (context, position, element) {
            //debugPrint('WJ - Element details: $element');
            debugPrint('Element with "${element.text}" text pressed');
            _displayElementMenu(context, position, element);
          },
          onHandlerPressed: (context, position, handler, element) {
            debugPrint(
                'handler pressed: position $position handler $handler" of element $element');
            _displayHandlerMenu(position, handler, element);
          },
          onHandlerLongPressed: (context, position, handler, element) {
            debugPrint(
                'handler long pressed: position $position handler $handler" of element $element');
          },
          onLineTapped: (context, position, srcElement, destElement) {
            _showTubingSettings(context, srcElement, destElement);
          },
          mqttService: widget.mqttService,
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: widget.dashboard.recenter,
        child: const Text(
          '>|<',
          textScaler: TextScaler.linear(2),
        ),
      ),
    );
  }

  @override
  bool get wantKeepAlive => true;

  //*********************
  //* POPUP MENUS
  //*********************

  /// Display a drop down menu when tapping on a handler
  void _displayHandlerMenu(
      Offset position, Handler handler, FlowElement element) {
    StarMenuOverlay.displayStarMenu(
      context,
      StarMenu(
        params: StarMenuParameters(
          shape: MenuShape.linear,
          openDurationMs: 60,
          linearShapeParams: const LinearShapeParams(
            angle: 270,
            space: 10,
          ),
          onHoverScale: 1.1,
          useTouchAsCenter: true,
          centerOffset: position -
              Offset(
                widget.dashboard.dashboardSize.width / 2,
                widget.dashboard.dashboardSize.height / 2,
              ),
        ),
        onItemTapped: (index, controller) => controller.closeMenu!(),
        items: [
          FloatingActionButton(
            child: const Icon(Icons.delete),
            onPressed: () {
              widget.dashboard.removeElementConnection(element, handler);
              _updateConnections();
            },
          )
        ],
        parentContext: context,
      ),
    );
  }

  /// Display a drop down menu when tapping on an element
  void _displayElementMenu(
      BuildContext context, Offset position, FlowElement element) {
    if (element is! Component) return;

    final Component comp = element;

    final items = deviceTypeMenuConfig[comp.deviceType] ??
        deviceTypeMenuConfig['default']!;

    StarMenuOverlay.displayStarMenu(
      context,
      StarMenu(
        // same as before
        items: items.map((item) => item.builder(context, comp)).toList(),
        onItemTapped: (index, controller) {
          if (!items[index].keepMenuOpen) controller.closeMenu?.call();
        },
        parentContext: context,
      ),
    );
  }

  void _save() {
    print('WJ - Attempting to publish');
    _updateConnections();
    _buildMqttReport();
    _mergeTubingIntoMqttReport(); //setState(() {});
    widget.mqttService.currDashboardJson = //Necessary for db operations?
        widget.dashboard.saveDashboard();
    widget.mqttService.publish(
        MqttTopics.getUITopic("FlowSketcher"), mqttReport.toJsonString());
  }

  /*
  void _displayElementMenu(
      BuildContext context, Offset position, FlowElement element) {
    StarMenuOverlay.displayStarMenu(
      context,
      StarMenu(
        params: StarMenuParameters(
          shape: MenuShape.linear,
          openDurationMs: 60,
          linearShapeParams: const LinearShapeParams(
            angle: 270,
            alignment: LinearAlignment.left,
            space: 10,
          ),
          onHoverScale: 1.1,
          centerOffset: position - const Offset(50, 0),
          backgroundParams: const BackgroundParams(
            backgroundColor: Colors.transparent,
          ),
          boundaryBackground: BoundaryBackground(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: Theme.of(context).cardColor,
              boxShadow: kElevationToShadow[6],
            ),
          ),
        ),
        onItemTapped: (index, controller) {
          if (!(index == 5 || index == 2)) {
            controller.closeMenu!();
          }
        },
        items: [
          Text(
            element.text,
            style: const TextStyle(fontWeight: FontWeight.w900),
          ),
          InkWell(
            onTap: () {
              widget.dashboard.removeElement(element);
              _updateConnections();
            },
            child: const Text('Delete'),
          ),
          TextMenu(element: element),
          InkWell(
            onTap: () {
              widget.dashboard.removeElementConnections(element);
              _updateConnections();
            },
            child: const Text('Remove all connections'),
          ),
          InkWell(
            onTap: () {
              widget.dashboard.setElementResizable(element, true);
            },
            child: const Text('Resize'),
          ),
          ElementSettingsMenu(element: element),
        ],
        parentContext: context,
      ),
    );
  }
  */

  /// Print all connections of all elements in the dashboard
  void _updateConnections() {
    for (var element in widget.dashboard.elements) {
      debugPrint(
          'WJ - Element ${widget.dashboard.nameFromId(element.id)} connections:');
      for (var connection in element.next) {
        debugPrint('WJ -> ${connection.destElementId}');
        widget.dashboard
            .appendElementUnique(element.id, connection.destElementId);
      }
      _buildMqttReport();
    }
    setState(() {});
    //debugPrint(('WJ -> ${widget.dashboard.connections.toString()}'));
  }

  void _buildMqttReport() {
    widget.mqttService.availableDevices = ["Delay", "WaitUntil"];

    for (var element in widget.dashboard.elements) {
      if (element.deviceName != "null" &&
          !widget.mqttService.availableDevices.contains(element.deviceName)) {
        widget.mqttService.availableDevices.add(element.deviceName);
      }
      mqttReport.report[element.id] = {
        "name": widget.dashboard.nameFromId(element.id),
        "flowsInto": widget.dashboard.connections[element.id],
        "deviceName": element.deviceName,
        "deviceType": element.deviceType,
        "volume": element.volume,
        "associatedCmndSource": element.associatedCmndSource,
      };
      widget.mqttService.currFlowScript = {"FlowSketcher": mqttReport.report};
    }
    //print("WJ - $availableDevices");
  }

  /// Display a linear menu for the dashboard with menu entries built with [menuEntries]
  void _displayDashboardMenu(BuildContext context, Offset position) {
    StarMenuOverlay.displayStarMenu(
      context,
      StarMenu(
        params: StarMenuParameters(
          shape: MenuShape.linear,
          openDurationMs: 60,
          linearShapeParams: const LinearShapeParams(
            angle: 270,
            alignment: LinearAlignment.left,
            space: 10,
          ),
          // calculate the offset from the dashboard center
          centerOffset: position -
              Offset(
                widget.dashboard.dashboardSize.width / 2,
                widget.dashboard.dashboardSize.height / 2,
              ),
        ),
        // onItemTapped: (index, controller) => controller.closeMenu!(),
        parentContext: context,
        controller: widget.outerMenuController,
        items: [
          Wrap(
            children: _buildCategoryChips(context, position),
          ),
        ],
      ),
    );
  }

  void _mergeTubingIntoMqttReport() {
    widget.updatedReport = {};
    int tubingCounter = 1;

    for (final element in widget.dashboard.elements) {
      final fromId = element.id;
      final flowsIntoList = <String>[];

      for (final connection in element.next) {
        final tubingId =
            "tubing_${tubingCounter}_${fromId}_${connection.destElementId}";

        flowsIntoList.add(tubingId); // Correctly named and ordered here

        widget.updatedReport[tubingId] = {
          "name": "Tubing",
          "flowsInto": [connection.destElementId],
          "deviceName": "tubing${connection.tubingType}",
          "deviceType": "Tubing",
          "volume": connection.tubingVolume,
        };

        tubingCounter++; // Increment after use
      }

      widget.updatedReport[fromId] = {
        "name": element.text,
        "flowsInto": flowsIntoList,
        "deviceName": element.deviceName,
        "deviceType": element.deviceType,
        "volume": element.volume,
        "associatedCmndSource": element.associatedCmndSource
      };
    }

    mqttReport.report = widget.updatedReport;
    widget.mqttService.currFlowScript = widget.updatedReport;
    debugPrint("Merged report with tubing: ${mqttReport.toJsonString()}");
  }

  void updateConnections() {
    widget.dashboard =
        widget.dashboard.loadDashboard(widget.mqttService.currDashboardJson);
  }

  void _showTubingSettings(
    BuildContext context,
    FlowElement srcElement,
    FlowElement destElement,
  ) {
    ConnectionParams? connection = srcElement.next.firstWhere(
      (c) => c.destElementId == destElement.id,
      orElse: () => ConnectionParams(
        destElementId: destElement.id,
        arrowParams: ArrowParams(),
      ),
    );

    double newVolume = connection.tubingVolume;
    String newType = connection.tubingType;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text("Tubing Settings"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                decoration: InputDecoration(labelText: "Volume (mL)"),
                keyboardType: TextInputType.number,
                onChanged: (value) => newVolume =
                    double.tryParse(value) ?? connection.tubingVolume,
              ),
              DropdownButton<String>(
                value: newType,
                items: ["Standard", "PTFE", "PEEK", "Steel"]
                    .map((type) =>
                        DropdownMenuItem(value: type, child: Text(type)))
                    .toList(),
                onChanged: (value) => newType = value ?? connection.tubingType,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text("Cancel"),
            ),
            TextButton(
              onPressed: () {
                setState(() {
                  connection.tubingVolume = newVolume;
                  connection.tubingType = newType;
                });
                //widget.dashboard.notifyListeners(); // Refresh UI
                Navigator.of(context).pop();
              },
              child: Text("Save"),
            ),
          ],
        );
      },
    );
  }

  List<Widget> _buildCategoryChips(BuildContext context, Offset position) {
    return componentConfig.entries.map((entry) {
      final categoryName = entry.key;
      final components = entry.value;

      return ActionChip(
        label: Text(categoryName),
        onPressed: () {
          StarMenuOverlay.displayStarMenu(
            context,
            StarMenu(
              controller: widget.innerMenuController,
              params: StarMenuParameters(
                shape: MenuShape.linear,
                openDurationMs: 60,
                linearShapeParams: const LinearShapeParams(
                  angle: 270,
                  alignment: LinearAlignment.left,
                  space: 10,
                ),
                centerOffset: position -
                    Offset(
                      widget.dashboard.dashboardSize.width / 2,
                      widget.dashboard.dashboardSize.height / 2,
                    ),
              ),
              onItemTapped: (index, controller) {
                widget.innerMenuController.closeMenu!();
                widget.outerMenuController.closeMenu!();
                widget.innerMenuController = StarMenuController();
                widget.outerMenuController = StarMenuController();
              },
              parentContext: context,
              items: components.map((comp) {
                return ActionChip(
                  label: Text(comp.label),
                  onPressed: () {
                    widget.dashboard.addElement(comp.build(position));
                    _updateConnections();
                  },
                );
              }).toList(),
            ),
          );
        },
      );
    }).toList();
  }
}

class ConnectionMqttReport {
  Map<String, Map<String, dynamic>> report = {};
  String toJsonString() {
    Map<String, dynamic> pub = {
      "reqUI": {
        "FlowSketcher": {"parseFlowsketch": report}
      }
    };
    return jsonEncode(pub);
  }
}

//Component config
class ComponentConfig {
  final String label;
  final Component Function(Offset position) build;

  ComponentConfig({required this.label, required this.build});
}

class ElementMenuItem {
  final Widget Function(BuildContext context, FlowElement element) builder;
  final bool keepMenuOpen;

  const ElementMenuItem({
    required this.builder,
    this.keepMenuOpen = false,
  });
}

final List<ElementMenuItem> elementMenuItems = [
  ElementMenuItem(
    builder: (context, element) => Text(
      element.text,
      style: const TextStyle(fontWeight: FontWeight.w900),
    ),
    keepMenuOpen: true,
  ),
  ElementMenuItem(
    builder: (context, element) => InkWell(
      onTap: () {
        final state = context.findAncestorStateOfType<FlowSketcherState>();
        state?.widget.dashboard.removeElement(element);
        state?._updateConnections();
      },
      child: const Text('Delete'),
    ),
  ),
  ElementMenuItem(
    builder: (context, element) => TextMenu(element: element),
    keepMenuOpen: true,
  ),
  ElementMenuItem(
    builder: (context, element) => InkWell(
      onTap: () {
        final state = context.findAncestorStateOfType<FlowSketcherState>();
        state?.widget.dashboard.removeElementConnections(element);
        state?._updateConnections();
      },
      child: const Text('Remove all connections'),
    ),
  ),
  ElementMenuItem(
    builder: (context, element) => InkWell(
      onTap: () {
        final state = context.findAncestorStateOfType<FlowSketcherState>();
        state?.widget.dashboard.setElementResizable(element, true);
      },
      child: const Text('Resize'),
    ),
  ),
  ElementMenuItem(
    builder: (context, element) => ElementSettingsMenu(element: element),
    keepMenuOpen: true,
  ),
];

final Map<String, List<ElementMenuItem>> deviceTypeMenuConfig = {
  'Pump': [
    ElementMenuItem(
      builder: (context, element) => Text(
        element.text,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      keepMenuOpen: true,
    ),
    ElementMenuItem(
      builder: (context, element) => InkWell(
        onTap: () {
          final state = context.findAncestorStateOfType<FlowSketcherState>();
          state?.widget.dashboard.removeElement(element);
          state?._updateConnections();
        },
        child: const Text('Delete Pump'),
      ),
    ),
    ElementMenuItem(
      builder: (context, element) => InkWell(
        onTap: () async {
          final state = context.findAncestorStateOfType<FlowSketcherState>();
          double? newVal = await SketcherInputDialog.getDouble(
              context: context, title: 'New Flowrate');
          if (element is Component) {
            String cmd = element.associatedCmndSource['flowrate'] ?? "";
            if (cmd == "") {
            } else {
              // String? newCmnd = jsonEncode(HardcodedCommands()
              //     .injectVal(element.deviceName, cmd, newVal));
              String? newCmnd = HardcodedCommands()
                      .injectVal(element.deviceName, cmd, newVal) ??
                  "";
              if (newCmnd == "") {}
              {
                state?.widget.mqttService.publish(
                    MqttTopics.getCmndTopic(element.deviceName), newCmnd);
              }
            }
          }
        },
        child: const Text('Set flowrate'),
      ),
    ),
    ElementMenuItem(
      builder: (context, element) => Text(
        element.text,
        style: const TextStyle(fontWeight: FontWeight.w900),
      ),
      keepMenuOpen: true,
    ),
    ElementMenuItem(
      builder: (context, element) => TextMenu(element: element),
      keepMenuOpen: true,
    ),
    ElementMenuItem(
      builder: (context, element) => InkWell(
        onTap: () {
          final state = context.findAncestorStateOfType<FlowSketcherState>();
          state?.widget.dashboard.removeElementConnections(element);
          state?._updateConnections();
        },
        child: const Text('Remove all connections'),
      ),
    ),
    ElementMenuItem(
      builder: (context, element) => ElementSettingsMenu(element: element),
      keepMenuOpen: true,
    ),
  ],
  'Valve': [
    ElementMenuItem(
      builder: (context, element) => Text(
        element.text,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      keepMenuOpen: true,
    ),
    ElementMenuItem(
      builder: (context, element) => InkWell(
        onTap: () {
          final state = context.findAncestorStateOfType<FlowSketcherState>();
          state?.widget.dashboard.removeElement(element);
          state?._updateConnections();
        },
        child: const Text('Delete Valve'),
      ),
    ),
  ],
  'default': [
    ElementMenuItem(
      builder: (context, element) => Text(
        element.text,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      keepMenuOpen: true,
    ),
    ElementMenuItem(
      builder: (context, element) => InkWell(
        onTap: () {
          final state = context.findAncestorStateOfType<FlowSketcherState>();
          state?.widget.dashboard.removeElement(element);
          state?._updateConnections();
        },
        child: const Text('Delete'),
      ),
    ),
    ElementMenuItem(
      builder: (context, element) => TextMenu(element: element),
      keepMenuOpen: true,
    ),
    ElementMenuItem(
      builder: (context, element) => InkWell(
        onTap: () {
          final state = context.findAncestorStateOfType<FlowSketcherState>();
          state?.widget.dashboard.removeElementConnections(element);
          state?._updateConnections();
        },
        child: const Text('Remove all connections'),
      ),
    ),
    ElementMenuItem(
      builder: (context, element) => InkWell(
        onTap: () {
          final state = context.findAncestorStateOfType<FlowSketcherState>();
          state?.widget.dashboard.setElementResizable(element, true);
        },
        child: const Text('Resize'),
      ),
    ),
    ElementMenuItem(
      builder: (context, element) => ElementSettingsMenu(element: element),
      keepMenuOpen: true,
    ),
  ],
};

final Map<String, List<ComponentConfig>> componentConfig = {
  "R4": [
    ComponentConfig(
      label: "R4 (HPLC) Pump A",
      build: (pos) => Component(
        position: pos,
        text: 'R4 (HPLC) A',
        size: const Size(100, 50),
        deviceName: 'vapourtecR4P1700',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Pump',
        volume: 5,
        associatedCmndSource: {"flowrate": "pafr"},
      ),
    ),
    ComponentConfig(
      label: "R4 (HPLC) Pump B",
      build: (pos) => Component(
        position: pos,
        text: 'R4 (HPLC) B',
        size: const Size(100, 50),
        deviceName: 'vapourtecR4P1700',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Pump',
        volume: 5,
        associatedCmndSource: {"flowrate": "pbfr"},
      ),
    ),
    ComponentConfig(
      label: "R4 3-way Valve (S/R A)",
      build: (pos) => Component(
        position: pos,
        deviceName: "null",
        volume: 0.25,
        size: const Size(100, 50),
        text: 'R4 S/R Valve A',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Valve',
        associatedCmndSource: {'valveState': 'svasr'},
      ),
    ),
    ComponentConfig(
      label: "R4 3-way Valve (S/R B)",
      build: (pos) => Component(
        position: pos,
        deviceName: "null",
        volume: 0.25,
        size: const Size(100, 50),
        text: 'R4 S/R Valve B',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Valve',
        associatedCmndSource: {'valveState': 'svbsr'},
      ),
    ),
    ComponentConfig(
      label: "R4 Inject A",
      build: (pos) => Component(
        position: pos,
        text: 'R4 Inject A',
        size: const Size(100, 50),
        deviceName: 'null',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Injector',
        volume: 0.25,
        associatedCmndSource: {},
      ),
    ),
    ComponentConfig(
      label: "R4 Inject B",
      build: (pos) => Component(
        position: pos,
        text: 'R4 Inject B',
        size: const Size(100, 50),
        deviceName: 'null',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Injector',
        volume: 0.25,
        associatedCmndSource: {},
      ),
    ),
  ],
  "Flowsyn Maxi": [
    ComponentConfig(
      label: "Flowsyn Maxi Pump A",
      build: (pos) => Component(
        position: pos,
        text: 'Maxi Pump A',
        size: const Size(100, 50),
        deviceName: 'flowsynmaxi2',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'FlowsynMaxi',
        volume: 5,
        associatedCmndSource: {"flowrate": "pafr"},
      ),
    ),
    ComponentConfig(
      label: "Flowsyn Maxi Pump B",
      build: (pos) => Component(
        position: pos,
        text: 'Maxi Pump B',
        size: const Size(100, 50),
        deviceName: 'flowsynmaxi1',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'FlowsynMaxi',
        volume: 5,
        associatedCmndSource: {"flowrate": "pbfr"},
      ),
    ),
    ComponentConfig(
      label: "3-way Valve (S/R A)",
      build: (pos) => Component(
        position: pos,
        deviceName: "null",
        volume: 0.25,
        size: const Size(100, 50),
        text: 'R4 S/R Valve A',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Valve',
        associatedCmndSource: {'valveState': 'svasr'},
      ),
    ),
    ComponentConfig(
      label: "3-way Valve (S/R B)",
      build: (pos) => Component(
        position: pos,
        deviceName: "null",
        volume: 0.25,
        size: const Size(100, 50),
        text: 'R4 S/R Valve B',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Valve',
        associatedCmndSource: {'valveState': 'svbsr'},
      ),
    ),
    ComponentConfig(
      label: "Flowsyn Inject A",
      build: (pos) => Component(
        position: pos,
        text: 'Flowsyn Inject A',
        size: const Size(100, 50),
        deviceName: 'null',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Injector',
        volume: 0.25,
        associatedCmndSource: {},
      ),
    ),
    ComponentConfig(
      label: "Flowsyn Inject B",
      build: (pos) => Component(
        position: pos,
        text: 'Flowsyn Inject B',
        size: const Size(100, 50),
        deviceName: 'null',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Injector',
        volume: 0.25,
        associatedCmndSource: {},
      ),
    ),
  ],
  "Columns": [
    ComponentConfig(
      label: "Column (2 mL)",
      build: (pos) => Component(
        position: pos,
        text: 'Column (2 mL)',
        textSize: 15,
        size: const Size(100, 50),
        deviceName: "null",
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Column',
        volume: 2,
        associatedCmndSource: {},
      ),
    ),
    ComponentConfig(
      label: "Column (5 mL)",
      build: (pos) => Component(
        position: pos,
        text: 'Column (5 mL)',
        textSize: 15,
        size: const Size(100, 50),
        deviceName: "null",
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Column',
        volume: 5,
        associatedCmndSource: {},
      ),
    ),
    ComponentConfig(
      label: "Column (10 mL)",
      build: (pos) => Component(
        position: pos,
        text: 'Column (10 mL)',
        textSize: 15,
        size: const Size(100, 50),
        deviceName: "null",
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Column',
        volume: 10,
        associatedCmndSource: {},
      ),
    ),
  ],
  "Analytical": [
    ComponentConfig(
      label: "Magritek 60",
      build: (pos) => Component(
        position: pos,
        text: 'Magritek 60',
        size: const Size(100, 50),
        deviceName: 'reactIR702L1', // TODO: fix if needed
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'NMR',
        volume: 0.25,
        associatedCmndSource: {},
      ),
    ),
    ComponentConfig(
      label: "ReactIR 702L1",
      build: (pos) => Component(
        position: pos,
        text: 'ReactIR 702L1',
        size: const Size(100, 50),
        deviceName: 'reactIR702L1',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'IR',
        volume: 0.25,
        associatedCmndSource: {},
      ),
    ),
  ],
  "BPRs": List.generate(4, (i) {
    final bar = [2, 5, 8, 10][i];
    return ComponentConfig(
      label: "BPR ($bar Bar)",
      build: (pos) => Component(
        position: pos,
        text: "BPR ($bar Bar)",
        size: const Size(100, 50),
        deviceName: "null",
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'BPR',
        volume: 0.1,
        associatedCmndSource: {},
      ),
    );
  }),
  "Stocks": [
    ComponentConfig(
      label: "Stock Solution",
      build: (pos) => Component(
        position: pos,
        text: 'Stock',
        size: const Size(100, 50),
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.rightCenter],
        deviceName: 'null',
        deviceType: 'FlowOrigin',
        volume: 0,
        associatedCmndSource: {},
      ),
    ),
    ComponentConfig(
      label: "Pushing Solvent",
      build: (pos) => Component(
        position: pos,
        text: 'Push',
        size: const Size(100, 50),
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.rightCenter],
        deviceName: 'null',
        deviceType: 'FlowOrigin',
        volume: 0,
        associatedCmndSource: {},
      ),
    ),
  ],
  "Standalone Pumps": [
    ComponentConfig(
      label: "Vapourtec SF10",
      build: (pos) => Component(
        position: pos,
        text: 'SF10',
        size: const Size(100, 50),
        deviceName: 'sf10vapourtec1',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter, Handler.rightCenter],
        deviceType: 'Pump',
        volume: 5,
        associatedCmndSource: {"flowrate": 'fr'},
      ),
    ),
  ],
  "Hotcoils": [
    for (var mL in [10, 20, 40])
      ComponentConfig(
        label: "Hotcoil ($mL mL)",
        build: (pos) => Component(
          position: pos,
          text: "Hotcoil ($mL mL)",
          size: const Size(100, 50),
          deviceName: "hotcoil1",
          handlerSize: 15,
          kind: ElementKind.rectangle,
          handlers: [Handler.leftCenter, Handler.rightCenter],
          deviceType: 'Coil',
          volume: mL.toDouble(),
          associatedCmndSource: {},
        ),
      ),
  ],
  "Connectors": [
    ComponentConfig(
      label: "T-Piece",
      build: (pos) => Component(
        position: pos,
        text: 'T-Piece',
        size: const Size(100, 50),
        deviceName: "null",
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [
          Handler.leftCenter,
          Handler.rightCenter,
          Handler.bottomCenter,
        ],
        deviceType: 'TPiece',
        volume: 0.05,
        associatedCmndSource: {},
      ),
    ),
  ],
  "Collection Points": [
    ComponentConfig(
      label: "Waste",
      build: (pos) => Component(
        position: pos,
        text: 'Waste',
        size: const Size(100, 50),
        deviceName: 'null',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter],
        deviceType: 'FlowTerminus',
        volume: 0,
        associatedCmndSource: {},
      ),
    ),
    ComponentConfig(
      label: "Product",
      build: (pos) => Component(
        position: pos,
        text: 'Product',
        size: const Size(100, 50),
        deviceName: 'null',
        handlerSize: 15,
        kind: ElementKind.rectangle,
        handlers: [Handler.leftCenter],
        deviceType: 'FlowTerminus',
        volume: 0,
        associatedCmndSource: {},
      ),
    ),
  ],
};

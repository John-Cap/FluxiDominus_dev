import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/components.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/dashboard.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/connection_params.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/flow_element.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/flow_chart.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/ui/draw_arrow.dart';
import 'package:star_menu/star_menu.dart';
import '../../config/UI/brokers_and_topics.dart';
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
        title: const Text('FlowSketcher'),
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
        "volume": element.volume
      };
      print('WJ connections of dash -> ${jsonEncode(mqttReport.report)}');
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
        onItemTapped: (index, controller) => controller.closeMenu!(),
        parentContext: context,
        items: [
          Wrap(
            children: [
              ActionChip(
                label: const Text('Add 3-way Valve'),
                onPressed: () {
                  widget.dashboard.addElement(
                    Component(
                      position: position,
                      deviceName: "null",
                      volume: 0.25,
                      size: const Size(100, 50),
                      text: 'Valve',
                      handlerSize: 15,
                      kind: ElementKind.rectangle,
                      handlers: [
                        Handler.leftCenter,
                        Handler.rightCenter,
                        Handler.bottomCenter,
                      ],
                      deviceType: 'Valve',
                    ),
                  );
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add column (2 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    textSize: 15,
                    text: 'Column (2 mL)',
                    deviceName: "null",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Column',
                    volume: 2,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add column (5 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    textSize: 15,
                    text: 'Column (5 mL)',
                    deviceName: "null",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Column',
                    volume: 5,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add column (10 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    textSize: 15,
                    text: 'Column (10 mL)',
                    deviceName: "null",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Column',
                    volume: 10,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Magritek 60'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Magritek 60',
                    deviceName: 'reactIR702L1', //TODO - correct name
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    volume: 0.25,
                    deviceType: 'NMR',
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add ReactIR 702L1'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'ReactIR 702L1',
                    deviceName: 'reactIR702L1',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'IR',
                    volume: 0.25,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (2 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'BPR (2 Bar)',
                    deviceName: "null",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'BPR',
                    volume: 0.1,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (5 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'BPR (5 Bar)',
                    deviceName: "null",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'BPR',
                    volume: 0.1,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (8 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'BPR (8 Bar)',
                    deviceName: "null",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'BPR',
                    volume: 0.1,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (10 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'BPR (10 Bar)',
                    deviceName: "null",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'BPR',
                    volume: 0.1,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Stock Solution'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Stock',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceName: 'null',
                    deviceType: 'FlowOrigin',
                    volume: 0,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Pushing Solvent'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Push',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceName: 'null',
                    deviceType: 'FlowOrigin',
                    volume: 0,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add collection point'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Collection point',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceName: 'null',
                    deviceType: 'FlowTerminus',
                    volume: 0,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Flowsyn Maxi 1'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Flowsyn Maxi 1',
                    deviceName: 'flowsynmaxi2',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'FlowsynMaxi',
                    volume: 5,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Flowsyn Maxi 2'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Flowsyn Maxi 2',
                    deviceName: 'flowsynmaxi1',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'FlowsynMaxi',
                    volume: 5,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Vapourtec R4 (HPLC) Pump'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'R4 (HPLC)',
                    deviceName: 'vapourtecR4P1700',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Pump',
                    volume: 5,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Vapourtec R4 (Peristaltic)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'R4 (Peristaltic)',
                    deviceName: 'vapourtecR4P1700',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'vapourtecR4',
                    volume: 5,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Vapourtec SF10'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'SF10',
                    deviceName: 'sf10vapourtec1',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Pump',
                    volume: 5,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add hotcoil (10 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Hotcoil (10 mL)',
                    deviceName: "hotcoil1",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Coil',
                    volume: 10,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add hotcoil (20 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Hotcoil (20 mL)',
                    deviceName: "hotcoil1",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Coil',
                    volume: 20,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add hotcoil (40 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Hotcoil (40 mL)',
                    deviceName: "hotcoil1",
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                    deviceType: 'Coil',
                    volume: 40,
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add T-Piece'),
                onPressed: () {
                  widget.dashboard.addElement(Component(
                    position: position,
                    size: const Size(100, 50),
                    text: 'T-Piece',
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Save'),
                onPressed: () {
                  print('WJ - Attempting to publish');
                  _updateConnections();
                  _buildMqttReport();
                  _mergeTubingIntoMqttReport(); //setState(() {});
                  widget.mqttService
                          .currDashboardJson = //Necessary for db operations?
                      widget.dashboard.saveDashboard();
                  widget.mqttService.publish(
                      MqttTopics.getUITopic("FlowSketcher"),
                      mqttReport.toJsonString());
                },
              ),
              ActionChip(
                label: const Text('Load'),
                onPressed: () {
                  widget.dashboard = widget.dashboard
                      .loadDashboard(widget.mqttService.currDashboardJson);
                  _updateConnections();
                },
              )
            ],
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
      };
    }

    mqttReport.report = widget.updatedReport;
    widget.mqttService.currFlowScript = widget.updatedReport;
    debugPrint("Merged report with tubing: ${mqttReport.toJsonString()}");
  }

/*
  void _mergeTubingIntoMqttReport() {
    final updatedReport = <String, Map<String, dynamic>>{};
    int tubingCounter = 1;

    for (final element in widget.dashboard.elements) {
      final fromId = element.id;

      // Include original element as-is
      updatedReport[fromId] = {
        "name": element.text,
        "flowsInto": element.next
            .map((conn) =>
                "tubing_${tubingCounter}_${fromId}_${conn.destElementId}")
            .toList(),
        "deviceName": element.deviceName,
        "deviceType": element.deviceType,
        "volume": element.volume,
      };

      for (final connection in element.next) {
        final tubingId =
            "tubing_${tubingCounter}_${fromId}_${connection.destElementId}";

        updatedReport[tubingId] = {
          "name": "Tubing",
          "flowsInto": [connection.destElementId],
          "deviceName": "tubing${connection.tubingType}",
          "deviceType": "Tubing",
          "volume": connection.tubingVolume,
        };

        tubingCounter++;
      }
    }

    mqttReport.report = updatedReport;
    widget.mqttService.currFlowScript = updatedReport;
    debugPrint("Merged report with tubing: ${mqttReport.toJsonString()}");
  }
*/
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

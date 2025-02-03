import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/dashboard.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/flow_element.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/flow_chart.dart';
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
    debugPrint(('WJ -> ${widget.dashboard.connections.toString()}'));
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
        "deviceName": element.deviceName
      };
      widget.mqttService.currFlowScript = mqttReport.report;
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
                label: const Text('Add valve'),
                onPressed: () {
                  widget.dashboard.addElement(
                    FlowElement(
                      position: position,
                      deviceName: "null",
                      size: const Size(100, 50),
                      text: 'Valve',
                      handlerSize: 15,
                      kind: ElementKind.rectangle,
                      handlers: [
                        Handler.leftCenter,
                        Handler.rightCenter,
                      ],
                    ),
                  );
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add column (2 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add column (5 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add column (10 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Magritek 60'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add ReactIR 702L1'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (2 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (5 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (8 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add BPR (10 Bar)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Stock Solution'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Stock',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Pushing Solvent'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Push',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add collection point'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
                    position: position,
                    size: const Size(100, 50),
                    text: 'Collection point',
                    handlerSize: 15,
                    kind: ElementKind.rectangle,
                    handlers: [
                      Handler.leftCenter,
                      Handler.rightCenter,
                    ],
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Flowsyn Maxi 1'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Flowsyn Maxi 2'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Vapourtec R4 (HPLC)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Vapourtec R4 (Peristaltic)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add Vapourtec SF10'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add hotcoil (10 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add hotcoil (20 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              ActionChip(
                label: const Text('Add hotcoil (40 mL)'),
                onPressed: () {
                  widget.dashboard.addElement(FlowElement(
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
                  ));
                  _updateConnections();
                },
              ),
              /*
              ActionChip(
                label: const Text('Set'),
                onPressed: () {
                  print('WJ - Attempting to publish');
                  _updateConnections();
                  _buildMqttReport();
                  //_publishMqttReport();
                },
              ),
              */
              ActionChip(
                label: const Text('Save'),
                onPressed: () {
                  print('WJ - Attempting to publish');
                  _updateConnections();
                  _buildMqttReport();
                  widget.mqttService.currDashboardJson =
                      widget.dashboard.saveDashboard();
                  //setState(() {});
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

  void updateConnections() {
    widget.dashboard =
        widget.dashboard.loadDashboard(widget.mqttService.currDashboardJson);
  }
}

class ConnectionMqttReport {
  Map<String, Map<String, dynamic>> report = {};
  String toJsonString() {
    return jsonEncode(report);
  }
}

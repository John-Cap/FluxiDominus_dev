import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/dashboard.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/flow_element.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/objects/diamond_widget.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/objects/hexagon_widget.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/objects/oval_widget.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/objects/parallelogram_widget.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/objects/rectangle_widget.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/objects/storage_widget.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/ui/element_handlers.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/ui/resize_widget.dart';

/// Widget that use [element] properties to display it on the dashboard scene
class ElementWidget extends StatefulWidget {
  final Dashboard dashboard;
  final MqttService mqttService;
  final FlowElement element;

  final Function(BuildContext context, Offset position)? onElementPressed;
  final Function(BuildContext context, Offset position)?
      onElementSecondaryTapped;
  final Function(BuildContext context, Offset position)? onElementLongPressed;
  final Function(BuildContext context, Offset position)?
      onElementSecondaryLongTapped;
  final Function(
    BuildContext context,
    Offset position,
    Handler handler,
    FlowElement element,
  )? onHandlerPressed;
  final Function(
    BuildContext context,
    Offset position,
    Handler handler,
    FlowElement element,
  )? onHandlerSecondaryTapped;
  final Function(
    BuildContext context,
    Offset position,
    Handler handler,
    FlowElement element,
  )? onHandlerLongPressed;
  final Function(
    BuildContext context,
    Offset position,
    Handler handler,
    FlowElement element,
  )? onHandlerSecondaryLongTapped;

  const ElementWidget({
    super.key,
    required this.dashboard,
    required this.element,
    this.onElementPressed,
    this.onElementSecondaryTapped,
    this.onElementLongPressed,
    this.onElementSecondaryLongTapped,
    this.onHandlerPressed,
    this.onHandlerSecondaryTapped,
    this.onHandlerLongPressed,
    this.onHandlerSecondaryLongTapped,
    required this.mqttService,
  });

  @override
  State<ElementWidget> createState() => _ElementWidgetState();
}

class _ElementWidgetState extends State<ElementWidget> {
  // local widget touch position when start dragging
  Offset delta = Offset.zero;

  @override
  void initState() {
    super.initState();
    widget.element.addListener(_elementChanged);
  }

  @override
  void dispose() {
    widget.element.removeListener(_elementChanged);
    super.dispose();
  }

  _elementChanged() {
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    Widget element;

    switch (widget.element.kind) {
      case ElementKind.diamond:
        element = DiamondWidget(element: widget.element);
        break;
      case ElementKind.storage:
        element = StorageWidget(element: widget.element);
        break;
      case ElementKind.oval:
        element = OvalWidget(element: widget.element);
        break;
      case ElementKind.parallelogram:
        element = ParallelogramWidget(element: widget.element);
        break;
      case ElementKind.hexagon:
        element = HexagonWidget(element: widget.element);
        break;
      case ElementKind.rectangle:
      default:
        element = RectangleWidget(element: widget.element);
    }

    if (widget.element.isResizing) {
      return Transform.translate(
        offset: widget.element.position,
        transformHitTests: true,
        child: ResizeWidget(
          element: widget.element,
          dashboard: widget.dashboard,
          child: element,
        ),
      );
    }

    element = Padding(
      padding: EdgeInsets.all(widget.element.handlerSize / 2),
      child: element,
    );

    Offset tapLocation = Offset.zero;
    Offset secondaryTapDownPos = Offset.zero;
    return Transform.translate(
      offset: widget.element.position,
      transformHitTests: true,
      child: GestureDetector(
        onTapDown: (details) => tapLocation = details.globalPosition,
        onSecondaryTapDown: (details) =>
            secondaryTapDownPos = details.globalPosition,
        onTap: () {
          if (widget.onElementPressed != null) {
            widget.onElementPressed!(context, tapLocation);
          }
        },
        onSecondaryTap: () {
          if (widget.onElementSecondaryTapped != null) {
            widget.onElementSecondaryTapped!(context, secondaryTapDownPos);
          }
        },
        onLongPress: () {
          if (widget.onElementLongPressed != null) {
            widget.onElementLongPressed!(context, tapLocation);
          }
        },
        onSecondaryLongPress: () {
          if (widget.onElementSecondaryLongTapped != null) {
            widget.onElementSecondaryLongTapped!(context, secondaryTapDownPos);
          }
        },
        child: Listener(
          onPointerDown: (event) {
            delta = event.localPosition;
          },
          child: Draggable<FlowElement>(
            data: widget.element,
            dragAnchorStrategy: childDragAnchorStrategy,
            childWhenDragging: const SizedBox.shrink(),
            feedback: Material(
              color: Colors.transparent,
              child: element,
            ),
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                ElementHandlers(
                  dashboard: widget.dashboard,
                  element: widget.element,
                  handlerSize: widget.element.handlerSize,
                  onHandlerPressed: widget.onHandlerPressed,
                  onHandlerSecondaryTapped: widget.onHandlerSecondaryTapped,
                  onHandlerLongPressed: widget.onHandlerLongPressed,
                  onHandlerSecondaryLongTapped:
                      widget.onHandlerSecondaryLongTapped,
                  child: element,
                ),
                Positioned(
                  top: -25,
                  left: 4,
                  child: ValueListenableBuilder<Map<String, dynamic>>(
                    valueListenable: widget.mqttService.flowtracking,
                    builder: (context, flowData, _) {
                      final route = flowData["route"] ?? {};
                      final thisId = widget.element.id;

                      if (!route.containsKey(thisId)) {
                        return const SizedBox.shrink();
                      }

                      final info = route[thisId] as Map<String, dynamic>;
                      final zeroEpoch = widget.mqttService.flowtrackingZerotime
                          .secSinceEpoch()
                          .round();

                      String frontReport = "";
                      String tailReport = "";

                      int? frontArrive = (info["slugFrontArrivesAt"] is num)
                          ? (info["slugFrontArrivesAt"] as num).round()
                          : null;
                      int? frontLeave = (info["slugFrontExitsAt"] is num)
                          ? (info["slugFrontExitsAt"] as num).round()
                          : null;

                      if (frontArrive != null && frontArrive != -1) {
                        int frontArrivesAt = frontArrive - zeroEpoch;
                        frontArrivesAt =
                            frontArrivesAt < 0 ? 0 : frontArrivesAt;

                        frontReport = frontArrivesAt > 120
                            ? "Front-> Arrives in ${(frontArrivesAt / 60).round()} min"
                            : "Front-> Arrives in ${frontArrivesAt.round()} s";
                      } else if (frontLeave != null && frontLeave != -1) {
                        int frontLeaveAt = frontLeave - zeroEpoch;
                        frontLeaveAt = frontLeaveAt < 0 ? 0 : frontLeaveAt;

                        frontReport = frontLeaveAt > 120
                            ? "Front-> Exits in ${(frontLeaveAt / 60).round()} min"
                            : "Front-> Exits in ${frontLeaveAt.round()} s";
                      }

                      int? tailArrive = (info["slugTailArrivesAt"] is num)
                          ? (info["slugTailArrivesAt"] as num).round()
                          : null;
                      int? tailLeave = (info["slugTailExitsAt"] is num)
                          ? (info["slugTailExitsAt"] as num).round()
                          : null;

                      if (tailArrive != null && tailArrive != -1) {
                        int tailArrivesAt = tailArrive - zeroEpoch;
                        tailArrivesAt = tailArrivesAt < 0 ? 0 : tailArrivesAt;

                        tailReport = tailArrivesAt > 60
                            ? "Tail-> Arrives in ${(tailArrivesAt / 60).round()} min"
                            : "Tail-> Arrives in ${tailArrivesAt.round()} s";
                      } else if (tailLeave != null && tailLeave != -1) {
                        int tailLeaveAt = tailLeave - zeroEpoch;
                        tailLeaveAt = tailLeaveAt < 0 ? 0 : tailLeaveAt;

                        tailReport = tailLeaveAt > 60
                            ? "Tail-> Exits in ${(tailLeaveAt / 60).round()} min"
                            : "Tail-> Exits in ${tailLeaveAt.round()} s";
                      }

                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (frontReport.isNotEmpty)
                            Text(frontReport,
                                style: const TextStyle(
                                    color: Colors.green, fontSize: 10)),
                          if (tailReport.isNotEmpty)
                            Text(tailReport,
                                style: const TextStyle(
                                    color: Colors.blue, fontSize: 10)),
                        ],
                      );
                    },
                  ),
                ),
              ],
            ),
            onDragUpdate: (details) {
              widget.element.changePosition(details.globalPosition -
                  widget.dashboard.dashboardPosition -
                  delta);
            },
            onDragEnd: (details) {
              widget.element.changePosition(
                  details.offset - widget.dashboard.dashboardPosition);
            },
          ),
        ),
      ),
    );
  }
}

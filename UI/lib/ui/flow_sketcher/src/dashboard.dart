import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_flow_chart/includes/components.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/connection_params.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/flow_element.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/ui/draw_arrow.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/ui/grid_background.dart';
import 'package:uuid/uuid.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter/cupertino.dart';

/// Class to store all the scene elements.
/// This also acts as the controller to the flow_chart widget
/// It notifies changes to [FlowChart]
class Dashboard extends ChangeNotifier {
  List<Component> elements;
  Offset dashboardPosition;
  Size dashboardSize;
  Map<String, List<dynamic>> connections;
  Map<String, String> idToName;

  String? nameFromId(String id) {
    return idToName[id];
  }

  /// [handlerFeedbackOffset] sets an offset for the handler when user is dragging it
  /// This can be used to prevent the handler being covered by user's finger on touch screens
  late Offset handlerFeedbackOffset;

  GridBackgroundParams gridBackgroundParams;
  bool blockDefaultZoomGestures;

  void appendElementUnique(String key, String value) {
    // Get the list associated with the key, or create a new list if it doesn't exist
    connections.putIfAbsent(key, () => []);

    // Check if the list already contains the value
    if (!connections[key]!.contains(value)) {
      connections[key]!
          .add(value); // Add the value to the list if it's not already present
    }
  }

  /// minimum zoom factor allowed
  /// default is 0.25
  /// setting it to 1 will prevent zooming out
  /// setting it to 0 will remove the limit
  double minimumZoomFactor;

  ///////////////////////////////////
  /// WJ additional methods/properties
  void addConnection(
      FlowElement sourceElement, String destId, ArrowParams arrowParams,
      {bool notify = true}) {
    FlowElement? destElement = findElementById(destId);
    if (destElement == null) {
      debugPrint('Destination element with ID $destId not found!');
      return;
    }
    // Method to find a connection by source and destination elements
    /*
    ConnectionParams? findConnection(
        FlowElement sourceElement, FlowElement destElement) {
      try {
        return sourceElement.next.firstWhere(
            (connection) => connection.destElementId == destElement.id);
      } catch (e) {
        return null;
      }
    }
    */

    arrowParams.setScale(1, gridBackgroundParams.scale);
    // Remove any existing connection to the same destination
    sourceElement.next
        .removeWhere((connection) => connection.destElementId == destId);
    // Add the new connection
    sourceElement.next
        .add(ConnectionParams(destElementId: destId, arrowParams: arrowParams));

    if (notify) {
      notifyListeners();
    }
  }

  // Method to remove a connection by source and destination elements
  void removeConnection(FlowElement sourceElement, FlowElement destElement,
      {bool notify = true}) {
    sourceElement.next.removeWhere(
        (connection) => connection.destElementId == destElement.id);
    if (notify) {
      notifyListeners();
    }
  }

  // Method to remove all connections for a specific element
  void removeAllConnections(FlowElement element, {bool notify = true}) {
    element.next.clear();
    if (notify) {
      notifyListeners();
    }
  }

  ///////////////////////////////////

  /// callback when the scale is updated
  void Function(double scale)? onScaleUpdate;

  Dashboard({
    Offset? handlerFeedbackOffset,
    this.blockDefaultZoomGestures = false,
    this.minimumZoomFactor = 0.25,
  })  : elements = [],
        dashboardPosition = Offset.zero,
        dashboardSize = const Size(0, 0),
        connections = {},
        idToName = {},
        gridBackgroundParams = GridBackgroundParams() {
    // This is a workaround to set the handlerFeedbackOffset
    // to improve the user experience on devices with touch screens
    // This will prevent the handler being covered by user's finger
    if (handlerFeedbackOffset != null) {
      this.handlerFeedbackOffset = handlerFeedbackOffset;
    } else {
      if (kIsWeb) {
        this.handlerFeedbackOffset = const Offset(0, 0);
      } else {
        if (Platform.isIOS || Platform.isAndroid) {
          this.handlerFeedbackOffset = const Offset(0, -50);
        } else {
          this.handlerFeedbackOffset = const Offset(0, 0);
        }
      }
    }
  }

  /// set grid background parameters
  setGridBackgroundParams(GridBackgroundParams params) {
    gridBackgroundParams = params;
    if (onScaleUpdate != null) {
      params.addOnScaleUpdateListener(onScaleUpdate!);
    }
    notifyListeners();
  }

  /// set the feedback offset to help on mobile device to see the
  /// end of arrow and not hiding behind the finger when moving it
  setHandlerFeedbackOffset(Offset offset) {
    handlerFeedbackOffset = offset;
  }

  /// set [isResizable] element property
  setElementResizable(FlowElement element, bool resizable,
      {bool notify = true}) {
    element.isResizing = resizable;
    if (notify) notifyListeners();
  }

  /// add a [FlowElement] to the dashboard
  addElement(Component element, {bool notify = true}) {
    if (element.id.isEmpty) {
      element.id = const Uuid().v4();
    }
    idToName[element.id] = element.text;
    // element.scale = _currentZoomFactor;
    element.setScale(1, gridBackgroundParams.scale);
    elements.add(element);
    if (notify) {
      notifyListeners();
    }
  }

  /// find the element by its [id]
  int findElementIndexById(String id) {
    return elements.indexWhere((element) => element.id == id);
  }

  /// find the element by its [id] for convenience
  /// return null if not found
  FlowElement? findElementById(String id) {
    try {
      return elements.firstWhere((element) => element.id == id);
    } catch (e) {
      return null;
    }
  }

  /// find the connection from [srcElement] to [destElement]
  /// return null if not found
  /// In case of multiple connections, first connection is returned
  ConnectionParams? findConnectionByElements(
      FlowElement srcElement, FlowElement destElement) {
    try {
      return srcElement.next
          .firstWhere((element) => element.destElementId == destElement.id);
    } catch (e) {
      return null;
    }
  }

  /// remove all elements
  removeAllElements({bool notify = true}) {
    elements.clear();
    if (notify) notifyListeners();
  }

  /// remove the [handler] connection of [element]
  removeElementConnection(
    FlowElement element,
    Handler handler, {
    bool notify = true,
  }) {
    Alignment alignment;
    switch (handler) {
      case Handler.topCenter:
        alignment = const Alignment(0.0, -1.0);
        break;
      case Handler.bottomCenter:
        alignment = const Alignment(0.0, 1.0);
        break;
      case Handler.leftCenter:
        alignment = const Alignment(-1.0, 0.0);
        break;
      case Handler.rightCenter:
      default:
        alignment = const Alignment(1.0, 0.0);
    }
    element.next.removeWhere((handlerParam) =>
        handlerParam.arrowParams.startArrowPosition == alignment);
    if (notify) notifyListeners();
  }

  /// remove the connection from [srcElement] to [destElement]
  removeConnectionByElements(FlowElement srcElement, FlowElement destElement,
      {bool notify = true}) {
    srcElement.next.removeWhere(
        (handlerParam) => handlerParam.destElementId == destElement.id);
    if (notify) notifyListeners();
  }

  /// remove all the connection from the [element]
  removeElementConnections(FlowElement element, {bool notify = true}) {
    element.next.clear();
    if (notify) notifyListeners();
  }

  /// remove all the elements with [id] from the dashboard
  removeElementById(String id, {bool notify = true}) {
    // remove the element
    String elementId = '';
    elements.removeWhere((element) {
      if (element.id == id) {
        elementId = element.id;
      }
      return element.id == id;
    });

    // remove all connections to the elements found
    for (FlowElement e in elements) {
      e.next.removeWhere((handlerParams) {
        return elementId.contains(handlerParams.destElementId);
      });
    }
    if (notify) notifyListeners();
  }

  /// remove element
  /// return true if it has been removed
  bool removeElement(FlowElement element, {bool notify = true}) {
    // remove the element
    bool found = false;
    String elementId = element.id;
    elements.removeWhere((e) {
      if (e.id == element.id) found = true;
      return e.id == element.id;
    });

    // remove all connections to the element
    for (FlowElement e in elements) {
      e.next.removeWhere(
          (handlerParams) => handlerParams.destElementId == elementId);
    }
    if (notify) notifyListeners();
    return found;
  }

  /// [factor] needs to be a non negative value
  /// 1 is the default value
  /// giving a value above 1 will zoom the dashboard by the given factor and vice versa
  /// Negative values will be ignored
  /// [zoomFactor] will not go below [minimumZoomFactor]
  /// [focalPoint] is the point where the zoom is centered
  /// default is the center of the dashboard
  void setZoomFactor(double factor, {Offset? focalPoint}) {
    if (factor < minimumZoomFactor || gridBackgroundParams.scale == factor) {
      return;
    }

    focalPoint ??= Offset(dashboardSize.width / 2, dashboardSize.height / 2);

    for (FlowElement element in elements) {
      // reversing current zoom
      element.position =
          (element.position - focalPoint) / gridBackgroundParams.scale +
              focalPoint;
      // applying new zoom
      element.position = (element.position - focalPoint) * factor + focalPoint;
      element.setScale(gridBackgroundParams.scale, factor);
    }

    gridBackgroundParams.setScale(factor, focalPoint);

    notifyListeners();
  }

  /// shorthand to get the current zoom factor
  double get zoomFactor {
    return gridBackgroundParams.scale;
  }

  /// needed to know the diagram widget position to compute
  /// offsets for drag and drop elements
  setDashboardPosition(Offset position) {
    dashboardPosition = position;
  }

  /// needed to know the diagram widget size
  setDashboardSize(Size size) {
    dashboardSize = size;
  }

  /// make an arrow connection from [sourceElement] to
  /// the elements with id [destId]
  /// [arrowParams] definition of arrow parameters
  addNextById(
    FlowElement sourceElement,
    String destId,
    ArrowParams arrowParams, {
    bool notify = true,
  }) {
    int found = 0;
    arrowParams.setScale(1, gridBackgroundParams.scale);
    for (int i = 0; i < elements.length; i++) {
      if (elements[i].id == destId) {
        // if the [id] already exist, remove it and add this new connection
        sourceElement.next
            .removeWhere((element) => element.destElementId == destId);
        sourceElement.next.add(ConnectionParams(
          destElementId: elements[i].id,
          arrowParams: arrowParams,
        ));

        found++;
      }
    }

    if (found == 0) {
      debugPrint('Element with $destId id not found!');
      return;
    }
    if (notify) {
      notifyListeners();
    }
  }

  //******************************* */
  /// manage load/save using json
  Map<String, dynamic> toMap() {
    print('WJ - Factory delivered dashboard 3');
    notifyListeners();
    return <String, dynamic>{
      'elements': elements.map((x) => x.toMap()).toList(),
    };
  }

  factory Dashboard.fromMap(Map<String, dynamic> map) {
    Dashboard d = Dashboard();
    d.elements = List<Component>.from(
      (map['elements'] as List<dynamic>).map<FlowElement>(
        (x) => FlowElement.fromMap(x as Map<String, dynamic>),
      ),
    );
    print('WJ - Factory delivered dashboard 1');
    return d;
  }

  String toJson() {
    print('WJ - Factory delivered dashboard 4');
    print('WJ - the JSON -> "${json.encode(toMap())}"');
    return json.encode(toMap());
  }

  void refreshDashboard() {
    notifyListeners();
  }

  factory Dashboard.fromJson(String source) {
    print('WJ - Factory delivered dashboard 2');
    return Dashboard.fromMap(json.decode(source) as Map<String, dynamic>);
  }

  String prettyJson() {
    var spaces = ' ' * 2;
    var encoder = JsonEncoder.withIndent(spaces);
    return encoder.convert(toMap());
  }

  /// recenter the dashboard
  void recenter() {
    Offset center = Offset(dashboardSize.width / 2, dashboardSize.height / 2);
    gridBackgroundParams.offset = center;
    if (elements.isNotEmpty) {
      Offset currentDeviation = elements.first.position - center;
      for (FlowElement element in elements) {
        element.position -= currentDeviation;
      }
    }
    notifyListeners();
  }

  /// save the dashboard into mqttService
  saveDashboard() {
    return toJson();
  }

  /// clear the dashboard and load the new one from mqttService
  loadDashboard(String currDashboardJson) {
    return Dashboard.fromJson(currDashboardJson);
  }

  void setStateFrom(Dashboard loadedDashboard) {}
}

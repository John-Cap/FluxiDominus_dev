import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/flow_element.dart';

class Component extends FlowElement {
  @override
  final String deviceName;
  final Map<String, String> associatedCmndSource;
  final String deviceType;
  final double volume;
  String topic;
  Component({
    required this.associatedCmndSource,
    required this.deviceName,
    required this.deviceType,
    required this.volume,
    this.topic = "",

    // Pass everything directly to super using this syntax:
    super.position,
    super.size,
    super.text,
    super.textColor,
    super.fontFamily,
    super.textSize,
    super.textIsBold,
    super.kind,
    super.handlers,
    super.handlerSize,
    super.backgroundColor,
    super.borderColor,
    super.borderThickness,
    super.elevation,
    super.next,
  });

  factory Component.fromMap(Map<String, dynamic> map) {
    // First deserialize the base FlowElement properties
    final base = FlowElement.fromMap(map);

    return Component(
      associatedCmndSource:
          Map<String, String>.from(map['associatedCmndSource'] ?? {}),
      deviceName: map['deviceName'] ?? 'null',
      deviceType: map['deviceType'] ?? '',
      volume: (map['volume'] ?? 0).toDouble(),
      topic: map['topic'] ?? '',
      position: base.position,
      size: base.size,
      text: base.text,
      textColor: base.textColor,
      fontFamily: base.fontFamily,
      textSize: base.textSize,
      textIsBold: base.textIsBold,
      kind: base.kind,
      handlers: base.handlers,
      handlerSize: base.handlerSize,
      backgroundColor: base.backgroundColor,
      borderColor: base.borderColor,
      borderThickness: base.borderThickness,
      elevation: base.elevation,
      next: base.next,
    )..setId(map['id']);
  }
}

/*
class Component extends FlowElement {
  @override
  final String deviceName;
  final Map<String, String> associatedCmndSource;
  final String deviceType;
  final double volume;
  String topic;

  Component({
    required this.associatedCmndSource,
    required this.deviceName,
    required this.deviceType,
    required this.volume,
    this.topic = "",
    Offset super.position,
    super.size,
    super.text,
    super.textColor,
    super.fontFamily,
    super.textSize,
    super.textIsBold,
    super.kind,
    super.handlers,
    super.handlerSize,
    super.backgroundColor,
    super.borderColor,
    super.borderThickness,
    super.elevation,
    List<ConnectionParams>? super.next,
  });
  
}
*/

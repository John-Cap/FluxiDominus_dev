import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/connection_params.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/elements/flow_element.dart';

class Component extends FlowElement {
  @override
  final String deviceName;
  final String deviceType;
  final double volume;

  Component({
    required this.deviceName,
    required this.deviceType,
    required this.volume,
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

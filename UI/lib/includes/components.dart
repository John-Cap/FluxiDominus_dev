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
    Offset position = Offset.zero,
    Size size = Size.zero,
    String text = '',
    Color textColor = Colors.black,
    String? fontFamily,
    double textSize = 10,
    bool textIsBold = false,
    ElementKind kind = ElementKind.rectangle,
    List<Handler> handlers = const [
      Handler.topCenter,
      Handler.bottomCenter,
      Handler.rightCenter,
      Handler.leftCenter,
    ],
    double handlerSize = 15.0,
    Color backgroundColor = Colors.white,
    Color borderColor = Colors.blue,
    double borderThickness = 3,
    double elevation = 4,
    List<ConnectionParams>? next,
  }) : super(
          position: position,
          size: size,
          text: text,
          textColor: textColor,
          fontFamily: fontFamily,
          textSize: textSize,
          textIsBold: textIsBold,
          kind: kind,
          handlers: handlers,
          handlerSize: handlerSize,
          backgroundColor: backgroundColor,
          borderColor: borderColor,
          borderThickness: borderThickness,
          elevation: elevation,
          next: next,
        );
}

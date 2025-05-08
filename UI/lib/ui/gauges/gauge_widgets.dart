import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/gauges/control_panel_widgets.dart';
import 'package:flutter_flow_chart/ui/script_builder/hardcoded_command_templates.dart';
import 'dart:async';
import 'package:syncfusion_flutter_gauges/gauges.dart';

abstract class GaugeWidget extends StatefulWidget {
  final String name;
  final String unit;
  final String deviceName;
  final String deviceValueName;
  final MqttService mqttService;
  final String topic;
  final double maxValue;
  final List<String> address;
  final String cmndTopic;
  final String cmndName;
  final double unitMultiplier;

  const GaugeWidget({
    super.key,
    required this.name,
    required this.unit,
    required this.deviceName,
    required this.mqttService,
    required this.deviceValueName,
    required this.topic,
    required this.address,
    required this.maxValue,
    required this.cmndTopic,
    required this.cmndName,
    required this.unitMultiplier,
  });
}

abstract class GaugeWidgetState<T extends GaugeWidget> extends State<T> {
  double value = 0.0;
  late Timer timer;

  @override
  void initState() {
    super.initState();
    //widget.mqttService.initializeMQTTClient();
    //widget.mqttService.connect();
    updateTimer();
  }

  void updateTimer() {
    timer = Timer.periodic(const Duration(milliseconds: 250), (timer) {
      if (widget.mqttService.lastMsgFromTopic.containsKey(widget.topic)) {
        final topicData = widget.mqttService.lastMsgFromTopic[widget.topic];
        if (topicData != null) {
          final newValue = getValueFromAddress(topicData, widget.address);
          if (newValue != null) {
            setVal(newValue);
          }
        }
      }
    });
  }

  dynamic getValueFromAddress(Map<String, dynamic> data, List<String> address) {
    dynamic value = data;
    for (var key in address) {
      if (value is Map<String, dynamic> && value.containsKey(key)) {
        value = value[key];
      } else {
        return null;
      }
    }
    return value;
  }

  void setVal(double val) {
    val = val * widget.unitMultiplier;
    if (value != val) {
      setState(() {
        value = val;
      });
    }
  }

  @override
  void dispose() {
    timer.cancel();
    super.dispose();
  }

  Widget buildGauge();

  @override
  Widget build(BuildContext context) {
    return buildGauge();
  }
}

class SemiCircularGauge extends GaugeWidget {
  const SemiCircularGauge({
    super.key,
    required super.name,
    required super.unit,
    required super.deviceName,
    required super.mqttService,
    required super.deviceValueName,
    required super.topic,
    required super.address,
    required super.maxValue,
    required super.cmndTopic,
    required super.cmndName,
    required super.unitMultiplier,
  });

  @override
  _SemiCircularGaugeState createState() => _SemiCircularGaugeState();
}

class _SemiCircularGaugeState extends GaugeWidgetState<SemiCircularGauge> {
  @override
  Widget buildGauge() {
    return SfRadialGauge(
      title: GaugeTitle(
        text: widget.name,
        textStyle: const TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
      ),
      axes: <RadialAxis>[
        RadialAxis(
          startAngle: 180,
          endAngle: 0,
          minimum: 0,
          maximum: widget.maxValue,
          ranges: <GaugeRange>[
            GaugeRange(
              startValue: 0,
              endValue: widget.maxValue * 0.8,
              color: Colors.green,
              startWidth: 1,
              endWidth: 1.5,
            ),
            GaugeRange(
              startValue: widget.maxValue * 0.8,
              endValue: widget.maxValue,
              color: Colors.orange,
              startWidth: 2,
              endWidth: 2.5,
            ),
          ],
          pointers: <GaugePointer>[NeedlePointer(value: value)],
          annotations: <GaugeAnnotation>[
            GaugeAnnotation(
              widget: Text(
                "${value.toStringAsFixed(1)} ${widget.unit}",
                style:
                    const TextStyle(fontSize: 25, fontWeight: FontWeight.bold),
              ),
              angle: 90,
              positionFactor: 0.5,
            ),
          ],
        ),
      ],
    );
  }
}

//With slider
class GaugeWithSlider extends GaugeWidget {
  final double min;
  final double max;
  final double initialValue;
  //final ValueChanged<double> onChanged;

  void _onChanged(val) {
    String? newCmnd = HardcodedCommands().injectVal(deviceName, cmndName, val);
    mqttService.publish(cmndTopic, newCmnd!);
  }

  const GaugeWithSlider({
    super.key,
    required super.name,
    required super.unit,
    required super.deviceName,
    required super.mqttService,
    required super.deviceValueName,
    required super.topic,
    required super.address,
    required this.min,
    required this.max,
    required this.initialValue,
    required super.maxValue,
    required super.cmndTopic,
    required super.cmndName,
    required super.unitMultiplier,
  });

  @override
  _GaugeWithSliderState createState() => _GaugeWithSliderState();
}

class _GaugeWithSliderState extends GaugeWidgetState<GaugeWithSlider> {
  late double _currentValue;
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _currentValue = widget.initialValue;
    _controller = TextEditingController(text: _currentValue.toString());
  }

  void _updateValue(double value) {
    setState(() {
      _currentValue = value;
      _controller.text = value.toString();
    });
    widget._onChanged(value);
  }

  @override
  Widget buildGauge() {
    return Column(
      children: [
        Flexible(
          flex: 3,
          child: SfRadialGauge(
            title: GaugeTitle(
              text: widget.name,
              textStyle:
                  const TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
            ),
            axes: <RadialAxis>[
              RadialAxis(
                startAngle: 180,
                endAngle: 0,
                minimum: 0,
                maximum: widget.maxValue,
                ranges: <GaugeRange>[
                  GaugeRange(
                    startValue: 0,
                    endValue: widget.maxValue * 0.8,
                    color: Colors.green,
                    startWidth: 1,
                    endWidth: 1.5,
                  ),
                  GaugeRange(
                    startValue: widget.maxValue * 0.8,
                    endValue: widget.maxValue,
                    color: Colors.orange,
                    startWidth: 2,
                    endWidth: 2.5,
                  ),
                ],
                pointers: <GaugePointer>[NeedlePointer(value: value)],
                annotations: <GaugeAnnotation>[
                  GaugeAnnotation(
                    widget: Text(
                      "${value.toStringAsFixed(1)} ${widget.unit}",
                      style: const TextStyle(
                          fontSize: 25, fontWeight: FontWeight.bold),
                    ),
                    angle: 90,
                    positionFactor: 0.5,
                  ),
                ],
              ),
            ],
          ),
        ),
        SliderWithTextField(
          min: widget.min,
          max: widget.max,
          initialValue: widget.initialValue,
          onChanged: _updateValue,
          name: widget.name,
          unit: widget.unit,
          deviceName: widget.deviceName,
          deviceValueName: widget.deviceValueName,
          mqttService: widget.mqttService,
          topic: widget.topic,
          address: widget.address,
        ),
      ],
    );
  }
}

//With toggle
class GaugeWithToggle extends GaugeWidget {
  final bool initialValue;

  void _onChanged(val) {
    String? newCmnd = HardcodedCommands().injectVal(deviceName, cmndName, val);
    mqttService.publish(cmndTopic, newCmnd!);
  }

  const GaugeWithToggle({
    super.key,
    required super.name,
    required super.unit,
    required super.deviceName,
    required super.mqttService,
    required super.deviceValueName,
    required super.topic,
    required super.address,
    required this.initialValue,
    required super.maxValue,
    required super.cmndTopic,
    required super.cmndName,
    required super.unitMultiplier,
  });

  @override
  _GaugeWithToggleState createState() => _GaugeWithToggleState();
}

class _GaugeWithToggleState extends GaugeWidgetState<GaugeWithToggle> {
  late bool currentValue;

  @override
  void initState() {
    super.initState();
    currentValue = widget.initialValue;
  }

  void _updateValue(bool value) {
    setState(() {
      currentValue = value;
    });
    widget._onChanged(value);
  }

  @override
  Widget buildGauge() {
    return Column(
      children: [
        Flexible(
          flex: 3,
          child: SfRadialGauge(
            title: GaugeTitle(
              text: widget.name,
              textStyle:
                  const TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
            ),
            axes: <RadialAxis>[
              RadialAxis(
                startAngle: 180,
                endAngle: 0,
                minimum: 0,
                maximum: widget.maxValue,
                ranges: <GaugeRange>[
                  GaugeRange(
                    startValue: 0,
                    endValue: widget.maxValue * 0.8,
                    color: Colors.green,
                    startWidth: 1,
                    endWidth: 1.5,
                  ),
                  GaugeRange(
                    startValue: widget.maxValue * 0.8,
                    endValue: widget.maxValue,
                    color: Colors.orange,
                    startWidth: 2,
                    endWidth: 2.5,
                  ),
                ],
                pointers: <GaugePointer>[NeedlePointer(value: value)],
                annotations: <GaugeAnnotation>[
                  GaugeAnnotation(
                    widget: Text(
                      "${value.toStringAsFixed(1)} ${widget.unit}",
                      style: const TextStyle(
                          fontSize: 25, fontWeight: FontWeight.bold),
                    ),
                    angle: 90,
                    positionFactor: 0.5,
                  ),
                ],
              ),
            ],
          ),
        ),
        Flexible(
          flex: 1,
          child: TrueFalseToggle(
            initialValue: widget.initialValue,
            onChanged: _updateValue,
            name: widget.name,
            unit: widget.unit,
            deviceName: widget.deviceName,
            deviceValueName: widget.deviceValueName,
            mqttService: widget.mqttService,
            topic: widget.topic,
            address: widget.address,
          ),
        ),
      ],
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';

abstract class ControlPanelWidget extends StatefulWidget {
  final String name;
  final String unit;
  final String deviceName;
  final String deviceValueName;
  final MqttService mqttService;
  final String topic;
  final List<String> address;
  final Map<String, dynamic> lastMsgFromTopic = {};

  ControlPanelWidget(
      {super.key,
      required this.name,
      required this.unit,
      required this.deviceName,
      required this.deviceValueName,
      required this.mqttService,
      required this.topic,
      required this.address});
}

class SliderWithTextField extends ControlPanelWidget {
  final double min;
  final double max;
  final double initialValue;
  final ValueChanged<double> onChanged;

  SliderWithTextField(
      {super.key,
      required this.min,
      required this.max,
      required this.initialValue,
      required this.onChanged,
      required super.name,
      required super.unit,
      required super.deviceName,
      required super.deviceValueName,
      required super.mqttService,
      required super.topic,
      required super.address});

  @override
  _SliderWithTextFieldState createState() => _SliderWithTextFieldState();
}

class _SliderWithTextFieldState extends State<SliderWithTextField> {
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
    //widget.onChanged(value);
  }

  void _onChangeEnd(double value) {
    widget.onChanged(value);
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Slider(
            min: widget.min,
            max: widget.max,
            value: _currentValue,
            onChanged: _updateValue,
            onChangeEnd: _onChangeEnd,
          ),
        ),
        SizedBox(
          width: 60,
          child: TextField(
            controller: _controller,
            keyboardType: TextInputType.number,
            onSubmitted: (value) {
              double newValue = double.tryParse(value) ?? _currentValue;
              if (newValue < widget.min) newValue = widget.min;
              if (newValue > widget.max) newValue = widget.max;
              _updateValue(newValue);
            },
          ),
        ),
      ],
    );
  }
}

class TrueFalseToggle extends ControlPanelWidget {
  final bool initialValue;
  final ValueChanged<bool> onChanged;

  TrueFalseToggle(
      {super.key,
      required this.initialValue,
      required this.onChanged,
      required super.name,
      required super.unit,
      required super.deviceName,
      required super.deviceValueName,
      required super.mqttService,
      required super.topic,
      required super.address});

  @override
  _TrueFalseToggleState createState() => _TrueFalseToggleState();
}

class _TrueFalseToggleState extends State<TrueFalseToggle> {
  late bool _currentValue;

  @override
  void initState() {
    super.initState();
    _currentValue = widget.initialValue;
  }

  void _updateValue(bool value) {
    setState(() {
      _currentValue = value;
    });
    widget.onChanged(value);
  }

  @override
  Widget build(BuildContext context) {
    return SwitchListTile(
      title: const Text('Toggle'),
      value: _currentValue,
      onChanged: _updateValue,
    );
  }
}

//Example
/*
class ControlPanel extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SliderWithTextField(
          min: 0,
          max: 20,
          initialValue: 0,
          onChanged: (value) {
            print('Slider value: $value');
          },
          name: 'Slider',
          unit: 'mL.min-1',
          deviceName: 'vapourtec',
          deviceValueName: 'Flowrate',
          mqttService: mqttService,
          topic: 'subflow/randomTopic',
          address: ["myOhMy", "rightHere"],
        ),
        TrueFalseToggle(
          initialValue: true,
          onChanged: (value) {
            print('Toggle value: $value');
          },
          name: 'Toggle me',
          unit: 'mL.min-1',
          deviceName: 'vapourtec',
          deviceValueName: 'Flowrate',
          mqttService: mqttService,
          topic: 'subflow/randomTopic',
          address: ["myOhMy", "rightHere"],
        ),
      ],
    );
  }
}
void main() {
  runApp(MaterialApp(
    home: Scaffold(
      appBar: AppBar(title: const Text('Control Panel')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: GaugeWithToggle(
          name: 'Moo',
          unit: 'bar',
          deviceName: 'flowsynmaxi2',
          mqttService: mqttService,
          deviceValueName: 'Pump',
          topic: 'subflow/flowsynmaxi2/tele',
          address: const ["state", "pressSystem"],
          initialValue: true,
          maxValue: 150,
          cmndTopic: '',
          cmndName: '',
        ),
      ),
    ),
  ));
}

*/
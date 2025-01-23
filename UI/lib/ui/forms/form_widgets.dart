import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:mqtt_client/mqtt_client.dart';

class FormPanelWidget extends StatefulWidget {
  final String title;
  final List<FormPanelElementWidget> elements;
  final MqttService mqttService;

  const FormPanelWidget({
    required this.title,
    required this.elements,
    super.key,
    required this.mqttService,
  });

  @override
  FormPanelWidgetState createState() => FormPanelWidgetState();
}

class FormPanelWidgetState extends State<FormPanelWidget> {
  final Map<String, String> submittedData = {};

  void updateFormData(String keyName, String value) {
    setState(() {
      submittedData[keyName] = value;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.title,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        ...widget.elements.map((element) {
          return FormPanelElementWidget(
            keyName: element.keyName,
            fieldTitle: element.fieldTitle,
            onValueChanged: updateFormData,
          );
        }),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () {
            widget.mqttService.publish(
              "ui/dbCmnd/in",
              jsonEncode({
                "instructions": {
                  "params": submittedData,
                  "function": "createStdExp"
                }
              }), //.toString(),
              qos: MqttQos.exactlyOnce,
            );
            // Handle form submission or further processing with submittedData
            print('WJ - Submitted data: ${submittedData.toString()}');
          },
          child: const Text('Create experiment'),
        ),
      ],
    );
  }
}

class FormPanelElementWidget extends StatefulWidget {
  final String keyName;
  final String fieldTitle;
  final Function(String, String) onValueChanged;

  const FormPanelElementWidget({
    required this.keyName,
    required this.fieldTitle,
    required this.onValueChanged,
    super.key,
  });

  @override
  _FormPanelElementWidgetState createState() => _FormPanelElementWidgetState();
}

class _FormPanelElementWidgetState extends State<FormPanelElementWidget> {
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: TextField(
        controller: _controller,
        decoration: InputDecoration(
          labelText: widget.fieldTitle,
          border: const OutlineInputBorder(),
        ),
        onChanged: (value) {
          widget.onValueChanged(widget.keyName, value);
        },
      ),
    );
  }
}

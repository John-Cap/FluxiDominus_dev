/*
Test name
Short Description
Long description
Test script -> from scriptbuilder
Flow setup -> from setup builder
*/

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/forms/form_widgets.dart';

class TestCreatorWidget extends StatelessWidget {
  const TestCreatorWidget({
    super.key,
    required this.mqttService,
  });

  final MqttService mqttService;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: FormPanelWidget(
        title: 'Create experiment',
        elements: [
          /*
            nameTest=_params["nameTest"] #Short description
            description=_params["description"] #Long description
            testScript=_params["testScript"] #Generated in UI
            lockScript=0
            flowScript="TODO" #Generated in UI
            labNotebookBaseRef=_params["labNotebookBaseRef"] #Needs to be built up automatically
          */
          FormPanelElementWidget(
            keyName: 'labNotebookBaseRef',
            fieldTitle: 'Lab Notebook Reference',
            onValueChanged: (key, value) {
              print('$key: $value');
            },
          ),
          FormPanelElementWidget(
            keyName: 'nameTest',
            fieldTitle: 'Experiment short description',
            onValueChanged: (key, value) {
              print('$key: $value');
            },
          ),
          FormPanelElementWidget(
            keyName: 'description',
            fieldTitle: 'Experiment long description',
            onValueChanged: (key, value) {
              print('$key: $value');
            },
          ),
        ],
        mqttService: mqttService,
      ),
    );
  }
}

void main() async {
  MqttService mqttService = MqttService(server: 'ws://localhost/');
  await mqttService.initializeMQTTClient();
  mqttService.connect();
  runApp(MaterialApp(
    home: Scaffold(
      appBar: AppBar(
        title: const Text('Test Creator Example'),
      ),
      body: TestCreatorWidget(
        mqttService: mqttService, // Assuming you have an MqttService instance
      ),
    ),
  ));
}

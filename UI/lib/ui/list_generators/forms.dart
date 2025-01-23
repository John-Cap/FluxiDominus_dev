import 'dart:async';

import 'package:flutter/material.dart';

// ignore: must_be_immutable
class DynamicTextFieldPanel extends StatefulWidget {
  final List<Map<String, String>> initialFields;
  Map<String, dynamic> fieldData = {};

  DynamicTextFieldPanel({
    super.key,
    this.initialFields = const [{}],
  });

  @override
  _DynamicTextFieldPanelState createState() => _DynamicTextFieldPanelState();
}

class _DynamicTextFieldPanelState extends State<DynamicTextFieldPanel> {
  final List<Map<String, String>> _fields = [];
  final Map<String, String> _inputValues = {};
  final List<TextEditingController> _controllers = [];

  @override
  void initState() {
    super.initState();
    // Initialize with provided fields
    _fields.addAll(widget.initialFields);
    for (var field in widget.initialFields) {
      final id = field['id']!;
      final controller = TextEditingController();
      _controllers.add(controller);
      _inputValues[id] = '';

      controller.addListener(() {
        setState(() {
          _inputValues[id] = controller.text;
        });
      });
    }
  }

  void addField(String id, String title) {
    final controller = TextEditingController();
    _controllers.add(controller);
    _fields.add({'id': id, 'title': title});
    _inputValues[id] = '';

    controller.addListener(() {
      setState(() {
        _inputValues[id] = controller.text;
      });
    });

    setState(() {}); // Trigger a rebuild to display the new field
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (var i = 0; i < _fields.length; i++)
          TextField(
            controller: _controllers[i],
            decoration: InputDecoration(labelText: _fields[i]['title']),
          ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () {
            widget.fieldData = _inputValues;
            //print(_inputValues); // For debugging purposes
          },
          child: const Text('Submit'),
        ),
      ],
    );
  }
}

void main() async {
  var fields = [
    {'id': 'labNotebookBaseRef', 'title': 'Lab notebook reference'}
  ];
  DynamicTextFieldPanel textPanel = DynamicTextFieldPanel(
    initialFields: fields,
  );
  runApp(MaterialApp(
    home: Scaffold(
      appBar: AppBar(title: const Text('New experiment')),
      body: Center(
        child: textPanel,
      ),
    ),
  ));
  print('WJ - ${textPanel.fieldData}');
  Timer(
      const Duration(seconds: 30), () => print('WJ - ${textPanel.fieldData}'));
}

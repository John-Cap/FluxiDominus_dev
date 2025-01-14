import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/script_builder.dart/script_generator.dart';

class ExpWidget extends StatefulWidget {
  final MqttService mqttService;

  const ExpWidget({super.key, required this.mqttService});

  @override
  _ExpWidgetState createState() => _ExpWidgetState();
}

class _ExpWidgetState extends State<ExpWidget> {
  Map<String, dynamic>? _projects;

  @override
  void initState() {
    super.initState();

    // Listen for MQTT updates and update state when data is received
    widget.mqttService.backendReturn["getAllExpWidgetInfo"]
        ?.addListener(_fetchBackendReturn);

    // Request data on initialization
    requestExpWidgetInfo();
  }

  void _fetchBackendReturn() {
    //TODO - is it listening to the entire mqttService instance??
    final expWidgetInfo =
        widget.mqttService.backendReturn["getAllExpWidgetInfo"]?.value;
    if (expWidgetInfo != null) {
      setState(() {
        _projects = expWidgetInfo;
      });
    }
  }

  @override
  void dispose() {
    widget.mqttService.backendReturn["getAllExpWidgetInfo"]
        ?.removeListener(_fetchBackendReturn);
    super.dispose();
  }

  void requestExpWidgetInfo() {
    final request = {
      "instructions": {
        "params": {"orgId": widget.mqttService.authenticator.user.orgId},
        "function": "getAllExpWidgetInfo"
      }
    };
    widget.mqttService.publish('ui/dbCmnd/in', jsonEncode(request));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your Projects')),
      body: _projects == null
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _projects!.length,
              itemBuilder: (context, index) {
                final projectKey = _projects!.keys.elementAt(index);
                final project = _projects![projectKey]["testlistEntries"];
                final displayName = _projects![projectKey]["projCode"];
                final projDescript = _projects![projectKey]["projDescript"];
                return ListTile(
                  title: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        projDescript,
                        textScaler: const TextScaler.linear(1.2),
                      ),
                      Text('Project ID: $displayName'),
                    ],
                  ),
                  onTap: () =>
                      _onProjectSelected(projectKey, project, projDescript),
                );
              },
            ),
    );
  }

  void _onProjectSelected(
      String projectId, Map<String, dynamic> project, String projectName) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => TestListScreen(
          projectId: projectId,
          testLists: project,
          projectName: projectName,
          mqttService: widget.mqttService,
        ),
      ),
    );
  }
}

class TestListScreen extends StatelessWidget {
  final String projectId;
  final String projectName;
  final Map<String, dynamic> testLists;
  final MqttService mqttService;

  const TestListScreen(
      {super.key,
      required this.projectId,
      required this.testLists,
      required this.projectName,
      required this.mqttService});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Testlist Entries for $projectName')),
      body: ListView.builder(
        itemCount: testLists.length,
        itemBuilder: (context, index) {
          final testlistKey = testLists.keys.elementAt(index);
          final testlist = testLists[testlistKey];

          // Make sure testlist has a valid structure
          if (testlist is Map<String, dynamic>) {
            return ListTile(
              title: Row(
                mainAxisAlignment:
                    MainAxisAlignment.spaceBetween, // Distribute space evenly
                children: [
                  Text(
                    testlist['description'],
                    textScaler: const TextScaler.linear(1.2),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      _createReplicate(testlist['labNotebookBaseRef']);
                      print(
                          'WJ - Request to add testrun for ${testlist['labNotebookBaseRef']}!');
                    },
                    child: const Text('Add testrun'),
                  ),
                ],
              ),
              subtitle: Text(
                'Lab Notebook base ref: ${testlist['labNotebookBaseRef']}',
              ),
              onTap: () => _onTestlistSelected(context, testlistKey, testlist,
                  testlist['labNotebookBaseRef']),
            );
          } else {
            return const SizedBox.shrink(); // Handle unexpected structure
          }
        },
      ),
    );
  }

  void _createReplicate(labNotebookBaseRef) {
    //createReplicate(self,labNotebookBaseRef,testScript="",flowScript={},notes="")
    final request = {
      "instructions": {
        "params": {
          "labNotebookBaseRef": labNotebookBaseRef,
          "testScript": mqttService.currTestScriptBlocks,
          "flowScript": mqttService.currDashboardJson,
          "notes": "",
        },
        "function": "createReplicate"
      }
    };
    mqttService.publish('ui/dbCmnd/in', jsonEncode(request));
  }

  void _onTestlistSelected(BuildContext context, String testlistKey,
      Map<String, dynamic> testlist, String labNotebookBaseRef) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => TestRunsScreen(
          testlistKey: testlistKey,
          testruns: testlist['testruns'],
          labNotebookBaseRef: labNotebookBaseRef,
          mqttService: mqttService,
        ),
      ),
    );
  }
}

class TestRunsScreen extends StatelessWidget {
  final String testlistKey;
  final List<dynamic> testruns;
  final String labNotebookBaseRef;
  final MqttService mqttService;

  const TestRunsScreen(
      {super.key,
      required this.testlistKey,
      required this.testruns,
      required this.labNotebookBaseRef,
      required this.mqttService});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          title: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(child: Text('Experiments for $labNotebookBaseRef')),
          Expanded(
            child: ElevatedButton(
              onPressed: () {
                _createReplicate(labNotebookBaseRef);
              },
              child: const Text('Add experiment'),
            ),
          ),
        ],
      )),
      body: ListView.builder(
        itemCount: testruns.length,
        itemBuilder: (context, index) {
          final testrun = testruns[index];
          return ListTile(
            title: Text(
              '${testrun[2]}_${testrun[3]}',
              textScaler: const TextScaler.linear(1.2),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Run number: ${testrun[3] + 1}'),
                Text('Run date: ${testrun[4]}'),
              ],
            ),
            onTap: () => _onTestrunSelected(context, testrun),
          );
        },
      ),
    );
  }

  void _createReplicate(labNotebookBaseRef) {
    //createReplicate(self,labNotebookBaseRef,testScript="",flowScript={},notes="")
    final request = {
      "instructions": {
        "params": {
          "labNotebookBaseRef": labNotebookBaseRef,
          "testScript": mqttService.currTestScriptBlocks,
          "flowScript": mqttService.currDashboardJson,
          "notes": "",
        },
        "function": "createReplicate"
      }
    };
    mqttService.publish('ui/dbCmnd/in', jsonEncode(request));
  }

  void _onTestrunSelected(BuildContext context, List<dynamic> testrun) {
    //Update script builder
    /*
      Json string for blocks available in 'testrun[8]',
      This class and ScriptGeneratorWidget share an instance of mqttService,
      which can be used to shuttle values (replace at some point)
    */
    //Update dashboard
    mqttService.currDashboardJson = testrun[9];
    ScriptGeneratorWidgetState? thisState =
        mqttService.scriptGeneratorWidgetKey.currentState;
    if (thisState != null) {
      thisState.updateScriptBlocks(testrun[8]);
    }
    //Access ScriptGeneratorWidgetState via GlobalKey
    mqttService.flowSketcherKey.currentState?.updateConnections();

    //Update backend current testlistid and testrunId
    final Map<String, Map<String, dynamic>> request = {
      "instructions": {
        "params": {
          "labNotebookBaseRef": labNotebookBaseRef,
          "testrunId": testrun[0],
          "testlistId": testrun[1]
        },
        "function": "updateTestrunDetails"
      }
    };
    mqttService.publish('ui/dbCmnd/in', jsonEncode(request));

    print('WJ - Selected Testrun: ${testrun[0]}');
  }
}

class ProjectBrowser extends StatelessWidget {
  final MqttService mqttService;

  const ProjectBrowser({super.key, required this.mqttService});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: ExpWidget(mqttService: mqttService),
    );
  }
}

//A little example
void main() async {
  MqttService mqttService = MqttService(server: "ws://localhost/");
  await mqttService.connect();
  mqttService.authenticator.user.orgId = "50403";
  runApp(ProjectBrowser(mqttService: mqttService));
}

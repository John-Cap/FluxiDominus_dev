import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';

import 'package:flutter_flow_chart/ui/list_generators/lists.dart';

class OptimizationTab extends StatefulWidget {
  final MqttService mqttService;

  const OptimizationTab({super.key, required this.mqttService});

  @override
  _OptimizationTabState createState() => _OptimizationTabState();
}

class _OptimizationTabState extends State<OptimizationTab>
    with AutomaticKeepAliveClientMixin {
  final List<String> selectedParameters = [];
  String? selectedOptimizer;
  String? selectedObjectiveFunction;

  bool isRunning = false;
  Map<String, dynamic> optimizationProgress = {};
  Map<String, List<double>> tempBounds = {
    "Temperature": [1, 100],
    "Flowrate": [0.15, 3],
    "Residence Time": [5, 30]
  };

  @override
  bool get wantKeepAlive => true; // Enable automatic keep-alive

  void startOptimization() {
    Map<String, List<double>> paramWithBounds = {};
    for (var value in selectedParameters) {
      paramWithBounds[value] = tempBounds[value]!;
    }
    final optimizationDetails = {
      'optimizer': selectedOptimizer,
      'objectiveFunction': selectedObjectiveFunction,
      'selectedParameters': paramWithBounds,
    };

    widget.mqttService.optimizationDetails = optimizationDetails;
    widget.mqttService.runTest = true;

    //Signal backend
    widget.mqttService.publish(
        "ui/opt/in", jsonEncode({"optInstructUI": optimizationDetails}));

    setState(() {
      isRunning = true;
    });

    listenForProgressUpdates();
  }

  void listenForProgressUpdates() {
    widget.mqttService.goOptimization.addListener(() {
      if (widget.mqttService.goOptimization.value) {
        setState(() {
          isRunning = true;
        });
      } else {
        if (isRunning) {
          print("WJ - Optimization stopping.");
          setState(() {
            isRunning = false;
          });
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Row(
      children: [
        // Left Panel: Optimization Settings
        Expanded(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Optimization Settings',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),

                  // Optimizer Selector
                  const Text('Select Optimizer:',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  Expanded(
                    child: ListBox(
                      listElements:
                          widget.mqttService.optimizationOptions.map((option) {
                        return GestureDetector(
                          onTap: () {
                            setState(() {
                              selectedOptimizer = option;
                            });
                          },
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4.0),
                            child: Text(option, style: TextStyle(fontSize: 16)),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text('Selected Optimizer: ${selectedOptimizer ?? 'None'}'),

                  const SizedBox(height: 16),

                  // Objective Function Selector
                  const Text('Select Objective Function:',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  Expanded(
                    child: ListBox(
                      listElements:
                          widget.mqttService.objectiveFunctions.map((option) {
                        return GestureDetector(
                          onTap: () {
                            setState(() {
                              selectedObjectiveFunction = option;
                            });
                          },
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4.0),
                            child: Text(option, style: TextStyle(fontSize: 16)),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                      'Selected Objective Function: ${selectedObjectiveFunction ?? 'None'}'),

                  const SizedBox(height: 16),

                  // Dynamic List of Parameters
                  Wrap(
                    spacing: 8.0,
                    children: [
                      ...['Temperature', 'Flowrate', 'Residence Time']
                          .map((param) => ChoiceChip(
                                label: Text(param),
                                selected: selectedParameters.contains(param),
                                onSelected: (selected) {
                                  setState(() {
                                    if (selected) {
                                      selectedParameters.add(param);
                                    } else {
                                      selectedParameters.remove(param);
                                    }
                                  });
                                },
                              )),
                    ],
                  ),

                  const Spacer(),

                  // Start Button
                  ElevatedButton(
                    onPressed: isRunning ||
                            selectedOptimizer == null ||
                            selectedObjectiveFunction == null
                        ? null
                        : startOptimization,
                    child: const Text('Start'),
                  ),
                ],
              ),
            ),
          ),
        ),

        // Right Panel: Optimization Progress
        Expanded(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Optimization Progress',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  Text(
                      'Selected Optimizer: ${widget.mqttService.optimizationDetails['optimizer'] ?? 'N/A'}'),
                  Text(
                      'Objective Evaluator: ${widget.mqttService.optimizationDetails['objectiveFunction'] ?? 'N/A'}'),
                  ValueListenableBuilder(
                    valueListenable: widget.mqttService.recommendedParams,
                    builder: (_, value, __) => Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('___________________'),
                        Text('Current Parametres:'),
                        Text(
                            '     Temperature: ${((value as Map<String, double>)["Temperature"])?.toStringAsFixed(1) ?? "N/A"} deg'),
                        Text(
                            '     Flowrate: ${((value)["Flowrate"])?.toStringAsFixed(3) ?? "N/A"} mL/min'),
                      ],
                    ),
                  ),
                  ValueListenableBuilder(
                    valueListenable: widget.mqttService.lastYield,
                    builder: (_, value, __) => Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('________________'),
                        Text('Best Parametres:'),
                        Text(
                            '     Temperature: ${widget.mqttService.bestParametres["Temperature"]?.toStringAsFixed(1) ?? "N/A"} deg'),
                        Text(
                            '     Flowrate: ${widget.mqttService.bestParametres["Flowrate"]?.toStringAsFixed(3) ?? "N/A"} mL/min'),
                        Text(
                            '     Yield: ${((value as double) * 100).toStringAsFixed(1)}%'),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text('History:',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  Expanded(
                    child: ValueListenableBuilder(
                      valueListenable: widget.mqttService.resultHistory,
                      builder: (_, List<dynamic> resultList, __) {
                        List<dynamic> safeResultList = resultList;
                        return ListView.builder(
                          itemCount: safeResultList.length,
                          itemBuilder: (context, index) {
                            final entry =
                                safeResultList[index]['recommendation'] ?? {};
                            return ListTile(
                              title: Text(
                                  '${index + 1}. T: ${(entry['Temperature']).toStringAsFixed(1) ?? 'N/A'}°C, F: ${(entry['Flowrate'].toStringAsFixed(2)) ?? 'N/A'} mL/min'),
                              subtitle: Text(
                                  ' Yield: ${(entry['yield'] * 100).toStringAsFixed(0) ?? 'N/A'}%'),
                            );
                          },
                        );
                      },
                    ),
                  ),
                  const Spacer(),
                  if (!isRunning)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                            'Final Yield: ${(widget.mqttService.lastYield.value * 100).toStringAsFixed(1)}%'),
                      ],
                    ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// void main() {
//   runApp(MyApp());
// }

// class MyApp extends StatelessWidget {
//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       title: 'Optimization Tab Test',
//       home: Scaffold(
//         appBar: AppBar(title: Text('Optimization Tab Test')),
//         body: OptimizationTab(mqttService: MqttService()),
//       ),
//     );
//   }
// }

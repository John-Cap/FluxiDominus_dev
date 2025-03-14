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

  @override
  bool get wantKeepAlive => true; // Enable automatic keep-alive

  void startOptimization() {
    final optimizationDetails = {
      'optimizer': selectedOptimizer,
      'objectiveFunction': selectedObjectiveFunction,
      'selectedParameters': selectedParameters,
    };

    widget.mqttService.optimizationDetails = optimizationDetails;
    widget.mqttService.runTest = true;

    setState(() {
      isRunning = true;
    });

    listenForProgressUpdates();
  }

  void listenForProgressUpdates() {
    widget.mqttService.optimizationProgressStream.listen((progress) {
      if (mounted) {
        setState(() {
          optimizationProgress = progress;
        });
      }
    }, onDone: () {
      setState(() {
        isRunning = false;
      });
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

                  // Display Progress Updates
                  Text(
                      'Selected Optimizer: ${optimizationProgress['optimizer'] ?? 'N/A'}'),
                  Text(
                      'Objective Evaluator: ${optimizationProgress['objectiveFunction'] ?? 'N/A'}'),
                  Text(
                      'Current Recommended Params: ${optimizationProgress['recommendedParams'] ?? 'N/A'}'),
                  Text(
                      'Best Yield: ${optimizationProgress['bestYield'] ?? 'N/A'}'),

                  const Spacer(),

                  // Timer & Final Details
                  if (!isRunning)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                            'Final Yield: ${optimizationProgress['finalYield'] ?? 'N/A'}'),
                        Text(
                            'Elapsed Time: ${optimizationProgress['elapsedTime'] ?? 'N/A'}'),
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

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
//import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/gauges/gauge_widgets.dart';

class GaugeBlock extends StatelessWidget {
  final List<GaugeWidget> gauges;
  final MqttService mqttService;

  const GaugeBlock(
      {super.key, required this.gauges, required this.mqttService});

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
      ),
      itemCount: gauges.length,
      itemBuilder: (context, index) {
        return GestureDetector(
          onTap: () {
            print('WJ - Tapped on gauge: ${gauges[index].name}');
          },
          child: Card(
            margin: const EdgeInsets.all(8.0),
            child: Center(
              child: gauges[index],
            ),
          ),
        );
      },
    );
  }
}

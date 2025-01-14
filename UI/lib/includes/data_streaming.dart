import 'dart:async';

import 'package:flutter_flow_chart/utils/timing.dart';

class TimedDataStream {
  List<List<double>> timeSeriesData = [];
  EpochDelta epochDelta = EpochDelta();
  final StreamController<List<double>> _controller =
      StreamController<List<double>>();
  double previousTime = 0; // Track the previous x value
  Completer<void>? _dataAvailableCompleter;
  bool started = false;

  Stream<List<double>> get stream => _controller.stream; //.asBroadcastStream();

  void appendTimeSeriesData(List<List<double>> data) {
    if (!started) {
      started = true;
      //Reset timer/clear previous
      epochDelta.reset();
      timeSeriesData.clear();
    }
    timeSeriesData.addAll(data);

    // If waiting for data, complete the Completer to resume processing
    _dataAvailableCompleter?.complete();
    _dataAvailableCompleter = null;
  }

  void start() async {
    while (true) {
      if (timeSeriesData.isEmpty) {
        // If no data is available, wait for more data to be appended
        _dataAvailableCompleter = Completer<void>();
        await _dataAvailableCompleter!.future;
      }

      // Process timeSeriesData, ensuring to wait until the time is correct
      while (timeSeriesData.isNotEmpty) {
        var dataPoint = timeSeriesData.removeAt(0);
        double time = dataPoint[0]; // x value (time since start in seconds)

        // Discard any points where the time is less than the previous time
        if (time < previousTime) {
          print('WJ - Data point too late, discarding: $dataPoint');
          continue;
        }

        // Wait until the current epoch time matches or exceeds the dataPoint's time
        while (epochDelta.secSinceEpoch() < time) {
          await Future.delayed(const Duration(
              milliseconds: 100)); // Small delay to avoid busy waiting
        }

        // Ensure we are at the right time and then emit the data point
        _controller.add(dataPoint);
        previousTime = time;
        //print('WJ - Plot point yielded! -> $dataPoint');
      }
    }
  }

  void stop() {
    started = false;
    previousTime = 0;
    _controller.close();
    _dataAvailableCompleter
        ?.complete(); // Ensure any awaiting Completer is completed
  }
}
/*
///////////////////////////////////////////////
//Main example
void main() async {
  MqttService mqttService = MqttService(server: 'ws://localhost');
  mqttService.connect();

/////////////////////////////////////////////////////////////////
// Create a GraphWidgets instance
  GraphWidgets graphWidgets = GraphWidgets(mqttService);
// Add a time series widget
  var diz = graphWidgets.addTimeSeriesWidgetVirtual(
    title: 'A fabulous example of streaming',
    xAxisTitle: 'Time',
    yAxisTitle: 'Value',
    mqttService: mqttService,
    maxDataPoints: 10,
    id: "120A3",
  );
  MyExampleGraph example = MyExampleGraph(
    title: 'None',
    example: diz,
  );
  print('WJ - ${diz.id}');
  runApp(MyApp(
    example: example,
  ));
  /*
  Timer(Duration(seconds: 60), () {
    var newThings = [
      [56.4, -3.0],
      [58.4, -2.0],
      [59.4, -1.0],
      [61.67, 0.0],
      [63.56, 1.4],
    ];
    diz.timedDataStream.appendTimeSeriesData(newThings);
  });
  */
}

class MyExampleGraph extends StatelessWidget {
  final String title;
  final Widget example;

  const MyExampleGraph({super.key, required this.title, required this.example});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: example,
    );
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key, required this.example});
  final MyExampleGraph example;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dynamic TabBar Demo',
      theme: ThemeData(
        useMaterial3: true,
      ),
      home: example,
    );
  }
}
*/
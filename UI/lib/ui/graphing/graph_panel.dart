import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/data_streaming.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:syncfusion_flutter_charts/charts.dart';
import 'package:uuid/uuid.dart';

class GraphWidgets {
  // List to store references to different graph widgets
  final List<dynamic> _widgets = [];
  Map<String, List<PlotData>> dataSources = {};
  final MqttService mqttService;

  // Store the parameters used for widget creation (optional for rebuilding widgets)
  List<Map<String, dynamic>> widgetCreationParams = [];

  GraphWidgets(this.mqttService);

  // Method to add a TimeSeriesWidget
  _TimeSeriesWidget addTimeSeriesWidget({
    required String title,
    required String xAxisTitle,
    required String yAxisTitle,
    required MqttService mqttService,
    required int maxDataPoints,
    required String teleKey,
    String id = "",
  }) {
    if (id == "") {
      id = const Uuid().v4();
    }
    String idConc = "${id}_$teleKey";

    // Ensure the MQTT notifier and data collection are set up
    if (!mqttService.teleDataNotifiers.containsKey(idConc)) {
      mqttService.teleDataNotifiers[idConc] = ValueNotifier([]);
    }
    if (!mqttService.teleToCollect.containsKey(id)) {
      mqttService.teleToCollect[id] = [];
      mqttService.teleToCollect[id]!.add(teleKey);
      print('Added tele source $idConc to new dataNotifier $id');
    } else {
      if (!(mqttService.teleToCollect[id]!.contains(teleKey))) {
        mqttService.teleToCollect[id]!.add(teleKey);
        print('Added tele source $idConc to existing dataNotifier $id');
      }
    }

    dataSources[id] = [];

    _TimeSeriesWidget timeSeriesWidget = _TimeSeriesWidget(
      title: title,
      xAxisTitle: xAxisTitle,
      yAxisTitle: yAxisTitle,
      mqttService: mqttService,
      maxDataPoints: maxDataPoints,
      id: idConc,
    );

    _widgets.add(timeSeriesWidget);

    // Save the creation parameters for rebuilding
    saveWidgetCreationParams(
      widgetType: 'TimeSeries',
      title: title,
      xAxisTitle: xAxisTitle,
      yAxisTitle: yAxisTitle,
      teleKey: teleKey,
      maxDataPoints: maxDataPoints,
    );

    return timeSeriesWidget;
  }

  // Method to add a virtual TimeSeriesWidget
  _TimeSeriesWidgetVirtual addTimeSeriesWidgetVirtual({
    required String title,
    required String xAxisTitle,
    required String yAxisTitle,
    required MqttService mqttService,
    required int maxDataPoints,
    String id = "",
  }) {
    if (id == "") {
      id = const Uuid().v4();
    }
    _TimeSeriesWidgetVirtual timeSeriesWidget = _TimeSeriesWidgetVirtual(
      title: title,
      xAxisTitle: xAxisTitle,
      yAxisTitle: yAxisTitle,
      mqttService: mqttService,
      maxDataPoints: maxDataPoints,
      id: id,
    );

    if (!mqttService.dbStreamDataNotifiers.containsKey(id)) {
      mqttService.dbStreamDataNotifiers[id] = ValueNotifier([]);
    }

    dataSources[id] = [];

    _widgets.add(timeSeriesWidget);

    // Save the creation parameters for rebuilding (if needed)
    saveWidgetCreationParams(
      widgetType: 'TimeSeriesVirtual',
      title: title,
      xAxisTitle: xAxisTitle,
      yAxisTitle: yAxisTitle,
      teleKey: '',
      maxDataPoints: maxDataPoints,
    );

    return timeSeriesWidget;
  }

  // Method to add a combined streamed and realtime graph
  _UnifiedTimeSeriesWidget addUnifiedTimeSeriesWidget({
    required String title,
    required String xAxisTitle,
    required String yAxisTitle,
    required MqttService mqttService,
    required int maxDataPoints,
    required String idStreaming,
    String idTele = "",
    required String teleKey,
  }) {
    if (idTele == "") {
      idTele = const Uuid().v4();
    }
    String idConc = "${idTele}_$teleKey";

    // Ensure the MQTT notifier and data collection are set up
    if (!mqttService.teleDataNotifiers.containsKey(idConc)) {
      mqttService.teleDataNotifiers[idConc] = ValueNotifier([]);
    }
    if (!mqttService.teleToCollect.containsKey(idTele)) {
      mqttService.teleToCollect[idTele] = [];
      mqttService.teleToCollect[idTele]!.add(teleKey);
      print('Added tele source $idConc to new dataNotifier $idTele');
    } else {
      if (!(mqttService.teleToCollect[idTele]!.contains(teleKey))) {
        mqttService.teleToCollect[idTele]!.add(teleKey);
        print('Added tele source $idConc to existing dataNotifier $idTele');
      }
    }

    if (!mqttService.dbStreamDataNotifiers.containsKey(idStreaming)) {
      mqttService.dbStreamDataNotifiers[idStreaming] = ValueNotifier([]);
    }

    _UnifiedTimeSeriesWidget timeSeriesWidget = _UnifiedTimeSeriesWidget(
      title: title,
      xAxisTitle: xAxisTitle,
      yAxisTitle: yAxisTitle,
      mqttService: mqttService,
      maxDataPoints: maxDataPoints,
      idTele: idConc,
      idStreaming: idStreaming,
    );

    dataSources[idTele] = [];

    _widgets.add(timeSeriesWidget);

    return timeSeriesWidget;
  }

  // Method to add an IRWidget
  _IRWidget addIRWidget({
    required String title,
    required String xAxisTitle,
    required String yAxisTitle,
    required MqttService mqttService,
    required int maxDataPoints,
    required List<PlotData> data,
  }) {
    String id = const Uuid().v4();

    _IRWidget iRWidget = _IRWidget(
      title: title,
      xAxisTitle: xAxisTitle,
      yAxisTitle: yAxisTitle,
      mqttService: mqttService,
      maxDataPoints: maxDataPoints,
      id: id,
      data: data,
    );

    dataSources[id] = [];

    _widgets.add(iRWidget);

    // Save the creation parameters for rebuilding (if needed)
    saveWidgetCreationParams(
      widgetType: 'IRWidget',
      title: title,
      xAxisTitle: xAxisTitle,
      yAxisTitle: yAxisTitle,
      teleKey: '',
      maxDataPoints: maxDataPoints,
    );

    return iRWidget;
  }

  // Method to retrieve all widgets
  List<dynamic> get widgets => _widgets;

  // Method to clear all stored widgets
  void clearWidgets() {
    _widgets.clear();
  }

  // Method to save widget creation parameters for later rebuild
  void saveWidgetCreationParams({
    required String widgetType,
    required String title,
    required String xAxisTitle,
    required String yAxisTitle,
    required String teleKey,
    required int maxDataPoints,
  }) {
    widgetCreationParams.add({
      'widgetType': widgetType,
      'title': title,
      'xAxisTitle': xAxisTitle,
      'yAxisTitle': yAxisTitle,
      'teleKey': teleKey,
      'maxDataPoints': maxDataPoints,
    });
  }

  // Method to rebuild all widgets from stored parameters
  void recreateWidgetsFromParams() {
    clearWidgets(); // Clear existing widgets first
    for (var params in widgetCreationParams) {
      if (params['widgetType'] == 'TimeSeries') {
        addTimeSeriesWidget(
          title: params['title'],
          xAxisTitle: params['xAxisTitle'],
          yAxisTitle: params['yAxisTitle'],
          mqttService: mqttService,
          maxDataPoints: params['maxDataPoints'],
          teleKey: params['teleKey'],
        );
      } else if (params['widgetType'] == 'TimeSeriesVirtual') {
        addTimeSeriesWidgetVirtual(
          title: params['title'],
          xAxisTitle: params['xAxisTitle'],
          yAxisTitle: params['yAxisTitle'],
          mqttService: mqttService,
          maxDataPoints: params['maxDataPoints'],
        );
      } else if (params['widgetType'] == 'IRWidget') {
        addIRWidget(
          title: params['title'],
          xAxisTitle: params['xAxisTitle'],
          yAxisTitle: params['yAxisTitle'],
          mqttService: mqttService,
          maxDataPoints: params['maxDataPoints'],
          data: dataSources[params['title']]!, // Ensure data is available
        );
      }
    }
  }

  // Method to trigger a rebuild of all widgets from scratch
  void rebuildWidgets() {
    // Clear the current widgets and data sources
    _widgets.clear();
    dataSources.clear();

    // Clear the MQTT notifiers and data collections
    mqttService.teleDataNotifiers.clear();
    mqttService.teleToCollect.clear();
    mqttService.dbStreamDataNotifiers.clear();

    // Rebuild all widgets from the stored creation parameters
    recreateWidgetsFromParams();
  }
}

//Definition of graph widget types
class _TimeSeriesWidget extends StatefulWidget {
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final MqttService mqttService;
  final int maxDataPoints;
  final String id;

  const _TimeSeriesWidget({
    required this.title,
    required this.xAxisTitle,
    required this.yAxisTitle,
    required this.mqttService,
    required this.maxDataPoints, // Maximum number of data points to display
    required this.id,
  });

  @override
  _TimeSeriesWidgetState createState() => _TimeSeriesWidgetState();
}

class _TimeSeriesWidgetState extends State<_TimeSeriesWidget> {
  List<PlotData> data = [];

  @override
  void initState() {
    super.initState();
    widget.mqttService.teleDataNotifiers[widget.id]!.addListener(_updateData);
    widget.mqttService.testRunning.addListener(_resetGraph);
  }

  @override
  void dispose() {
    widget.mqttService.teleDataNotifiers[widget.id]!
        .removeListener(_updateData);
    widget.mqttService.testRunning.removeListener(_resetGraph);
    super.dispose();
  }

  void _updateData() {
    if (widget.mqttService.teleDataNotifiers[widget.id]!.value.isNotEmpty) {
      data.addAll(widget.mqttService.teleDataNotifiers[widget.id]!.value);
      if (data.length > widget.maxDataPoints) {
        data = data.sublist(data.length - widget.maxDataPoints);
      }
      widget.mqttService.teleDataNotifiers[widget.id]!.value = [];

      // Check the maximum x value in the data
      double maxXValue =
          data.map((point) => point.x).reduce((a, b) => a > b ? a : b);

      // Update the visible axis limits if needed
      if (maxXValue > widget.mqttService.timeBracketMax) {
        // Increase visibleMaximum to keep it fixed to the upper limit
        widget.mqttService.timeBracketMin = maxXValue - 120; // Adjust as needed
        widget.mqttService.timeBracketMax = maxXValue;
      }
      //print("WJ - Visible chart ranges: ${[timeBracketMin, timeBracketMax]}");
    }
    setState(() {});
  }

  void _resetGraph() {
    setState(() {
      if (widget.mqttService.testRunning.value) {
        widget.mqttService.testRunning.removeListener(_resetGraph);
        data = [];
        //widget.mqttService.teleDataNotifiers[id]!.value = [];
        widget.mqttService.timeBracketMax = 120;
        widget.mqttService.timeBracketMin = 0;
        print('WJ - Resetting graph ${widget.id}');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return SfCartesianChart(
      primaryXAxis: NumericAxis(
        initialVisibleMinimum: widget.mqttService.timeBracketMin,
        initialVisibleMaximum: widget.mqttService.timeBracketMax,
        minimum: widget.mqttService.timeBracketMin,
        maximum: widget.mqttService.timeBracketMax,
        rangePadding: ChartRangePadding.additional,
        anchorRangeToVisiblePoints: false,
        interval: 10,
        title: AxisTitle(text: widget.xAxisTitle),
      ),
      primaryYAxis: NumericAxis(
        interval: 1,
        title: AxisTitle(text: widget.yAxisTitle),
      ),
      title: ChartTitle(text: widget.title),
      tooltipBehavior: TooltipBehavior(enable: true),
      series: <CartesianSeries<PlotData, double>>[
        LineSeries<PlotData, double>(
          dataSource: data,
          animationDuration: 0,
          xValueMapper: (PlotData data, _) => data.x,
          yValueMapper: (PlotData data, _) => data.y,
          dataLabelSettings: const DataLabelSettings(isVisible: true),
        ),
      ],
    );
  }
}

///////////////////////////////////////////////////////
//Virtual, db-fed graphs
class _TimeSeriesWidgetVirtual extends StatefulWidget {
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final MqttService mqttService;
  final int maxDataPoints;
  final String id;
  final TimedDataStream timedDataStream = TimedDataStream();

  _TimeSeriesWidgetVirtual({
    required this.title,
    required this.xAxisTitle,
    required this.yAxisTitle,
    required this.mqttService,
    required this.maxDataPoints,
    required this.id,
  });

  @override
  _TimeSeriesWidgetVirtualState createState() =>
      _TimeSeriesWidgetVirtualState();
}

class _TimeSeriesWidgetVirtualState extends State<_TimeSeriesWidgetVirtual>
    with AutomaticKeepAliveClientMixin<_TimeSeriesWidgetVirtual> {
  List<PlotData> data = [];
  late StreamSubscription<List<double>> streamSubscription;
  bool isListening =
      false; //Listening flag to block attempts to add multiple listeners

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    print('WJ - Virtual ts graph initialized');
    _startListening();
    widget.mqttService.dbStreamDataNotifiers[widget.id]!.addListener(_addData);
    widget.mqttService.testRunning.addListener(_resetGraph);
  }

  void _startListening() {
    if (!isListening) {
      isListening = true;
      // Start the time series drip
      streamSubscription = widget.timedDataStream.stream.listen((dataPoint) {
        data.add(PlotData(dataPoint[0], dataPoint[1]));
        _updateData();
      });
      widget.timedDataStream.start();
    }
  }

  @override
  void dispose() {
    widget.mqttService.dbStreamDataNotifiers[widget.id]!
        .removeListener(_addData);
    widget.mqttService.testRunning.removeListener(_resetGraph);
    streamSubscription.cancel();
    widget.timedDataStream.stop(); //TODO - goeie idee?
    widget.timedDataStream.started = false;
    super.dispose();
  }

  void _addData() {
    if (widget.mqttService.dbStreamDataNotifiers[widget.id]!.value.isNotEmpty) {
      if (!widget.mqttService.runTest) {
        widget.timedDataStream.started = false;
      }
      widget.timedDataStream.appendTimeSeriesData(
          widget.mqttService.dbStreamDataNotifiers[widget.id]!.value);
      widget.mqttService.dbStreamDataNotifiers[widget.id]!.value.clear();
    }
  }

  void _updateData() {
    if (data.length > widget.maxDataPoints) {
      //TODO - chop liewers af volgengs min/max x values
      data = data.sublist(data.length - widget.maxDataPoints);
    }
    double maxXValue =
        data.map((point) => point.x).reduce((a, b) => a > b ? a : b);

    // Update the visible axis limits if needed
    if (maxXValue > widget.mqttService.timeBracketMax) {
      // Increase visibleMaximum to keep it fixed to the upper limit
      widget.mqttService.timeBracketMin = maxXValue - 120; // Adjust as needed
      widget.mqttService.timeBracketMax = maxXValue;
    }
    setState(() {}); // Ensure UI is updated
  }

  @override
  Widget build(BuildContext context) {
    super.build(context); // Required for AutomaticKeepAliveClientMixin

    return SfCartesianChart(
      primaryXAxis: NumericAxis(
        initialVisibleMinimum: widget.mqttService.timeBracketMin,
        initialVisibleMaximum: widget.mqttService.timeBracketMax,
        minimum: widget.mqttService.timeBracketMin,
        maximum: widget.mqttService.timeBracketMax,
        rangePadding: ChartRangePadding.additional,
        anchorRangeToVisiblePoints: false,
        interval: 10,
        title: AxisTitle(text: widget.xAxisTitle),
      ),
      primaryYAxis: NumericAxis(
        interval: 1,
        title: AxisTitle(text: widget.yAxisTitle),
      ),
      title: ChartTitle(text: widget.title),
      tooltipBehavior: TooltipBehavior(enable: true),
      series: <CartesianSeries<PlotData, double>>[
        LineSeries<PlotData, double>(
          dataSource: data,
          animationDuration: 0,
          xValueMapper: (PlotData data, _) => data.x,
          yValueMapper: (PlotData data, _) => data.y,
          dataLabelSettings: const DataLabelSettings(isVisible: true),
        ),
      ],
    );
  }

  void _resetGraph() {
    data.clear();
  }
}

//Definition of graph widget types
class _UnifiedTimeSeriesWidget extends StatefulWidget {
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final MqttService mqttService;
  final int maxDataPoints;
  final String idTele;
  final String idStreaming;
  final TimedDataStream timedDataStream = TimedDataStream();

  _UnifiedTimeSeriesWidget({
    required this.title,
    required this.xAxisTitle,
    required this.yAxisTitle,
    required this.mqttService,
    required this.maxDataPoints, // Maximum number of data points to display
    required this.idTele,
    required this.idStreaming,
  });

  @override
  _UnifiedTimeSeriesWidgetState createState() =>
      _UnifiedTimeSeriesWidgetState();
}

class _UnifiedTimeSeriesWidgetState extends State<_UnifiedTimeSeriesWidget>
    with AutomaticKeepAliveClientMixin<_UnifiedTimeSeriesWidget> {
  List<PlotData> dataTele = [];
  List<PlotData> dataStreamed = [];
  late StreamSubscription<List<double>> streamSubscription;
  bool isListening =
      false; //Listening flag to block attempts to add multiple listeners

  //Keep widget alive
  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    //Virtual
    print('WJ - Virtual ts graph initialized');
    _startListening();
    widget.mqttService.dbStreamDataNotifiers[widget.idStreaming]!
        .addListener(_addData);
    widget.mqttService.teleDataNotifiers[widget.idTele]!
        .addListener(_updateDataTele);
    widget.mqttService.testRunning.addListener(_resetGraph);
  }

  @override
  void dispose() {
    widget.mqttService.teleDataNotifiers[widget.idTele]!
        .removeListener(_updateDataTele);
    widget.mqttService.testRunning.removeListener(_resetGraph);
    widget.mqttService.dbStreamDataNotifiers[widget.idStreaming]!
        .removeListener(_addData);
    streamSubscription.cancel();
    widget.timedDataStream.stop(); //TODO - goeie idee?
    widget.timedDataStream.started = false;
    super.dispose();
  }

  void _startListening() {
    if (!isListening) {
      isListening = true;
      // Start the time series drip
      streamSubscription = widget.timedDataStream.stream.listen((dataPoint) {
        dataStreamed.add(PlotData(dataPoint[0], dataPoint[1]));
        _updateDataStreamed();
      });
      widget.timedDataStream.start();
    }
  }

  void _addData() {
    if (widget.mqttService.dbStreamDataNotifiers[widget.idStreaming]!.value
        .isNotEmpty) {
      if (!widget.mqttService.runTest) {
        widget.timedDataStream.started = false;
      }
      widget.timedDataStream.appendTimeSeriesData(
          widget.mqttService.dbStreamDataNotifiers[widget.idStreaming]!.value);
      widget.mqttService.dbStreamDataNotifiers[widget.idStreaming]!.value
          .clear();
    }
  }

  void _updateDataTele() {
    //Real time data
    if (widget.mqttService.teleDataNotifiers[widget.idTele]!.value.isNotEmpty) {
      dataTele
          .addAll(widget.mqttService.teleDataNotifiers[widget.idTele]!.value);
      if (dataTele.length > widget.maxDataPoints) {
        dataTele = dataTele.sublist(dataTele.length - widget.maxDataPoints);
      }
      widget.mqttService.teleDataNotifiers[widget.idTele]!.value = [];

      // Check the maximum x value in the data
      double maxXValue =
          dataTele.map((point) => point.x).reduce((a, b) => a > b ? a : b);

      // Update the visible axis limits if needed
      if (maxXValue > widget.mqttService.timeBracketMax) {
        // Increase visibleMaximum to keep it fixed to the upper limit
        widget.mqttService.timeBracketMin = maxXValue - 120; // Adjust as needed
        widget.mqttService.timeBracketMax = maxXValue;
      }
      //print("WJ - Visible chart ranges: ${[timeBracketMin, timeBracketMax]}");
    }
    setState(() {});
  }

  void _updateDataStreamed() {
    if (dataTele.length > widget.maxDataPoints) {
      //TODO - chop liewers af volgengs min/max x values
      dataTele = dataTele.sublist(dataTele.length - widget.maxDataPoints);
    }
    double maxXValue =
        dataTele.map((point) => point.x).reduce((a, b) => a > b ? a : b);

    // Update the visible axis limits if needed
    if (maxXValue > widget.mqttService.timeBracketMax) {
      // Increase visibleMaximum to keep it fixed to the upper limit
      widget.mqttService.timeBracketMin = maxXValue - 120; // Adjust as needed
      widget.mqttService.timeBracketMax = maxXValue;
    }
    setState(() {}); // Ensure UI is updated
  }

  void _resetGraph() {
    setState(() {
      if (widget.mqttService.testRunning.value) {
        widget.mqttService.testRunning.removeListener(_resetGraph);
        dataTele = [];
        dataStreamed = [];
        //widget.mqttService.teleDataNotifiers[id]!.value = [];
        widget.mqttService.timeBracketMax = 120;
        widget.mqttService.timeBracketMin = 0;
        print('WJ - Resetting graph ${widget.idTele}');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return SfCartesianChart(
      primaryXAxis: NumericAxis(
        initialVisibleMinimum: widget.mqttService.timeBracketMin,
        initialVisibleMaximum: widget.mqttService.timeBracketMax,
        minimum: widget.mqttService.timeBracketMin,
        maximum: widget.mqttService.timeBracketMax,
        rangePadding: ChartRangePadding.additional,
        anchorRangeToVisiblePoints: false,
        interval: 10,
        title: AxisTitle(text: widget.xAxisTitle),
      ),
      primaryYAxis: NumericAxis(
        interval: 1,
        title: AxisTitle(text: widget.yAxisTitle),
      ),
      title: ChartTitle(text: widget.title),
      tooltipBehavior: TooltipBehavior(enable: true),
      series: <CartesianSeries<PlotData, double>>[
        LineSeries<PlotData, double>(
          dataSource: dataTele,
          animationDuration: 0,
          xValueMapper: (PlotData data, _) => data.x,
          yValueMapper: (PlotData data, _) => data.y,
          dataLabelSettings: const DataLabelSettings(isVisible: true),
        ),
        LineSeries<PlotData, double>(
          dataSource: dataStreamed,
          animationDuration: 0,
          color: const Color(0xFFFF9000),
          xValueMapper: (PlotData data, _) => data.x,
          yValueMapper: (PlotData data, _) => data.y,
          dataLabelSettings: const DataLabelSettings(isVisible: true),
        ),
      ],
    );
  }
}

//IR widget
class _IRWidget extends StatefulWidget {
  final String title;
  final String xAxisTitle;
  final String yAxisTitle;
  final MqttService mqttService;
  final int maxDataPoints;
  final String id;
  final List<PlotData> data;

  const _IRWidget({
    required this.title,
    required this.xAxisTitle,
    required this.yAxisTitle,
    required this.mqttService,
    required this.maxDataPoints,
    required this.id,
    required this.data, // Maximum number of data points to display
  });

  @override
  _IRWidgetState createState() => _IRWidgetState();
}

class _IRWidgetState extends State<_IRWidget> {
  List<PlotData> data = [];
  late String id = widget.id;

  @override
  void initState() {
    super.initState();
    data = widget.data;
    widget.mqttService.reactIR702L1PlotDataNotifier.addListener(_updateData);
    //_updateData();
  }

  @override
  void dispose() {
    // Remove listener when the widget is disposed
    widget.mqttService.reactIR702L1PlotDataNotifier.removeListener(_updateData);
    super.dispose();
  }

  void _updateData() {
    setState(() {
      if (widget.mqttService.reactIR702L1PlotDataNotifier.value.isNotEmpty) {
        data = [];
        // Append new data and trim if necessary
        data.addAll(widget.mqttService.reactIR702L1PlotDataNotifier.value);
        widget.mqttService.reactIR702L1PlotDataNotifier.value = [];
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    double len = data.length.toDouble();
    if (len == 0) {
      len = 1000;
    }
    return SfCartesianChart(
      primaryXAxis: NumericAxis(
        rangePadding: ChartRangePadding.none,
        maximum: len,
        minimum: 0,
        interval: 25,
        title: AxisTitle(text: widget.xAxisTitle),
      ),
      primaryYAxis: NumericAxis(
        rangePadding: ChartRangePadding.none,
        maximum: 2,
        minimum: -2,
        interval: 0.1,
        title: AxisTitle(text: widget.yAxisTitle),
      ),
      title: ChartTitle(text: widget.title),
      tooltipBehavior: TooltipBehavior(enable: true),
      series: <CartesianSeries<PlotData, double>>[
        LineSeries<PlotData, double>(
          dataSource: data,
          animationDuration: 0,
          xValueMapper: (PlotData data, _) => data.x,
          yValueMapper: (PlotData data, _) => data.y,
          dataLabelSettings: const DataLabelSettings(isVisible: true),
        ),
      ],
    );
  }
}

// Auxiliary classes
class PlotData {
  PlotData(this.x, this.y);

  final double x;
  final double y;
}

class IRPlotData {
  List<PlotData> allPlotData = [];
  int i = 0;

  List<PlotData> parse(List<double> irData) {
    for (var x in irData) {
      allPlotData.add(PlotData(i.toDouble(), x));
      i += 1;
    }
    return allPlotData;
  }

  //irData.forEach((x) {allPlotData.add(PlotData(x,i))});
}

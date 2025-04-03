import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/config/UI/brokers_and_topics.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/sketcher.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/src/dashboard.dart';
import 'package:flutter_flow_chart/ui/gauges/gauge_page_widget.dart';
import 'package:flutter_flow_chart/ui/gauges/gauge_widgets.dart';
import 'package:flutter_flow_chart/ui/graphing/graph_panel.dart';
import 'package:flutter_flow_chart/ui/list_generators/project_browser.dart';
import 'package:flutter_flow_chart/ui/optimization_tab/optimization_tab.dart';
import 'package:flutter_flow_chart/ui/script_builder.dart/script_generator.dart';
import 'package:flutter_flow_chart/ui/tabs/includes/dynamic_tabbar.dart';

class FluxiDominusDefTabs {
  FluxiDominusDefTabs({required this.mqttService}) {
    //MqttService mqttService = MqttService();
    // Initialize tabList here in the constructor
    //Pre-initialize scriptgenerator
    GlobalKey<ScriptGeneratorWidgetState> scriptGeneratorKey = GlobalKey();
    ScriptGeneratorWidget scriptGeneratorWidget = ScriptGeneratorWidget(
      mqttService: mqttService,
      key: scriptGeneratorKey,
    );
    OptimizationTab optimizationTab = OptimizationTab(mqttService: mqttService);
    mqttService.scriptGeneratorWidget = scriptGeneratorWidget;
    mqttService.scriptGeneratorWidgetKey = scriptGeneratorKey;
    //Pre-initialize flowsketcher
    GlobalKey<FlowSketcherState> flowSketcherKey = GlobalKey();
    FlowSketcher flowSketcher = FlowSketcher(
      key: flowSketcherKey,
      mqttService: mqttService,
      topic: MqttTopics.getUITopic("FlowSketcher"),
      dashboard: Dashboard(),
    );
    mqttService.flowSketcher = flowSketcher;
    mqttService.flowSketcherKey = flowSketcherKey;
    ProjectBrowser projectBrowser = ProjectBrowser(
      mqttService: mqttService,
    );

    /////////////////////////////////////////////////////////////////
    // Create a GraphWidgets instance
    GraphWidgets graphWidgets = GraphWidgets(mqttService);
    mqttService.graphWidgets = graphWidgets;

    /*
    // Add a time series widget
    graphWidgets.addUnifiedTimeSeriesWidget(
      title: 'Hotcoil 1 - Temperature',
      xAxisTitle: 'time',
      yAxisTitle: 'Deg',
      mqttService: mqttService,
      maxDataPoints: 1000,
      teleKey: 'temp',
      idTele: "subflow/hotcoil1/tele",
      idStreaming: "hotcoil1_temp",
    );
    graphWidgets.addUnifiedTimeSeriesWidget(
      title: 'Maxi 2 - Pump A Pressure',
      xAxisTitle: 'Time',
      yAxisTitle: 'Bar',
      mqttService: mqttService,
      maxDataPoints: 1000,
      teleKey: 'pressFlowSynA',
      idTele: "subflow/flowsynmaxi2/tele",
      idStreaming: "flowsynmaxi2_pressA",
    );
    graphWidgets.addUnifiedTimeSeriesWidget(
      title: 'Maxi 2 - Pump B Pressure',
      xAxisTitle: 'Time',
      yAxisTitle: 'Bar',
      mqttService: mqttService,
      maxDataPoints: 1000,
      teleKey: 'pressFlowSynB',
      idTele: "subflow/flowsynmaxi2/tele",
      idStreaming: "flowsynmaxi2_pressB",
    );
    graphWidgets.addUnifiedTimeSeriesWidget(
      title: 'Maxi 2 - System Pressure',
      xAxisTitle: 'Time',
      yAxisTitle: 'Bar',
      mqttService: mqttService,
      maxDataPoints: 1000,
      teleKey: 'pressSystem',
      idTele: "subflow/flowsynmaxi2/tele",
      idStreaming: "flowsynmaxi2_pressSystem",
    );
    graphWidgets.addUnifiedTimeSeriesWidget(
      title: 'R4 - Pressure Pump A',
      xAxisTitle: 'Time',
      yAxisTitle: 'Bar',
      mqttService: mqttService,
      maxDataPoints: 1000,
      teleKey: 'pressPumpA',
      idTele: "subflow/vapourtecR4P1700/tele",
      idStreaming: "vapourtecR4P1700_pressA",
    );
    graphWidgets.addUnifiedTimeSeriesWidget(
      title: 'R4 - Pressure Pump B',
      xAxisTitle: 'Time',
      yAxisTitle: 'Bar',
      mqttService: mqttService,
      maxDataPoints: 1000,
      teleKey: 'pressPumpB',
      idTele: "subflow/vapourtecR4P1700/tele",
      idStreaming: "vapourtecR4P1700_pressB",
    );
    graphWidgets.addUnifiedTimeSeriesWidget(
      title: 'R4 - System Pressure',
      xAxisTitle: 'Time',
      yAxisTitle: 'Bar',
      mqttService: mqttService,
      maxDataPoints: 1000,
      teleKey: 'pressSystem',
      idTele: "subflow/vapourtecR4P1700/tele",
      idStreaming: "vapourtecR4P1700_pressSystem",
    );
    graphWidgets.addIRWidget(
      title: 'Current IR Graph',
      xAxisTitle: 'Wavelength',
      yAxisTitle: 'Absorbance',
      mqttService: mqttService,
      maxDataPoints: 900,
      data: mqttService.reactIR702L1PlotDataNotifier.value,
    );
    */

    /////////////////////////////////////////////////////////////////

    tabList = [
      //Script builder
      TabData(
        index: 1,
        title: const Tab(
          child: Text('Script Builder and Flowsketcher'),
        ),
        content: Row(
          children: [
            Expanded(child: scriptGeneratorWidget),
            Expanded(child: flowSketcher),
          ],
        ),
      ),
      //FlowSketcher
      TabData(
          index: 2,
          title: const Tab(
            child: Text('Project Browser'),
          ),
          content: projectBrowser //flowSketcher,
          ),
      //Gauges
      TabData(
        index: 3,
        title: const Tab(
          child: Text('Telemetry'),
        ),
        content: Center(
          child: GaugeBlock(
            mqttService: mqttService,
            gauges: [
              //Pump A flowrate
              SemiCircularGauge(
                name: 'Maxi - Flowrate A',
                unit: 'mL/min',
                deviceName: 'flowsynmaxi2',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('flowsynmaxi2'),
                address: const ["tele", "state", "flowRatePumpA"],
                maxValue: 15,
                cmndTopic: '',
                cmndName: '',
                unitMultiplier: 1,
              ),
              //Pump A pressure + flowrate slider
              GaugeWithSlider(
                cmndName: 'pafr',
                unit: 'bar',
                deviceName: 'flowsynmaxi2',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('flowsynmaxi2'),
                address: const ["tele", "state", "pressFlowSynA"],
                min: 0,
                max: 6,
                initialValue: 0,
                maxValue: 20,
                cmndTopic: MqttTopics.getCmndTopic('flowsynmaxi2'),
                name: 'Maxi - Pump A Pressure',
                unitMultiplier: 1,
              ),
              //Pump B flowrate
              SemiCircularGauge(
                name: 'Maxi - Flowrate B',
                unit: 'mL/min',
                deviceName: 'flowsynmaxi2',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('flowsynmaxi2'),
                address: const ["tele", "state", "flowRatePumpB"],
                maxValue: 15,
                cmndTopic: '',
                cmndName: '',
                unitMultiplier: 1,
              ),
              //Pump B pressure + flowrate slider
              GaugeWithSlider(
                cmndName: 'pbfr',
                unit: 'bar',
                deviceName: 'flowsynmaxi2',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('flowsynmaxi2'),
                address: const ["tele", "state", "pressFlowSynB"],
                min: 0,
                max: 6,
                initialValue: 0,
                maxValue: 20,
                cmndTopic: MqttTopics.getCmndTopic('flowsynmaxi2'),
                name: 'Maxi - Pump B Pressure',
                unitMultiplier: 1,
              ),
              GaugeWithSlider(
                cmndName: 'temp',
                unit: 'deg',
                deviceName: 'hotcoil1',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('hotcoil1'),
                address: const ["tele", "state", "temp"],
                min: 0,
                max: 100,
                initialValue: 0,
                maxValue: 100,
                cmndTopic: MqttTopics.getCmndTopic('hotcoil1'),
                name: 'Hotcoil 1 Temp',
                unitMultiplier: 1,
              ),
              //System pressure
              SemiCircularGauge(
                name: 'Maxi - System Pressure',
                unit: 'bar',
                deviceName: 'flowsynmaxi2',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('flowsynmaxi2'),
                address: const ["tele", "state", "pressSystem"],
                maxValue: 30,
                cmndTopic: '',
                cmndName: '',
                unitMultiplier: 1,
              ),
              SemiCircularGauge(
                name: 'R4 - Flowrate A',
                unit: 'mL/min',
                deviceName: 'vapourtecR4P1700',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('vapourtecR4P1700'),
                address: const ["tele", "state", "flowRatePumpA"],
                maxValue: 15,
                cmndTopic: '',
                cmndName: '',
                unitMultiplier: 0.001,
              ),
              //Pump A pressure + flowrate slider
              GaugeWithSlider(
                cmndName: 'pafr',
                unit: 'bar',
                deviceName: 'vapourtecR4P1700',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('vapourtecR4P1700'),
                address: const ["tele", "state", "pressPumpA"],
                min: 0,
                max: 6,
                initialValue: 0,
                maxValue: 20,
                cmndTopic: MqttTopics.getCmndTopic('vapourtecR4P1700'),
                name: 'R4 - Pump A Pressure',
                unitMultiplier: 1,
              ),
              //Pump B flowrate
              SemiCircularGauge(
                name: 'R4 - Flowrate B',
                unit: 'mL/min',
                deviceName: 'vapourtecR4P1700',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('vapourtecR4P1700'),
                address: const ["tele", "state", "flowRatePumpB"],
                maxValue: 15,
                cmndTopic: '',
                cmndName: '',
                unitMultiplier: 0.001,
              ),
              //Pump B pressure + flowrate slider
              GaugeWithSlider(
                cmndName: 'pbfr',
                unit: 'bar',
                deviceName: 'vapourtecR4P1700',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('vapourtecR4P1700'),
                address: const ["tele", "state", "pressPumpB"],
                min: 0,
                max: 6,
                initialValue: 0,
                maxValue: 20,
                cmndTopic: MqttTopics.getCmndTopic('vapourtecR4P1700'),
                name: 'R4 - Pump B Pressure',
                unitMultiplier: 1,
              ),
              //System pressure
              SemiCircularGauge(
                name: 'R4 - System Pressure',
                unit: 'bar',
                deviceName: 'vapourtecR4P1700',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('vapourtecR4P1700'),
                address: const ["tele", "state", "pressSystem"],
                maxValue: 30,
                cmndTopic: '',
                cmndName: '',
                unitMultiplier: 1,
              ),
              /*
              GaugeWithToggle(
                name: 'Collecting',
                unit: '',
                deviceName: 'flowsynmaxi2',
                mqttService: mqttService,
                deviceValueName: '',
                topic: MqttTopics.getTeleTopic('flowsynmaxi2'),
                address: const ["tele", "state", "valveOpenCW"],
                initialValue: false,
                maxValue: 150,
                cmndTopic: 'subflow/flowsynmaxi2/cmnd',
                cmndName: 'svcw',
              ),
              */
            ],
          ),
        ),
      ),
      //Graphs
      TabData(
        index: 4,
        title: const Tab(
          child: Text('Graphing'),
        ),
        content: SingleChildScrollView(
          child: Column(
            children: graphWidgets.widgets.cast<Widget>(),
          ),
        ),
      ),
      TabData(
          index: 5, title: Tab(text: 'Optimization'), content: optimizationTab)
    ];
  }

  final MqttService mqttService;
  late List<TabData> tabList; // Declare tabList as a late variable

  List<TabData> get tabs => tabList;
}

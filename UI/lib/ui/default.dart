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

    GaugeBlock gauges = GaugeBlock(
      gauges: mqttService.dynamicGaugeWidgets,
      mqttService: mqttService,
    );

    /////////////////////////////////////////////////////////////////
    // Create a GraphWidgets instance
    GraphWidgets graphWidgets = GraphWidgets(mqttService);
    mqttService.graphWidgets = graphWidgets;
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
        content: Center(child: gauges),
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

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_flow_chart/config/UI/brokers_and_topics.dart';
import 'package:flutter_flow_chart/ui/authentication/login_page.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/flutter_flow_chart.dart';
import 'package:flutter_flow_chart/ui/flow_sketcher/sketcher.dart';
import 'package:flutter_flow_chart/ui/graphing/graph_panel.dart';
import 'package:flutter_flow_chart/ui/script_builder.dart/hardcoded_tele_templates.dart';
import 'package:flutter_flow_chart/ui/script_builder.dart/script_generator.dart';
//import 'package:flutter_flow_chart/config/UI/data_queue_instructions.dart' as dq;
import 'package:flutter_flow_chart/utils/timing.dart';
import 'package:mqtt_client/mqtt_browser_client.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:uuid/uuid.dart';

import '../ui/gauges/gauge_widgets.dart';

class MqttService extends ChangeNotifier {
  late MqttClient client;
  Map<String, String> topicsCmnd = MqttTopics.getCmndTopics();
  Map<String, String> topicsTele = MqttTopics.getTeleTopics();
  Map<String, String> topicsUI = MqttTopics.getUITopics();
  Map<String, dynamic> lastMsgFromTopic = {};
  final String server;
  final builder = MqttClientPayloadBuilder();
  List<String> availableDevices = [];

  double minTeleGap = 0.25; //Min time to wait between logging tele

  Map<String, Map<String, dynamic>> currFlowScript = {};
  String currDashboardJson = '{"elements":[]}';
  late Dashboard currDashboard;

  late FlowSketcher flowSketcher;
  late GlobalKey<FlowSketcherState> flowSketcherKey;

  late ScriptGeneratorWidget scriptGeneratorWidget;
  late GlobalKey<ScriptGeneratorWidgetState> scriptGeneratorWidgetKey;

  //Map<String, dynamic> currDashboard = {};
  Map<String, List<Map<String, dynamic>>> currTestScriptBlocks = {};

  ///////////////////////////////////////////////////
  //Graphs
  // Variables to hold x-axis time limits
  double timeBracketMin = 0;
  double timeBracketMax = 120;
  //Track which already created
  Set<String> alreadyGraphed = {};
  //Eligible for graphing and what to graph
  Map<String, Map<String, dynamic>> eligibleForGraphing = {
    "subflow/hotcoil1/tele": {
      "temp": {
        "title": "Hotcoil 1 - Temperature",
        "xAxisTitle": "Time",
        "yAxisTitle": "Deg",
        "maxDataPoints": 1000,
        "idStreaming": "hotcoil1_temp",
      },
    },
    "subflow/vapourtecR4P1700/tele": {
      "pressPumpA": {
        "title": "R4 - Pump A Pressure",
        "xAxisTitle": "Time",
        "yAxisTitle": "Bar",
        "maxDataPoints": 1000,
        "idStreaming": "vapourtecR4P1700_pressA",
      },
      "pressPumpB": {
        "title": "R4 - Pump B Pressure",
        "xAxisTitle": "Time",
        "yAxisTitle": "Bar",
        "maxDataPoints": 1000,
        "idStreaming": "vapourtecR4P1700_pressB",
      },
      "pressSystem": {
        "title": "R4 - System Pressure",
        "xAxisTitle": "Time",
        "yAxisTitle": "Bar",
        "maxDataPoints": 1000,
        "idStreaming": "vapourtecR4P1700_pressSystem",
      },
    },
  };

  //////////////////////////////////////////////////////////////////
  //Gauges
  Set<String> alreadyGauged = {};
  List<GaugeWidget> dynamicGaugeWidgets = [];
  Map<String, Map<int, Map<String, dynamic>>> eligibleForGauge = {
    //Topics might have multiple gauges, each topic's gauges have index 0 -> n
    "subflow/hotcoil1/tele": {
      0: {
        "gaugeType": GaugeWithSlider, //Use as pointer?
        "cmndName": 'temp',
        "unit": 'deg',
        "deviceName": 'hotcoil1',
        "deviceValueName": '',
        "address": const ["tele", "state", "temp"],
        "min": 0,
        "max": 100,
        "initialValue": 0,
        "maxValue": 100,
        "cmndTopic": MqttTopics.getCmndTopic('hotcoil1'),
        "name": 'Hotcoil 1 Temp',
        "unitMultiplier": 1
      },
    },
    "subflow/vapourtecR4P1700/tele": {
      0: {
        "gaugeType": SemiCircularGauge,
        "name": 'R4 - Pressure A',
        "unit": 'Bar',
        "deviceName": 'vapourtecR4P1700',
        "deviceValueName": '',
        "address": const ["tele", "state", "pressPumpA"],
        "maxValue": 15,
        "cmndTopic": '',
        "cmndName": '',
        "unitMultiplier": 1,
      },
      1: {
        "gaugeType": GaugeWithSlider,
        "name": 'R4 - Pump A Flowrate',
        "cmndName": 'pafr',
        "unit": 'mL/min',
        "deviceName": 'vapourtecR4P1700',
        "deviceValueName": '',
        "address": const ["tele", "state", "flowRatePumpA"],
        "min": 0,
        "max": 6,
        "initialValue": 0,
        "maxValue": 6,
        "cmndTopic": MqttTopics.getCmndTopic('vapourtecR4P1700'),
        "unitMultiplier": 1,
      },
      2: {
        "gaugeType": SemiCircularGauge,
        "name": 'R4 - Pressure B',
        "unit": 'Bar',
        "deviceName": 'vapourtecR4P1700',
        "deviceValueName": '',
        "address": const ["tele", "state", "pressPumpB"],
        "maxValue": 15,
        "cmndTopic": '',
        "cmndName": '',
        "unitMultiplier": 1,
      },
      3: {
        "gaugeType": GaugeWithSlider,
        "name": 'R4 - Pump B Flowrate',
        "cmndName": 'pbfr',
        "unit": 'mL/min',
        "deviceName": 'vapourtecR4P1700',
        "deviceValueName": '',
        "address": const ["tele", "state", "flowRatePumpB"],
        "min": 0,
        "max": 6,
        "initialValue": 0,
        "maxValue": 6,
        "cmndTopic": MqttTopics.getCmndTopic('vapourtecR4P1700'),
        "unitMultiplier": 1,
      },
      4: {
        "gaugeType": SemiCircularGauge,
        "name": 'R4 - System Pressure',
        "unit": 'Bar',
        "deviceName": 'vapourtecR4P1700',
        "deviceValueName": '',
        "address": const ["tele", "state", "pressSystem"],
        "maxValue": 15,
        "cmndTopic": '',
        "cmndName": '',
        "unitMultiplier": 1,
      },
    },
  };

  //

  //Optimization
  Map<String, dynamic> optimizationDetails = {};
  ValueNotifier<List<Map<String, Map<String, double>>>> resultHistory =
      ValueNotifier([]);
  ValueNotifier<Map<String, double>> recommendedParams = ValueNotifier({});
  ValueNotifier<double> lastYield = ValueNotifier(0);
  ValueNotifier<bool> goOptimization = ValueNotifier(false);
  // List<String> objectiveFunctions = [];

  // Mock options for optimizer and objective function
  final List<String> optimizationOptions = ["SUMMIT_SOBO"];
  final List<String> objectiveFunctions = ["WJ_IR_ALLYL_BROMIDE"];

  //
  //////////////////////////////////////////////////////////////////////////
  //Data streams *TODO - generalize
  ValueNotifier<List<PlotData>> hotcoil1PlotDataNotifier = ValueNotifier([]);

  Map<String, List<String>> teleToCollect = {};

  Map<String, ValueNotifier<List<PlotData>>> teleDataNotifiers = {};
  Map<String, ValueNotifier<List<List<double>>>> dbStreamDataNotifiers = {};
  ValueNotifier<List<PlotData>> reactIR702L1PlotDataNotifier =
      ValueNotifier([]);
  EpochDelta epochDelta = EpochDelta();

  Map<String, EpochDelta> lastReceivedTime = {};

  Map<String, ValueNotifier<Map<String, dynamic>>> backendReturn = {
    "getAllExpWidgetInfo": ValueNotifier({}),
    "loadTestrun": ValueNotifier({})
  };
  //////////////////////////////////////////////////////////////////////////

  //Authentication
  Authenticator authenticator = Authenticator();

  bool runTest = false;
  ValueNotifier<bool> testRunning = ValueNotifier(false);

  late GraphWidgets graphWidgets;

  //Construct.
  MqttService({required this.server}) {
    try {
      //print("WJ - Now here");
      // Other initialization code if any
    } catch (e) {
      //print("WJ - Error in constructor: $e");
    }
  }
  //

  Future<void> initializeMQTTClient() async {
    String identifier = 'flutter_client_${Uuid().v4()}';
    client = MqttBrowserClient(server, identifier);
    client.port = 9001;
    client.logging(on: false);
    client.keepAlivePeriod = 20;
    client.onConnected = onConnected;
    client.onSubscribed = onSubscribed;
    client.autoReconnect = true;
    //client.onDisconnected = onDisconnected;
    client.resubscribeOnAutoReconnect = true;
    //client.onAutoReconnected = onConnected;

    final connMess = MqttConnectMessage()
        .withClientIdentifier(identifier)
        .startClean()
        .withWillQos(MqttQos.atMostOnce);

    client.connectionMessage = connMess;
  }

  Future<void> connect() async {
    try {
      print('WJ - Initializing Mqtt Browser Client');
      await initializeMQTTClient();
      print('WJ - Attempting to connect');
      MqttClientConnectionStatus? status = await client.connect();
      print('WJ - Connection state $status');
      if (status != null &&
          status.state.toString() != 'MqttConnectionState.disconnected') {
        print(
            'WJ - MqttClientConnectionStatus returned ${status.state.toString()}!');
        client.updates!.listen(onMessage);
      }
    } catch (e) {
      print('WJ - Connection failed: $e');
    }
  }

  void onSubscribed(String topic) {
    print('Subscribed to $topic');
  }

  ////////////////////////////////////////////
  //Main message processor
  void onMessage(List<MqttReceivedMessage<MqttMessage>> event) {
    final MqttPublishMessage recMess = event[0].payload as MqttPublishMessage;
    final String message =
        MqttPublishPayload.bytesToStringAsString(recMess.payload.message);

    String topic = event[0].topic;
    Map<String, dynamic> messageMap = jsonDecode(message);

    lastMsgFromTopic[topic] = messageMap;

    //Graph it?
    maybeCreateGraphsForTopic(topic, messageMap);
    maybeCreateGaugesForTopic(topic);

    if (!lastReceivedTime.containsKey(topic)) {
      lastReceivedTime[topic] = EpochDelta();
    }

    //Fix hierdie gemors, dis stupid
    if (messageMap.containsKey("LoginPageWidget")) {
      if ((messageMap["LoginPageWidget"]).containsKey("authenticated") &&
          (messageMap["LoginPageWidget"])["authenticated"]) {
        authenticator.signedIn = true;
        print('WJ - Sign in successful!');
        if (authenticator.signInFailed) {
          authenticator.signInFailed = false;
        }
      } else {
        print('WJ - Sign in failed!');
        authenticator.signInFailed = true;
        if (authenticator.signedIn) {
          authenticator.signedIn = false;
        }
      }
      //
    } else if (topic == "ui/opt/out") {
      if (messageMap.containsKey("optInfo")) {
        if (messageMap["optInfo"].containsKey("eval")) {
          if (messageMap["optInfo"]["eval"].containsKey("yield")) {
            lastYield.value = messageMap["optInfo"]["eval"]["yield"];
          }
        }
        if (messageMap["optInfo"].containsKey("recommendedParams")) {
          recommendedParams.value =
              (messageMap["optInfo"]["recommendedParams"]);
        }
        if (messageMap["optInfo"].containsKey("recommendationResult")) {
          var result = Map<String, double>.from(
              messageMap["optInfo"]["recommendationResult"]);
          double yield = result["yield"] ?? 0;

          // Update resultHistory
          resultHistory.value = [
            ...resultHistory.value,
            {
              'recommendation': {
                'Temperature': result['Temperature'] ?? 0,
                'Flowrate': result['Flowrate'] ?? 0,
                'yield': yield
              }
            }
          ];

          // Optionally update best yield if you want to keep a separate variable for it
          if (yield > lastYield.value) {
            lastYield.value = yield;
          }
        }
      }
      if (messageMap.containsKey("goOptimization")) {
        lastYield.value = 0;
        resultHistory.value = [];
        goOptimization.value = true;
      }
    } else if (messageMap.containsKey("GraphWidgets")) {
      //TODO - FIX THIS HARDCODED DISASTER
    } else if (topic == "subflow/flowsynmaxi2/tele" &&
        lastReceivedTime[topic]!.secSinceEpoch() > minTeleGap) {
      lastReceivedTime[topic]?.reset();
      if (teleToCollect.containsKey(topic)) {
        if (teleToCollect[topic]!.isNotEmpty) {
          for (var x in teleToCollect[topic]!) {
            String id = "${topic}_$x";
            teleDataNotifiers[id]!.value = [
              ...teleDataNotifiers[id]!.value,
              PlotData(
                epochDelta.secSinceEpoch().toDouble(),
                HardcodedTeleKeys.getTeleVal(messageMap, x),
              ),
            ];
          }
        }
      }
      //
    } else if (topic == "subflow/vapourtecR4P1700/tele" &&
        lastReceivedTime[topic]!.secSinceEpoch() > minTeleGap) {
      lastReceivedTime[topic]?.reset();
      if (teleToCollect.containsKey(topic)) {
        if (teleToCollect[topic]!.isNotEmpty) {
          for (var x in teleToCollect[topic]!) {
            String id = "${topic}_$x";
            teleDataNotifiers[id]!.value = [
              ...teleDataNotifiers[id]!.value,
              PlotData(
                epochDelta.secSinceEpoch().toDouble(),
                HardcodedTeleKeys.getTeleVal(messageMap, x),
              ),
            ];
          }
        }
      }
      //
    } else if (topic == "subflow/hotcoil1/tele" &&
        lastReceivedTime[topic]!.secSinceEpoch() > minTeleGap) {
      lastReceivedTime[topic]?.reset();
      for (var x in teleToCollect[topic]!) {
        String id = "${topic}_$x";
        teleDataNotifiers[id]?.value = [
          ...teleDataNotifiers[id]!.value,
          PlotData(
            epochDelta.secSinceEpoch().toDouble(),
            HardcodedTeleKeys.getTeleVal(messageMap, x),
          ),
        ];
      }
      //
    } else if (topic == "subflow/reactIR702L1/tele" &&
        lastReceivedTime[topic]!.secSinceEpoch() > minTeleGap) {
      lastReceivedTime[topic]?.reset();
      IRPlotData thisData = IRPlotData();
      List<double> raw = (messageMap["tele"]["state"]["data"]).cast<double>();
      List<PlotData> gd = thisData.parse(raw);
      reactIR702L1PlotDataNotifier.value = gd;
      //
    } else if (topic == "ui/dbStreaming/out") {
      messageMap = messageMap['dbStreaming'];
      String id = messageMap.keys.first;
      print(
        'WJ - ${dbStreamDataNotifiers[id]?.value}, keys: ${messageMap.keys}',
      );
      if (!dbStreamDataNotifiers.containsKey(id)) {
        dbStreamDataNotifiers[id] = ValueNotifier([]);
      }
      print('WJ - received: ${messageMap[id]}');
      dbStreamDataNotifiers[id]?.value.addAll(messageMap[id]);
      //notifyListeners();
      //Doesn't seem neccessary to notify listeners?!
    } else if (topic == "ui/dbCmnd/ret") {
      if (messageMap.containsKey("searchForTest")) {
        backendReturn["searchForTest"]!.value = messageMap["searchForTest"];
        //
      } else if (messageMap.containsKey("getAllExpWidgetInfo")) {
        backendReturn["getAllExpWidgetInfo"]!.value =
            messageMap["getAllExpWidgetInfo"];
        //
      } else if (messageMap.containsKey("createReplicate")) {
        backendReturn["getAllExpWidgetInfo"]!.value =
            messageMap["createReplicate"];
        //
      } else if (messageMap.containsKey("loadTestrun")) {
        //
      } else if (messageMap.containsKey("handleStreamRequest")) {
        messageMap = messageMap["handleStreamRequest"];
        if (messageMap.keys.length == 1) {
          String id = messageMap.keys.first;
          if (!dbStreamDataNotifiers.containsKey(id)) {
            dbStreamDataNotifiers[id] = ValueNotifier([]);
          }
          List<List<double>> rawData = (messageMap[id] as List)
              .map((e) => List<double>.from(e))
              .toList();
          /*
          List<PlotData> plotData =
              rawData.map((xy) => PlotData(xy[0], xy[1])).toList();
          */
          dbStreamDataNotifiers[id]!.value =
              dbStreamDataNotifiers[id]!.value + rawData;
          print(
              'WJ - Received streamed db tele number of: ${dbStreamDataNotifiers[id]!.value.length}');
          //
        }
      } else if (messageMap.containsKey("runTest")) {
        print("WJ WE HERE");
        if (messageMap["runTest"]) {
          epochDelta.reset();
        }
        runTest = messageMap["runTest"];
        testRunning.value = messageMap["runTest"];
        print('WJ - Setting testRunning to ${messageMap["runTest"]}');
      }
    }
  }

  void onConnected() {
    topicsTele.forEach((key, value) {
      if (client.getSubscriptionsStatus(value).name == 'doesNotExist') {
        print('WJ - topic $value is being subscribed to!');
        client.subscribe(value, MqttQos.atMostOnce);
      }
    });
    topicsUI.forEach((key, value) {
      //print('WJ - ${client.getSubscriptionsStatus(value).name}');
      if (client.getSubscriptionsStatus(value).name == 'doesNotExist') {
        print('WJ - topic $value is being subscribed to!');
        client.subscribe(value, MqttQos.atMostOnce);
      }
    });
  }

  void publish(String topic, String message,
      {MqttQos qos = MqttQos.exactlyOnce}) {
    if (client.connectionStatus.toString() == 'disconnected') {
      //TODO - What then?
      //connect();
    }
    builder.clear();
    builder.addString(message);
    print('WJ - Attempting to publish $message!');
    var ret = client.publishMessage(topic, qos, builder.payload!);
    print('WJ - Publish attempt for $message resulted in: $ret!');
  }

  //Util methods
  void maybeCreateGraphsForTopic(
      String topic, Map<String, dynamic> messageMap) {
    //TODO - trigger rebuild without having to tab away
    if (!eligibleForGraphing.containsKey(topic)) return;

    var teleMap = messageMap["tele"]?["state"];
    if (teleMap == null) return;

    eligibleForGraphing[topic]!.forEach((teleKey, config) {
      if (teleMap.containsKey(teleKey)) {
        String uniqueGraphID = "${topic}_$teleKey";
        if (!alreadyGraphed.contains(uniqueGraphID)) {
          graphWidgets.addUnifiedTimeSeriesWidget(
            title: config['title'],
            xAxisTitle: config['xAxisTitle'],
            yAxisTitle: config['yAxisTitle'],
            mqttService: this,
            maxDataPoints: config['maxDataPoints'],
            teleKey: teleKey,
            idTele: topic,
            idStreaming: config['idStreaming'],
          );
          alreadyGraphed.add(uniqueGraphID);
          print("Graph added for $uniqueGraphID");
        }
      }
    });
  }

  //Gauges
  void maybeCreateGaugesForTopic(String topic) {
    //TODO - trigger rebuild without having to tab away
    if (!eligibleForGauge.containsKey(topic)) return;

    eligibleForGauge[topic]!.forEach((index, config) {
      String uniqueID = "$topic:${config['name']}";
      if (alreadyGauged.contains(uniqueID)) return;

      Type gaugeType = config["gaugeType"];
      late GaugeWidget widget;

      if (gaugeType == GaugeWithSlider) {
        widget = GaugeWithSlider(
          name: config["name"],
          unit: config["unit"],
          deviceName: config["deviceName"],
          deviceValueName: config["deviceValueName"],
          mqttService: this,
          topic: topic,
          address: List<String>.from(config["address"]),
          min: config["min"],
          max: config["max"],
          initialValue: config["initialValue"],
          maxValue: config["maxValue"],
          cmndTopic: config["cmndTopic"],
          cmndName: config["cmndName"],
          unitMultiplier: config["unitMultiplier"],
        );
      } else if (gaugeType == SemiCircularGauge) {
        widget = SemiCircularGauge(
          name: config["name"],
          unit: config["unit"],
          deviceName: config["deviceName"],
          deviceValueName: config["deviceValueName"],
          mqttService: this,
          topic: topic,
          address: List<String>.from(config["address"]),
          maxValue: config["maxValue"],
          cmndTopic: config["cmndTopic"],
          cmndName: config["cmndName"],
          unitMultiplier: config["unitMultiplier"],
        );
      } else {
        print("Unsupported gauge type for $uniqueID");
        return;
      }

      dynamicGaugeWidgets.add(widget);
      alreadyGauged.add(uniqueID);
      print("Gauge added: $uniqueID");
      notifyListeners(); // in case widgets rebuild live
    });
  }
}

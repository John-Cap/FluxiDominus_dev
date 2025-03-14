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

class MqttService extends ChangeNotifier {
  late MqttBrowserClient client;
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

  //Graphs
  // Variables to hold x-axis time limits
  double timeBracketMin = 0;
  double timeBracketMax = 120;

  //Optimization
  Map<String, dynamic> optimizationDetails = {};
  // List<String> optimizationOptions = [];
  // List<String> objectiveFunctions = [];

  // Mock options for optimizer and objective function
  final List<String> optimizationOptions = [
    "VIDAL_C13_3415",
    "VIDAL_C13_3465",
    "ERSILIA_BLANK_TS_54",
    "WJ_LEAP_2024_01_30_3",
    "STD_SUMMIT_1"
  ];
  final List<String> objectiveFunctions = [
    "WJ_IR_800_2",
    "WJ_IR_800_5",
    "GEN_NMR_IR_13000"
  ];
  // Mocking a stream for optimization progress updates
  Stream<Map<String, dynamic>> get optimizationProgressStream async* {
    for (int i = 0; i <= 10; i++) {
      await Future.delayed(Duration(seconds: 1));
      yield {
        'optimizer': optimizationDetails['optimizer'] ?? 'N/A',
        'objectiveFunction': optimizationDetails['objectiveFunction'] ?? 'N/A',
        'recommendedParams': {
          'Temperature': '${20 + i}°C',
          'Flowrate': '${5 + i * 0.5} mL/min'
        },
        'bestYield': '${80 + i}%',
        'finalYield': i == 10 ? '${90 + i}%' : null,
        'elapsedTime': '$i seconds',
      };
    }
    runTest = false;
  }

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
    client = MqttBrowserClient(server, 'flutter-web-client');
    client.port = 9001;
    client.logging(on: false);
    client.keepAlivePeriod = 20;
    client.onConnected = onConnected;
    client.onSubscribed = onSubscribed;
    client.autoReconnect = true;
    //client.onDisconnected = onDisconnected;
    client.resubscribeOnAutoReconnect = false;
    //client.onAutoReconnected = onConnected;

    final connMess = MqttConnectMessage()
        .withClientIdentifier('flutter-web-client')
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
}

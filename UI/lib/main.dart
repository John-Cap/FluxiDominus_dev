import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:flutter_flow_chart/ui/default.dart';
import 'package:flutter_flow_chart/ui/tabs/tab_box.dart';

import 'ui/authentication/login_page.dart';

//
void main() async {
  MqttService thisMqttService = MqttService(server: 'ws://172.30.243.138/');
  //MqttService thisMqttService = MqttService(server: 'ws://192.168.1.141');
  await thisMqttService.initializeMQTTClient();
  await thisMqttService.connect();
  runApp(MyApp(
    mqttService: thisMqttService,
  ));
}

class MyApp extends StatelessWidget {
  final MqttService mqttService;

  const MyApp({super.key, required this.mqttService});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dynamic TabBar Demo',
      theme: ThemeData(
        useMaterial3: true,
      ),
      home: MyHomePage(
        title: 'FluxiDominus Demo',
        mqttService: mqttService,
      ),
      /*
      initialRoute: '/login',
      routes: {
        '/login': (context) => MyLoginPage(
              mqttService: mqttService,
              title: 'Hello there! Please sign in with your organizational ID',
            ),
        '/home': (context) => const MyHomePage(title: 'FluxiDominus Demo'),
      },
      */
    );
  }
}

class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key, required this.title, required this.mqttService});
  final String title;
  final MqttService mqttService;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: TabBox(
        title: 'FluxiDominus Demo',
        tabs: FluxiDominusDefTabs(mqttService: mqttService).tabs,
      ),
    );
  }
}

class MyLoginPage extends StatelessWidget {
  const MyLoginPage({
    super.key,
    required this.title,
    required this.mqttService,
  });
  final String title;
  final MqttService mqttService;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: LoginPage(mqttService: mqttService),
    );
  }
}

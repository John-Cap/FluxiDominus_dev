/*
import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'dart:typed_data';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('3D Surface Plot')),
        body: PlotWidget(
          mqttService: MqttService(server: 'localhost'),
        ),
      ),
    );
  }
}

class PlotWidget extends StatefulWidget {
  final MqttService mqttService;

  const PlotWidget({super.key, required this.mqttService});
  @override
  _PlotWidgetState createState() => _PlotWidgetState();
}

class _PlotWidgetState extends State<PlotWidget> {
  final WebSocketChannel channel = WebSocketChannel.connect(
    Uri.parse(
        //'ws://localhost:9003'), // Replace <your-pi-ip> with the IP address of your Raspberry Pi
        'ws://146.64.91.174:9003'), // Replace <your-pi-ip> with the IP address of your Raspberry Pi
  );

  Uint8List? _imageBytes;

  void _sendCommand(String action, double value) {
    final command = jsonEncode({'action': action, 'value': value});
    channel.sink.add(command);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: RepaintBoundary(
            child: StreamBuilder(
              stream: channel.stream,
              builder: (context, snapshot) {
                if (snapshot.hasData) {
                  // Update image bytes only when new data is received
                  _imageBytes = base64Decode(snapshot.data as String);
                }

                if (_imageBytes != null) {
                  return Image.memory(_imageBytes!);
                } else if (snapshot.hasError) {
                  return Text('Error: ${snapshot.error}');
                }

                return const Center(child: CircularProgressIndicator());
              },
            ),
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () => _sendCommand('zoom', 10), // Zoom In
              child: const Text('Zoom In'),
            ),
            const SizedBox(width: 10),
            ElevatedButton(
              onPressed: () => _sendCommand('zoom', -10), // Zoom Out
              child: const Text('Zoom Out'),
            ),
            const SizedBox(width: 10),
            ElevatedButton(
              onPressed: () =>
                  _sendCommand('tilt_left_right', 10), // Tilt Right
              child: const Text('Tilt Right'),
            ),
            const SizedBox(width: 10),
            ElevatedButton(
              onPressed: () =>
                  _sendCommand('tilt_left_right', -10), // Tilt Left
              child: const Text('Tilt Left'),
            ),
            const SizedBox(width: 10),
            ElevatedButton(
              onPressed: () => _sendCommand('tilt_up_down', 10), // Tilt Up
              child: const Text('Tilt Up'),
            ),
            const SizedBox(width: 10),
            ElevatedButton(
              onPressed: () => _sendCommand('tilt_up_down', -10), // Tilt Down
              child: const Text('Tilt Down'),
            ),
          ],
        ),
      ],
    );
  }

  @override
  void dispose() {
    channel.sink.close();
    super.dispose();
  }
}
*/
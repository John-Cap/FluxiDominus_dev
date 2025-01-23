import 'dart:convert';
import 'package:encrypt/encrypt.dart' as encrypt;
import 'package:encrypt/encrypt.dart';
import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/config/UI/brokers_and_topics.dart';
import 'package:flutter_flow_chart/includes/plutter.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:uuid/uuid.dart';

class Authenticator {
  final User user = User();
  final String sessionId = const Uuid().v4();
  bool signedIn = false;
  bool signInFailed = false;
  // 32-char key for AES-256
  final kryptKey = encrypt.Key.fromUtf8(
      'my32lengthsupersecretnooneknows1'); //TODO - find out where you would keep these keys
  final iv = encrypt.IV.fromUtf8('16byteslongiv123'); // 16 bytes IV
}

// Base class
class UserBase {
  String user;
  String orgId; // Employee num
  String role; // Admin/user, etc
  String sessionId;

  // Constructor for the base class
  UserBase({this.user = '', this.orgId = '', this.role = ''})
      : sessionId = const Uuid().v4(); // Generate a full UUID
}

// Derived class for regular user
class User extends UserBase {
  User({super.user, super.orgId}) : super(role: 'user');
}

// Derived class for administrator
class Administrator extends UserBase {
  Administrator({super.user, super.orgId}) : super(role: 'admin');
}

class Profile {
  final String firstName;
  final String lastName;
  final String orgId;
  final String role;
  final Authenticator authenticator;

  Profile(
    this.firstName,
    this.lastName,
    this.orgId,
    this.role,
    this.authenticator,
  );
}

class LoginPage extends StatefulWidget {
  LoginPage({super.key, required this.mqttService});
  final MqttService mqttService;
  final Authenticator authenticator = Authenticator();

  @override
  LoginPageState createState() => LoginPageState();
}

class LoginPageState extends State<LoginPage> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final bool _requestSent = false;

  Stream<bool> get signInStream async* {
    while (!widget.mqttService.authenticator.signedIn) {
      await Future.delayed(const Duration(milliseconds: 500));
      yield false;
    }
    //print('WJ - Signed in!');
    yield true;
  }

  get iv => widget.authenticator.iv;

  encrypt.Key get kryptKey => widget.authenticator.kryptKey;
  void _login() {
    if (!_requestSent) {
      Encrypted encrypted =
          (encrypt.Encrypter(encrypt.AES(kryptKey, mode: encrypt.AESMode.cbc)))
              .encrypt((_passwordController.text), iv: iv);
      widget.mqttService.publish(
        MqttTopics.getUITopic("LoginPageWidget"),
        jsonEncode({
          "LoginPageWidget": {
            "orgId": _usernameController.text,
            "password": encrypted.base64,
          }
        }),
        qos: MqttQos.exactlyOnce,
      );

      widget.mqttService.authenticator.user.orgId = _usernameController.text;
      _usernameController.text = "";
      _passwordController.text = "";

      // Use a StreamBuilder to listen to the sign-in status
      showDialog(
        context: context,
        builder: (context) {
          return StreamBuilder<bool>(
            stream: signInStream,
            builder: (context, snapshot) {
              if (snapshot.hasData && snapshot.data == true) {
                Navigator.of(context).pop(); // Close the dialog
                Navigator.of(context)
                    .pushReplacementNamed('/home'); // Navigate to the home page
                return Container(); // Return an empty container once signed in
              } else {
                return const AlertDialog(
                  title: Text('Logging in...'),
                  content: CircularProgressIndicator(),
                );
              }
            },
          );
        },
      );
    } else {
      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: const Text('Login Failed'),
            content: const Text('Incorrect username or password.'),
            actions: <Widget>[
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                child: const Text('OK'),
              ),
            ],
          );
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _login,
              child: const Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}

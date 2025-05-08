import 'package:flutter/material.dart';

class SketcherInputDialog {
  /// Prompts user for a double input (e.g., flowrate, volume, etc.)
  static Future<double?> getDouble({
    required BuildContext context,
    required String title,
    String label = 'Enter a value',
  }) {
    double? value;

    return showDialog<double>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          content: TextField(
            decoration: InputDecoration(labelText: label),
            keyboardType: TextInputType.number,
            onChanged: (input) {
              value = double.tryParse(input);
            },
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, null),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, value),
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  /// Prompts user to choose between true/false
  static Future<bool?> getBool({
    required BuildContext context,
    required String title,
    String trueText = 'Yes',
    String falseText = 'No',
  }) {
    return showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(title),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text(falseText),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              child: Text(trueText),
            ),
          ],
        );
      },
    );
  }
}

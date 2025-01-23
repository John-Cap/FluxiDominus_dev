import 'package:flutter/material.dart';

class ListWidgetElement {
  final String title;
  final List<String> dropDownInfo;
  bool isExpanded;

  ListWidgetElement({
    required this.title,
    required this.dropDownInfo,
    this.isExpanded = false,
  });
}

class ExperimentListWidgetElement extends ListWidgetElement {
  ExperimentListWidgetElement({
    required super.title,
    List<String>? dropDownInfo, // Optional parameter
  }) : super(
          dropDownInfo: dropDownInfo ?? [''], // Provide default value here
        );
}

class ListWidgetElementWidget extends StatefulWidget {
  final ListWidgetElement element;

  const ListWidgetElementWidget({super.key, required this.element});

  @override
  _ListWidgetElementWidgetState createState() =>
      _ListWidgetElementWidgetState();
}

class _ListWidgetElementWidgetState extends State<ListWidgetElementWidget> {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: () {
          setState(() {
            widget.element.isExpanded = !widget.element.isExpanded;
          });
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                widget.element.title,
                style: const TextStyle(
                    fontSize: 18.0, fontWeight: FontWeight.bold),
              ),
            ),
            if (widget.element.isExpanded)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: widget.element.dropDownInfo
                      .map((info) => Text(info))
                      .toList(),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

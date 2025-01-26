import 'package:flutter/material.dart';

class ListBox extends StatelessWidget {
  final List<Widget> listElements;

  const ListBox({super.key, this.listElements = const []});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      shrinkWrap: true,
      itemCount: listElements.length,
      itemBuilder: (context, index) {
        return listElements[index];
      },
    );
  }
}

void main() async {
  runApp(MaterialApp(
    home: MyExample(),
  ));
}

class MyExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListBox(
      listElements: const [
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
        Text('List element 1'),
        Text('List element 2'),
        Text('List element 3'),
      ],
    );
  }
}

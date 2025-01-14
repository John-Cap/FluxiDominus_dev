import 'package:flutter/material.dart';

class SearchBox extends StatelessWidget {
  final Function(String) onSubmit;

  const SearchBox({super.key, required this.onSubmit});

  @override
  Widget build(BuildContext context) {
    return TextField(
      onSubmitted: onSubmit,
      decoration: InputDecoration(
        hintText: 'Search...',
        prefixIcon: const Icon(Icons.search),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide.none,
        ),
        filled: true,
        fillColor: Colors.grey[200],
      ),
    );
  }
}

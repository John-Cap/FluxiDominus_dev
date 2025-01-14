class CustomCommands {
  final Map<String, List<String>> _commands = {};

  void registerCommand(String commandName, List<String> params) {
    _commands[commandName] = params;
  }

  List<String>? getCommandParams(String commandName) {
    return _commands[commandName];
  }
}

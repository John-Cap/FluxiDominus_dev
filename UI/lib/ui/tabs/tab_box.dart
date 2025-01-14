import 'package:flutter/material.dart';
import 'package:flutter_flow_chart/ui/tabs/includes/dynamic_tabbar.dart';
//import 'package:flutter_flow_chart/ui/flow_sketcher/main_flowchart.dart';

class TabBox extends StatefulWidget {
  final String title;
  final List<TabData> tabs;
  //final Widget flowSketcher;

  const TabBox({super.key, required this.title, required this.tabs});

  @override
  State<TabBox> createState() => _TabBoxState();
}

class _TabBoxState extends State<TabBox> {
  bool isScrollable = true;
  bool showNextIcon = true;
  bool showBackIcon = true;

  // Leading icon
  Widget? leading;

  // Trailing icon
  Widget? trailing;

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return DynamicTabBarWidget(
      dynamicTabs: widget.tabs,
      // optional properties :-----------------------------
      isScrollable: isScrollable,
      onTabControllerUpdated: (controller) {
        debugPrint("onTabControllerUpdated");
      },
      onTabChanged: (index) {
        debugPrint("Tab changed: $index");
      },
      onAddTabMoveTo: MoveToTab.last,
      // backIcon: Icon(Icons.keyboard_double_arrow_left),
      // nextIcon: Icon(Icons.keyboard_double_arrow_right),
      showBackIcon: showBackIcon,
      showNextIcon: showNextIcon,
      leading: leading,
      trailing: trailing,
    );
  }

  void addTab(Widget tabWidget) {
    setState(() {
      var tabNumber = widget.tabs.length + 1;
      widget.tabs.add(
        TabData(
          index: tabNumber,
          title: Tab(
            child: Text('Tab $tabNumber'),
          ),
          content: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Expanded(
                child: tabWidget,
              ),
              //Text('Dynamic Tab $tabNumber'),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => removeTab(tabNumber - 1),
                child: const Text('Remove this Tab'),
              ),
            ],
          ),
        ),
      );
    });
  }

  void removeTab(int id) {
    setState(() {
      widget.tabs.removeAt(id);
    });
  }

  void addLeadingWidget() {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
      content: Text(
          'Adding Icon button Widget \nYou can add any customized widget)'),
    ));

    setState(() {
      leading = Tooltip(
        message: 'Add your desired Leading widget here',
        child: IconButton(
          onPressed: () {},
          icon: const Icon(Icons.more_horiz_rounded),
        ),
      );
    });
  }

  void removeLeadingWidget() {
    setState(() {
      leading = null;
    });
  }

  void addTrailingWidget() {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
      content: Text(
          'Adding Icon button Widget \nYou can add any customized widget)'),
    ));

    setState(() {
      trailing = Tooltip(
        message: 'Add your desired Trailing widget here',
        child: IconButton(
          onPressed: () {},
          icon: const Icon(Icons.more_horiz_rounded),
        ),
      );
    });
  }

  void removeTrailingWidget() {
    setState(() {
      trailing = null;
    });
  }
}

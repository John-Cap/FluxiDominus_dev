
  // /// Display a drop down menu when tapping on an element
  // void _displayElementMenu(
  //     BuildContext context, Offset position, FlowElement element) {
  //   StarMenuOverlay.displayStarMenu(
  //     context,
  //     StarMenu(
  //       params: StarMenuParameters(
  //         shape: MenuShape.linear,
  //         openDurationMs: 60,
  //         linearShapeParams: const LinearShapeParams(
  //           angle: 270,
  //           alignment: LinearAlignment.left,
  //           space: 10,
  //         ),
  //         onHoverScale: 1.1,
  //         centerOffset: position - const Offset(50, 0),
  //         backgroundParams: const BackgroundParams(
  //           backgroundColor: Colors.transparent,
  //         ),
  //         boundaryBackground: BoundaryBackground(
  //           padding: const EdgeInsets.all(16),
  //           decoration: BoxDecoration(
  //             borderRadius: BorderRadius.circular(8),
  //             color: Theme.of(context).cardColor,
  //             boxShadow: kElevationToShadow[6],
  //           ),
  //         ),
  //       ),
  //       onItemTapped: (index, controller) {
  //         if (!(index == 5 || index == 2)) {
  //           controller.closeMenu!();
  //         }
  //       },
  //       items: [
  //         Text(
  //           element.text,
  //           style: const TextStyle(fontWeight: FontWeight.w900),
  //         ),
  //         InkWell(
  //           onTap: () {
  //             widget.dashboard.removeElement(element);
  //             _updateConnections();
  //           },
  //           child: const Text('Delete'),
  //         ),
  //         TextMenu(element: element),
  //         InkWell(
  //           onTap: () {
  //             widget.dashboard.removeElementConnections(element);
  //             _updateConnections();
  //           },
  //           child: const Text('Remove all connections'),
  //         ),
  //         InkWell(
  //           onTap: () {
  //             widget.dashboard.setElementResizable(element, true);
  //           },
  //           child: const Text('Resize'),
  //         ),
  //         ElementSettingsMenu(element: element),
  //       ],
  //       parentContext: context,
  //     ),
  //   );
  // }

//Data queue function pointers

import 'package:flutter/material.dart';
//import 'package:flutter_flow_chart/ui/graphing/graph_panel.dart';

abstract class DataQueueHandlers {
  static dynamic getValueFromAddress(
      Map<String, dynamic> data, List<String> address) {
    dynamic value = data;
    for (var key in address) {
      if (value is Map<String, dynamic> && value.containsKey(key)) {
        value = value[key];
      } else {
        return null;
      }
    }
    return value;
  }

  /*
    Hardcoded default addresses
  */
  //Flowsynmaxi Pressure pump A
  static const List<String> flowsynmaxiPressA = ["state", "pressFlowSynA"];
  static const List<String> flowsynmaxiPressB = ["state", "pressFlowSynB"];
  static const List<String> flowsynmaxiPressSys = ["state", "pressSystem"];
  static const List<String> hotcoilTemp = ["state", "temp"];

  static const Map<String, List<String>> valueAddresses = {
    "hotcoilTemp": hotcoilTemp,
    "flowsynmaxiPressA": flowsynmaxiPressA,
    "flowsynmaxiPressB": flowsynmaxiPressB,
    "flowsynmaxiPressSys": flowsynmaxiPressSys,
  };

  static List<String> getValAddress(String valName) {
    if (valueAddresses.containsKey(valName)) {
      List<String>? ret = valueAddresses[valName];
      if (ret != null) {
        return ret;
      } else {
        return [];
      }
    } else {
      return [];
    }
  }

  /*
    Hardcoded default handlers
  */
  //Flowsynmaxi Pressure pump A for graphWidget
  /*
  static Function queuePlotData = (
    Map<String, dynamic> kwargs,
  ) {
    double val = kwargs["val"];
    double seconds = kwargs["seconds"];
    List<PlotData> queue = kwargs["queue"];

    queue.add(PlotData(seconds, val));
  };
  */
}

/////////////////////////////////////////////////////////////////////
/*
    dataQueue contains queued data for a specific identifier.
    for example, {"GraphWidgets":{"GRAPH_UUID":List<someData>}}
*/
Map<String, ValueNotifier<Map<String, dynamic>>> dataQueue = {
  "GraphWidgets": ValueNotifier<Map<String, dynamic>>({"dataQueue": dataQueue})
};
/*
    Topic as key, with pointer to function explaining what to do with new data
*/
/*
final Map<String, List<dynamic>> dataQueueTopicsAndHandlers = {
  "subflow/hotcoil1/tele": [
    DataQueueHandlers.queuePlotData,
    {"dataQueue": dataQueue}
  ] //[pointer,kwargs]
};
*/
/////////////////////////////////////////////////////////////////////

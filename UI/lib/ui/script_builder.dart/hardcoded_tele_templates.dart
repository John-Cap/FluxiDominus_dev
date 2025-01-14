class HardcodedTeleKeys {
  static final Map<String, List<String>> devicesAndTheirTele = {
    "sf10vapourtec1": [
      "TODO"
    ], //Doesn't really have tele...essentially only an "OK" upon successful command received
    "sf10vapourtec2": [
      "TODO"
    ], //Doesn't really have tele...essentially only an "OK" upon successful command received
    "hotcoil1": ["temp"],
    "hotcoil2": ["temp"],
    "hotchip1": ["temp"],
    "hotchip2": ["temp"],
    "flowsynmaxi1": [
      "pressSystem",
      "pressFlowSynA",
      "pressFlowSynB",
      "tempReactor1",
      "tempReactor2",
      "valveOpenA",
      "valveOpenB",
      "valveOpenCW",
      "valveInjOpenA",
      "valveInjOpenB",
      "flowRatePumpA",
      "flowRatePumpB"
    ],
    "flowsynmaxi2": [
      "pressSystem",
      "pressFlowSynA",
      "pressFlowSynB",
      "tempReactor1",
      "tempReactor2",
      "valveOpenA",
      "valveOpenB",
      "valveOpenCW",
      "valveInjOpenA",
      "valveInjOpenB",
      "flowRatePumpA",
      "flowRatePumpB"
    ],
    "reactIR702L1": ["data"],
    "vapourtecR4P1700": [
      "flowRatePumpA",
      "flowRatePumpB",
      "pressPumpA",
      "pressPumpB",
      "pressSystem",
      "pressSystem2",
      "valveASR",
      "valveBSR",
      "valveAIL",
      "valveBIL",
      "valveWC",
      "tempReactor1",
      "tempReactor2",
      "tempReactor3",
      "tempReactor4"
    ],
  };

  static dynamic getTeleVal(Map<String, dynamic> input, String valName) {
    if (input.containsKey("tele")) {
      input = input["tele"];
      if (input.containsKey("state")) {
        input = input["state"];
        if (input.containsKey(valName)) {
          return input[valName];
        }
      }
    }
    return null;
  }
}

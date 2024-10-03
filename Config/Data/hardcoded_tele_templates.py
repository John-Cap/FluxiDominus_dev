class HardcodedTeleKeys:
    devicesAndTheirTele = {
        "sf10vapourtec1": ["TODO"],
        "sf10vapourtec2": ["TODO"],
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
    }

    @staticmethod
    def getTeleVal(inputDict, valName):
        if "tele" in inputDict:
            inputDict = inputDict["tele"]
            if "state" in inputDict:
                inputDict = inputDict["state"]
                return inputDict.get(valName, None)
        return None

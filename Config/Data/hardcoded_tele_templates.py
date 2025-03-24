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

if __name__ == "__main__":
    _msg={"deviceName": "hotcoil1", "deviceType": "Hotchip", "inUse": True, "remoteEnabled": False, "ipAddr": "192.168.1.213", "port": 81, "tele": {"cmnd": "POLL", "settings": {"temp": 0.1}, "state": {"temp": 17.83, "state": "ON"}, "timestamp": ""}}
    print(HardcodedTeleKeys.getTeleVal(_msg,"temp"))
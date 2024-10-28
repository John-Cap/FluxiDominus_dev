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
            print('Here 1')
            inputDict = inputDict["tele"]
            if "state" in inputDict:
                print('Here 2')
                inputDict = inputDict["state"]
                return inputDict.get(valName, None)
        
        print('Here 3')
        return None

if __name__ == "__main__":
    _msg={"deviceName": "vapourtecR4P1700", "deviceType": "PumpValveHeater", "inUse": True, "remoteEnabled": False, "connDetails": {"ipCom": {"addr": "192.168.1.53", "port": 43344}}, "tele": {"cmnd": "POLL", "cmndResp": "", "settings": {"valveASR": False, "valveBSR": False, "valveCSR": False, "valveDSR": False, "valveAIL": False, "valveBIL": False, "valveCIL": False, "valveDIL": False, "valveWC": False, "flowRatePumpA": 0.0, "flowRatePumpB": 0.0, "flowRatePumpC": 0.0, "flowRatePumpD": 0.0, "pressSystem": 0.0, "pressPumpA": 0.0, "pressPumpB": 0.0, "pressSystem2": 0.0, "pressPumpC": 0.0, "pressPumpD": 0.0, "tempReactor1": 0.0, "tempReactor2": 0.0, "tempReactor3": 0.0, "tempReactor4": 0.0}, "state": {"valveASR": False, "valveBSR": False, "valveCSR": False, "valveDSR": False, "valveAIL": False, "valveBIL": False, "valveCIL": False, "valveDIL": False, "valveWC": False, "flowRatePumpA": 0, "flowRatePumpB": 0, "flowRatePumpC": 0, "flowRatePumpD": 0, "pressSystem": 0.03999999910593033, "pressPumpA": 0.25, "pressPumpB": 0.3400000035762787, "pressSystem2": 0.0, "pressPumpC": 0.0, "pressPumpD": 0.0, "tempReactor1": -100.0, "tempReactor2": -100.0, "tempReactor3": -100.0, "tempReactor4": -100.0}, "timestamp": ""}}
    print(HardcodedTeleKeys.getTeleVal(_msg,"pressPumpA"))
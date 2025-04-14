from Core.Fluids.FlowPath import FlowPath


class FromUI:

    widgetRequests = {
        "FormPanelWidget":{},
        "FlowSketcher":{
            "parseFlowsketch":FlowPath.parseFlowSketch
        }
    }

    @staticmethod
    def widgetRequestVal(inputDict, valName):
        if "tele" in inputDict:
            inputDict = inputDict["tele"]
            if "state" in inputDict:
                inputDict = inputDict["state"]
                return inputDict.get(valName, None)
            
        return None

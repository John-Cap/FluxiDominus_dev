'''
self.streamRequestDetails[id]["labNotebookBaseRef"]=req["labNotebookBaseRef"]
self.streamRequestDetails[id]["runNr"]=req["runNr"]
self.streamRequestDetails[id]["timeWindow"]=req["timeWindow"]
self.streamRequestDetails[id]["nestedField"]=req["nestedField"]
self.streamRequestDetails[id]["nestedValue"]=req["nestedValue"]
self.streamRequestDetails[id]["deviceName"]=req["deviceName"]
self.streamRequestDetails[id]["setting"]=req["setting"]
'''
{
    'dbStreaming':{
        'myCoolId':{
            "id":"anEvenCoolerId",
            "labNotebookBaseRef":"WJ_TEST_12",
            "runNr":16,
            "timeWindow":30,
            "nestedField":"deviceName",
            "nestedValue":"A_BICYCLE_BUILT_FOR_TWO",
            "setting":"pressSys"
        }
    }
}
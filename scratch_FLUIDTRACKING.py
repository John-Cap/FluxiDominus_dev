
#################################
#Database operations example
from datetime import datetime
import random
import time

from Core.Data.database import DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService
'''
mqttService=MqttService(broker_address='146.64.91.174')
mqttService.start()
time.sleep(1)
mqttService.orgId="309930"
dbStream=DatabaseStreamer(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=mqttService)
dbStream.connect()
time.sleep(1)
dbStream.mongoDb.currZeroTime=datetime.now()
_i=15
while _i > 0:
    dbStream.handleStreamRequest(
        {
            "id":"anEvenCoolerId",
            "labNotebookBaseRef":"WJ_TEST_11",
            "runNr":0,
            "deviceName":"A_BICYCLE_BUILT_FOR_TWO",
            "timeWindow":10,
            "nestedField":"deviceName",
            "nestedValue":"A_BICYCLE_BUILT_FOR_TWO",
            "setting":"exampleSetting"
        }
    )
    _i-=1
    time.sleep(5)
'''
from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseOperations, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.Data.experiment import StandardExperiment
from Core.UI.plutter import MqttService

if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService()
    thisThing.start()
    thisThing.orgId="50403"
    #Instantiate
    dbOp=DatabaseOperations(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=thisThing)
    dbOp.connect()
    
    ##################################
    #MySql
    tests=dbOp.getUserRow(email='jdtoit@csir.co.za')
    print(tests)
    print("\n")
    
    tests=dbOp.getUserTests(email='jdtoit@csir.co.za')
    print(tests)
    print("\n")
    
    tests=dbOp.getTestRuns('50403_jdtoit_DSIP012A')
    print(tests)
    print("\n")
    
    tests=dbOp.getTestRuns('50403_jdtoit_PNDOS013A')
    print(tests)
    print("\n")
    
    tests=dbOp.assignProject(1,orgId=50403)
    print(tests)
    print("\n")
    
    tests=dbOp.assignProject('C1PPT53',email='jdtoit@csir.co.za')
    print(tests)
    print("\n")
        
    tests=dbOp.getUserProjects(orgId=50403)
    print(tests)
    print("\n")
        
    tests=dbOp.getProjCode(1)
    print(tests)
    print("\n")
        
    tests=dbOp.getAllExpWidgetInfo()
    print(tests)
    print("\n")

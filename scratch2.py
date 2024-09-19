import random
import time
from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseOperations, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService


if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService()
    thisThing.start()
    thisThing.orgId="309930"
    #Instantiate
    dbOp=DatabaseOperations(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=thisThing)
    dbOp.connect()
    
    ##################################
    #MySql
    tests=dbOp.getUserTests()
    print(tests)
    print("\n")
    #Get unique id of testlist entry
    thisTest=dbOp.getTestlistId("WJ_Disprin")
    print(thisTest)
    print("\n")
    #Get id's of all thisTest's replicate runs
    theseTests=dbOp.getReplicateIds("WJ_Disprin")
    print(theseTests)
    print('\n')
    dbOp.createReplicate("WJ_Disprin")
    theseTests=dbOp.getReplicateIds("WJ_Disprin")
    print(theseTests)
    print('\n')

    ##################################
    #Mongo

    testId=thisTest
    runId=dbOp.createReplicate("WJ_Disprin")
    labNotebookBaseRefs=["MY_REF_2","WJ_Disprin","ANOTHER_ONE"]
    devices=["FLOWSYNMAXI","OHM_DEVICE","A_BICYCLE_BUILT_FOR_TWO"]
    dataSet=[]
    print([testId,runId])
    _i=100
    while _i > 0:
        dataSet.append(DataPointFDE(testlistId=).toDict())
        _i-=1
    
    thisData=DataSetFDD(dataSet)
    dbOp.mongoDb.start("309930","WJ_Disprin")
    for _x in thisData.dataPoints:
        dbOp.mongoDb.insertDataPoint(_x)
        time.sleep(3)
    dbOp.mongoDb.pauseInsertion=True
    print(dbOp.mongoDb.fetchTimeSeriesData(orgId="309930",labNotebookBaseRef="MY_REF_2"))
    dbOp.mongoDb.kill()

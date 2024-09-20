from datetime import datetime
import random
import time

from bson import utc
from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseOperations, MySQLDatabase, TimeSeriesDatabaseMongo
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
    '''
    tests=dbOp.getUserTests()
    print(tests)
    print("\n")
    #Get unique id of testlist entry
    thisTest=dbOp.getTestlistId("WJ_Disprin")
    print(thisTest)
    print("\n")
    #Get id's of all thisTest's replicate runs
    theseTests=dbOp.getReplicateIds("50403_jdtoit_DSIP012A")
    print(theseTests)
    print('\n') #[116, 120, 121, 124, 131] #[118, 122, 123, 127, 128, 129, 130]
  
    #dbOp.createReplicate("WJ_Disprin")
    theseTests=dbOp.getReplicateIds("50403_jdtoit_DSIP013A")
    print(theseTests)
    print('\n')
    '''
    ##################################
    #Mongo
    _yeahNow=datetime.now(utc)
    time.sleep(2)
    dbOp.mongoDb.prevZeroTime=_yeahNow
    dbOp.mongoDb.currZeroTime=datetime.now(utc)
    for x in [116,120,118,122]:
        dbOp.mySqlDb.updateRecordById('testruns',x,'startTime',_yeahNow)
    dataSet=[]
    _i=50
    while _i > 0:
        _tstlstId=random.choice([296,298])
        if _tstlstId==296:
            dataSet.append(
                DataPointFDE(
                    testlistId=_tstlstId,
                    testrunId=random.choice([116,120]),
                    data={"meemah":"123","anotherField":{"aNestedField":1}},
                    timestamp=datetime.now(utc)
                ).toDict()
            )
        else:
            dataSet.append(
                DataPointFDE(
                    testlistId=_tstlstId,
                    testrunId=random.choice([118,122]),
                    data={"meemah":"123","anotherField":{"aNestedField":1}},
                    timestamp=datetime.now(utc)
                ).toDict()
            )
        _i-=1
        
    
    thisData=DataSetFDD(dataSet)
    #dbOp.mongoDb.start("309930","WJ_Disprin")
    for _x in thisData.dataPoints:
        dbOp.mongoDb.insertDataPoint(_x)
        time.sleep(0.25)
        
    _yeahNow2=datetime.now(utc)

    for x in [116,120,118,122]:
        dbOp.mySqlDb.updateRecordById('testruns',x,'endTime',_yeahNow2)
    dbOp.mongoDb.prevStopTime=_yeahNow2
    #print(dbOp.mongoDb.streamTimeBracket(timeWindowInSeconds=15,testlistId=298,testrunId=122))
    print(
        dbOp.mongoDb.fetchTimeSeriesData(
            testlistId=298,
            testrunId=122,
            #nestedField='data.anotherField.aNestedField',
            #nestedValue=1,
            startTime=_yeahNow,
            endTime=datetime.now(utc)
            #startTime=_yeahNow,
            #endTime=_yeahNow2
        )
    )
    dbOp.mongoDb.kill()

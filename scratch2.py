from datetime import datetime
import random
import time
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
    '''
    _yeahNow=datetime.now()
    dataSet=[]
    _i=50
    while _i > 0:
        _tstlstId=random.choice([296,298])
        if _tstlstId==296:
            dataSet.append(
                DataPointFDE(
                    testlistId=_tstlstId,
                    testrunId=random.choice([116,120]),
                    data={"meemah":"123","anotherField":{"aNestedField":1}}
                ).toDict())    
        else:
            dataSet.append(
                DataPointFDE(
                    testlistId=_tstlstId,
                    testrunId=random.choice([118,122]),
                    data={"meemah":"123","anotherField":{"aNestedField":1}}
                ).toDict())
        _i-=1
        
    
    thisData=DataSetFDD(dataSet)
    #dbOp.mongoDb.start("309930","WJ_Disprin")
    for _x in thisData.dataPoints:
        dbOp.mongoDb.insertDataPoint(_x)
        time.sleep(0.25)
    _yeahNow2=datetime.now()
    '''
    #print(dbOp.mongoDb.streamData(timeWindowInSeconds=120,testId=296))
    print(dbOp.mongoDb.fetchTimeSeriesData(testlistId=298,testrunId=122))
    dbOp.mongoDb.kill()

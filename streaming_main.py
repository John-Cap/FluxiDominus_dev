from datetime import datetime, timedelta
import random
import time

from bson import utc
import bson
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
    timestamp_1='2024-09-26T04:21:53.485144'
    timestamp_1=datetime.fromisoformat(timestamp_1)
    dbOp.setZeroTime(120,timestamp_1)
    #dbOp.mongoDb.prevZeroTime=timestamp_1
    '''
    for x in [116,120,118,122]:
        dbOp.mySqlDb.updateRecordById('testruns',x,'startTime',timestamp_1)
    dataSet=[]
    _i=50
    while _i > 0:
        _tstlstId=random.choice([296])

        dataSet.append(
            DataPointFDE(
                testlistId=_tstlstId,
                testrunId=random.choice([116,120]),
                data={
                    'deviceName':random.choice(['flowsynmaxi2','aCoolDevice']),
                    'settings':{'someSettings':[1,2,3]},
                    'state':{
                        'theAbsoluteStateOfThisPlace':'dorty'
                    }
                },
                timestamp=timestamp_1
            ).toDict()
        )
        timestamp_1 = timestamp_1 + timedelta(seconds=random.choice([2,3,7]))
        _i-=1
        
    
    thisData=DataSetFDD(dataSet)
    for _x in thisData.dataPoints:
        dbOp.mongoDb.insertDataPoint(_x)
    '''
    timestamp_2=timestamp_1 + timedelta(seconds=4000)

    print((timestamp_2 - timestamp_1).total_seconds())

    dbOp.setStopTime(120,timestamp_2)
    
    dbOp.mongoDb.currZeroTime=datetime.now(tz=utc)
    dbOp.setStreamingBracket(labNotebookBaseRef=(dbOp.mySqlDb.fetchColumnValById(tableName='testruns',columnName='labNotebookBaseRef',id=120)),runNr=1)
    #print(dbOp.mongoDb.streamData(now=timestamp_2,timeWindowInSeconds=100,testlistId=296,testrunId=120))
    dbOp.mongoDb.streamTimeBracket(now=dbOp.mongoDb.currZeroTime,timeWindowInSeconds=1000,testlistId=296,testrunId=120,nestedField='data.deviceName',nestedValue='flowsynmaxi2')
    '''
    {
        "id":"123",
        "labNotebookBaseRef":"50403_jdtoit_DSIP012A",
        "runNr":0,
        "timeWindow":30,
        "nestedField":None,
        "nestedValue":None,
        "deviceName":"flowsynmaxi2",
        "setting":"pafr"
    }
    '''
    dbOp.mongoDb.kill()

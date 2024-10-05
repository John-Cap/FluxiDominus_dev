from datetime import datetime, timedelta
import random
import time

from bson import utc
import bson
from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseOperations, DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService


if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService()
    thisThing.start()
    thisThing.orgId="50403"
    #Instantiate
    #dbOp=DatabaseOperations(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=thisThing)
    dbOp=DatabaseStreamer(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=thisThing)
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
    ##timestamp_1='2024-09-26T04:21:53.485144'
    ##timestamp_1=datetime.fromisoformat(timestamp_1)
    ##dbOp.setZeroTime(120,timestamp_1)
    
    '''
    dataSet=[]
    _i=60
    while _i > 0:
        _tstlstId=random.choice([
            296
        ])
        timestamp_1 = timestamp_1 + timedelta(seconds=random.choice([1]))
        dataSet.append(
            DataPointFDE(
                testlistId=_tstlstId,
                testrunId=random.choice([
                    120
                ]),
                data={
                    'deviceName':random.choice(['flowsynmaxi2']),
                    'settings':{'someSettings':[
                        1,
                        2,
                        3
                    ]},
                    'state':{
                        'pressFlowSynA':random.choice([1,2,3])
                    }
                },
                timestamp=timestamp_1
            ).toDict()
        )
        _i-=1
        
    timestamp_1 = timestamp_1 + timedelta(seconds=random.choice([1]))    
    thisData=DataSetFDD(
        dataSet
    )
    for _x in thisData.dataPoints:
        dbOp.mongoDb.insertDataPoint(_x)
        
    '''
        
    ##dbOp.setStopTime(120,timestamp_1)
    
    dbOp.mongoDb.currZeroTime=datetime.now()
    dbOp.setZeroTime()
    dbOp.setStreamingBracket(labNotebookBaseRef=(dbOp.mySqlDb.fetchColumnValById(tableName='testruns',columnName='labNotebookBaseRef',id=296)),runNr=6)

    time.sleep(1)
    '''
    Message from Flutter
    '''
    print(
        dbOp.handleStreamRequest(
            {
                "id":"120A3",
                "labNotebookBaseRef":"50403_jdtoit_DSIP012A_7",
                "runNr":7,
                "timeWindow":25, #Get all desired datapoints from now to 45 seconds in future
                "deviceName":"flowsynmaxi2",
                "setting":"pressA"
            }
        )
    )
    
    dbOp.mongoDb.kill()

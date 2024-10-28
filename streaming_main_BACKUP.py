from datetime import datetime, timedelta
import random
import time

import bson
from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseOperations, DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService


if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService(broker_address='146.64.91.174')
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
    #dbOp.setStreamingBracket(labNotebookBaseRef="50403_jdtoit_DSIP012A",runNr=11)
    #self.currTestrunId and self.currTestlistId and self.logData
    thisThing.currTestlistId=296
    thisThing.currTestrunId=143
    #thisThing.logData=True
    time.sleep(1)
    dbOp.mongoDb.fetchTimeSeriesData(296,139,startTime=(datetime.fromisoformat('2024-10-09T06:58:12.001+00:00')),endTime=(datetime.fromisoformat('2024-10-09T06:59:12.001+00:00')),nestedField='data.deviceName',nestedValue='flowsynmaxi2')
    print('\n')
    time.sleep(1)
    dbOp.mongoDb.prevZeroTime=(datetime.fromisoformat('2024-10-09T06:57:12.001+00:00'))
    dbOp.mongoDb.streamTimeBracket(296,139,timeWindowInSeconds=120,nestedField='data.deviceName',nestedValue='flowsynmaxi2')
    
    '''
    Message from Flutter
    '''    
    print(
        dbOp.handleStreamRequest(
            {
                "id":"120A3",
                "labNotebookBaseRef":"50403_jdtoit_DSIP012A",
                "runNr":16,
                "timeWindow":1200, #Get all desired datapoints from now to 45 seconds in future
                "deviceName":"hotcoil1",
                "setting":'temp'
            }
        )
    )

    time.sleep(15)
    
    dbOp.mongoDb.kill()

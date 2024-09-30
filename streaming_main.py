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
        
    dbOp.mongoDb.currZeroTime=datetime.now()
    #dbOp.setStreamingBracket(labNotebookBaseRef=(dbOp.mySqlDb.fetchColumnValById(tableName='testruns',columnName='labNotebookBaseRef',id=120)),runNr=1)

    _now=time.time()
    
    '''
    Message from Flutter
    '''
    while (time.time() - _now)<60:
        dbOp.handleStreamRequest(
            {
                "id":"120A3",
                "labNotebookBaseRef":"50403_jdtoit_DSIP012A",
                "runNr":1,
                "timeWindow":6, #Get all desired datapoints from now to 45 seconds in future
                "deviceName":"flowsynmaxi2",
                "setting":"pressA"
            }
        )
        time.sleep(5)
    dbOp.mongoDb.kill()

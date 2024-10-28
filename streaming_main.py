from datetime import datetime
import time

from Core.Data.database import DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
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
    
    ''' "ui/dbCmnd/in"
    Message from Flutter:
    {
        "instructions":{
            "function":"handleStreamRequest",
            "params":{
                "id":"120A3",
                "labNotebookBaseRef":"50403_jdtoit_DSIP012A",
                "runNr":1,
                "timeWindow":6,
                "deviceName":"hotcoil1",
                "setting":"pressA"
            }
        }
    }
    '''
    while (time.time() - _now)<60:
        dbOp.handleStreamRequest(
            {
                "id":"120A3",
                "labNotebookBaseRef":"50403_jdtoit_DSIP012A",
                "runNr":6,
                "timeWindow":60,
                "deviceName":"hotcoil1",
                "setting":"temp"
            }
        )
        time.sleep(5)
    dbOp.mongoDb.kill()

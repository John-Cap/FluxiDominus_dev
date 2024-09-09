
from datetime import datetime
from time import sleep
import time
from Core.Data.database import DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService

mqttService=MqttService()
mqttService.start()

sleep(2)

dbStrmr=DatabaseStreamer(
    mySqlDb=MySQLDatabase(host='146.64.91.174'),
    mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),
    mqttService=mqttService
)

dbStrmr.connect()

sleep(1)

dbStrmr.setStreamingBracket(labNotebookBaseRef='WJ_TEST_11',runNr=1)
dbStrmr.mongoDb.currZeroTime=datetime.now()

#print(dbStrmr.mongoDb.prevZeroTime)

print(dbStrmr.streamToMqtt(id="thisId1234",labNotebookBaseRef='WJ_TEST_11',runNr=1,timeWindow=10,nestedField='deviceName',nestedValue='A_BICYCLE_BUILT_FOR_TWO'))
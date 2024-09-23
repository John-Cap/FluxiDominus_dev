
from Core.Data.database import DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService

mqttService=MqttService().start()
dbStrmr=DatabaseStreamer(
    mySqlDb=MySQLDatabase(host='146.64.91.174'),
    mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),
    mqttService=mqttService
)

print(dbStrmr.streamToMqtt(labNotebookBaseRef='WJ_TEST_12',runNr=0,timeWindow=30))
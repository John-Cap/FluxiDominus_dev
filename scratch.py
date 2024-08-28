
from Core.Data.database import DatabaseOperations, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService

mqttService=MqttService(broker_address='146.64.91.174')
mqttService.start()
dbOps=DatabaseOperations(mqttService=mqttService,mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mySqlDb=MySQLDatabase(host='146.64.91.174'))

dbOps.connect()

print(dbOps.fetchStreamingBracket('WJ_TEST_11',0))
print(dbOps.fetchStreamingBracket('WJ_TEST_10',1))
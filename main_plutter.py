from datetime import datetime
from Core.Data.database import DatabaseOperations, DatabaseStreamer, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.UI.plutter import MqttService


if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService()
    thisThing.start()
    thisThing.orgId="50403"
    #Instantiate
    mySqlDb=MySQLDatabase(host='146.64.91.174')
    mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174')

    dbStreaming=DatabaseStreamer(mySqlDb=mySqlDb,mongoDb=mongoDb,mqttService=thisThing)
    dbStreaming.connect()
    dbStreaming.mongoDb.currZeroTime=datetime.now()
    dbStreaming.handleStreamRequest(
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
    )
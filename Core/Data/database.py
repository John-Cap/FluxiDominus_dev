
import mysql.connector
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import threading

from Core.Data.experiment import StandardExperiment

class Database:
    def __init__(self) -> None:
        pass

class MySQLDatabase:
    def __init__(self, host='localhost',port=3306,user="pharma",password="pharma",database="pharma"):
        """Initialize the MySQLDatabase class with connection parameters."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
        self.tableVar={
            "users":['orgId', 'lastLogin', 'firstName', 'lastName'],
            "testlist":['nameTest', 'description', 'nameTester', 'fumehoodId', 'testScript', 'lockScript', 'flowScript', 'datetimeCreate', 'labNotebookRef', 'orgId'],
            "testruns":['testlistId', 'createTime', 'startTime', 'stopTime', 'recorded','labNotebookRef','runNr']
        } #hardcoded

    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print("Connected to the database.")
        except OSError as e:
            print(f"WJ - Database connection error: {e}")
            self.connection = None

    def createTable(self, tableName, schema):
        """Create a table with the given schema."""
        if self.cursor:
            createTableQuery = f"""
            CREATE TABLE IF NOT EXISTS {tableName} (
                {schema}
            )
            """
            self.cursor.execute(createTableQuery)
            print(f"Table '{tableName}' created successfully.")

    def insertRecords(self, tableName, records):
        """Insert multiple records into the specified table."""
        if self.cursor:
            columns=self.tableVar[tableName]
            insertQuery = f"""
            INSERT INTO {tableName} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
            """
            self.cursor.executemany(insertQuery, records)
            self.connection.commit()
            print(f"Records inserted successfully into '{tableName}'.")

    def fetchRecords(self, tableName):# WHERE id=%s
        """Fetch all records from the specified table."""
        if self.cursor:
            fetchQuery = f"SELECT * FROM {tableName}"
            self.cursor.execute(fetchQuery)
            results = self.cursor.fetchall()
            return results

    def fetchRecordByColumnValue(self, tableName, columnName, value):
        """Fetch a single record from the specified table where the column matches the given value."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {columnName} = %s"
            self.cursor.execute(fetch_query, (value,))
            result = self.cursor.fetchone()  # fetchone returns a single matching row
            return result

    def fetchRecordsByColumnValue(self, tableName, columnName, value):
        """Fetch all records from the specified table where the column matches the given value."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {columnName} = %s"
            self.cursor.execute(fetch_query, (value,))
            result = self.cursor.fetchall()
            return result
                
    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")

class TimeSeriesDatabaseMongo:
    def __init__(self, host='localhost', port=27017, databaseName="Pharma", collectionName="pharma-data"):
        #self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.client = MongoClient(host=host,port=port)
        self.db = self.client[databaseName]
        self.collection = self.db[collectionName]
        self.dataPoints=[]
        self.insertionInterval=10
        self.pauseInsertion=True
        self.pauseFetching=True
        self.insertionThread=None
        self.fetchingThread=None
        
        self.currZeroTime=None

    def insertDataPoint(self,dataPoint):
        dataPoint["timestamp"]=datetime.now()
        self.collection.insert_one(dataPoint)
        #print(f"Inserted data point: {dataPoint}")

    def continuousInsertion(self):
        while True:
            while self.pauseInsertion:
                time.sleep(0.1)
            if self.dataPoints is None or len(self.dataPoints)==0:
                pass
            else:
                _numOf=len(self.dataPoints)
                for _x in self.dataPoints:
                    self.insertDataPoint(_x)
                self.dataPoints=[]
                print('WJ - Inserted '+str(_numOf)+' datapoints into database '+str(self.db)+'!')
            time.sleep(self.insertionInterval) #Kannie so lank hier wag nie

    def fetchTimeSeriesData(self, testId, runNr=0, startTime: datetime = None, endTime: datetime = None):
        # Prepare the query with required filters
        query = {
            'testId': testId,
            'runNr': runNr
        }

        # Add time filtering to the query if provided
        if startTime and endTime:
            query['timestamp'] = {'$gte': startTime, '$lte': endTime}

        # Fetch and sort the data
        cursor = self.collection.find(query).sort('timestamp', 1)
        _ret = []
        _num = 0
        for document in cursor:
            _ret.append(document)
            _num += 1

        print(f'Fetched {_num} documents for experiment {testId} from {startTime} to {endTime}!')
        return _ret

    def streamData(self, timeWindowInSeconds, testId, runNr=0, now=None):
        if now is None:
            now = datetime.now()

        if timeWindowInSeconds < 0:  # into past
            endTime = now
            startTime = max(now - timedelta(seconds=abs(timeWindowInSeconds)), self.currZeroTime)
        else:  # into future
            startTime = now
            endTime = now + timedelta(seconds=timeWindowInSeconds)

        return self.fetchTimeSeriesData(testId=testId, runNr=runNr, startTime=startTime, endTime=endTime)

    def streamComparisonData(self, currentTestId, previousTestId, timeWindowInSeconds, currentRunNr=0, previousRunNr=0, now=None):
        if now is None:
            now = datetime.now()

        # Calculate elapsed time since the start of the current experiment
        elapsedTime = (now - self.currZeroTime).total_seconds()

        # Calculate the corresponding start and end times for the previous experiment
        prevStartTime = self.prevZeroTime + timedelta(seconds=elapsedTime)
        prevEndTime = prevStartTime + timedelta(seconds=timeWindowInSeconds)

        # Fetch data for the current experiment
        currentData = self.streamData(timeWindowInSeconds, currentTestId, runNr=currentRunNr, now=now)

        # Fetch data for the previous experiment using the mapped times
        previousData = self.fetchTimeSeriesData(testId=previousTestId, runNr=previousRunNr, startTime=prevStartTime, endTime=prevEndTime)

        return currentData, previousData

    def continuousFetching(self, **kwargs):
        orgId = kwargs.get('orgId')
        labNotebookRef = kwargs.get('labNotebookRef')
        try:
            while not self.pauseFetching:
                self.fetchTimeSeriesData(orgId,labNotebookRef)
                time.sleep(6)  # Fetch data every 10 seconds
        except KeyboardInterrupt:
            print("Stopped fetching data.")

    def kill(self):
        self.pauseInsertion=True
        self.pauseFetching=True

    def pause(self):
        self.pauseInsertion=True
        self.pauseFetching=True

    def purgeAndPause(self):
        self.dataPoints=[] #What happens if updater still wants to add some datapoints?
        self.pause()

    def start(self,orgId: str,labNotebookRef: str,runId=0):
        kwargs={"orgId":orgId,"labNotebookRef":labNotebookRef,"runId":runId}
        if not (self.insertionThread is None):
            self.pauseInsertion=False
        else:
            
            insertion_thread = threading.Thread(target=self.continuousInsertion)
            fetching_thread = threading.Thread(target=self.continuousFetching,kwargs=kwargs)
            self.pauseInsertion = False
            self.pauseFetching = False

            insertion_thread.start()
            fetching_thread.start()

            #insertion_thread.join()
            #fetching_thread.join()
            
            self.insertionThread=insertion_thread
            self.fetchingThread=fetching_thread
                        
#################################
#Main class to interface with both db's

class DatabaseOperations:
    def __init__(self,mySqlDb=MySQLDatabase(),mongoDb=TimeSeriesDatabaseMongo(),mqttService=None) -> None:
        self.mySqlDb=mySqlDb
        self.mongoDb=mongoDb
        
        self.mqttService=mqttService

    def createStdExp(self,labNotebookRef,nameTest="Short description",description="Long description",flowScript={},testScript=b"script_content"):
        return (StandardExperiment(self.mySqlDb,tables=["testlist"])).createExperiment(
            nameTest=nameTest,
            nameTester="",
            lockScript=0,
            flowScript=flowScript,
            description=description,
            testScript=testScript,
            datetimeCreate=datetime.now(),
            labNotebookRef=labNotebookRef,
            orgId=self.mqttService.orgId
        )

    def connect(self):
        self.mySqlDb.connect()
        self.mongoDb.purgeAndPause() #Good idea? :/
        
    def getTestlistId(self,labNotebookRef,tableName='testlist',columnName='labNotebookRef'):
        return (self.mySqlDb.fetchRecordByColumnValue(tableName,columnName,labNotebookRef)[0])
                
    def getUserTests(self, tableName='testlist', columnName='orgId'):
        return self.mySqlDb.fetchRecordsByColumnValue(tableName,columnName,self.mqttService.orgId)
        
    def searchForTest(self, labNotebookRef, tableName='testlist', columnName='labNotebookRef'):
        return self.mySqlDb.fetchRecordByColumnValue(tableName,columnName,labNotebookRef)

    def getReplicateIds(self, labNotebookRef, tableName='testlist', columnName='labNotebookRef'):
        testListId=self.getTestlistId(labNotebookRef,tableName,columnName)
        replicates=self.mySqlDb.fetchRecordsByColumnValue('testruns','testlistId',testListId)
        ret=[]
        for _x in replicates:
            ret.append(_x[0])
        return ret

    def getRunNrs(self, labNotebookRef, tableName='testlist', columnName='labNotebookRef'):
        replicates=self.getReplicateIds(labNotebookRef,tableName,columnName)
        ret=[]
        for _x in replicates:
            ret.append(self.mySqlDb.fetchRecordByColumnValue('testruns','id',_x)[-1])
        return ret

    def createReplicate(self, labNotebookRef, tableName='testlist', columnName='labNotebookRef'):
        testListId=self.getTestlistId(labNotebookRef,tableName,columnName)
        replicates=self.getRunNrs(labNotebookRef) #Error handling!
        idNext=-1
        if (len(replicates)==0):
            idNext=0
        else:
            idNext=replicates[-1] + 1
        insert=[(testListId,datetime.now(),datetime.now(),datetime.now(),0,labNotebookRef,idNext)] #['testlistId', 'createTime', 'startTime', 'stopTime', 'recorded','labNotebookRef','runNr']
        self.mySqlDb.insertRecords('testruns',insert)
        return idNext

#################################
#Database operations example
'''
if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService()
    thisThing.start()
    thisThing.orgId="309930"
    #Instantiate
    dbOp=DatabaseOperations(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=thisThing)
    dbOp.connect()
    
    ##################################
    #MySql
    tests=dbOp.getUserTests()
    print(tests)
    print("\n")
    #Get unique id of testlist entry
    thisTest=dbOp.getTestlistId("WJ_Disprin")
    print(thisTest)
    print("\n")
    #Get id's of all thisTest's replicate runs
    theseTests=dbOp.getReplicateIds("WJ_Disprin")
    print(theseTests)
    print('\n')
    dbOp.createReplicate("WJ_Disprin")
    theseTests=dbOp.getReplicateIds("WJ_Disprin")
    print(theseTests)
    print('\n')
    ##################################
    #Mongo

    testId=thisTest
    runId=dbOp.createReplicate("WJ_Disprin")
    labNotebookRefs=["MY_REF_2","WJ_Disprin","ANOTHER_ONE"]
    devices=["FLOWSYNMAXI","OHM_DEVICE","A_BICYCLE_BUILT_FOR_TWO"]
    dataSet=[]
    print([testId,runId])
    _i=100
    while _i > 0:
        dataSet.append(DataPointFDE(
            orgId="309930",
            testId=testId,
            runNr=runId,
            labNotebookRef=(random.choice(labNotebookRefs)),
            deviceName=(random.choice(devices)),
            data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
            metadata={"location": "Room 101"}
        ).toDict())
        _i-=1
    
    thisData=DataSetFDD(dataSet)
    dbOp.mongoDb.start("309930","WJ_Disprin")
    for _x in thisData.dataPoints:
        dbOp.mongoDb.insertDataPoint(_x)
        time.sleep(3)
    dbOp.mongoDb.pauseInsertion=True
    print(dbOp.mongoDb.fetchTimeSeriesData(orgId="309930",labNotebookRef="MY_REF_2"))
    dbOp.mongoDb.kill()
'''
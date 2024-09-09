
import json
import mysql.connector
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import threading

from Config.Data.hardcoded_command_templates import HardcodedTeleAddresses
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
    
    def updateRecordById(self, tableName, uniqueId, columnName, newValue):
        """Update a specific column's value in a row identified by a unique ID."""
        if self.cursor:
            # Prepare the SQL query to update the specific column in the table.
            updateQuery = f"""
            UPDATE {tableName}
            SET {columnName} = %s
            WHERE id = %s
            """
            # Execute the query with the provided newValue and uniqueId
            self.cursor.execute(updateQuery, (newValue, uniqueId))
            # Commit the transaction to the database
            self.connection.commit()
            print(f"Record with ID {uniqueId} updated successfully in '{tableName}'.")

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
        
    def fetchRecordByColumnValues(self, tableName, column1Name, value1, column2Name, value2):
        """Fetch a single record from the specified table where two columns match the given values."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {column1Name} = %s AND {column2Name} = %s"
            self.cursor.execute(fetch_query, (value1, value2))
            result = self.cursor.fetchone()  # fetchone returns a single matching row
            return result
        
    def fetchSpecifiedColumnsByValues(self, tableName, columnNames, column1Name, value1, column2Name, value2):
        """Fetch specified columns from a table where two columns match the given values."""
        if self.cursor:
            # Join the list of column names into a single string separated by commas
            columns = ", ".join(columnNames)
            fetch_query = f"SELECT {columns} FROM {tableName} WHERE {column1Name} = %s AND {column2Name} = %s"
            self.cursor.execute(fetch_query, (value1, value2))
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
        self.prevZeroTime=None
        
        self.currStopTime=None
        self.prevStopTime=None

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

    def fetchTimeSeriesData(self, testId, runNr=0, startTime: datetime = None, endTime: datetime = None, nestedField: str = None, nestedValue=None):
        # Prepare the query with required filters
        query = {
            'testId': testId,
            'runNr': runNr
        }

        # Add time filtering to the query if provided
        if startTime and endTime: 
            query['timestamp'] = {'$gte': startTime, '$lte': endTime}

        # Add nested field filtering if provided
        if (nestedField and nestedValue): #Include 'field':value requirement to search
            query[nestedField] = nestedValue
        elif nestedField:
            query[nestedField] = {'$exists': True} #Fetch if nested field exists regardless of value
        # Fetch and sort the data
        cursor = self.collection.find(query).sort('timestamp', 1)
        _ret = []
        _num = 0
        for document in cursor:
            _ret.append(document)
            _num += 1

        # Uncomment the line below to print the number of fetched documents
        print(f'Fetched {_num} documents for experiment {testId} from {startTime} to {endTime} with nested field {nestedField} = {nestedValue}!')
        return _ret
    
    def streamData(self, timeWindowInSeconds, testId, runNr=0, now=None, nestedField: str = None, nestedValue=None):
        if now is None:
            now = datetime.now()

        if timeWindowInSeconds < 0:  # into past
            endTime = now
            startTime = max(now - timedelta(seconds=abs(timeWindowInSeconds)), self.currZeroTime)
        else:  # into future
            startTime = now
            endTime = now + timedelta(seconds=timeWindowInSeconds) #Must also check if 'endTime' is within time bracket

        return self.fetchTimeSeriesData(testId=testId, runNr=runNr, startTime=startTime, endTime=endTime, nestedField=nestedField, nestedValue=nestedValue)

    def streamTimeBracket(self, testId, timeWindowInSeconds=0, runNr=0, now=None, nestedField=None, nestedValue=None):
        if now is None:
            now = datetime.now()

        # Calculate elapsed time since the start of the current experiment
        elapsedTime = (now - self.currZeroTime).total_seconds()

        # Calculate the corresponding start and end times for the previous experiment
        prevStartTime = self.prevZeroTime + timedelta(seconds=elapsedTime)
        prevEndTime = prevStartTime + timedelta(seconds=timeWindowInSeconds)

        return self.fetchTimeSeriesData(testId=testId, runNr=runNr, startTime=prevStartTime, endTime=prevEndTime, nestedField=nestedField, nestedValue=nestedValue)

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

#Main
class DatabaseOperations:
    def __init__(self,mySqlDb=MySQLDatabase(),mongoDb=TimeSeriesDatabaseMongo(),mqttService=None) -> None:
        self.mySqlDb=mySqlDb
        self.mongoDb=mongoDb
        
        self.mqttService=mqttService
        
        self.currReplicate=None

    '''
    id	projId	userId	description	    labNotebookBaseRef	    datetimeCreate	    locked
    296	1	    22	    Making Disprins	50403_jdtoit_DSIP012A	2024-09-08 11:42:28	0

    '''

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

    def createReplicate(self, labNotebookRef, tableName='testlist', columnName='labNotebookBaseRef'):
        testListId=self.getTestlistId(labNotebookRef,tableName,columnName)
        replicates=self.getRunNrs(labNotebookRef) #Error handling!
        idNext=-1
        if (len(replicates)==0):
            idNext=0
        else:
            idNext=replicates[-1] + 1
        insert=[(testListId,datetime.now(),None,None,0,labNotebookRef,idNext)] #['testlistId', 'createTime', 'startTime', 'stopTime', 'recorded','labNotebookRef','runNr']
        self.mySqlDb.insertRecords('testruns',insert)
        return idNext

    def getTestlistId(self,labNotebookRef,tableName='testlist',columnName='labNotebookBaseRef'):
        return (self.mySqlDb.fetchRecordByColumnValue(tableName,columnName,labNotebookRef)[0])

    def getTestlistRow(self,labNotebookRef):
        return (self.mySqlDb.fetchRecordByColumnValue('testlist','labNotebookRef',labNotebookRef))
                                
    def getUserId(self,orgId=None,email=None):
        '''
        >id<	orgId	email	            cellphone	lastLogin	firstName	lastName	password	admin	active
        22	    50403	jdtoit@csir.co.za	0824440997		        Jurie	    du Toit		            1	    1
        '''
        if not orgId:
           return (self.mySqlDb.fetchRecordByColumnValue('users','email',email))[0]
        if not email:
           return (self.mySqlDb.fetchRecordByColumnValue('users','orgId',orgId))[0]

    def getUserRow(self,orgId=None,email=None):
        if not orgId:
           return (self.mySqlDb.fetchRecordByColumnValue('users','email',email))
        if not email:
           return (self.mySqlDb.fetchRecordByColumnValue('users','orgId',orgId))
    
    def getPassword(self,orgId=None,email=None):
        if not orgId:
           return (self.mySqlDb.fetchRecordByColumnValue('users','email',email))[7]
        if not email:
           return (self.mySqlDb.fetchRecordByColumnValue('users','orgId',orgId))[7]
    
    def getTestlistId(self,labNotebookRef,tableName='testlist',columnName='labNotebookBaseRef'):
        return (self.mySqlDb.fetchRecordByColumnValue(tableName,columnName,labNotebookRef)[0])
                
    def getUserTests(self,orgId=None,email=None):
        _ret=[]
        if not orgId and email:
            _id=self.getUserId(email=email)
            for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testlist',columnName='userId',value=_id):
                _ret.append(_x[0])
            return _ret
        elif not email and orgId:
            _id=self.getUserId(orgId=orgId)
            for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testlist',columnName='userId',value=_id):
                _ret.append(_x[0])
            return _ret

    def getTestRunIds(self,labNotebookRef):
        _ret=[]
        _id=self.getTestlistId(labNotebookRef)
        for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testruns',columnName='testlistId',value=_id):
            _ret.append(_x[0])
        return _ret
        
    def getTestRuns(self,labNotebookRef):
        _ret=[]
        _id=self.getTestlistId(labNotebookRef=labNotebookRef)
        for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testruns',columnName='testlistId',value=_id):
            _ret.append(_x)
        return _ret
        
    def createStdExp(self,labNotebookRef,nameTest="Short description",description="Long description",flowScript=b"",testScript=b"script_content"):
        ret=(StandardExperiment(self.mySqlDb,tables=["testlist"])).createExperiment(
            nameTest=nameTest,
            nameTester="",
            lockScript=0,
            flowScript=flowScript,
            description=description,
            testScript=testScript,
            labNotebookRef=labNotebookRef,
            orgId=self.mqttService.orgId
        )
        self.createReplicate(labNotebookRef=labNotebookRef)
        return ret

    def setZeroTime(self, id, zeroTime=None):
        if not zeroTime:
            zeroTime=datetime.now()
        self.mySqlDb.updateRecordById(tableName='testruns',uniqueId=id,columnName='startTime',newValue=zeroTime)
    def setStopTime(self, id, stopTime=None):
        if not stopTime:
            stopTime=datetime.now()
        self.mySqlDb.updateRecordById(tableName='testruns',uniqueId=id,columnName='stopTime',newValue=stopTime)

    def connect(self):
        self.mySqlDb.connect()
        self.mongoDb.purgeAndPause() #Good idea? :/

    def fetchStreamingBracket(self,labNotebookRef,runNr): #Fetches previous experiment's start time and end time
        _ret=self.mySqlDb.fetchSpecifiedColumnsByValues(tableName='testruns',columnNames=['startTime','stopTime'],column1Name='labNotebookRef',value1=labNotebookRef,column2Name='runNr',value2=runNr)
        return [_ret[0],_ret[1]]
    def setStreamingBracket(self,labNotebookRef,runNr): #Fetches previous experiment's start time and end time
        _ret=self.fetchStreamingBracket(labNotebookRef,runNr)
        self.mongoDb.prevZeroTime=_ret[0]
        self.mongoDb.prevStopTime=_ret[1]

class ParseStreamingData: #Defines what exactly to send to Flutter
    def __init__(self) -> None:
        self._protocols={
            '''
            Function pointers that parse data to be sent to UI
            "hotcoil1":{'fr',function}
            '''
        }

class DatabaseStreamer(DatabaseOperations):
    def __init__(self, mySqlDb=MySQLDatabase(), mongoDb=TimeSeriesDatabaseMongo(), mqttService=None) -> None:
        super().__init__(mySqlDb, mongoDb, mqttService)
        self.loopThread=None
        self.dataQueues={} #Contains id:[...data], id tells Flutter where streamed data must go
        self.streamRequestDetails={}
        self.zeroTimes={}

    def handleStreamRequest(self,req: dict): #Looks at 'req' received from Flutter and works out what it wants
        id=req["id"]
        if not (id in self.streamRequestDetails):
            self.streamRequestDetails[id]={}
        self.streamRequestDetails[id]["labNotebookRef"]=req["labNotebookRef"]
        self.streamRequestDetails[id]["runNr"]=req["runNr"]
        self.streamRequestDetails[id]["timeWindow"]=req["timeWindow"]
        self.streamRequestDetails[id]["nestedField"]=req["nestedField"]
        self.streamRequestDetails[id]["nestedValue"]=req["nestedValue"]
        self.streamRequestDetails[id]["deviceName"]=req["deviceName"]
        self.streamRequestDetails[id]["setting"]=req["setting"]
        self._returnMqttStreamRequest(id)

    def _streamingThread(self): #TODO
        pass

    def _packageData(self,data,deviceName,setting,timestamp,zeroTime):
        _val=HardcodedTeleAddresses.getValFromAddress(data,device=deviceName,setting=setting)
        return [(timestamp - zeroTime).total_seconds(),_val]
    
    def _returnMqttStreamRequest(self,id):
        if not (id in self.dataQueues):
            self.dataQueues[id]=[]
        _rec=self.streamFrom(
            labNotebookRef=self.streamRequestDetails[id]["labNotebookRef"],
            runNr=self.streamRequestDetails[id]["runNr"],
            timeWindow=self.streamRequestDetails[id]["timeWindow"],
            nestedField=self.streamRequestDetails[id]["nestedField"],
            nestedValue=self.streamRequestDetails[id]["nestedValue"]
        )
        _ret=[]
        _zT=(self.fetchStreamingBracket(
            labNotebookRef=self.streamRequestDetails[id]["labNotebookRef"],
            runNr=self.streamRequestDetails[id]["runNr"]
        ))[0]
        for _x in _rec:
            _ret.append(self._packageData(
                _x["data"],
                self.streamRequestDetails[id]["deviceName"],
                self.streamRequestDetails[id]["setting"],
                _x["timestamp"],
                _zT
            ))
        _data={"dbStreaming":{id:_ret}}
        self.mqttService.client.publish(
            topic="ui/dbStreaming/out",
            payload=json.dumps(_data),
            qos=2
        )
        self.streamRequestDetails[id]={}
        self.dataQueues[id]=[]
    '''
    def streamToMqtt(self,id,labNotebookRef,runNr,timeWindow,nestedField=None,nestedValue=None):
        if not (id in self.dataQueues):
            self.dataQueues[id]=[]
        _rec=self.streamFrom(labNotebookRef,runNr,timeWindow=timeWindow,nestedField=nestedField,nestedValue=nestedValue)
        for _x in _rec:
            _x=self._packageData(_x["data"],_x["data"]["deviceName"],_x["data"]["setting"])
        self.dataQueues[id]=self.dataQueues[id] + self.streamFrom(labNotebookRef,runNr,timeWindow=timeWindow,nestedField=nestedField,nestedValue=nestedValue)
        _data={'dbStreaming':{id:self.dataQueues[id]}}
        self.mqttService.client.publish(
            topic="ui/dbStreaming/out",
            payload=str(_data),
            qos=2
        )
        self.streamRequestDetails[id]={}
        self.dataQueues[id]=[]
    '''    
    def streamFrom(self,labNotebookRef,runNr,timeWindow=30,nestedField: str = None,nestedValue=None): #This is not streaming
        return self._retrieve(labNotebookRef,runNr,timeWindow,nestedField,nestedValue)
                
    def _retrieve(self,labNotebookRef,runNr,timeWindow,nestedField: str = None,nestedValue=None):
        self.setStreamingBracket(labNotebookRef,runNr)
        return self.mongoDb.streamTimeBracket(testId=(self.getTestlistId(labNotebookRef)),timeWindowInSeconds=timeWindow,runNr=runNr,nestedField=nestedField,nestedValue=nestedValue)
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
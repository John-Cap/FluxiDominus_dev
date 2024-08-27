
import mysql.connector
from pymongo import MongoClient
from datetime import datetime
import time
import threading

from Core.UI.plutter import MqttService

class MySQLDatabase:
    def __init__(self, host='localhost',port=3306,user="pharma",password="pharma",database="pharma"):
        """Initialize the MySQLDatabase class with connection parameters."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connected = False
        self.cursor = None
        
        self.tableVar={
            "users":['orgId', 'lastLogin', 'firstName', 'lastName'],
            "testlist":['nameTest', 'description', 'nameTester', 'fumehoodId', 'testScript', 'lockScript', 'flowScript', 'datetimeCreate', 'labNotebookRef', 'orgId']
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
            print(f"Error: {e}")
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
        """Fetch a single record from the specified table where the column matches the given value."""
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
    host = "146.64.91.174"
    port = 27017
    databaseName = "Pharma"
    collectionName = "pharma-data"
    
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

    def insertDataPoint(self,dataPoint):
        dataPoint["timestamp"]=datetime.utcnow()
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

    def fetchTimeSeriesData(self,orgId: str,labNotebookRef: str):
        cursor = self.collection.find({
            'orgId': orgId,
            'labNotebookRef':labNotebookRef
        }).sort('timestamp', 1)  # Sort by timestamp in ascending order
        _ret=[]
        _num=0
        for document in cursor:
            _ret.append(document)
            _num=_num+1
        print(f'Fetched {_num} documents!')
        return _ret

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

    def start(self,orgId: str,labNotebookRef: str):
        kwargs={"orgId":orgId,"labNotebookRef":labNotebookRef}
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
    def __init__(self,mySqlDb=MySQLDatabase(),mongoDb=TimeSeriesDatabaseMongo(),mqttService=MqttService()) -> None:
        self.mySqlDb=mySqlDb
        self.mongoDb=mongoDb
        
        self.mqttService=mqttService
        
    def connect(self):
        self.mySqlDb.connect()
        self.mongoDb.purgeAndPause()
        
    def getUserTests(self, tableName='testList', columnName='orgId'):
        """Fetch a single record from the specified table where the column matches the given value."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {columnName} = %s"
            self.cursor.execute(fetch_query, (self.mqttService.orgId,))
            result = self.cursor.fetchall()
            return result
        
#################################
#Database operations example
if __name__ == '__main__':
    thisThing=MqttService()
    thisThing.orgId="309930"
    thisThing.start()
    dbOp=DatabaseOperations(mySqlDb=MySQLDatabase(host='146.64.91.174'))
    print(dbOp.getUserTests())
#################################
'''
# Example usage //Kyk, camel vs snekcase
if __name__ == "__main__":
    db = MySQLDatabase(
        host="146.64.91.174",
        port=3306,
        user="pharma",
        password="pharma",
        database="pharma"
    )

    db.connect()
    
    records = [
        ("309930",datetime.now(),"Wessel","Bonnet")
    ]
    db.insertRecords("users", records) #['orgId', 'lastLogin', 'firstName', 'lastName']
    
    results = db.fetchRecords("users")
    for row in results:
        print(row)
        
    print(db.fetchRecordByColumnValue("users","orgId","309930"))
        
    db.close()

if __name__ == "__main__":
    
    #################################################
    #MySQL
    db = MySQLDatabase(
        host="146.64.91.174",
        port=3306,
        user="pharma",
        password="pharma",
        database="pharma"
    )

    db.connect()
    ## id, nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate, labNotebookRef
    ##'146', 'asd', 'asd', 'asd', 'd8:3a:dd:55:99:09', ?, '0', ?, '2024-03-22 08:14:12', NULL

    records = [
        ("Mr_Test","Just_a_test","MRS_TEST","MAC MAC",b"Hi there!",0,b"NO VAL",datetime.now(),"THIS_REF_1","309930"),
        ("Mr_Test2","Just_a_test","MRS_TEST","MAC MAC",b"Hi there!",0,b"NO VAL",datetime.now(),"THIS_REF_2","309930"),
        ("Mr_Test3","Just_a_test","MRS_TEST","MAC MAC",b"Hi there!",0,b"NO VAL",datetime.now(),"THIS_REF_3","309930"),
    ]
    db.insertRecords("testlist", records) #['orgId', 'lastLogin', 'firstName', 'lastName']
    
    results = db.fetchRecordsByColumnValue("testlist","orgId","309930")
    for row in results:
        print(row)
        
    print(db.fetchRecordByColumnValue("users","orgId","309930"))
        
    db.close()
    ################################################
    #Mongo
    host = "146.64.91.174"
    port = 27017
    databaseName = "Pharma"
    collectionName = "pharma-data"

    dp1 = DataPointFDE(
        labNotebookRef="MY_REF_1",
        deviceName="flowsynmaxi2",
        data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
        metadata={"location": "Room 101"}
    ).toDict()

    dp2 = DataPointFDE(
        labNotebookRef="MY_REF_2",
        dataType=DataType("JUMP_THE_MOON"),
        deviceName="IRSCANNER",
        data={'irScan': [1.2, 3.4, 5.6, 7.8]},
        metadata={"location": "Room 101", "type": "IR"}
    ).toDict()

    dp3 = DataPointFDE(
        labNotebookRef="MY_REF_1",
        deviceName="FIZZBANG",
        data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
        metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
    ).toDict()

    dp4 = DataPointFDE(
        labNotebookRef="MY_REF_1",
        dataType=DataType("IR_SCAN"),
        data={'irScan': [1.2, 3.4, 5.6, 7.8]},
        metadata={"location": "Room 101", "type": "IR"}
    ).toDict()

    dp5 = DataPointFDE(
        labNotebookRef="MY_REF_2",
        deviceName="FIZZBANG",
        data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
        metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
    ).toDict()
    
    dataSet=DataSetFDD(
        [dp1,dp2,dp3,dp4,dp5,dp1,dp2,dp3,dp4,dp5]
    )

    ts_db = TimeSeriesDatabaseMongo(host, port, databaseName, collectionName,[])
    ts_db.start(orgId="309930",labNotebookRef="MY_REF_2")
    _testNum=["MY_REF_2","MY_REF_1"]
    for _x in dataSet.dataPoints:
        #_x.labNotebookRef=random.choice(_testNum)
        ts_db.insertDataPoint(_x)
        time.sleep(3)
    ts_db.pauseInsertion=True
    print(ts_db.fetchTimeSeriesData(orgId="309930",labNotebookRef="MY_REF_2"))
    ts_db.kill()
    #ts_db.start()
'''
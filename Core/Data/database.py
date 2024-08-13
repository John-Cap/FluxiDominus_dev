import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import time
import threading

from Core.Data.data import DataPoint, DataPointFDE, DataSet, DataSetFDD, DataType

class MySQLDatabase:
    def __init__(self, host, port, user, password, database):
        """Initialize the MySQLDatabase class with connection parameters."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

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
        except Error as e:
            print(f"Error: {e}")
            self.connection = None

    def createTable(self, table_name, schema):
        """Create a table with the given schema."""
        if self.cursor:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {schema}
            )
            """
            self.cursor.execute(create_table_query)
            print(f"Table '{table_name}' created successfully.")

    def insertRecords(self, table_name, columns, records):
        """Insert multiple records into the specified table."""
        if self.cursor:
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
            """
            self.cursor.executemany(insert_query, records)
            self.connection.commit()
            print(f"Records inserted successfully into '{table_name}'.")

    def fetchRecords(self, table_name):
        """Fetch all records from the specified table."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {table_name}"
            self.cursor.execute(fetch_query)
            results = self.cursor.fetchall()
            return results

    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")

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
    db.create_table("sample_table", "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, age INT NOT NULL")
    
    records = [
        ("Alice", 30),
        ("Bob", 25),
        ("Charlie", 35)
    ]
    db.insert_records("sample_table", ["name", "age"], records)
    
    results = db.fetch_records("sample_table")
    for row in results:
        print(row)
    
    db.close()
'''
class TimeSeriesDatabaseMongo:
    def __init__(self, host, port, database_name, collection_name, dataPoints):
        #self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.client = MongoClient(host=host,port=port)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
        self.dataPoints=dataPoints
        self.insertionInterval=10
        self.pauseCollection=True
        self.insertion_thread=None

    def insertDataPoint(self,dataPoint):
        dataPoint["timestamp"]=datetime.utcnow()
        self.collection.insert_one(dataPoint)
        #print(f"Inserted data point: {dataPoint}")

    def continuousInsertion(self):
        while True:
            while self.pauseCollection:
                time.sleep(0.1)
            if self.dataPoints is None or len(self.dataPoints)==0:
                pass
            else:
                _numOf=len(self.dataPoints)
                for _x in self.dataPoints:
                    self.insertDataPoint(_x)
                self.dataPoints=[]
                print('WJ - Inserted '+str(_numOf)+' datapoints into database '+str(self.db)+'!')
            time.sleep(self.insertionInterval)
            

    def fetchRecentData(self):
        now = datetime.utcnow()
        thirty_sec_ago = now - timedelta(seconds=30)
        cursor = self.collection.find({
            'timestamp': {
                '$gte': thirty_sec_ago,
                '$lt': now
            }
        }).sort('timestamp', 1)  # Sort by timestamp in ascending order

        print('Fetched the following documents:')
        for document in cursor:
            print(document)

    def continuousFetching(self):
        try:
            while True:
                self.fetchRecentData()
                time.sleep(6)  # Fetch data every 10 seconds
        except KeyboardInterrupt:
            print("Stopped fetching data.")

    def pause(self):
        self.pauseCollection=True

    def start(self):
        if not (self.insertion_thread is None):
            self.pauseCollection=False
        else:
            insertion_thread = threading.Thread(target=self.continuousInsertion)

            fetching_thread = threading.Thread(target=self.continuousFetching)

            insertion_thread.start()
            fetching_thread.start()

            #insertion_thread.join()
            #fetching_thread.join()
            
            self.insertion_thread=insertion_thread
            self.pauseCollection=False
            
if __name__ == "__main__":
    host = "146.64.91.174"
    port = 27017
    database_name = "Pharma"
    collection_name = "pharma-data"
    
    dp1 = DataPointFDE(
        experimentId="exp123",
        deviceName="flowsynmaxi2",
        data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
        metadata={"location": "Room 101"}
    ).toDict()

    dp2 = DataPointFDE(
        dataType=DataType("JUMP_THE_MOON"),
        experimentId="exp123",
        deviceName="IRSCANNER",
        data={'irScan': [1.2, 3.4, 5.6, 7.8]},
        metadata={"location": "Room 101", "type": "IR"}
    ).toDict()

    dp3 = DataPointFDE(
        experimentId="exp123",
        deviceName="FIZZBANG",
        data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
        metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
    ).toDict()

    dp4 = DataPointFDE(
        dataType=DataType("IR_SCAN"),
        experimentId="exp123",
        deviceName="IRSCANNER",
        data={'irScan': [1.2, 3.4, 5.6, 7.8]},
        metadata={"location": "Room 101", "type": "IR"}
    ).toDict()

    dp5 = DataPointFDE(
        experimentId="exp123",
        deviceName="FIZZBANG",
        data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
        metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
    ).toDict()
    
    dataSet=DataSetFDD(
        [dp1,dp2,dp3,dp4,dp5]
    )

    ts_db = TimeSeriesDatabaseMongo(host, port, database_name, collection_name,dataSet.dataPoints)
    ts_db.insertDataPoint(dp1)
    #ts_db.start()

import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import time
import threading

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

    def create_table(self, table_name, schema):
        """Create a table with the given schema."""
        if self.cursor:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {schema}
            )
            """
            self.cursor.execute(create_table_query)
            print(f"Table '{table_name}' created successfully.")

    def insert_records(self, table_name, columns, records):
        """Insert multiple records into the specified table."""
        if self.cursor:
            insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
            """
            self.cursor.executemany(insert_query, records)
            self.connection.commit()
            print(f"Records inserted successfully into '{table_name}'.")

    def fetch_records(self, table_name):
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
# Example usage
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
class TimeSeriesDatabase:
    def __init__(self, host, port, database_name, collection_name):
        self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def insertDataPoint(self):
        data_point = {
            'timestamp': datetime.utcnow(),
            'value': random.uniform(20.0, 30.0),  # Example data
            'metadata': {'sensor': 'sensor1'}
        }
        self.collection.insert_one(data_point)
        print(f"Inserted data point: {data_point}")

    def continuousInsertion(self):
        _i=25
        try:
            while _i!=0:
                self.insertDataPoint()
                time.sleep(1)  # Insert data every second
                _i-=1
        except KeyboardInterrupt:
            print("Stopped inserting data.")

    def fetchRecentData(self):
        now = datetime.utcnow()
        ten_minutes_ago = now - timedelta(seconds=5)
        cursor = self.collection.find({
            'timestamp': {
                '$gte': ten_minutes_ago,
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
                time.sleep(10)  # Fetch data every 10 seconds
        except KeyboardInterrupt:
            print("Stopped fetching data.")

    def start(self):
        insertion_thread = threading.Thread(target=self.continuousInsertion)
        fetching_thread = threading.Thread(target=self.continuousFetching)

        insertion_thread.start()
        fetching_thread.start()

        insertion_thread.join()
        fetching_thread.join()

if __name__ == "__main__":
    host = "146.64.91.174"
    port = 27017
    database_name = "Pharma"
    collection_name = "pharma-data"

    ts_db = TimeSeriesDatabase(host, port, database_name, collection_name)
    ts_db.start()

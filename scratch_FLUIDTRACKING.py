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

import datetime
import pickle
from time import sleep
import mysql.connector
from mysql.connector import Error

from Core.UI.brokers_and_topics import MqttTopics

# Connect to the MySQL database
db = mysql.connector.connect(
    host="146.64.91.174",
    port=3306,
    user="pharma",
    password="pharma",
    database="pharma"
)

cursor = db.cursor()

# Example Python object
my_object = MqttTopics()

# Serialize the object
serialized_object = pickle.dumps(my_object)

# Example data
nameTest = 'TestName'
description = 'TestDescription'
nameTester = 'PietPompies'  # Provide a value for the `nameTester` field
fumehoodId = 'FumehoodID'
testScript = serialized_object  # This is the serialized Python object
lockScript = 1
flowScript = b'Some binary data'  # Example binary data
datetimeCreate = datetime.datetime.now()

# Insert statement with all required fields
insert_query = """
INSERT INTO testlist (nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

values = (nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate)

try:
    cursor.execute(insert_query, values)
    db.commit()
    print("Record inserted successfully.")
except Error as e:
    print(f"Error inserting record: {e}")

cursor.close()
db.close()

sleep(5)

# Connect to the MySQL database
db = mysql.connector.connect(
    host="146.64.91.174",
    port=3306,
    user="pharma",
    password="pharma",
    database="pharma"
)

cursor = db.cursor()

# Fetch serialized object from the database by ID
fetch_query = "SELECT testScript FROM testlist WHERE id = %s"
cursor.execute(fetch_query,[211])  # Replace 4 with the correct ID if necessary
result = cursor.fetchone()

if result:
    serialized_object = result[0]
    
    # Deserialize the object
    try:
        my_object = pickle.loads(serialized_object)
        print("Object fetched and deserialized successfully.")
        print(my_object.getUiTopic('FlowSketcher'))
    except Exception as e:
        print(f"Error deserializing object: {e}")
else:
    print("No record found with the given ID.")

cursor.close()
db.close()


# Example usage
from datetime import datetime
from Core.Data.database import MySQLDatabase
from Core.Data.experiment import StandardExperiment


if __name__ == "__main__":
    db = MySQLDatabase(
        host="146.64.91.174",
        port=3306,
        user="pharma",
        password="pharma",
        database="pharma"
    )

    db.connect()

    exp = StandardExperiment(db,tables=["testlist"])
    newExperiment = exp.createExperiment(
        nameTest="MrTest",
        nameTester="MrTester",
        lockScript=0,
        flowScript=b"R",
        description="Description of Test",
        testScript=b"script_content",
        datetimeCreate=datetime.now(),
        labNotebookRef="MOUSE_BABY_MOUSE_61",
        orgId="309930"
    )
    print("Created experiment ID, ref: ", newExperiment.id, newExperiment.labNotebookRef)

    fetchedExperiment = exp.fromDbByLabNotebookRef("MOUSE_BABY_MOUSE_61").toDict()
    if fetchedExperiment:
        print(fetchedExperiment)

    db.close()
'''
Connected to the database.
Data inserted/updated successfully.
Created experiment ID, ref:  251 MOUSE_BABY_MOUSE_59
WJ - Fetched query:  (251, 'MrTest', 'Description of Test1', 'MrTester', 'c0:e4:34:25:17:63', b'script_content', 0, b'R', datetime.datetime(2024, 8, 28, 8, 40, 55), 'MOUSE_BABY_MOUSE_59', '309930')
WJ - Labbook ref: MOUSE_BABY_MOUSE_59
{'id': 251, 'nameTest': 'MrTest', 'description': 'Description of Test1', 'nameTester': 'MrTester', 'fumehoodId': 'c0:e4:34:25:17:63', 'testScript': b'script_content', 'lockScript': 0, 'flowScript': b'R', 'datetimeCreate': datetime.datetime(2024, 8, 28, 8, 40, 55), 'labNotebookRef': 'MOUSE_BABY_MOUSE_59', 'orgId': '309930'}
Database connection closed.
'''
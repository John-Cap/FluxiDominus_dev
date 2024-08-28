from datetime import datetime
from getmac import get_mac_address as gma
from Core.Data.data import DataObj_TEMP
from Core.Data.database import MySQLDatabase

class Experiment:
    def __init__(self, db, tables):
        """Initialize the Experiment with a MySQLDatabase instance."""
        self.db = db
        self.tables=tables
        self.table=tables[0]

    def toDB(self, dataObj, table=None): #Handle case where duplicate unique entries throw errors
        if not table:
            table=self.table
        """Insert or update a DataObj_TEMP instance in the database."""
        if self.db.cursor:
            if dataObj.id:
                # Update existing record
                updateQuery = f"""
                UPDATE {table}
                SET nameTest=%s, description=%s, nameTester=%s, fumehoodId=%s, testScript=%s,
                    lockScript=%s, flowScript=%s, datetimeCreate=%s, labNotebookRef=%s, orgId=%s
                WHERE id=%s
                """
                values = (
                    dataObj.nameTest, dataObj.description, dataObj.nameTester, dataObj.fumehoodId,
                    dataObj.testScript, dataObj.lockScript, dataObj.flowScript, dataObj.datetimeCreate,
                    dataObj.labNotebookRef,dataObj.orgId,
                    dataObj.id
                )
                self.db.cursor.execute(updateQuery, values)
            else:
                # Insert new record
                insertQuery = f"""
                INSERT INTO {table} (nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate, labNotebookRef, orgId)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    dataObj.nameTest, dataObj.description, dataObj.nameTester, dataObj.fumehoodId,
                    dataObj.testScript, dataObj.lockScript, dataObj.flowScript, dataObj.datetimeCreate,
                    dataObj.labNotebookRef,dataObj.orgId
                )
                self.db.cursor.execute(insertQuery, values)
                dataObj.id = self.db.cursor.lastrowid
            self.db.connection.commit()
            print("Data inserted/updated successfully.")

    def fromDbById(self, id, table=None):
        if not table:
            table=self.table
        """Fetch a DataObj_TEMP instance from the database by ID."""
        if self.db.cursor:
            fetchQuery = f"SELECT * FROM {table} WHERE id=%s"
            self.db.cursor.execute(fetchQuery, (id,))
            result = self.db.cursor.fetchone()
            if result:
                return DataObj_TEMP(
                    id=result[0],
                    nameTest=result[1],
                    description=result[2],
                    nameTester=result[3],
                    fumehoodId=result[4],
                    testScript=result[5],
                    lockScript=result[6],
                    flowScript=result[7],
                    datetimeCreate=result[8],
                    labNotebookRef=result[9]
                )
            else:
                print(f"No record found with ID {id}.")
                return None

    def fromDbByLabNotebookRef(self, labNotebookRef, table=None):
        if not table:
            table=self.table
        """Fetch a DataObj_TEMP instance from the database by labNotebookRef."""
        if self.db.cursor:
            fetchQuery = f"SELECT * FROM {table} WHERE labNotebookRef=%s"
            self.db.cursor.execute(fetchQuery, (labNotebookRef,))
            result = self.db.cursor.fetchone()
            if result:
                print('WJ - Fetched query: ',result)
                return DataObj_TEMP(
                    id=result[0],
                    nameTest=result[1],
                    description=result[2],
                    nameTester=result[3],
                    fumehoodId=result[4],
                    testScript=result[5],
                    lockScript=result[6],
                    flowScript=result[7],
                    datetimeCreate=result[8],
                    labNotebookRef=result[9],
                    orgId=result[10]
                )
            else:
                print(f"No record found with lab notebook ref {labNotebookRef}.")
                return None
''''''   
class StandardExperiment(Experiment):
    def __init__(self, db, tables):
        super().__init__(db, tables)

    def createExperiment(self, nameTest, description, nameTester, testScript,
                         lockScript, flowScript, datetimeCreate, labNotebookRef, orgId):
        """Create a new experiment and save it to the database."""
        dataObj = DataObj_TEMP(
            nameTest=nameTest,
            description=description,
            nameTester=nameTester,
            fumehoodId=gma(), #Erm, goeie idee? :/
            testScript=testScript,
            lockScript=lockScript,
            flowScript=flowScript,
            datetimeCreate=datetimeCreate,
            labNotebookRef=labNotebookRef,
            orgId=orgId
        )
        self.toDB(dataObj)
        return dataObj

    def getExperimentBylabNotebookRef(self, labNotebookRef):
        """Fetch an experiment by labNotebookRef."""
        return self.fromDbByLabNotebookRef(labNotebookRef)
    
    def getExperimentById(self, id):
        """Fetch an experiment by ID."""
        return self.fromDbById(id)

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

    exp = StandardExperiment(db,tables=["testlist"])
    newExperiment = exp.createExperiment(
        nameTest="MrTest",
        nameTester="MrTester",
        lockScript=0,
        flowScript=b"R",
        description="Description of Test1",
        testScript=b"script_content",
        datetimeCreate=datetime.now(),
        labNotebookRef="MOUSE_BABY_MOUSE_59",
        orgId="309930"
    )
    print("Created experiment ID, ref: ", newExperiment.id, newExperiment.labNotebookRef)

    fetchedExperiment = exp.fromDbByLabNotebookRef("MOUSE_BABY_MOUSE_59").toDict()
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
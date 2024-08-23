from datetime import datetime

from Core.Data.data import DataObj_TEMP
from Core.Data.database import MySQLDatabase

class Experiment:
    def __init__(self, db, tables):
        """Initialize the Experiment with a MySQLDatabase instance."""
        self.db = db
        self.tables=tables
        self.table=tables[0]

    def toDB(self, dataObj, table=None):
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

    def createExperiment(self, nameTest, description, nameTester, fumehoodId, testScript,
                         lockScript, flowScript, datetimeCreate, labNotebookRef, orgId):
        """Create a new experiment and save it to the database."""
        dataObj = DataObj_TEMP(
            nameTest=nameTest,
            description=description,
            nameTester=nameTester,
            fumehoodId=fumehoodId,
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
        description="Description of Test1",
        fumehoodId="Fumehood1",
        testScript=b"script_content",
        datetimeCreate=datetime.now(),
        labNotebookRef="MOUSE_BABY_MOUSE_15",
        orgId="309930"
    )
    print("Created experiment ID, ref: ", newExperiment.id, newExperiment.labNotebookRef)

    fetchedExperiment = exp.fromDbByLabNotebookRef("MOUSE_BABY_MOUSE_15").toDict()
    if fetchedExperiment:
        print(fetchedExperiment)

    db.close()
'''
Connected to the database.
Data inserted/updated successfully.
Created experiment ID, ref:  245 MOUSE_BABY_MOUSE_15
WJ - Fetched query:  (245, 'MrTest', 'Description of Test1', 'Tester1', 'Fumehood1', b'script_content', 1, b'flow_content', 
datetime.datetime(2024, 8, 23, 7, 17, 27), 'MOUSE_BABY_MOUSE_15')
WJ - Labbook ref: MOUSE_BABY_MOUSE_15
{'id': 245, 'nameTest': 'MrTest', 'description': 'Description of Test1', 'nameTester': 'Tester1', 'fumehoodId': 'Fumehood1', 'testScript': b'script_content', 'lockScript': 1, 'flowScript': b'flow_content', 'datetimeCreate': datetime.datetime(2024, 
8, 23, 7, 17, 27), 'labNotebookRef': 'MOUSE_BABY_MOUSE_15'}
'''
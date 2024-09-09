from datetime import datetime
from getmac import get_mac_address as gma
from Core.Data.data import DataObj_TEMP

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
                    lockScript=%s, flowScript=%s, datetimeCreate=%s, labNotebookBaseRef=%s, orgId=%s
                WHERE id=%s
                """
                values = (
                    dataObj.nameTest, dataObj.description, dataObj.nameTester, dataObj.fumehoodId,
                    dataObj.testScript, dataObj.lockScript, dataObj.flowScript, dataObj.datetimeCreate,
                    dataObj.labNotebookBaseRef,dataObj.orgId,
                    dataObj.id
                )
                self.db.cursor.execute(updateQuery, values)
            else:
                # Insert new record
                insertQuery = f"""
                INSERT INTO {table} (nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate, labNotebookBaseRef, orgId)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    dataObj.nameTest, dataObj.description, dataObj.nameTester, dataObj.fumehoodId,
                    dataObj.testScript, dataObj.lockScript, dataObj.flowScript, dataObj.datetimeCreate,
                    dataObj.labNotebookBaseRef,dataObj.orgId
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
                    labNotebookBaseRef=result[9]
                )
            else:
                print(f"No record found with ID {id}.")
                return None

    def fromDbByLabNotebookRef(self, labNotebookBaseRef, table=None):
        if not table:
            table=self.table
        """Fetch a DataObj_TEMP instance from the database by labNotebookBaseRef."""
        if self.db.cursor:
            fetchQuery = f"SELECT * FROM {table} WHERE labNotebookBaseRef=%s"
            self.db.cursor.execute(fetchQuery, (labNotebookBaseRef,))
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
                    labNotebookBaseRef=result[9],
                    orgId=result[10]
                )
            else:
                print(f"No record found with lab notebook ref {labNotebookBaseRef}.")
                return None
''''''   
class StandardExperiment(Experiment):
    def __init__(self, db, tables):
        super().__init__(db, tables)

    def createExperiment(self, nameTest, description, nameTester, testScript,
                         lockScript, flowScript, labNotebookBaseRef, orgId):
        """Create a new experiment and save it to the database."""
        dataObj = DataObj_TEMP(
            nameTest=nameTest, #Display name
            description=description,
            nameTester=nameTester,
            fumehoodId=gma(), #Erm, goeie idee? :/
            testScript=testScript,
            lockScript=lockScript,
            flowScript=flowScript,
            datetimeCreate=datetime.now(),
            labNotebookBaseRef=labNotebookBaseRef,
            orgId=orgId
        )
        self.toDB(dataObj)
        return dataObj

    def getExperimentBylabNotebookBaseRef(self, labNotebookBaseRef):
        """Fetch an experiment by labNotebookBaseRef."""
        return self.fromDbByLabNotebookRef(labNotebookBaseRef)

    def getExperimentId(self, labNotebookBaseRef):
        """Fetch an experiment by labNotebookBaseRef."""
        return self.fromDbByLabNotebookRef(labNotebookBaseRef)[0]
        
    def getExperimentById(self, id):
        """Fetch an experiment by ID."""
        return self.fromDbById(id)

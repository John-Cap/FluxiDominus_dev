from datetime import datetime

from Core.Data.data import DataObj_TEMP
from Core.Data.database import MySQLDatabase

class Experiment_TEMP:
    def __init__(self, db):
        """Initialize the Experiment_TEMP with a MySQLDatabase instance."""
        self.db = db

    def toDB(self, dataObj):
        """Insert or update a DataObj_TEMP instance in the database."""
        if self.db.cursor:
            if dataObj.id:
                # Update existing record
                updateQuery = """
                UPDATE testlist
                SET nameTest=%s, description=%s, nameTester=%s, fumehoodId=%s, testScript=%s,
                    lockScript=%s, flowScript=%s, datetimeCreate=%s
                WHERE id=%s
                """
                values = (
                    dataObj.nameTest, dataObj.description, dataObj.nameTester, dataObj.fumehoodId,
                    dataObj.testScript, dataObj.lockScript, dataObj.flowScript, dataObj.datetimeCreate,
                    dataObj.id
                )
                self.db.cursor.execute(updateQuery, values)
            else:
                # Insert new record
                insertQuery = """
                INSERT INTO testlist (nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    dataObj.nameTest, dataObj.description, dataObj.nameTester, dataObj.fumehoodId,
                    dataObj.testScript, dataObj.lockScript, dataObj.flowScript, dataObj.datetimeCreate
                )
                self.db.cursor.execute(insertQuery, values)
                dataObj.id = self.db.cursor.lastrowid
            self.db.connection.commit()
            print("Data inserted/updated successfully.")

    def fromDB(self, id):
        """Fetch a DataObj_TEMP instance from the database by ID."""
        if self.db.cursor:
            fetchQuery = "SELECT * FROM testlist WHERE id=%s"
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
                    datetimeCreate=result[8]
                )
            else:
                print(f"No record found with ID {id}.")
                return None
            
class StandardExperiment_TEMP(Experiment_TEMP):
    def __init__(self, db):
        super().__init__(db)

    def createExperiment(self, nameTest, description, nameTester, fumehoodId, testScript,
                         lockScript, flowScript, datetimeCreate):
        """Create a new experiment and save it to the database."""
        dataObj = DataObj_TEMP(
            nameTest=nameTest,
            description=description,
            nameTester=nameTester,
            fumehoodId=fumehoodId,
            testScript=testScript,
            lockScript=lockScript,
            flowScript=flowScript,
            datetimeCreate=datetimeCreate
        )
        self.toDB(dataObj)
        return dataObj

    def getExperiment(self, id):
        """Fetch an experiment by ID."""
        return self.fromDB(id)

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

    exp = StandardExperiment_TEMP(db)
    newExperiment = exp.createExperiment(
        nameTest="MrTest",
        description="Description of Test1",
        nameTester="Tester1",
        fumehoodId="Fumehood1",
        testScript=b"script_content",
        lockScript=1,
        flowScript=b"flow_content",
        datetimeCreate=datetime.now()
    )
    print("Created experiment ID:", newExperiment.id)

    fetchedExperiment = exp.getExperiment(newExperiment.id)
    if fetchedExperiment:
        print(fetchedExperiment.toDict())

    db.close()

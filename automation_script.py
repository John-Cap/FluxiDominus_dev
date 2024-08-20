

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
        description="Description of Test1",
        nameTester="Tester1",
        fumehoodId="Fumehood1",
        testScript=b"script_content",
        lockScript=1,
        flowScript=b"flow_content",
        datetimeCreate=datetime.now(),
        labNotebookRef="MOUSE_BABY_MOUSE_13"
    )
    print("Created experiment ID, ref: ", newExperiment.id, newExperiment.labNotebookRef)

    fetchedExperiment = exp.fromDbByLabNotebookRef("MOUSE_BABY_MOUSE_13").toDict()
    if fetchedExperiment:
        print(fetchedExperiment)

    db.close()

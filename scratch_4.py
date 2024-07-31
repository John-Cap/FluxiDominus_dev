
# Example usage
import datetime
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

    exp = StandardExperiment(db)
    newExperiment = exp.createExperiment(
        nameTest="Test1",
        description="Description of Test1",
        nameTester="Tester1",
        fumehoodId="Fumehood1",
        testScript=b'''
mr_block=[{"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 1.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 15}}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.5}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.5}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 0}}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.3}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.7}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}, {"Delay": {"initTimestamp": None, "sleepTime": 5}}, {"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.85}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": 
True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.15}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}];
flowsyn_fr_2=[{"deviceName": "flowsynmaxi2", "inUse": True, "settings": {"subDevice": "PumpBFlowRate", "command": "SET", "value": 0.0}, "topic": "subflow/flowsynmaxi2/cmnd", "client": "client"}, {"deviceName": "sf10Vapourtec1", "inUse": True, "settings": {"command": "SET", "mode": "FLOW", "flowrate": 0.0}, "topic": "subflow/sf10vapourtec1/cmnd", "client": "client"}];
''',
        lockScript=1,
        flowScript=b"flow_content",
        datetimeCreate=datetime.datetime.now()
    )
    print("Created experiment ID:", newExperiment.id)

    fetchedExperiment = exp.getExperiment(newExperiment.id)
    if fetchedExperiment:
        print((fetchedExperiment.toDict()['testScript']).decode('utf-8'))

    db.close()

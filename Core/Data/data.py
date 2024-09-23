from datetime import datetime

from bson import utc
from Core.Utils.Utils import Utils

class DataObj_TEMP:
    def __init__(self, id=None, nameTest=None, description=None, nameTester=None, fumehoodId=None,
                 testScript=None, lockScript=None, flowScript=None, datetimeCreate=None, labNotebookBaseRef=None, orgId=None):
        self.id = id
        self.nameTest = nameTest
        self.description = description
        self.nameTester = nameTester
        self.fumehoodId = fumehoodId
        self.testScript = testScript
        self.lockScript = lockScript
        self.flowScript = flowScript
        self.datetimeCreate = datetimeCreate
        self.labNotebookBaseRef= labNotebookBaseRef
        self.orgId = orgId

    def toDict(self):
        """Convert DataObj to a dictionary."""
        print('WJ - Labbook ref:',self.labNotebookBaseRef)
        return {
            "id": self.id,
            "nameTest": self.nameTest,
            "description": self.description,
            "nameTester": self.nameTester,
            "fumehoodId": self.fumehoodId,
            "testScript": self.testScript,
            "lockScript": self.lockScript,
            "flowScript": self.flowScript,
            "datetimeCreate": self.datetimeCreate,
            "labNotebookBaseRef": self.labNotebookBaseRef,
            "orgId": self.orgId
        }

class DataObj(DataObj_TEMP):
    def __init__(self, id=None, nameTest=None, description=None, nameTester=None, fumehoodId=None, testScript=None, lockScript=None, flowScript=None, datetimeCreate=None, labNotebookBaseRef=None):
        super().__init__(id, nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate, labNotebookBaseRef)
        self.id = Utils.generateUuid()
        self.description="GENERAL"
        self.fields={"id":self.fields,"description":self.description}

    def addDataField(self,field,val=None):
        self.fields[field]=val
        
    def toDict(self):
        """Convert DataObj to a dictionary."""
        return self.fields

class IrData(DataObj):
    def __init__(self,nameTest=None, description=None, nameTester=None, fumehoodId=None, testScript=None, lockScript=None, flowScript=None, datetimeCreate=None):
        super().__init__(id, nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate)
        self.nameTest = nameTest
        self.nameTester = nameTester
        self.fumehoodId = fumehoodId
        self.testScript = testScript
        self.lockScript = lockScript
        self.flowScript = flowScript
        self.datetimeCreate = datetimeCreate

class DataType:
    def __init__(self, type="ANY") -> None:
        self.type = type
    
    def getType(self):
        return self.type

class DataPoint:
    def __init__(self,testlistId,testrunId,data,metadata=None,timestamp=datetime.now()):
        self.timestamp=timestamp
        self.data=data
        self.metadata=metadata
        self.testlistId=testlistId
        self.testrunId=testrunId
    
    def toDict(self):
        if not self.metadata:
            self.metadata={}
        """Convert the DataPoint to a dictionary format."""
        self.metadata["testlistId"]=self.testlistId
        self.metadata["testrunId"]=self.testrunId
        return {
            'data': self.data,
            'metadata': self.metadata,
            'timestamp':self.timestamp
        }

class DataPointFDE(DataPoint):
    def __init__(self, testlistId, testrunId, data, metadata=None, timestamp=datetime.now()):
        super().__init__(testlistId, testrunId, data, metadata, timestamp)
        
class DataSet:
    def __init__(self, dataPoints = []):
        self.dataPoints = dataPoints

    def addDataPoint(self, dataPoint):
        if isinstance(dataPoint, DataPoint):
            self.dataPoints.append(dataPoint)
        else:
            raise TypeError("Expected a DataPoint instance")

    def toDict(self):
        """Convert the DataSet to a dictionary format."""
        return [dataPoint.toDict() for dataPoint in self.dataPoints]

    def __repr__(self):
        return f"<DataSet(numDataPoints={len(self.dataPoints)})>"
        
class DataSetFDD(DataSet):
    def __init__(self, dataPoints=[]):
        super().__init__(dataPoints)
        
if __name__ == "__main__":
    # Create DataPoint instances
    dp1 = DataPoint(
        testlistId=1,
        testrunId=2,
        data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
        metadata={"location": "Room 101", "type": "temperature"}
    )
    dp2 = DataPoint(
        testlistId=1,
        testrunId=2,
        data={'systemPressure': 2.2, 'pumpPressure': 3.5, 'temperature': 24.5},
        metadata={"location": "Room 101", "type": "temperature"}
    )

    # Create DataSet and add DataPoints
    dataSet = DataSet()
    dataSet.addDataPoint(dp1)
    dataSet.addDataPoint(dp2)

    # Print DataSet
    print(dataSet)
    print(dataSet.toDict())

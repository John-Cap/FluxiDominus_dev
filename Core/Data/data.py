from datetime import datetime
from Core.Utils.Utils import Utils

class DataObj_TEMP:
    def __init__(self, id=None, nameTest=None, description=None, nameTester=None, fumehoodId=None,
                 testScript=None, lockScript=None, flowScript=None, datetimeCreate=None):
        self.id = id
        self.nameTest = nameTest
        self.description = description
        self.nameTester = nameTester
        self.fumehoodId = fumehoodId
        self.testScript = testScript
        self.lockScript = lockScript
        self.flowScript = flowScript
        self.datetimeCreate = datetimeCreate

    def toDict(self):
        """Convert DataObj to a dictionary."""
        return {
            "id": self.id,
            "nameTest": self.nameTest,
            "description": self.description,
            "nameTester": self.nameTester,
            "fumehoodId": self.fumehoodId,
            "testScript": self.testScript,
            "lockScript": self.lockScript,
            "flowScript": self.flowScript,
            "datetimeCreate": self.datetimeCreate
        }

class DataObj:
    def __init__(self):
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
    def __init__(self, data, metadata=None, dataType = DataType()):
        self.timestamp = datetime.utcnow()
        self.data = data
        self.metadata = metadata if metadata else {}
        self.dataType = dataType
    
    def toDict(self):
        """Convert the DataPoint to a dictionary format."""
        return {
            'data': self.data,
            'dataType': self.dataType.getType(),
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    def __repr__(self):
        return f"<DataPoint(experimentId={self.experimentId}, deviceName={self.deviceName}, timestamp={self.timestamp})>"

class DataPointFDE(DataPoint): #Fluxidominus default database obj
    def __init__(self, data, metadata=None, dataType=DataType(), experimentId = "myNiceExperiment", deviceName = "NONE"):
        super().__init__(data, metadata, dataType)
        self.experimentId = experimentId
        self.deviceName = deviceName
    
    def toDict(self):
        """Convert the DataPoint to a dictionary format."""
        return {
            'experimentId': self.experimentId,
            'deviceName': self.deviceName,
            'timestamp': self.timestamp,
            'data': self.data,
            'dataType': self.dataType.getType(),
            'metadata': self.metadata
        }
    
    def __repr__(self):
        return f"{self.toDict()}"

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
        experimentId="exp123",
        deviceName="flowsynmaxi2",
        data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
        metadata={"location": "Room 101", "type": "temperature"}
    )
    
    dp2 = DataPoint(
        experimentId="exp123",
        deviceName="IRSCANNER",
        data={'irScan': [1.2, 3.4, 5.6, 0.8]},
        metadata={"location": "Room 101", "type": "IR"},
        dataType=DataType("BEER_FOR_BOYS").type()
    )

    # Create DataSet and add DataPoints
    dataSet = DataSet()
    dataSet.addDataPoint(dp1)
    dataSet.addDataPoint(dp2)

    # Print DataSet
    print(dataSet)
    print(dataSet.toDict())
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

class DataPoint:
    def __init__(self, experimentId, deviceName, data, metadata=None):
        self.experimentId = experimentId
        self.deviceName = deviceName
        self.timestamp = datetime.utcnow()
        self.data = data
        self.metadata = metadata if metadata else {}
    
    def toDict(self):
        """Convert the DataPoint to a dictionary format."""
        return {
            'experimentId': self.experimentId,
            'deviceName': self.deviceName,
            'timestamp': self.timestamp,
            'data': self.data,
            'metadata': self.metadata
        }
    
    def __repr__(self):
        return f"<DataPoint(experimentId={self.experimentId}, deviceName={self.deviceName}, timestamp={self.timestamp})>"

class DataSet:
    def __init__(self):
        self.dataPoints = []

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
        metadata={"location": "Room 101", "type": "IR"}
    )
    
    dp3 = DataPoint(
        experimentId="exp123",
        deviceName="FIZZBANG",
        data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
        metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
    )

    # Create DataSet and add DataPoints
    dataSet = DataSet()
    dataSet.addDataPoint(dp1)
    dataSet.addDataPoint(dp2)
    dataSet.addDataPoint(dp3)

    # Print DataSet
    print(dataSet)
    print(dataSet.toDict())

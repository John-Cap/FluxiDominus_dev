
import time
from Core.Data.data import DataPointFDE, DataSetFDD, DataType
from Core.Data.database import TimeSeriesDatabaseMongo


host = "146.64.91.174"
port = 27017
database_name = "Pharma"
collection_name = "pharma-data"

tsdm=TimeSeriesDatabaseMongo(host,port,database_name,collection_name,[])

dp1 = DataPointFDE(
    labNotebookRef="MY_REF_1",
    deviceName="flowsynmaxi2",
    data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
    metadata={"location": "Room 101"}
).toDict()

dp2 = DataPointFDE(
    labNotebookRef="MY_REF_2",
    dataType=DataType("JUMP_THE_MOON"),
    deviceName="IRSCANNER",
    data={'irScan': [1.2, 3.4, 5.6, 7.8]},
    metadata={"location": "Room 101", "type": "IR"}
).toDict()

dp3 = DataPointFDE(
    labNotebookRef="MY_REF_1",
    deviceName="FIZZBANG",
    data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
    metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
).toDict()

dp4 = DataPointFDE(
    labNotebookRef="MY_REF_1",
    dataType=DataType("IR_SCAN"),
    data={'irScan': [1.2, 3.4, 5.6, 7.8]},
    metadata={"location": "Room 101", "type": "IR"}
).toDict()

dp5 = DataPointFDE(
    labNotebookRef="MY_REF_2",
    deviceName="FIZZBANG",
    data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
    metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
).toDict()

dataSet=DataSetFDD(
    [dp1,dp2,dp3,dp4,dp5,dp1,dp2,dp3,dp4,dp5]
)

ts_db = TimeSeriesDatabaseMongo(host, port, database_name, collection_name,[])
ts_db.start(orgId="309930",labNotebookRef="MY_REF_2")
_testNum=["MY_REF_2","MY_REF_1"]
for _x in dataSet.dataPoints:
    #_x.labNotebookRef=random.choice(_testNum)
    ts_db.insertDataPoint(_x)
    time.sleep(3)
ts_db.pauseInsertion=True
print(ts_db.fetchTimeSeriesData(orgId="309930",labNotebookRef="MY_REF_2"))
ts_db.kill()
#ts_db.start()

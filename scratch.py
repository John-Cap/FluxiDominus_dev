
import random
import time
from Core.Data.data import DataPointFDE, DataSetFDD, DataType
from Core.Data.database import TimeSeriesDatabaseMongo


if __name__ == "__main__":
    host = "146.64.91.174"
    port = 27017
    database_name = "Pharma"
    collection_name = "pharma-data"
    
    tsdm=TimeSeriesDatabaseMongo(host,port,database_name,collection_name,[])
    
    dp1 = DataPointFDE(
        deviceName="flowsynmaxi2",
        data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
        metadata={"location": "Room 101"}
    ).toDict()

    dp2 = DataPointFDE(
        dataType=DataType("JUMP_THE_MOON"),
        deviceName="IRSCANNER",
        data={'irScan': [1.2, 3.4, 5.6, 7.8]},
        metadata={"location": "Room 101", "type": "IR"}
    ).toDict()

    dp3 = DataPointFDE(
        experimentId="exp123",
        deviceName="FIZZBANG",
        data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
        metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
    ).toDict()

    dp4 = DataPointFDE(
        dataType=DataType("IR_SCAN"),
        experimentId="exp123",
        deviceName="IRSCANNER",
        data={'irScan': [1.2, 3.4, 5.6, 7.8]},
        metadata={"location": "Room 101", "type": "IR"}
    ).toDict()

    dp5 = DataPointFDE(
        experimentId="exp123",
        deviceName="FIZZBANG",
        data={'numOfFloff': [1.2, 3.4, 5.6, 0.8, 0]},
        metadata={"location": "Room 101", "type": "U_N_K_N_O_W_N"}
    ).toDict()
    
    dataSet=DataSetFDD(
        [dp1,dp2,dp3,dp4,dp5,dp1,dp2,dp3,dp4,dp5]
    )

    ts_db = TimeSeriesDatabaseMongo(host, port, database_name, collection_name,[])
    ts_db.start()
    _testNum=[123,321]
    for _x in dataSet.dataPoints:
        _x["testId"]=random.choice(_testNum)
        ts_db.insertDataPoint(_x)
        time.sleep(3)
    ts_db.purgeAndPause()
    #ts_db.start()

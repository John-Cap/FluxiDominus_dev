
#################################
#Database operations example
from datetime import datetime, timedelta
import random
import time

from Core.Data.data import DataPointFDE, DataSetFDD
from Core.Data.database import DatabaseOperations, MySQLDatabase, TimeSeriesDatabaseMongo
from Core.Data.experiment import StandardExperiment
from Core.UI.plutter import MqttService

if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService()
    thisThing.start()
    thisThing.orgId="309930"
    #Instantiate
    dbOp=DatabaseOperations(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=thisThing)
    dbOp.connect()
    notebookRef='WJ_TEST_12'
    testNames = [notebookRef,"WJ_SECOND"]
    
    ##################################
    #Create exp
    stdExp=dbOp.createStdExp(
        labNotebookRef=notebookRef
    )
    id=stdExp.id
    
    ##################################
    #MySql
    theseTests=dbOp.getReplicateIds(notebookRef)
    print(theseTests)
    print('\n')
    ##################################
    #Mongo

    runNrs=dbOp.getRunNrs(notebookRef)
    labNotebookRefs=[notebookRef]
    devices=["FLOWSYNMAXI","OHM_DEVICE","A_BICYCLE_BUILT_FOR_TWO"]
    dataSet=[]
    
    sillyVal=1
    
    print([id,runNrs])
    _i=50
    
    dbOp.setZeroTime(id=theseTests[-1])
    dbOp.mongoDb.prevZeroTime=datetime.now()

    while _i > 0:
        dataSet.append(DataPointFDE(
            orgId="309930",
            testId=id,
            runNr=runNrs[-1],
            labNotebookRef=(random.choice(labNotebookRefs)),
            deviceName=(random.choice(devices)),
            data={'systemPressure': sillyVal, 'pumpPressure': 3.4, 'temperature': 22.5},
            metadata={"location": "Room 101"},
            zeroTime=thisThing.zeroTime
        ).toDict())
        sillyVal+=1
        dbOp.mongoDb.insertDataPoint(dataSet[-1])
        _i-=1
        time.sleep(random.choice([0.5,15]))

    dbOp.setStopTime(theseTests[-1])

    print(dbOp.mySqlDb.fetchRecordsByColumnValue('testruns','id',theseTests[-1]))
        
    dbOp.createReplicate(notebookRef)
    theseTests=dbOp.getReplicateIds(notebookRef)
    
    runNrs=dbOp.getRunNrs(notebookRef)
    print([id,runNrs])
    _i=50
    
    dbOp.setZeroTime(id=theseTests[-1])
    dbOp.mongoDb.currZeroTime=datetime.now()

    sillyVal=1

    start=time.time()
    streamEvery=2
    meh=False  
    while _i > 0:
        if not meh or (time.time()-start>streamEvery):
            start=time.time()
            if not meh:
                meh=True
            print('\n')
            print('###########################')
            print(f"Corresponding data from {streamEvery} seconds ahead in previous experiment:")
            print(dbOp.mongoDb.streamTimeBracket(currentTestId=id,previousTestId=id,timeWindowInSeconds=streamEvery,currentRunNr=1,previousRunNr=0))
        dataSet.append(DataPointFDE(
            orgId="309930",
            testId=id,
            runNr=runNrs[-1],
            labNotebookRef=(random.choice(labNotebookRefs)),
            deviceName=(random.choice(devices)),
            data={'systemPressure': 1.2, 'pumpPressure': 3.4, 'temperature': 22.5},
            metadata={"location": "Room 101"},
            zeroTime=thisThing.zeroTime
        ).toDict())
        sillyVal+=1
        dbOp.mongoDb.insertDataPoint(dataSet[-1])
        
        _i-=1
        time.sleep(random.choice([0.5,15]))

    dbOp.setStopTime(theseTests[-1])

    print(dbOp.mySqlDb.fetchRecordsByColumnValue('testruns','id',theseTests[-1]))
        
    '''
    thisData=DataSetFDD(dataSet)
    dbOp.mongoDb.start("309930","WJ_Disprin")
    dbOp.mongoDb.pauseFetching=True
    for _x in thisData.dataPoints:
        dbOp.mongoDb.insertDataPoint(_x)
        time.sleep(0.25)
    dbOp.mongoDb.pauseInsertion=True

    thisInput=0
    while True:
        thisInput=eval(input('Input timeWindowInSeconds: '))
        if thisInput == -1:
            break
        #print(dbOp.mongoDb.streamData(runNr=lastRun,testId=testId,timeWindowInSeconds=thisInput))

    dbOp.mongoDb.kill()
######################################
'''
'''
# Example usage //Kyk, camel vs snekcase
if __name__ == "__main__":
    db = MySQLDatabase(
        host="146.64.91.174",
        port=3306,
        user="pharma",
        password="pharma",
        database="pharma"
    )

    db.connect()

    ret=db.fetchRecordsByColumnValue("testlist","orgId","309930")
    for x in ret:
        print(x)

    db.close()

if __name__ == "__main__":
    
    #################################################
    #MySQL
    db = MySQLDatabase(
        host="146.64.91.174",
        port=3306,
        user="pharma",
        password="pharma",
        database="pharma"
    )

    db.connect()
    ## id, nameTest, description, nameTester, fumehoodId, testScript, lockScript, flowScript, datetimeCreate, labNotebookRef
    ##'146', 'asd', 'asd', 'asd', 'd8:3a:dd:55:99:09', ?, '0', ?, '2024-03-22 08:14:12', NULL

    records = [
        ("Mr_Test","Just_a_test","MRS_TEST","MAC MAC",b"Hi there!",0,b"NO VAL",datetime.now(),"THIS_REF_1","309930"),
        ("Mr_Test2","Just_a_test","MRS_TEST","MAC MAC",b"Hi there!",0,b"NO VAL",datetime.now(),"THIS_REF_2","309930"),
        ("Mr_Test3","Just_a_test","MRS_TEST","MAC MAC",b"Hi there!",0,b"NO VAL",datetime.now(),"THIS_REF_3","309930"),
    ]
    db.insertRecords("testlist", records) #['orgId', 'lastLogin', 'firstName', 'lastName']
    
    results = db.fetchRecordsByColumnValue("testlist","orgId","309930")
    for row in results:
        print(row)
        
    print(db.fetchRecordByColumnValue("users","orgId","309930"))
        
    db.close()
    ################################################
    #Mongo
    host = "146.64.91.174"
    port = 27017
    databaseName = "Pharma"
    collectionName = "pharma-data"

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

    ts_db = TimeSeriesDatabaseMongo(host, port, databaseName, collectionName,[])
    ts_db.start(orgId="309930",labNotebookRef="MY_REF_2")
    _testNum=["MY_REF_2","MY_REF_3"]
    for _x in dataSet.dataPoints:
        _x.labNotebookRef=random.choice(_testNum)
        ts_db.insertDataPoint(_x)
        time.sleep(3)
    ts_db.pauseInsertion=True
    print(ts_db.fetchTimeSeriesData(orgId="309930",labNotebookRef="MY_REF_2"))
    ts_db.kill()
    #ts_db.start()
'''
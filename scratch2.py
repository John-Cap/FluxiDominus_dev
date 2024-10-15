
from ast import literal_eval
import json
from bson import utc
import mysql.connector
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import threading

from Config.Data.hardcoded_command_templates import HardcodedTeleAddresses
from Core.Data.experiment import StandardExperiment
from Core.UI.plutter import MqttService

class Database:
    def __init__(self) -> None:
        pass

class MySQLDatabase:
    def __init__(self, host='localhost',port=3306,user="pharma",password="pharma",database="pharma"):
        """Initialize the MySQLDatabase class with connection parameters."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
        self.tableVar={
            "users":['orgId', 'email', 'cellphone', 'lastLogin', 'firstName', 'lastName', 'password', 'admin', 'active', 'assignedProjects'],
            "testlist":['projId', 'userId', 'description', 'labNotebookBaseRef', 'datetimeCreate', 'locked'],
            "testruns":['testlistId', 'labNotebookBaseRef', 'runNr', 'createTime', 'startTime', 'endTime', 'locked', 'testScript', 'flowScript', 'optimizer', 'optimizerModel', 'recorded', 'notes', 'availableTele'],
            "projects":['projCode', 'description', 'active'],
            "fumehoods":['fumehoodNr', 'macAddr', 'ipAddr', 'port', 'userId']
        } #hardcoded
    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print("Connected to the database.")
        except OSError as e:
            print(f"WJ - Database connection error: {e}")
            self.connection = None

    def createTable(self, tableName, schema):
        """Create a table with the given schema."""
        if self.cursor:
            createTableQuery = f"""
            CREATE TABLE IF NOT EXISTS {tableName} (
                {schema}
            )
            """
            self.cursor.execute(createTableQuery)
            print(f"Table '{tableName}' created successfully.")

    def insertRecords(self, tableName, records):
        """Insert multiple records into the specified table."""
        if not isinstance(records,list):
            records=[records]
        if self.cursor:
            columns=self.tableVar[tableName]
            insertQuery = f"""
            INSERT INTO {tableName} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
            """
            self.cursor.executemany(insertQuery, records)
            self.connection.commit()
            print(f"Records inserted successfully into '{tableName}'.")
            
    def updateRecordById(self, tableName, uniqueId, columnName, newValue, override=True):
        """Update a specific column's value in a row identified by a unique ID. override=True allows a current value to be overriden."""
        if self.cursor:
            if not override:
                # Check the current value of the column
                checkQuery = f"""
                SELECT {columnName} FROM {tableName} WHERE id = %s
                """
                self.cursor.execute(checkQuery, (uniqueId,))
                currentValue = self.cursor.fetchone()

                # If there is a current value and it's not NULL or empty, skip the update
                if currentValue and currentValue[0] not in (None, '', 'NULL'):
                    print(f"Update skipped: Column '{columnName}' already has a value in record with ID {uniqueId}.")
                    return
            
            # Prepare the SQL query to update the specific column in the table.
            updateQuery = f"""
            UPDATE {tableName}
            SET {columnName} = %s
            WHERE id = %s
            """
            # Execute the query with the provided newValue and uniqueId
            self.cursor.execute(updateQuery, (newValue, uniqueId))
            # Commit the transaction to the database
            self.connection.commit()
            print(f"Record with ID {uniqueId} updated successfully in '{tableName}'.")

    def fetchRecordById(self, tableName, id):# WHERE id=%s
        """Fetch all records from the specified table."""
        if self.cursor:
            fetchQuery = f"SELECT * FROM {tableName} WHERE id=%s"
            self.cursor.execute(fetchQuery,[id])
            results = self.cursor.fetchone()
            return results

    def fetchRecords(self, tableName):# WHERE id=%s
        """Fetch all records from the specified table."""
        if self.cursor:
            fetchQuery = f"SELECT * FROM {tableName}"
            self.cursor.execute(fetchQuery)
            results = self.cursor.fetchall()
            return results

    def fetchRecordByColumnValue(self, tableName, columnName, value):
        """Fetch a single record from the specified table where the column matches the given value."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {columnName} = %s"
            self.cursor.execute(fetch_query, (value,))
            result = self.cursor.fetchone()  # fetchone returns a single matching row
            return result
        
    def fetchRecordByColumnValues(self, tableName, column1Name, value1, column2Name, value2):
        """Fetch a single record from the specified table where two columns match the given values."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {column1Name} = %s AND {column2Name} = %s"
            self.cursor.execute(fetch_query, (value1, value2))
            result = self.cursor.fetchone()  # fetchone returns a single matching row
            return result
        
    def fetchSpecifiedColumnsByValues(self, tableName, columnNames, column1Name, value1, column2Name, value2):
        """Fetch specified columns from a table where two columns match the given values."""
        if self.cursor:
            # Join the list of column names into a single string separated by commas
            columns = ", ".join(columnNames)
            fetch_query = f"SELECT {columns} FROM {tableName} WHERE {column1Name} = %s AND {column2Name} = %s"
            self.cursor.execute(fetch_query, (value1, value2))
            result = self.cursor.fetchone()  # fetchone returns a single matching row
            return result
        
    def fetchRecordsByColumnValues(self, tableName, column1Name, value1, column2Name, value2):
        """Fetch specified columns from a table where two columns match the given values."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {column1Name} = %s AND {column2Name} = %s"
            self.cursor.execute(fetch_query, (value1,value2))
            result = self.cursor.fetchall()
            return result

    def fetchRecordsByColumnValue(self, tableName, columnName, value):
        """Fetch all records from the specified table where the column matches the given value."""
        if self.cursor:
            fetch_query = f"SELECT * FROM {tableName} WHERE {columnName} = %s"
            self.cursor.execute(fetch_query, (value,))
            result = self.cursor.fetchall()
            return result
        
    def fetchColumnValById(self, tableName, columnName, id):
        """
        Fetches the value from a specified column by row ID.

        """
        try:
            if self.connection.is_connected():
                if tableName not in self.tableVar:
                    print(f"Error: Table '{tableName}' not found in tableVar.")
                    return None

                # Ensure column exists in the table schema
                if columnName not in self.tableVar[tableName]:
                    print(f"Error: Column '{columnName}' does not exist in table '{tableName}'.")
                    return None

                # Formulate the query
                query = f"SELECT {columnName} FROM {tableName} WHERE id = %s"
                self.cursor.execute(query, (id,))
                
                # Fetch the result
                result = self.cursor.fetchone()
                if result:
                    return result[0]
                else:
                    print(f"No row found with ID {id}.")
                    return None
        except mysql.connector.Error as e:
            print(f"Error fetching data: {e}")
            return None
                        
    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")

class TimeSeriesDatabaseMongo:
    def __init__(self, host='localhost', port=27017, databaseName="Pharma", collectionName="pharma-data"):
        #self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.client = MongoClient(host=host,port=port)
        self.db = self.client[databaseName]
        self.collection = self.db[collectionName]
        self.dataPoints=[]
        self.insertionInterval=10
        self.pauseInsertion=True
        self.pauseFetching=True
        self.insertionThread=None
        self.fetchingThread=None
        
        self.currZeroTime=None
        self.prevZeroTime=None
        
        self.currStopTime=None
        self.prevStopTime=None

    def insertDataPoint(self,dataPoint):
        self.collection.insert_one(dataPoint)

    def insertDataPoints(self,dataPoints):
        self.collection.insert_many(dataPoints)
        
    def continuousInsertion(self):
        while True:
            while self.pauseInsertion:
                time.sleep(0.1)
            if self.dataPoints is None or len(self.dataPoints)==0:
                pass
            else:
                _numOf=len(self.dataPoints)
                for _x in self.dataPoints:
                    self.insertDataPoint(_x)
                self.dataPoints=[]
                print('WJ - Inserted '+str(_numOf)+' datapoints into database '+str(self.db)+'!')
            time.sleep(self.insertionInterval) #Kannie so lank hier wag nie

    def fetchTimeSeriesData(self, testlistId, testrunId, startTime: datetime = None, endTime: datetime = None, nestedField: str = None, nestedValue=None):
        # Prepare the query with required filters
        query = {
            'metadata.testlistId': testlistId,
            'metadata.testrunId': testrunId
        }

        # Add time filtering to the query if provided
        if startTime:
            if not (startTime.tzname()):
                startTime.replace(tzinfo=utc).isoformat()
        if endTime:
            if not (endTime.tzname()):
                endTime.replace(tzinfo=utc).isoformat()
        query['timestamp'] = {'$gte': startTime, '$lte': endTime}

        # Add nested field filtering if provided
        if (nestedField and nestedValue): #Include 'field':value requirement to search
            query[nestedField] = nestedValue
        elif nestedField:
            query[nestedField] = {'$exists': True} #Fetch if nested field exists regardless of value
        print(f'Query: ${query}')
        # Fetch and sort the data
        cursor = self.collection.find(query).sort('timestamp', 1)
        _ret = []
        _num = 0
        for document in cursor:
            _ret.append(document)
            _num += 1

        # Uncomment the line below to print the number of fetched documents
        print(f'Fetched {_num} documents for experiment {testlistId} from {startTime} to {endTime} with nested field {nestedField} = {nestedValue}!')
        return _ret
    
    def streamData(self, testlistId, testrunId, timeWindowInSeconds, now=None, nestedField: str = None, nestedValue=None):
        if now is None:
            now = datetime.now()

        if timeWindowInSeconds < 0:  # into past
            endTime = now
            startTime = max(now - timedelta(seconds=abs(timeWindowInSeconds)), self.currZeroTime)
        else:  # into future
            startTime = now
            endTime = now + timedelta(seconds=timeWindowInSeconds) #Must also check if 'endTime' is within time bracket

        return self.fetchTimeSeriesData(testlistId=testlistId, testrunId=testrunId, startTime=startTime, endTime=endTime, nestedField=nestedField, nestedValue=nestedValue)

    def streamTimeBracket(self, testlistId, testrunId, timeWindowInSeconds=0,  now=None, nestedField=None, nestedValue=None):
        if now is None:
            now = datetime.now()

        # Calculate elapsed time since the start of the current experiment
        elapsedTime = (now - self.currZeroTime).total_seconds()
        
        print(f'WJ - Elapsed time: {elapsedTime}')

        # Calculate the corresponding start and end times for the previous experiment
        prevStartTime = self.prevZeroTime + timedelta(seconds=elapsedTime)
        prevEndTime = prevStartTime + timedelta(seconds=timeWindowInSeconds)

        return self.fetchTimeSeriesData(testlistId=testlistId, testrunId=testrunId, startTime=prevStartTime, endTime=prevEndTime, nestedField=nestedField, nestedValue=nestedValue)

    def continuousFetching(self, **kwargs):
        orgId = kwargs.get('orgId')
        labNotebookBaseRef = kwargs.get('labNotebookBaseRef')
        try:
            while not self.pauseFetching:
                self.fetchTimeSeriesData(orgId,labNotebookBaseRef)
                time.sleep(6)  # Fetch data every 10 seconds
        except KeyboardInterrupt:
            print("Stopped fetching data.")

    def kill(self):
        self.pauseInsertion=True
        self.pauseFetching=True

    def pause(self):
        self.pauseInsertion=True
        self.pauseFetching=True

    def purgeAndPause(self):
        self.dataPoints=[] #What happens if updater still wants to add some datapoints?
        self.pause()

    def start(self,orgId: str,labNotebookBaseRef: str,runId=0):
        kwargs={"orgId":orgId,"labNotebookBaseRef":labNotebookBaseRef,"runId":runId}
        if not (self.insertionThread is None):
            self.pauseInsertion=False
        else:
            
            insertion_thread = threading.Thread(target=self.continuousInsertion)
            fetching_thread = threading.Thread(target=self.continuousFetching,kwargs=kwargs)
            self.pauseInsertion = False
            self.pauseFetching = False

            insertion_thread.start()
            fetching_thread.start()

            #insertion_thread.join()
            #fetching_thread.join()
            
            self.insertionThread=insertion_thread
            self.fetchingThread=fetching_thread
                        
#################################
#Main class to interface with both db's

#Main
class DatabaseOperations:
    def __init__(self,mySqlDb=MySQLDatabase(),mongoDb=TimeSeriesDatabaseMongo(),mqttService=None) -> None:
        self.mySqlDb=mySqlDb
        self.mongoDb=mongoDb
        
        self.mqttService=mqttService
        
        self.currReplicate=None

    '''
    id	projId	userId	description	    labNotebookBaseRef	    datetimeCreate	    locked
    296	1	    22	    Making Disprins	50403_jdtoit_DSIP012A	2024-09-08 11:42:28	0
    '''

    def searchForTest(self, labNotebookBaseRef, tableName='testlist', columnName='labNotebookBaseRef'):
        return self.mySqlDb.fetchRecordByColumnValue(tableName,columnName,labNotebookBaseRef)

    def getReplicateIds(self, labNotebookBaseRef, tableName='testlist', columnName='labNotebookBaseRef'):
        testListId=self.getTestlistId(labNotebookBaseRef,tableName,columnName)
        replicates=self.mySqlDb.fetchRecordsByColumnValue('testruns','testlistId',testListId)
        ret=[]
        for _x in replicates:
            ret.append(_x[0])
        return ret
    
    def getTestrunId(self,labNotebookBaseRef,runNr): #'labNotebookBaseRef', 'runNr'
        return (self.mySqlDb.fetchRecordByColumnValues(tableName='testruns',column1Name='labNotebookBaseRef',value1=labNotebookBaseRef,column2Name='runNr',value2=runNr))[0]

    def getRunNrs(self, labNotebookBaseRef, tableName='testlist', columnName='labNotebookBaseRef'):
        replicates=self.getReplicateIds(labNotebookBaseRef,tableName,columnName)
        ret=[]
        for _x in replicates:
            ret.append(self.mySqlDb.fetchRecordByColumnValue('testruns','id',_x)[3])
        return ret

    def createTestlistEntry(self,userId,projId,labNotebookBaseRef,description="",testScript="",flowScript={},notes=""):
        '''testlist columns->projId, userId, description, labNotebookBaseRef, datetimeCreate, locked'''
        #Check if this project is assigned to user
        if isinstance(projId,str):
            projId=self.getProjId(projId)
        if not (projId in self.getUserProjects(userId=userId)):
            print('Project not assigned to user!')
            return -1
        #print([projId,userId,description,labNotebookBaseRef,datetime.now().isoformat(),0])
        insert=[(projId,userId,description,labNotebookBaseRef,datetime.now().isoformat(),0)]
        self.mySqlDb.insertRecords('testlist',insert)
        self.createReplicate(labNotebookBaseRef=labNotebookBaseRef,testScript=testScript,flowScript=flowScript,notes=notes)
        return self.getTestlistId(labNotebookBaseRef)
        
    def createReplicate(self,labNotebookBaseRef,testScript="",flowScript={},notes="",availableTele={}):
        '''
        id, testlistId, labNotebookBaseRef, runNr, createTime, startTime, endTime, locked, testScript, flowScript, optimizer, optimizerModel, recorded, notes
        '''
        testListId=self.getTestlistId(labNotebookBaseRef,'testlist','labNotebookBaseRef')
        replicates=self.getRunNrs(labNotebookBaseRef) #Error handling!
        idNext=-1
        if (len(replicates)==0):
            idNext=0
        else:
            idNext=replicates[-1] + 1
        if isinstance(flowScript,str):
            flowScript=flowScript.replace("'",'"')
            flowScript=flowScript.replace("null",'None')
            flowScript=eval(flowScript)
        insert=[(testListId,labNotebookBaseRef,idNext,datetime.now().isoformat(),None,None,0,json.dumps(testScript),json.dumps(flowScript),b'',b'',0,notes,json.dumps(availableTele))]
        print('WJ - Preparing to insert: '+str(insert))
        self.mySqlDb.insertRecords('testruns',insert)
        return idNext

    def getTestlistId(self,labNotebookBaseRef,tableName='testlist',columnName='labNotebookBaseRef'):
        return (self.mySqlDb.fetchRecordByColumnValue(tableName,columnName,labNotebookBaseRef)[0])

    def getTestlistRow(self,labNotebookBaseRef):
        return (self.mySqlDb.fetchRecordByColumnValue('testlist','labNotebookBaseRef',labNotebookBaseRef))
                                
    def getUserId(self,orgId=None,email=None):
        '''
        users columns->orgId	email   cellphone	lastLogin	firstName	lastName	password	admin	active
        '''
        if not orgId:
           return (self.mySqlDb.fetchRecordByColumnValue('users','email',email))[0]
        if not email:
           return (self.mySqlDb.fetchRecordByColumnValue('users','orgId',orgId))[0]

    def createProject(self,projCode,descript,active=1):
        self.mySqlDb.insertRecords('projects',(projCode,descript,active))
        
    def assignProject(self,projId,orgId=None,email=None):

        _proj=self.getUserProjects(orgId=orgId,email=email)
        if (isinstance(_proj,str)):
            _proj=eval(_proj)
        if (isinstance(projId,str)):
            projId=self.getProjId(projId)
        if _proj is None:
            _proj=[]
        if not (projId in _proj):
            _proj.append(projId)
        else:
            return -1
        _id=self.getUserId(orgId=orgId,email=email)
        self.mySqlDb.updateRecordById('users',_id,'assignedProjects',json.dumps(str(_proj))) #updateRecordById(self, tableName, uniqueId, columnName, newValue)
        return (len(_proj)-1)
        
    def getUserProjects(self,orgId=None,email=None,userId=None):
        _proj=self.getUserRow(orgId=orgId,email=email,userId=userId)[10]
        _proj=eval(literal_eval(_proj))
        if _proj is None:
            return []
        else:
            return _proj
        
    def getAllExpWidgetInfo(self,orgId=None):
        
        if not orgId:
            orgId=self.mqttService.orgId
        
        _ret={"getAllExpWidgetInfo":{}}
        _userId=self.getUserId(orgId)
        _userProj=self.getUserProjects(orgId) #Get all project ids
        if (isinstance(_userProj,str)):
            _userProj=eval(_userProj)
        for _x in _userProj: #For each project id, get its name, associated tests, and each test's testruns
            _ret["getAllExpWidgetInfo"][str(_x)]={}
            _ret["getAllExpWidgetInfo"][str(_x)]["projCode"]=self.getProjCode(_x)
            _ret["getAllExpWidgetInfo"][str(_x)]["projDescript"]=self.getProjDescript(_x)
            _ret["getAllExpWidgetInfo"][str(_x)]["testlistEntries"]={}
            for _y in self.mySqlDb.fetchRecordsByColumnValues(tableName='testlist',column1Name='projId',value1=_x,column2Name='userId',value2=_userId):
                _ret["getAllExpWidgetInfo"][str(_x)]["testlistEntries"][str(_y[0])]={
                    "testruns":self.getTestrunsByTestId(_y[0]),
                    "description":_y[3],
                    "labNotebookBaseRef":_y[4],
                    "datetimeCreate":_y[5].isoformat()
                }
        return json.dumps(_ret)

    def getUserProjsDet(self,orgId=None,email=None):
        _proj=self.getUserProjects(orgId=orgId,email=email)
        if len(_proj)!=0:
            _ret={}
            _proj=self.getProjsDet(_proj)
            _i=0
            for _x in _proj:
                _active=True
                if _x[3]==0:
                    _active=False
                _ret[_i]={
                    "projCode":_x[1],
                    "projDescript":_x[2],
                    "active":_active
                }
                _i+=1
            return _ret
        else:
            return {}
        
    def getProjsDet(self,proj):
        _ret=[]
        if isinstance(proj,str):
            proj=eval(proj)
        for _x in proj:
            _ret.append(self.mySqlDb.fetchRecordById(tableName='projects',id=_x))
        return _ret
    
    def getProjId(self,projCode):
        return self.mySqlDb.fetchRecordByColumnValue(tableName='projects',columnName='projCode',value=projCode)[0]
    
    def getProjCode(self,id):
        return (self.mySqlDb.fetchRecordById(tableName='projects',id=id))[1]
    
    def getProjDescript(self,id):
        return (self.mySqlDb.fetchRecordById(tableName='projects',id=id))[2]
        
    def getUserRow(self,orgId=None,email=None,userId=None):
        if orgId:
           return (self.mySqlDb.fetchRecordByColumnValue('users','orgId',orgId))
        elif email:
           return (self.mySqlDb.fetchRecordByColumnValue('users','email',email))
        elif userId:
            if isinstance(userId,str):
                userId=eval(userId)
            return (self.mySqlDb.fetchRecordByColumnValue('users','id',userId))
        
    def getPassword(self,orgId=None,email=None):
        if not orgId:
           return (self.mySqlDb.fetchRecordByColumnValue('users','email',email))[7]
        if not email:
           return (self.mySqlDb.fetchRecordByColumnValue('users','orgId',orgId))[7]
    
    def getTestlistId(self,labNotebookBaseRef,tableName='testlist',columnName='labNotebookBaseRef'):
        return (self.mySqlDb.fetchRecordByColumnValue(tableName,columnName,labNotebookBaseRef)[0])
                
    def getUserTests(self,orgId=None,email=None):
        _ret=[]
        if not orgId and email:
            _id=self.getUserId(email=email)
            for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testlist',columnName='userId',value=_id):
                _ret.append(_x[0])
            return _ret
        elif not email and orgId:
            _id=self.getUserId(orgId=orgId)
            for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testlist',columnName='userId',value=_id):
                _ret.append(_x[0])
            return _ret

    def getTestRunIds(self,labNotebookBaseRef):
        _ret=[]
        _id=self.getTestlistId(labNotebookBaseRef)
        for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testruns',columnName='testlistId',value=_id):
            _ret.append(_x[0])
        return _ret
        
    def getTestRuns(self,labNotebookBaseRef):
        _ret=[]
        _id=self.getTestlistId(labNotebookBaseRef=labNotebookBaseRef)
        for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testruns',columnName='testlistId',value=_id):
            _x=list(_x)
            for _i, _y in enumerate(_x):
                if isinstance(_y,datetime):
                    _x[_i]=_y.isoformat()
                if isinstance(_y,bytes):
                    _x[_i]=_y.decode()
            _ret.append(_x)
        return _ret
        
    def getTestrunsByTestId(self,id):
        _ret=[]
        for _x in self.mySqlDb.fetchRecordsByColumnValue(tableName='testruns',columnName='testlistId',value=id):
            _x=list(_x)
            for _i, _y in enumerate(_x):
                if isinstance(_y,datetime):
                    _x[_i]=_y.isoformat()
                if isinstance(_y,bytes):
                    _x[_i]=_y.decode()
            _ret.append(_x)
        return _ret
    
    def registerAvailableTele(self,testrunId,device,setting):
        '''
        testrunId: id for 'testlist' table \n
        device: device name (eg. 'sf10vapourtec1') \n
        setting: key for desired tele (eg. 'pafr') \n
        displayName: UI-name for telemetry
        '''
        _insrt=self.mySqlDb.fetchColumnValById('testruns','availableTele',testrunId)
        if _insrt == "" or _insrt == "{}":
            _insrt={}
        else:
            _insrt=eval(_insrt)
        _changed=False
        if not device in _insrt:
            if isinstance(setting,list):
                _insrt[device]=setting
            else:
                _insrt[device]=[setting]
            _changed=True
        else:
            if isinstance(setting,list):
                for _x in setting:
                    if not _x in _insrt[device]:
                        _insrt[device].append(_x)
                        if not _changed:
                            _changed=True
            else:
                if not setting in _insrt[device]:
                    (_insrt[device]).append(setting)
                    _changed=True
                else:
                    return
        if _changed:
            self.mySqlDb.updateRecordById('testruns',testrunId,'availableTele',json.dumps(_insrt))
        else:
            print('Record not altered')
            
    def getAvailableTele(self,testrunId):
        '''
        testrunId: id for 'testlist' table
        '''
        return eval(self.mySqlDb.fetchColumnValById('testruns','availableTele',testrunId))
    
    def getAvailableTeleForDevice(self,testrunId,device):
        '''
        testrunId: id for 'testlist' table
        '''
        return (eval(self.mySqlDb.fetchColumnValById('testruns','availableTele',testrunId)).get(device,[]))
    
    '''
    def createStdExp(self,labNotebookBaseRef,nameTest="Short description",description="Long description",flowScript=b"",testScript=b"script_content"):
        ret=(StandardExperiment(self.mySqlDb,tables=["testlist"])).createExperiment(
            nameTest=nameTest,
            nameTester="",
            lockScript=0,
            flowScript=flowScript,
            description=description,
            testScript=testScript,
            labNotebookBaseRef=labNotebookBaseRef,
            orgId=self.mqttService.orgId
        )
        self.createReplicate(labNotebookBaseRef=labNotebookBaseRef)
        return ret
    '''
    def setZeroTime(self, id, zeroTime=None):
        if not zeroTime:
            zeroTime=datetime.now(tz=utc)
        self.mySqlDb.updateRecordById(tableName='testruns',uniqueId=id,columnName='startTime',newValue=zeroTime)
    def setStopTime(self, id, stopTime=None):
        if not stopTime:
            stopTime=datetime.now(tz=utc)
        self.mySqlDb.updateRecordById(tableName='testruns',uniqueId=id,columnName='endTime',newValue=stopTime)

    def connect(self):
        self.mySqlDb.connect()
        self.mongoDb.purgeAndPause() #Good idea? :/

    def fetchStreamingBracket(self,labNotebookBaseRef,runNr): #Fetches previous experiment's start time and end time
        _ret=self.mySqlDb.fetchSpecifiedColumnsByValues(tableName='testruns',columnNames=['startTime','endTime'],column1Name='labNotebookBaseRef',value1=labNotebookBaseRef,column2Name='runNr',value2=runNr)
        return [_ret[0],_ret[1]]
    
    def setStreamingBracket(self,labNotebookBaseRef,runNr): #Fetches previous experiment's start time and end time
        _ret=self.fetchStreamingBracket(labNotebookBaseRef,runNr)
        self.mongoDb.prevZeroTime=_ret[0]
        self.mongoDb.prevStopTime=_ret[1]

class ParseStreamingData: #Defines what exactly to send to Flutter
    def __init__(self) -> None:
        self._protocols={
            '''
            Function pointers that parse data to be sent to UI
            "hotcoil1":{'fr',function}
            '''
        }

class DatabaseStreamer(DatabaseOperations):
    def __init__(self, mySqlDb=MySQLDatabase(), mongoDb=TimeSeriesDatabaseMongo(), mqttService=None) -> None:
        super().__init__(mySqlDb, mongoDb, mqttService)
        self.loopThread=None
        self.dataQueues={} #Contains id:[...data], id tells Flutter where streamed data must go
        self.streamRequestDetails={}
        self.zeroTimes={}

    def handleStreamRequest(self,req: dict): #Looks at 'req' received from Flutter and works out what it wants
        '''
        Fetches and publishes requested telemetry for time period
        '''       
        id=req["id"]
        if not (id in self.streamRequestDetails):
            self.streamRequestDetails[id]={}
        self.streamRequestDetails[id]["labNotebookBaseRef"]=req["labNotebookBaseRef"]
        self.streamRequestDetails[id]["runNr"]=req["runNr"]
        self.streamRequestDetails[id]["timeWindow"]=req["timeWindow"]
        self.streamRequestDetails[id]["deviceName"]=req["deviceName"]
        self.streamRequestDetails[id]["setting"]=req["setting"]
        
        #Hardcoded
        self.streamRequestDetails[id]["nestedField"]="data.deviceName"
        self.streamRequestDetails[id]["nestedValue"]=self.streamRequestDetails[id]["deviceName"]
        
        return self._returnMqttStreamRequest(id)

    def _streamingThread(self): #TODO
        pass

    def _packageData(self,data,deviceName,setting,timestamp,zeroTime):
        _val=HardcodedTeleAddresses.getValFromAddress(data,device=deviceName,setting=setting)
        return [(timestamp - zeroTime).total_seconds(),_val]
    
    def _returnMqttStreamRequest(self,id):
        if not (id in self.dataQueues):
            self.dataQueues[id]=[]
        _rec=self._streamFrom(
            labNotebookBaseRef=self.streamRequestDetails[id]["labNotebookBaseRef"],
            runNr=self.streamRequestDetails[id]["runNr"],
            timeWindow=self.streamRequestDetails[id]["timeWindow"],
            nestedField=self.streamRequestDetails[id]["nestedField"],
            nestedValue=self.streamRequestDetails[id]["nestedValue"]
        )
        _ret=[]
        _zT=(self.fetchStreamingBracket(
            labNotebookBaseRef=self.streamRequestDetails[id]["labNotebookBaseRef"],
            runNr=self.streamRequestDetails[id]["runNr"]
        ))[0]
        for _x in _rec:
            _ret.append(self._packageData(
                _x["data"],
                self.streamRequestDetails[id]["deviceName"],
                self.streamRequestDetails[id]["setting"],
                _x["timestamp"],
                _zT
            ))
        _data={"handleStreamRequest":{id:_ret}}
        self.streamRequestDetails[id]={}
        self.dataQueues[id]=[]
        return json.dumps(_data)

    def _streamFrom(self,labNotebookBaseRef,runNr,timeWindow=30,nestedField: str = None,nestedValue=None): #This is not streaming
        return self._retrieve(labNotebookBaseRef,runNr,timeWindow,nestedField,nestedValue)
                
    def _retrieve(self,labNotebookBaseRef,runNr,timeWindow,nestedField: str = None,nestedValue=None):
        self.setStreamingBracket(labNotebookBaseRef,runNr)
        return self.mongoDb.streamTimeBracket(testlistId=(self.getTestlistId(labNotebookBaseRef)),timeWindowInSeconds=timeWindow,testrunId=self.getTestrunId(labNotebookBaseRef,runNr),nestedField=nestedField,nestedValue=nestedValue)
#################################
#Database operations example
if __name__ == '__main__':
    #Mqtt
    thisThing=MqttService()
    thisThing.start()
    thisThing.orgId="309930"
    #Instantiate
    dbOp=DatabaseOperations(mySqlDb=MySQLDatabase(host='146.64.91.174'),mongoDb=TimeSeriesDatabaseMongo(host='146.64.91.174'),mqttService=thisThing)
    dbOp.connect()
    
    dbOp.mySqlDb.updateRecordById('testruns',137,'startTime',datetime.now(),override=True)
    
    time.sleep(5)
    
    dbOp.mySqlDb.updateRecordById('testruns',137,'startTime',datetime.now(),override=False)
    
    dbOp.mongoDb.kill()
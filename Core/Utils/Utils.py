import re
from datetime import datetime, timedelta
from time import sleep

class Utils:
    def __init__(self) -> None:
        self.conversions = {
            "null": None,
            "none": None,
            "true": True,
            "false": False
        }

    def getOrDef(self, dictionary, key, default):
        """
        Fetches the value from the dictionary for the given key. If the key is not present, returns the default value.
        """
        return dictionary.get(key, default)

    def findIn(self,item,items):
        pass

    def removeComments(self,text):
        # Pattern to match /* ... */
        pattern = r'/\*.*?\*/'
        # Replace matched pattern with an empty string
        return re.sub(pattern, '', text, flags=re.DOTALL)

    def parseToFloat(self,s):
        """Parse the string to a float if it's a number."""
        if self.isNumeric(s):
            return float(s)
        else:
            raise ValueError(f"'{s}' is not a valid number.")

    @staticmethod
    def isNumeric(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def parseValue(self,value):
        if not isinstance(value,str):
            return value
        _lowerValue = value.lower()

        if _lowerValue in self.conversions:
            return self.conversions[_lowerValue]
        elif Utils.isNumeric(value):
            return float(value)
        else:
            return value
import os
from datetime import datetime

class TimestampGenerator:
    def __init__(self, genesisTime: datetime = None):
        if genesisTime is None:
            self.genesisTime = datetime.now()
        else:
            self.genesisTime = genesisTime
    
    def generateTimestamp(self) -> str:
        currentTime = datetime.now()
        timestamp = currentTime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return timestamp
    
    def convertToSecondsSinceGenesis(self, timestamp: str) -> float:
        timestampFormat = "%Y-%m-%d %H:%M:%S.%f"
        timestampDatetime = datetime.strptime(timestamp, timestampFormat)
        timeDelta = timestampDatetime - self.genesisTime
        return timeDelta.total_seconds()

class DataLogger:
    def __init__(self, logFilename: str, logDir: str = 'Debug'):
        self.logDir = logDir
        self.logFilename = logFilename
        
        # Ensure the log directory exists
        os.makedirs(self.logDir, exist_ok=True)
        
        # Set the full path for the log file
        self.logFilePath = os.path.join(self.logDir, self.logFilename)
        
        # Initialize the timestamp generator
        self.timestampGenerator = TimestampGenerator()
        
    def logData(self, value: float, array: list):
        timestamp = self.timestampGenerator.generateTimestamp()
        with open(self.logFilePath, 'a') as logFile:
            arrayStr = str(array)
            logLine = f"{timestamp}, {value}, {arrayStr}\n"
            logFile.write(logLine)
            logFile.flush()  # Ensure the data is written to the file immediately

if __name__ == "__main__":

    # Example usage
    logger = DataLogger('continuous_log.txt')
    # Generate some example data
    value = 123.456
    array = [1, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5, 2, 3, 4, 5]
    # Log the data
    logger.logData(value, array)
    sleep(5)
    
    # Generate some example data
    value = 113.456
    array = [5, 2, 3, 5, 1]
    # Log the data
    logger.logData(value, array)
    sleep(5)
    
    # Generate some example data
    value = 125
    array = [1, 35, 3, 4,1]
    # Log the data
    logger.logData(value, array)
import os
import re
from datetime import datetime, timedelta
from time import sleep
import uuid

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

    def generateUuid():
        uniqueId = str(uuid.uuid1())
        return uniqueId

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
            
class Bracketer:
    def __init__(self, minValue, maxValue):
        """
        Initializes the Bracketer with a given range [minValue, maxValue].
        """
        self.minValue = minValue
        self.maxValue = maxValue

    def fromBracket(self, value):
        """
        Scales the given value from the range [minValue, maxValue] to [0, 1].
        """
        return (value - self.minValue) / (self.maxValue - self.minValue)

    def toBracket(self, bracketValue):
        """
        Converts a scaled value in the range [0, 1] back to the original range [minValue, maxValue].
        """
        return bracketValue * (self.maxValue - self.minValue) + self.minValue

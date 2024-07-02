import re

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

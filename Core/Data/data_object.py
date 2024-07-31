class DataObj:
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

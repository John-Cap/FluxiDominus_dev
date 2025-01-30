
import uuid

#Holder class
class ReactionParametres:
    def __init__(self):
        self.tweakables={}
        self.types=[Temp,ResidenceTime,Flowrate,Equivalents]
        
    def addTweakable(self, tweakable):
        if not any(isinstance(tweakable, allowed_type) for allowed_type in self.types):
            raise TypeError(f"Invalid tweakable type: {type(tweakable).__name__}. Allowed types: {[t.__name__ for t in self.types]}")
        self.tweakables[tweakable.name]=tweakable
    def getAllTweakables(self):
        return (self.tweakables.values())

#Base class
class ReactionParametre:
    def __init__(self, name, associatedCommand, ranges=None):
        self.id = uuid.uuid4()
        self.name = name
        self.ranges = {} if ranges is None else ranges  # Store ranges in a dictionary
        self.currentRange = []  # Stores the currently active range
        self._rangeCntr = 0  # Internal counter for tracking range indexes
        self.associatedCommand = associatedCommand

    def setRange(self, range):
        """
        Sets a range for the parameter. The range can be:
        - A simple list: [lowerBound, upperBound]
        - A list of lists: [[lowerBound1, upperBound1], [lowerBound2, upperBound2], ...]
        """
        if isinstance(range, list):
            if all(isinstance(i, list) and len(i) == 2 for i in range):
                # If given a list of lists, store each range separately
                for r in range:
                    self.ranges[self._rangeCntr] = r
                    self._rangeCntr += 1
            elif len(range) == 2:
                # If given a single range, store it
                self.ranges[self._rangeCntr] = range
                self._rangeCntr += 1
            else:
                raise ValueError("Invalid range format. Must be [lower, upper] or [[lower, upper], ...].")
        else:
            raise TypeError("Range must be a list.")
        
    def getRanges(self):
        """Ensure that ranges are returned as a list, regardless of initialization issues."""
        if isinstance(self.ranges, dict):
            return list(self.ranges.values())
        elif isinstance(self.ranges, list):  # Temporary fix if some objects were initialized incorrectly
            return self.ranges
        return []
    
    def getCurrentRange(self):
        """Returns the currently active range if set, otherwise the first stored range."""
        if self.currentRange:
            return self.currentRange
        elif self.ranges:
            return self.ranges[0]  # Default to first range if no specific range is set
        return None

    def setCurrentRange(self, index):
        """
        Sets the current active range by index.
        """
        if index in self.ranges:
            self.currentRange = self.ranges[index]
        else:
            raise IndexError(f"Invalid range index {index}. Available indices: {list(self.ranges.keys())}")


class Temp(ReactionParametre):
    def __init__(self, name, associatedCommand, ranges=None):
        super().__init__(name, associatedCommand, ranges)
class ResidenceTime(ReactionParametre):
    def __init__(self, name, associatedCommand, ranges=None):
        super().__init__(name, associatedCommand, ranges)
class Flowrate(ReactionParametre):
    def __init__(self, name, associatedCommand, ranges=None):
        super().__init__(name, associatedCommand, ranges)
class Equivalents(ReactionParametre):
    def __init__(self, name, associatedCommand, ranges=None):
        super().__init__(name, associatedCommand, ranges)
        
if __name__ == "__main__":
    # Create an instance of ReactionParametres
    params = ReactionParametres()

    # Create valid tweakables
    temp1 = Temp("Temperature_1")
    temp2 = Temp("Temperature_2")
    residence_time1 = ResidenceTime("ResidenceTime_1")
    flowrate1 = Flowrate("Flowrate_1")
    equivalents1 = Equivalents("Equivalents_1")

    # Test adding valid tweakables
    try:
        params.addTweakable(temp1)
        print(f"Added tweakable: {temp1.name}")
        
        params.addTweakable(temp2)  # Duplicate type allowed
        print(f"Added tweakable: {temp2.name}")

        params.addTweakable(residence_time1)
        print(f"Added tweakable: {residence_time1.name}")

        params.addTweakable(flowrate1)
        print(f"Added tweakable: {flowrate1.name}")

        params.addTweakable(equivalents1)
        print(f"Added tweakable: {equivalents1.name}")

    except TypeError as e:
        print(f"Error: {e}")

    # Attempt to add an invalid tweakable type
    class InvalidTweakable:
        def __init__(self, name):
            self.name = name

    invalid_tweakable = InvalidTweakable("Invalid")

    try:
        params.addTweakable(invalid_tweakable)
    except TypeError as e:
        print(f"Expected error: {e}")

    # Print all tweakables
    print("\nAll tweakables in params:")
    for tweakable in params.getAllTweakables():
        print(f"- {tweakable.name} (ID: {tweakable.id})")

    param_1 = Temp("Temperature")
    param_2 = Flowrate("Flowrate 2")

    # Add single range
    param_1.setRange([10, 50])

    # Add multiple ranges
    param_2.setRange([[60, 100], [120, 150]])

    print("All ranges:", param_1.getRanges())  # [[10, 50], [60, 100], [120, 150]]

    print("Current range:", param_1.getCurrentRange())  # Defaults to [10, 50]

    print("All ranges:", param_2.getRanges())  # [[10, 50], [60, 100], [120, 150]]

    print("Current range:", param_2.getCurrentRange())  # Defaults to [10, 50]

    # Change current range
    param_1.setCurrentRange(0)
    print("New current range 2:", param_1.getCurrentRange())  # [60, 100]

    param_2.setCurrentRange(1)
    print("New current range 2:", param_2.getCurrentRange())  # [60, 100]

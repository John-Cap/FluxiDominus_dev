
import ast

import numpy as np

class IRScanner:
    def __init__(self) -> None:
        self.arraysListAllyl=[]
        self.arraysListIsoVal=[]
        self.arraysListMix=[]
        self.arraysListHeatedReaction=[]

        self.arraysListAllylAvg=[]
        self.arraysListIsoValAvg=[]
        self.arraysListMixAvg=[]
        self.arraysListHeatedReactionAvg=[]        
        self.bothSubtractedAvg=[]

        self.allAvgArrays=[]

    def parseIrData(self):

        # Open the text file for reading
        with open('devJunk/Allyl_plus_MeOHH2O.txt', 'r') as file:
            # Iterate through each line in the file
            for line in file:
                if '->' not in line:
                    continue
                # Split the line into timestamp and array parts
                _, array_str = line.strip().split('->')

                # Convert the array string to a Python list
                array = ast.literal_eval(array_str)

                #del array[750:]
                #del array[410:540]

                # Append the array to the list
                self.arraysListAllyl.append(array)

            _i=0
            _len=len(self.arraysListAllyl)
            _arrLen=len(self.arraysListAllyl[0])
            while _i<_arrLen:
                _total=0

                for _x in self.arraysListAllyl:
                    _total=_total+_x[_i]
                self.arraysListAllylAvg.append(
                    _total/_len
                )
                _i+=1
            #self.allAvgArrays.append(self.arraysListAllylAvg)

        # Open the text file for reading
        with open('devJunk/Isoval_plus_MeOH.txt','r') as file:
            # Iterate through each line in the file
            for line in file:
                if '->' not in line:
                    continue
                # Split the line into timestamp and array parts
                _, array_str = line.strip().split('->')

                # Convert the array string to a Python list
                array = ast.literal_eval(array_str)

                #del array[750:]
                #del array[410:540]

                # Append the array to the list
                self.arraysListIsoVal.append(array)

            _i=0
            _len=len(self.arraysListIsoVal)
            _arrLen=len(self.arraysListIsoVal[0])
            while _i<_arrLen:
                _total=0

                for _x in self.arraysListIsoVal:
                    _total=_total+_x[_i]
                self.arraysListIsoValAvg.append(
                    _total/_len
                )
                _i+=1
            #self.allAvgArrays.append(self.arraysListIsoValAvg)

        # Open the text file for reading
        with open('devJunk/Both.txt', 'r') as file:
            # Iterate through each line in the file
            for line in file:
                if '->' not in line:
                    continue
                # Split the line into timestamp and array parts
                _, array_str = line.strip().split('->')

                # Convert the array string to a Python list
                array = ast.literal_eval(array_str)

                #del array[750:]
                #del array[410:540]

                # Append the array to the list
                self.arraysListMix.append(array)

            _i=0
            _len=len(self.arraysListMix)
            _arrLen=len(self.arraysListMix[0])
            while _i<_arrLen:
                _total=0

                for _x in self.arraysListMix:
                    _total=_total+_x[_i]
                self.arraysListMixAvg.append(
                    _total/_len
                )
                _i+=1
            self.allAvgArrays.append(self.arraysListMixAvg)

        # Open the text file for reading
        with open('devJunk/heated_reaction.txt', 'r') as file:
            # Iterate through each line in the file
            for line in file:
                if '->' not in line:
                    continue
                # Split the line into timestamp and array parts
                _, array_str = line.strip().split('->')

                # Convert the array string to a Python list
                array = ast.literal_eval(array_str)

                #del array[750:]
                #del array[410:540]

                # Append the array to the list
                self.arraysListHeatedReaction.append(array)

            _i=0
            _len=len(self.arraysListHeatedReaction)
            _arrLen=len(self.arraysListHeatedReaction[0])
            while _i<_arrLen:
                _total=0

                for _x in self.arraysListHeatedReaction:
                    _total=_total+_x[_i]
                self.arraysListHeatedReactionAvg.append(
                    _total/_len
                )
                _i+=1
            self.allAvgArrays.append(self.arraysListHeatedReactionAvg)

    def subtractBlanks(self):
        _i=0
        _len=len(self.arraysListIsoValAvg)
        while _i<_len:
            #self.bothSubtractedAvg.append(self.arraysListMixAvg[_i]-(self.arraysListAllylAvg[_i]+self.arraysListIsoValAvg[_i]))
            self.bothSubtractedAvg.append(self.arraysListHeatedReactionAvg[_i]-(self.arraysListAllylAvg[_i]))
            _i+=1
        self.allAvgArrays.append(self.bothSubtractedAvg)
        return self.bothSubtractedAvg
    def jiggle_array(arr, percentage_range):
        """
        Jiggles array values by a given percentage range.

        Parameters:
            arr (array-like): Input array.
            percentage_range (float): Percentage range within which values will be jiggled.
                                    For example, 0.1 means values will be jiggled within -10% to +10%.

        Returns:
            array-like: Jiggled array.
        """
        # Convert percentage range to actual range
        range_value = np.abs(arr) * percentage_range

        # Generate random jiggles within the range for each element
        jiggles = np.random.uniform(-range_value, range_value, size=arr.shape)

        # Apply jiggles to the original array
        jiggled_array = arr + jiggles

        return jiggled_array
        '''
        # Example usage:
        original_array = np.array([
            1,
            2,
            3,
            4,
            5
        ])
        percentage_range = 0.05  # 10%
        jiggled_array = IRScanner.jiggle_array(original_array, percentage_range)
        print("Original Array:", original_array)
        print("Jiggled Array:", jiggled_array)
        '''
import copy
import numpy as np
import matplotlib.pyplot as plt

from Core.Control.IR import IRScanner

#Example 1

_IRscanner = IRScanner()
_IRscanner.parseIrData()
_yData=copy.deepcopy(_IRscanner.arraysListHeatedReaction) #Array with ~35 arrays with ~840 elements each
_MixAvg=copy.deepcopy(_IRscanner.arraysListMixAvg) #Array with ~35 arrays with ~840 elements each
#_yData=[_yData[0],_MixAvg,_MixAvg,_yData[1],_MixAvg,_MixAvg,_yData[2],_MixAvg,_MixAvg,_yData[3],_MixAvg,_MixAvg,_yData[4],_MixAvg,_MixAvg,_yData[5],_MixAvg,_MixAvg]
_processedData=_yData
'''
for _x in _yData:
    _processedData.append(_x)
    _processedData.append(_MixAvg)
    _processedData.append(_MixAvg)
    #_processedData.append(_MixAvg)
''' 
num_time_steps = len(_processedData)
num_x_steps = len(_processedData[0])
#data_series = [[np.sin(x / num_x_steps * np.pi) * np.cos(x / num_x_steps * np.pi * t) for x in range(num_x_steps)] for t in range(num_time_steps)]

# Convert data to numpy array for easier manipulation
data_array = np.array(_processedData)

# Create x and t arrays
x = np.arange(num_x_steps)
t = np.arange(num_time_steps)

# Create meshgrid from x and t
T, X = np.meshgrid(x, t)

# Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, T, data_array, cmap='viridis')

ax.set_xlabel('X')
ax.set_ylabel('Time Steps')
ax.set_zlabel('Y')
ax.set_title('Surface Map of Time Steps')

plt.show()

#Example 2
import copy
import numpy as np
import matplotlib.pyplot as plt

from Core.Control.IR import IRScanner

_IRscanner = IRScanner()
_IRscanner.parseIrData()
_yData=copy.deepcopy(_IRscanner.arraysListHeatedReaction) #Array with ~35 arrays with ~840 elements each
_MixAvg=copy.deepcopy(_IRscanner.arraysListMixAvg) #Array with ~35 arrays with ~840 elements each
#_yData=[_yData[0],_MixAvg,_MixAvg,_yData[1],_MixAvg,_MixAvg,_yData[2],_MixAvg,_MixAvg,_yData[3],_MixAvg,_MixAvg,_yData[4],_MixAvg,_MixAvg,_yData[5],_MixAvg,_MixAvg]
_processedData=_yData
'''
for _x in _yData:
    _processedData.append(_x)
    _processedData.append(_MixAvg)
    _processedData.append(_MixAvg)
    #_processedData.append(_MixAvg)
''' 
num_time_steps = len(_processedData)
num_x_steps = len(_processedData[0])
#data_series = [[np.sin(x / num_x_steps * np.pi) * np.cos(x / num_x_steps * np.pi * t) for x in range(num_x_steps)] for t in range(num_time_steps)]

# Convert data to numpy array for easier manipulation
data_array = np.array(_processedData)

# Create x and t arrays
x = np.arange(num_x_steps)
t = np.arange(num_time_steps)

# Create meshgrid from x and t
T, X = np.meshgrid(x, t)

# Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, T, data_array, cmap='viridis')

ax.set_xlabel('X')
ax.set_ylabel('Time Steps')
ax.set_zlabel('Y')
ax.set_title('Surface Map of Time Steps')

plt.show()

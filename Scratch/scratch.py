
import copy
import threading
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import io
import asyncio
import websockets
import base64
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import io
import asyncio
import websockets
import base64
import json

from Core.Control.IR import IRScanner

class IRPlotter:
    def __init__(self, maxSlices=50, elev=30, azim=45, zoom=1):
        self.maxSlices = maxSlices
        self.elev = elev
        self.azim = azim
        self.zoom = zoom

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('Steps')
        self.ax.set_ylabel('Time')
        self.ax.set_zlabel('Absorbance')

        self.data = []

    def addIrData(self, irData):
        self.data.append(irData)
        if len(self.data) > self.maxSlices:
            self.data.pop(0)

    def initPlot(self):
        if not self.data:
            raise ValueError("No data to initialize plot")
        dataArray = np.array(self.data)
        x = np.arange(dataArray.shape[1])
        y = np.arange(dataArray.shape[0])
        x, y = np.meshgrid(x, y)
        surface = self.ax.plot_surface(x, y, dataArray, cmap='viridis')
        return surface,

    def updatePlot(self):
        if not self.data:
            raise ValueError("No data to update plot")
        self.ax.clear()
        self.ax.set_xlabel('Steps')
        self.ax.set_ylabel('Time')
        self.ax.set_zlabel('Absorbance')
        self.ax.view_init(elev=self.elev, azim=self.azim)
        self.ax.dist = self.zoom  # Apply zoom
        dataArray = np.array(self.data)
        x = np.arange(dataArray.shape[1])
        y = np.arange(dataArray.shape[0])
        x, y = np.meshgrid(x, y)
        surface = self.ax.plot_surface(x, y, dataArray, cmap='viridis')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf

    async def sendPlot(self, websocket):
        while True:
            imgBuf = self.updatePlot()
            imgBase64 = base64.b64encode(imgBuf.read()).decode('utf-8')
            await websocket.send(imgBase64)
            await asyncio.sleep(1)

    async def handler(self, websocket, path):
        consumerTask = asyncio.create_task(self.sendPlot(websocket))

        try:
            async for message in websocket:
                command = json.loads(message)
                if command['action'] == 'zoom':
                    self.zoom += command['value']
                elif command['action'] == 'tilt_left_right':
                    self.azim += command['value']
                elif command['action'] == 'tilt_up_down':
                    self.elev += command['value']
                elif command['action'] == 'add_data':
                    irData = command['data']
                    self.addIrData(irData)
        finally:
            consumerTask.cancel()

    def startServer(self, host='localhost', port=9003):
        startServer = websockets.serve(self.handler, host, port)
        asyncio.get_event_loop().run_until_complete(startServer)
        asyncio.get_event_loop().run_forever()

    def injectDataThread(self, data):
        def injectData():
            for irScan in data:
                self.addIrData(irScan)
                time.sleep(1)
        
        threading.Thread(target=injectData, daemon=True).start()

if __name__ == "__main__":

    _IRscanner = IRScanner()
    _IRscanner.parseIrData()
    _yData = copy.deepcopy(_IRscanner.arraysListHeatedReaction)
    print(_yData)
    
    plotter = IRPlotter()
    plotter.injectDataThread(_yData)
    plotter.startServer()

'''
class IRPlotter:
    def __init__(self, maxSlices=50, elev=30, azim=45, zoom=1):
        self.maxSlices = maxSlices
        self.elev = elev
        self.azim = azim
        self.zoom = zoom

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('Wavelength')
        self.ax.set_ylabel('Time')
        self.ax.set_zlabel('Absorbance')

        self.data = []

    def addIrData(self, irData):
        self.data.append(irData)
        if len(self.data) > self.maxSlices:
            self.data.pop(0)

    def initPlot(self):
        if not self.data:
            raise ValueError("No data to initialize plot")
        dataArray = np.array(self.data)
        x = np.arange(dataArray.shape[1])
        y = np.arange(dataArray.shape[0])
        x, y = np.meshgrid(x, y)
        surface = self.ax.plot_surface(x, y, dataArray, cmap='viridis')
        return surface,

    def updatePlot(self):
        if not self.data:
            raise ValueError("No data to update plot")
        self.ax.clear()
        self.ax.set_xlabel('Steps')
        self.ax.set_ylabel('Time')
        self.ax.set_zlabel('Absorbance')
        self.ax.view_init(elev=self.elev, azim=self.azim)
        self.ax.dist = self.zoom  # Apply zoom
        dataArray = np.array(self.data)
        x = np.arange(dataArray.shape[1])
        y = np.arange(dataArray.shape[0])
        x, y = np.meshgrid(x, y)
        surface = self.ax.plot_surface(x, y, dataArray, cmap='viridis')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf

    async def sendPlot(self, websocket):
        while True:
            imgBuf = self.updatePlot()
            imgBase64 = base64.b64encode(imgBuf.read()).decode('utf-8') #Hoekom encode en dan decode hy dit weer?!
            await websocket.send(imgBase64)
            await asyncio.sleep(1)

    async def handler(self, websocket, path):
        consumerTask = asyncio.create_task(self.sendPlot(websocket))

        try:
            async for message in websocket:
                command = json.loads(message)
                if command['action'] == 'zoom':
                    self.zoom += command['value']
                elif command['action'] == 'tilt_left_right':
                    self.azim += command['value']
                elif command['action'] == 'tilt_up_down':
                    self.elev += command['value']
                elif command['action'] == 'add_data':
                    irData = command['data']
                    self.addIrData(irData)
        finally:
            consumerTask.cancel()

    def startServer(self, host='localhost', port=9003):
        startServer = websockets.serve(self.handler, host, port)
        asyncio.get_event_loop().run_until_complete(startServer)
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    _IRscanner=IRScanner()
    _IRscanner.parseIrData()
    _yData=copy.deepcopy(_IRscanner.arraysListHeatedReaction)
    
    plotter = IRPlotter()
    plotter.startServer()
'''
'''
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import io
import asyncio
import websockets
import base64
import json

MAX_SLICES = 50  # Define the maximum number of X-Y slices

# Initialize view parameters
elevation = 30
azimuth = 45

growCoeff=0.05

# Generate some example data
def generateIrData(step):
    global growCoeff
    absorbance = (np.sin(np.linspace(0, 2 * np.pi, 100)) + np.random.normal(0, 0.1, 100))*growCoeff
    growCoeff=growCoeff+0.01
    return absorbance

# Generate a 3D surface plot from IR data
def generateSurfacePlot(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X = np.arange(data.shape[1])
    Y = np.arange(data.shape[0])
    X, Y = np.meshgrid(X, Y)
    ax.plot_surface(X, Y, data, cmap='viridis')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Time')
    ax.set_zlabel('Absorbance')

    ax.view_init(elev=elevation, azim=azimuth)  # Set the view parameters

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf

async def sendPlot(websocket):
    data = []
    while True:
        stepData = generateIrData(len(data))
        data.append(stepData)
        if len(data) > MAX_SLICES:  # Keep only the last MAX_SLICES steps
            data.pop(0)
        dataArray = np.array(data)

        imgBuf = generateSurfacePlot(dataArray)
        imgBase64 = base64.b64encode(imgBuf.read()).decode('utf-8')
        await websocket.send(imgBase64)
        await asyncio.sleep(1)  # Adjust the interval as needed

async def handler(websocket, path):
    global elevation, azimuth
    consumerTask = asyncio.create_task(sendPlot(websocket))

    try:
        async for message in websocket:
            command = json.loads(message)
            if command['action'] == 'zoom':
                elevation += command['value']
            elif command['action'] == 'tilt_left_right':
                azimuth += command['value']
            elif command['action'] == 'tilt_up_down':
                elevation += command['value']
    finally:
        consumerTask.cancel()

startServer = websockets.serve(handler, 'localhost',9003)

asyncio.get_event_loop().run_until_complete(startServer)
asyncio.get_event_loop().run_forever()
'''

#Example 1
'''
_IRscanner = IRScanner()
_IRscanner.parseIrData()
_yData=copy.deepcopy(_IRscanner.arraysListHeatedReaction) #Array with ~35 arrays with ~840 elements each
_MixAvg=copy.deepcopy(_IRscanner.arraysListMixAvg) #Array with ~35 arrays with ~840 elements each
#_yData=[_yData[0],_MixAvg,_MixAvg,_yData[1],_MixAvg,_MixAvg,_yData[2],_MixAvg,_MixAvg,_yData[3],_MixAvg,_MixAvg,_yData[4],_MixAvg,_MixAvg,_yData[5],_MixAvg,_MixAvg]
_processedData=_yData

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
'''
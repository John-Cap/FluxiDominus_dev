
import copy
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
import io
import asyncio
import websockets
import base64
import json
import matplotlib.pyplot as plt
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
            # Encode the image buffer to base64 string
            imgBase64 = base64.b64encode(imgBuf.read()).decode('utf-8')
            await websocket.send(imgBase64)
            await asyncio.sleep(1)
    '''
    async def sendPlot(self, websocket):
        while True:
            imgBuf = self.updatePlot()
            imgBase64 = base64.b64encode(imgBuf.read()).decode('utf-8')
            await websocket.send(imgBase64)
            await asyncio.sleep(1)
    '''
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

    #Debug
    def injectDataThread(self, data):
        def injectData():
            while True:
                for irScan in data:
                    self.addIrData(irScan)
                    time.sleep(0.25)
        
        threading.Thread(target=injectData, daemon=True).start()

if __name__ == "__main__":

    _IRscanner = IRScanner()
    _IRscanner.parseIrData()
    _yData = copy.deepcopy(_IRscanner.arraysListHeatedReaction)
    #print(_yData)
    
    plotter = IRPlotter()
    plotter.injectDataThread(_yData)
    plotter.startServer()

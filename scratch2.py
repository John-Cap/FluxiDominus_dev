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
elev = 0
azim = 0

incrCoeff=0.05
incrVal=0.01

# Generate some example data
def generate_ir_data(step):
    global incrCoeff
    global incrVal
    
    absorbance = (np.sin(np.linspace(0, 2 * np.pi, 100)) + np.random.normal(0, 0.1, 100))*incrCoeff
    incrCoeff=incrCoeff+incrVal
    return absorbance

# Generate a 3D surface plot from IR data
def generate_surface_plot(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X = np.arange(data.shape[1])
    Y = np.arange(data.shape[0])
    X, Y = np.meshgrid(X, Y)
    ax.plot_surface(X, Y, data, cmap='viridis')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Time')
    ax.set_zlabel('Absorbance')

    ax.view_init(elev=elev, azim=azim)  # Set the view parameters

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf

async def send_plot(websocket):
    data = []
    while True:
        step_data = generate_ir_data(len(data))
        data.append(step_data)
        if len(data) > MAX_SLICES:  # Keep only the last MAX_SLICES steps
            data.pop(0)
        data_array = np.array(data)

        img_buf = generate_surface_plot(data_array)
        img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        await websocket.send(img_base64)
        await asyncio.sleep(1)  # Adjust the interval as needed

async def handler(websocket, path):
    global elev, azim
    consumer_task = asyncio.create_task(send_plot(websocket))

    try:
        async for message in websocket:
            command = json.loads(message)
            if command['action'] == 'zoom':
                elev += command['value']
            elif command['action'] == 'tilt_left_right':
                azim += command['value']
            elif command['action'] == 'tilt_up_down':
                elev += command['value']
    finally:
        consumer_task.cancel()

start_server = websockets.serve(handler, 'localhost',9003)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

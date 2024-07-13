import ast
from time import sleep
import threading
import paho.mqtt.client as mqtt

class MQTTTemperatureUpdater:
    def __init__(self, broker_address="localhost", port=1883, topic="subflow/hotcoil1/tele"):
        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        self.temp = None
        self.client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            self.client.subscribe(self.topic)
        else:
            print("Connection failed with error code " + str(rc))

    def on_message(self, client, userdata, msg):
        _msgContents = msg.payload.decode()
        _msgContents = _msgContents.replace("true", "True").replace("false", "False")
        _msgContents = ast.literal_eval(_msgContents)
        
        if "deviceName" in _msgContents:
            self.temp = _msgContents['state']['temp']
            print(self.temp)

    def start(self):
        self.client.connect(self.broker_address, self.port)
        thread = threading.Thread(target=self.run)
        thread.start()
        return thread

    def run(self):
        self.client.loop_start()
        while True:
            sleep(1)

# Example usage
updater = MQTTTemperatureUpdater()
thread = updater.start()

# Now, updater.temp will be continuously updated with the latest temperature value

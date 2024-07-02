import time
import paho.mqtt.client as mqtt
import json

from Core.Control.ScriptGenerator import FlowChemAutomation

class CommandHandler:
    def __init__(self, broker_address='localhost', port=1883, topic_command='chemistry/command', topic_response='chemistry/response',automation=FlowChemAutomation()):
        self.broker_address = broker_address
        self.port = port
        self.topic_command = topic_command
        self.topic_response = topic_response
        self.commands = {}
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.automation = automation

    def register_command(self, command, handler):
        self.commands[command] = handler

    def on_connect(self, client, userdata, flags, rc):
        print(str(self.client) + " has connected to MQTT!")
        
    def on_message(self,client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        print("Received:", payload)

        if 'command' in payload and payload['command'] == 'addBlock':
            block_name = payload['data']['block_name']
            device_settings = payload['data']['device_settings']
            try:
                self.automation.addBlock(device_settings, blockName=block_name)
                response = {'status': 'success', 'message': 'Block added'}
            except ValueError as e:
                response = {'status': 'error', 'message': str(e)}
            self.publishResponse(response)
        else:
            response = {'status': 'error', 'message': 'Unknown command'}
            self.publishResponse(response)

    def publishResponse(self, response):
        self.client.publish('chemistry/response', json.dumps(response))

    '''
    def on_message(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        print('Received: ' + str(payload))
        command = payload['command']
        data = payload['data']
        
        if command in self.commands:
            result = self.commands[command](data)
            response = {"status": "success", "result": result}
        else:
            response = {"status": "error", "message": "Unknown command"}
        
        print('Attempting to publish response: ' + str(response))
        self.client.publish(self.topic_response, json.dumps(response))
    '''
    def start(self):
        self.client.connect(self.broker_address, self.port)
        self.client.subscribe(self.topic_command)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    CommandHandler().start()
    while True:
        time.sleep(0.1)
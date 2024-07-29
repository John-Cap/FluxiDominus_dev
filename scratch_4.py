import time
import paho.mqtt.client as mqtt
import json
from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.UI.brokers_and_topics import MqttTopics

class CommandHandler:
    def __init__(self, broker_address='localhost', port=1883, topic_command='chemistry/cmnd', topic_response='chemistry/response', automation=FlowChemAutomation(),topicSets=MqttTopics.getAllTopicSets()):
        self.broker_address = broker_address
        self.port = port
        self.topic_command = topic_command
        self.topic_response = topic_response
        self.commands = {}
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.automation = automation
        self.topicSets=topicSets

    def register_command(self, command, handler):
        self.commands[command] = handler

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker")

    def on_message(self, client, userdata, message):
        topic=message.topic
        print(topic)
        payload = json.loads(message.payload.decode('utf-8'))
        device = payload.get('device')
        command = payload.get('command')
        value = payload.get('value')

        print('Received message: '+str(payload))

        if device in self.commands:
            self.commands[device](command, value)
        else:
            print(f"Unknown device: {device}")

    def start(self):
        self.client.connect(self.broker_address, self.port)
        self.client.subscribe(self.topic_command)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

def handle_command(command, value):
    print(f"Handling command: {command} with value: {value}")
    # Add logic to handle the command using FlowChemAutomation

def main():
    command_handler = CommandHandler()
    command_handler.register_command('Delay', handle_command)
    # Register more commands as needed

    command_handler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        command_handler.stop()

if __name__ == "__main__":
    main()

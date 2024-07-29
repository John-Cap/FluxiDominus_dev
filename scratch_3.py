import time
import paho.mqtt.client as mqtt
import json
from Core.Control.ScriptGenerator import FlowChemAutomation
from Core.UI.brokers_and_topics import MqttTopics

class CommandHandler:
    def __init__(self, broker_address='localhost', port=1883, topicCmnd='chemistry/cmnd', topicResponse='chemistry/response', automation=FlowChemAutomation(),topicSets=MqttTopics.getAllTopicSets()):
        self.brokerAddress = broker_address
        self.port = port
        self.topicCmnd = topicCmnd
        self.topicResponse = topicResponse
        self.commands = {}
        self.client = mqtt.Client()
        self.client.on_message = self.onMessage
        self.client.on_connect = self.onConnect
        self.automation = automation
        self.topicSets=topicSets
        
        #TODO - move to config
        self.lastMsgFromTopic={}
        
    def updateLastMsg(self,topic,msg):
        self.lastMsgFromTopic[topic]=msg

    def register_command(self, command, handler):
        self.commands[command] = handler

    def onConnect(self, client, userdata, flags, rc):
        for set in self.topicSets:
            #print(set.values())
            for val in set.values():
                self.client.subscribe(val)
        #   self.client.subscribe(self.topicCmnd)
        print("Connected to MQTT broker")

    def onMessage(self, client, userdata, message):
        payload = json.loads(message.payload.decode('utf-8'))
        self.updateLastMsg(message.topic,payload)
        print(self.lastMsgFromTopic)
        device = payload.get('device')
        command = payload.get('command')
        value = payload.get('value')

        #print('Received message: '+str(payload))

        if device in self.commands:
            self.commands[device](command, value)
        else:
            print(f"Unknown device: {device}")

    def start(self):
        self.client.connect(self.brokerAddress, self.port)
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

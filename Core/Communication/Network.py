
import ast
import datetime
import paho.mqtt.client as mqtt

from Core.Diagnostics.Logging import Diag_log

class MQTTReader:

    def __init__(self):

        self.currentScript=""
        self.runTest=False

        self.IrUpdated=False
        self.currentIrScan=[]

        # MQTT Broker Settings
        self.brokerAddress="localhost"
        self.port=1883

        self.topicTestCommandsNRtoPY="test/settings/"
        self.topicTestCommandsPYtoNR="test/status/"

        self.topic_SF10="subflow/sf10vapourtec1/cmnd"  # Change this to the topic you want to publish to
        self.topic_SF10_tele="subflow/sf10vapourtec1/tele"  # Change this to the topic you want to publish to
        self.topic_flowsynmax2="subflow/flowsynmax2/cmnd"  # Change this to the topic you want to publish to
        self.topic_flowsynmax2_tele="subflow/flowsynmax2/tele"  # Change this to the topic you want to publish to
        self.topic_hotchip1="subflow/hotchip1/cmnd"  # Change this to the topic you want to publish to
        self.topic_hotchip2="subflow/hotchip2/cmnd"  # Change this to the topic you want to publish to
        self.topic_hotcoil1="subflow/hotcoil1/cmnd"  # Change this to the topic you want to publish to
        self.topic_hotchip1_tele="subflow/hotchip1/tele"  # Change this to the topic you want to publish to
        self.topic_hotchip2_tele="subflow/hotchip2/tele"  # Change this to the topic you want to publish to
        self.topic_hotcoil1_tele="subflow/hotcoil1/tele"  # Change this to the topic you want to publish to
        self.topic_reactIR1_tele="subflow/reactIR702L1/tele"
        self.topic_reactIR1="subflow/reactIR702L1/cmnd"

        self.topics=[
            self.topicTestCommandsNRtoPY,
            self.topicTestCommandsPYtoNR,
            self.topic_SF10,
            #topic_SF10_tele,
            self.topic_flowsynmax2,
            #topic_flowsynmax2_tele,
            self.topic_hotchip1,
            self.topic_hotchip2,
            self.topic_hotcoil1,
            #topic_hotchip1_tele,
            #topic_hotchip2_tele,
            #topic_hotcoil1_tele,
            self.topic_reactIR1_tele,
            self.topic_reactIR1
        ]

    def clearScript(self):
        self.currentScript=""

    # Callback function to handle when the client receives a CONNACK response from the server
    def on_connect(self,client,userdata,flags,rc):
        if rc == 0:
            #print("Connected to broker")
            for _x in self.topics:
                client.subscribe(_x)
                #print("Subscribed to topic:",_x)
        else:
            print("Connection failed with error code " + str(rc))
    # Callback function to handle when a message is received from the broker
    def on_message(self,client,userdata,msg):

        _msgContents=(msg.payload.decode())
        #print(_msgContents)
        _msgContents=_msgContents.replace("true","True")
        _msgContents=_msgContents.replace("false","False")

        _msgContents=ast.literal_eval(_msgContents)
        #print("MQTT payload received!")
        #print("MQTT payload received: " + str(_msgContents))
        if "script" in _msgContents:
            print(_msgContents)
            _msgContents=_msgContents["script"]
            #print("Received message: " + _msgContents)
            self.currentScript=_msgContents
            return _msgContents
        if "running" in _msgContents:
            _msgContents=_msgContents["running"]
            #print("Received message: " + str(_msgContents))
            self.runTest=_msgContents
            return _msgContents        
        if "deviceName" in _msgContents:
            #print(_msgContents["deviceName"])
            _name=_msgContents["deviceName"]
            if _name == "reactIR702L1":
                #print("IR scan received")
                # Get the current time
                current_time = datetime.datetime.now()

                # Format the time as HH:MM:SS
                timestamp = current_time.strftime("%H:%M:%S")
                _msgContents=timestamp+"->"+str((_msgContents["state"])["data"])
                Diag_log().toLog(_msgContents)

                if not self.IrUpdated:
                    self.currentIrScan=((_msgContents["state"])["data"])
                    #self.IrUpdated=True

                return _msgContents
            elif _name=="flowsynmaxi2":
                pass
                #print("Maxi command: " + str(_msgContents))
            elif _name=="sf10Vapourtec1":
                pass
                #print("SF10 command: " + str(_msgContents))
                        
    def readMQTTLoop(self):

        # Create MQTT client instance
        client=mqtt.Client(client_id="",clean_session=True,userdata=None,protocol=mqtt.MQTTv311)

        # Assign callbacks to client
        client.on_connect=self.on_connect
        client.on_message=self.on_message

        # Connect to MQTT broker
        client.connect(self.brokerAddress,self.port,1)
        # Start loop to process callbacks
        client.loop_start()

'''
#Target URL
my_url="http://:1880/nmr1Cmnd"

#Voorbeeld payload
payload={"deviceName":"nmr1","settings":{"command":"START","protocol":"1D"}}  # Replace with your actual payload

#Sender funksie
def send_post_request(url,data,headers):
    try:
        response=requests.post(url, json=data,headers=headers)
        print(response.content.decode())
        print(f"POST request sent to {url}. Response: {response.status_code}")
    except Exception as e:
        print(f"Error sending POST request: {e}")


# Define login credentials
username="user"
password="flowie"

# Create a string with the credentials and encode in Base64
credentials=f'{username}:{password}'
credentials_b64=base64.b64encode(credentials.encode('ascii')).decode('ascii')
print(credentials_b64)
# Create a dictionary of headers with Basic Authentication credentials
headers={'Authorization': 'Basic ' + credentials_b64}

print("HERE")

#Stuur requests
while True:
    send_post_request(my_url,headers=headers,data=payload)
    time.sleep(1)
'''
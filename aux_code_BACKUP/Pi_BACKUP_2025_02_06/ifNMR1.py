# -*- coding: utf-8 -*-� # Use UTF-8 encoding for better compatibility
import paho.mqtt.client as mqtt
import time
import socket
import json
# from json import JSONEncoder
import threading
import xmltodict
import xml.etree.ElementTree as ET

# Constants
MQTT_TOPIC_CMND = "subflow/nmr1/cmnd"
MQTT_TOPIC_TELE = "subflow/nmr1/tele"
MQTT_BROKER_ADDRESS = "146.64.91.174"  # Replace with your broker address
MQTT_BROKER_PORT = 1883
DEVICE_IP_ADDRESS = "192.168.1.52"
DEVICE_PORT = 13000
DEVICE_RT_POLL_PERIOD = 2

# Global variables
device_info = {
    "deviceName": "nmr1",
    "deviceType": "NMR",
    "inUse": False,
    "remoteEnabled": False,
    "connDetails":{
        "ipCom" : {
            "addr": DEVICE_IP_ADDRESS,
            "port": DEVICE_PORT,
        }
    },
    "tele": {
        "cmnd": "",
        "cmndResp" : "",
        "settings": {"folder": ""},
        "status" : { },
        "state": {
            "shim" : {
                "check" : {
                    "response" : {}
                },
                "quick" : {
                    "response" : {}
                },
                "power" : {
                    "response" : {}
                }
            }
        },
        "timestamp": ""
    }
}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))

def clean_xml(xml_data):
    """Cleans XML data by removing junk characters after the root element.

    Args:
        xml_data (str): The XML data to be cleaned.

    Returns:
        str: The cleaned XML data.
    """

    try:
        # Parse the XML data
        root = ET.fromstring(xml_data)

        # Find the root element's tail and remove it
        root.tail = None

        # Serialize the cleaned XML data
        cleaned_xml = ET.tostring(root, encoding='utf-8').strip()

        return cleaned_xml
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return ""

def xml_to_json(xml_data):
    """Converts cleaned XML data to JSON.

    Args:
        xml_data (str): The cleaned XML data.

    Returns:
        dict: The JSON representation of the XML data.
    """

    try:
        # Parse the cleaned XML data
        root = ET.fromstring(xml_data)

        # Convert the XML element to a Python dictionary
        json_dict = dict(root.attrib)
        for child in root:
            json_dict[child.tag] = xml_to_json(ET.tostring(child, encoding='unicode').strip())

        return json_dict
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return {}

# Function to handle MQTT messages
def on_message(client, userdata, message):
    global device_info, sock

    try:
        payload = message.payload.decode()
        data = json.loads(payload)

        if (data["deviceName"] == device_info["deviceName"]):

            if (data["settings"]["command"] == "STOP"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "STOP"
                # device_info["tele"]["state"]["state"] = "ON"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <Abort/>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            if (data["settings"]["command"] == "RUN_CHECKSHIM"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "RUN_CHECKSHIM"
                # device_info["tele"]["state"]["state"] = "ON"

                device_info["tele"]["state"]["shim"]["check"]["response"]["error"] = ""
                device_info["tele"]["state"]["shim"]["check"]["response"]["operatingTemp"] = ""
                device_info["tele"]["state"]["shim"]["check"]["response"]["stableTemp"] = ""
                device_info["tele"]["state"]["shim"]["check"]["response"]["stableLock"] = ""
                device_info["tele"]["state"]["shim"]["check"]["response"]["lineWidth"] = ""
                device_info["tele"]["state"]["shim"]["check"]["response"]["baseWidth"] = ""
                device_info["tele"]["state"]["shim"]["check"]["response"]["systemIsReady"] = ""

                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <CheckShimRequest/>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            if (data["settings"]["command"] == "RUN_POWERSHIM"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "RUN_POWERSHIM"
                # device_info["tele"]["state"]["state"] = "ON"

                device_info["tele"]["state"]["shim"]["power"]["response"]["error"] = ""
                device_info["tele"]["state"]["shim"]["power"]["response"]["operatingTemp"] = ""
                device_info["tele"]["state"]["shim"]["power"]["response"]["stableTemp"] = ""
                device_info["tele"]["state"]["shim"]["power"]["response"]["stableLock"] = ""
                device_info["tele"]["state"]["shim"]["power"]["response"]["lineWidth"] = ""
                device_info["tele"]["state"]["shim"]["power"]["response"]["baseWidth"] = ""
                device_info["tele"]["state"]["shim"]["power"]["response"]["systemIsReady"] = ""

                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <PowerShimRequest/>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            if (data["settings"]["command"] == "RUN_QUICKSHIM"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "RUN_QUICKSHIM"
                # device_info["tele"]["state"]["state"] = "ON"

                device_info["tele"]["state"]["shim"]["quick"]["response"]["error"] = ""
                device_info["tele"]["state"]["shim"]["quick"]["response"]["operatingTemp"] = ""
                device_info["tele"]["state"]["shim"]["quick"]["response"]["stableTemp"] = ""
                device_info["tele"]["state"]["shim"]["quick"]["response"]["stableLock"] = ""
                device_info["tele"]["state"]["shim"]["quick"]["response"]["lineWidth"] = ""
                device_info["tele"]["state"]["shim"]["quick"]["response"]["baseWidth"] = ""
                device_info["tele"]["state"]["shim"]["quick"]["response"]["systemIsReady"] = ""

                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <QuickShimRequest/>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            if (data["settings"]["command"] == "RUN_QUICKSCAN"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "RUN_QUICKSCAN"
                # device_info["tele"]["state"]["state"] = "ON"

                device_info["tele"]["state"]["protocol"] = ""
                device_info["tele"]["state"]["completed"] = ""
                device_info["tele"]["state"]["successful"] = ""

                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <Start protocol="1D PROTON" >
			                <Option name="Scan" value="QuickScan" />
		                </Start>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            if (data["settings"]["command"] == "RUN_STANDARDSCAN"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "RUN_STANDARDSCAN"
                # device_info["tele"]["state"]["state"] = "ON"

                device_info["tele"]["state"]["protocol"] = ""
                device_info["tele"]["state"]["completed"] = ""
                device_info["tele"]["state"]["successful"] = ""

                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <Start protocol="1D PROTON" >
			                <Option name="Scan" value="StandardScan" />
		                </Start>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            if (data["settings"]["command"] == "RUN_POWERSCAN"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "RUN_POWERSCAN"
                # device_info["tele"]["state"]["state"] = "ON"

                device_info["tele"]["state"]["protocol"] = ""
                device_info["tele"]["state"]["completed"] = ""
                device_info["tele"]["state"]["successful"] = ""

                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <Start protocol="1D PROTON" >
			                <Option name="Scan" value="PowerScan" />
		                </Start>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            if (data["settings"]["command"] == "SET_OUTPUT_FOLDER"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "SET_OUTPUT_FOLDER"
                device_info["tele"]["settings"]["folder"] = data["settings"]["folder"]
                # device_info["tele"]["state"]["state"] = "ON"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]
                folder = device_info["tele"]["settings"]["folder"]

                xmlCmnd = """
                <?xml version="1.0" encoding="utf-8"?>
                    <Message>
		                <Set>
			                <DataFolder>
			                    <UserFolder>*""" + folder + """*</UserFolder> 
			                </DataFolder>
		                </Set>
		            </Message>                
                """

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                # sock.settimeout(10.0)

            elif data["settings"]["command"] == "REMOTEEN":
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "REMOTEEN"
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

            elif (data["settings"]["command"] == "REMOTEDIS") :
                device_info["inUse"] = False
                device_info["remoteEnabled"] = False
                device_info["tele"]["cmnd"] = "REMOTEDIS"
                device_info["tele"]["state"]["state"] = "OFF"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())
                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())

                print('\r\nSend message:')
                print(xmlCmnd)
                sock.send(xmlCmnd.encode())

            elif data["settings"]["command"] == "RECONNECT":
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "RECONNECT"
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))               

    except Exception as e:
        print("Error On Msg:", e)
        print("Global: {}".format(device_info))

# class setEncoder(JSONEncoder):
#         def default(self, obj):
#             return list(obj)

def convert_xml_to_json(xml_data):
    """Converts XML data to JSON, handling multiple <Message> tags.

    Args:
        xml_data (str): The XML data to convert.

    Returns:
        list: A list of JSON objects, each representing a <Message> tag.
    """

    # Convert XML to a Python dictionary
    xml_dict = xmltodict.parse(xml_data)

    # If there's a single <Message> tag, return it as a list
    if 'Message' in xml_dict:
        return [xml_dict['Message']]

    # If there are multiple <Message> tags, extract them into a list
    elif 'Message' in xml_dict['Messages']:
        return xml_dict['Messages']['Message']

    # If no <Message> tags are found, return an empty list
    else:
        return []

# Function to start the periodic task for reading real-time data
def read_real_time_data():
    global device_info, sock

    if (device_info["inUse"] == True) :
        try:
            chunk = sock.recv(8192)
            if chunk:
                # xml_data = chunk.decode()
                # Split the chunk into individual XML documents based on the "<?xml version="1.0" encoding="utf-8"?>" header
                xml_documents = chunk.decode().split('<?xml version="1.0" encoding="utf-8"?>')

                # print("RAW XML : {}".format(xml_documents))
                # cleaned_xml = clean_xml(xml_documents)
                if xml_documents:
                    for xml_data in xml_documents:
                        if xml_data.strip():  # Ignore empty strings
                            xml_bytes = xml_data.encode()
                            json_data = convert_xml_to_json(xml_bytes)

                            # json_data = convert_xml_to_json(cleaned_xml) #xml_to_json(cleaned_xml)
                            # print("RAW JSON : {}".format(json_data))
                            if json_data:
                                # print(json_data)
                                # my_dict = xmltodict.parse(xml_data)
                                jsonFromXML = json_data
                                for message in jsonFromXML:
                                    # print(json.dumps(message, indent=4))

                                    print("RAW JSON : {}".format(message))
                                    # print(my_dict)
                                    device_info["tele"]["cmndResp"] = str(xml_documents)  #jsonFromXML

                                    if "StatusNotification" in message:
                                        if "State" in message["StatusNotification"]:
                                            device_info["tele"]["status"]["protocol"] = message["StatusNotification"]["State"]["@protocol"]
                                            device_info["tele"]["status"]["status"] = message["StatusNotification"]["State"]["@status"]
                                            device_info["tele"]["status"]["dataFolder"] = message["StatusNotification"]["State"]["@dataFolder"]

                                        if "Progress" in message["StatusNotification"]:
                                            device_info["tele"]["status"]["protocol"] = message["StatusNotification"]["Progress"]["@protocol"]
                                            device_info["tele"]["status"]["percentage"] = eval(message["StatusNotification"]["Progress"]["@percentage"])
                                            device_info["tele"]["status"]["secondsRemaining"] = eval(message["StatusNotification"]["Progress"]["@secondsRemaining"])

                                        if "Completed" in message["StatusNotification"]:
                                            device_info["tele"]["status"]["protocol"] = message["StatusNotification"]["Completed"]["@protocol"]
                                            device_info["tele"]["status"]["completed"] = message["StatusNotification"]["Completed"]["@completed"]
                                            device_info["tele"]["status"]["successful"] = message["StatusNotification"]["Completed"]["@successful"]

                                        if "Error" in message["StatusNotification"]:
                                            device_info["tele"]["status"]["protocol"] = message["StatusNotification"]["Error"]["@protocol"]
                                            device_info["tele"]["status"]["error"] = message["StatusNotification"]["Error"]["@error"]

                                    if "CheckShimResponse" in message:
                                        device_info["tele"]["state"]["shim"]["check"]["response"]["error"] = message["CheckShimResponse"]["@error"]
                                        device_info["tele"]["state"]["shim"]["check"]["response"]["operatingTemp"] = message["CheckShimResponse"]["OperatingTemperature"]
                                        device_info["tele"]["state"]["shim"]["check"]["response"]["stableTemp"] = message["CheckShimResponse"]["StableTemperatures"]
                                        device_info["tele"]["state"]["shim"]["check"]["response"]["stableLock"] = message["CheckShimResponse"]["StableLock"]
                                        device_info["tele"]["state"]["shim"]["check"]["response"]["lineWidth"] = eval(message["CheckShimResponse"]["LineWidth"])
                                        device_info["tele"]["state"]["shim"]["check"]["response"]["baseWidth"] = eval(message["CheckShimResponse"]["BaseWidth"])
                                        device_info["tele"]["state"]["shim"]["check"]["response"]["systemIsReady"] = message["CheckShimResponse"]["SystemIsReady"]

                                    if "QuickShimResponse" in message:
                                        device_info["tele"]["state"]["shim"]["quick"]["response"]["error"] = message["QuickShimResponse"]["@error"]
                                        device_info["tele"]["state"]["shim"]["quick"]["response"]["operatingTemp"] = message["QuickShimResponse"]["OperatingTemperature"]
                                        device_info["tele"]["state"]["shim"]["quick"]["response"]["stableTemp"] = message["QuickShimResponse"]["StableTemperatures"]
                                        device_info["tele"]["state"]["shim"]["quick"]["response"]["stableLock"] = message["QuickShimResponse"]["StableLock"]
                                        device_info["tele"]["state"]["shim"]["quick"]["response"]["lineWidth"] = eval(message["QuickShimResponse"]["LineWidth"])
                                        device_info["tele"]["state"]["shim"]["quick"]["response"]["baseWidth"] = eval(message["QuickShimResponse"]["BaseWidth"])
                                        device_info["tele"]["state"]["shim"]["quick"]["response"]["systemIsReady"] = message["QuickShimResponse"]["SystemIsReady"]

                                    if "PowerShimResponse" in message:
                                        device_info["tele"]["state"]["shim"]["power"]["response"]["error"] = message["PowerShimResponse"]["@error"]
                                        device_info["tele"]["state"]["shim"]["power"]["response"]["operatingTemp"] = message["PowerShimResponse"]["OperatingTemperature"]
                                        device_info["tele"]["state"]["shim"]["power"]["response"]["stableTemp"] = message["PowerShimResponse"]["StableTemperatures"]
                                        device_info["tele"]["state"]["shim"]["power"]["response"]["stableLock"] = message["PowerShimResponse"]["StableLock"]
                                        device_info["tele"]["state"]["shim"]["power"]["response"]["lineWidth"] = eval(message["PowerShimResponse"]["LineWidth"])
                                        device_info["tele"]["state"]["shim"]["power"]["response"]["baseWidth"] = eval(message["PowerShimResponse"]["BaseWidth"])
                                        device_info["tele"]["state"]["shim"]["power"]["response"]["systemIsReady"] = message["PowerShimResponse"]["SystemIsReady"]

                                    if "CompletedNotificationType" in message:
                                        device_info["tele"]["state"]["protocol"] = message["CompletedNotificationType"]["Completed"]["protocol"]
                                        device_info["tele"]["state"]["completed"] = message["CompletedNotificationType"]["Completed"]["completed"]
                                        device_info["tele"]["state"]["successful"] = message["CompletedNotificationType"]["Completed"]["successful"]

                            else:
                                print("Failed to convert XML to JSON.")
                                # print("RECONNECTING ... ")
                                # sock.close()
                                # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                # sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))               
                                # print("RECONNECTED !!!")
                else:
                    print("Failed to clean XML.")
                    # print("RECONNECTING ... ")
                    # sock.close()
                    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))               
                    # print("RECONNECTED !!!")

                print("RESPONSE: {}".format(device_info))

                # Publish the updated device_info
                client.publish(MQTT_TOPIC_TELE, json.dumps(device_info))
        except Exception as e:
            print("Error reading real-time data:", e)
            print("Global: {}".format(device_info))
            print("RECONNECTING ... ")
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))               
            print("RECONNECTED !!!")

    threading.Timer(DEVICE_RT_POLL_PERIOD, read_real_time_data).start()

# Initialize MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT)
client.subscribe(MQTT_TOPIC_CMND)
print("MQTT Setup complete...")

# polling_thread = threading.Thread(target=read_real_time_data)
# polling_thread.start()
threading.Timer(DEVICE_RT_POLL_PERIOD, read_real_time_data).start()
print("Thread started complete...")

# Start the MQTT loop
print("MQTT Loop started complete...")
client.loop_forever()

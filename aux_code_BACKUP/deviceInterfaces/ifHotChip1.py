# -*- coding: utf-8 -*-� # Use UTF-8 encoding for better compatibility
import paho.mqtt.client as mqtt
import time
import socket
import json
import threading

# Constants
MQTT_TOPIC_CMND = "subflow/hotchip1/cmnd"
MQTT_TOPIC_TELE = "subflow/hotchip1/tele"
MQTT_BROKER_ADDRESS = "146.64.91.174"  # Replace with your broker address
MQTT_BROKER_PORT = 1883
DEVICE_IP_ADDRESS = "192.168.1.211"
DEVICE_PORT = 81
DEVICE_RT_POLL_PERIOD = 2

# Global variables
device_info = {
    "deviceName": "hotchip1",
    "deviceType": "Hotchip",
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
        "settings": {"temp": 0.0},
        "state": {"temp": 0.0, "state": "OFF"},
        "timestamp": ""
    }
}

# Function to handle MQTT messages
def on_message(client, userdata, message):
    global device_info, polling_thread

    try:
        payload = message.payload.decode()
        data = json.loads(payload)

        if (data["deviceName"] == device_info["deviceName"]):

            if (data["settings"]["command"] == "SET"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "SET"
                device_info["tele"]["state"]["state"] = "ON"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                temperature = float(data["settings"]["temp"])
                device_info["tele"]["settings"]["temp"] = temperature

                try:
                    # Create a socket (SOCK_STREAM means a TCP socket)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        # Connect to server and send data
                        data = "out_sp_00 " + str(temperature)
                        sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))
                        sock.sendall(bytes(data + "\n", "utf-8"))

                        # Receive data from the server and shut down
                        received = str(sock.recv(1024), "utf-8")

                        # print("Sent:{}".format(data))
                        # print("Received:{}".format(received))
                        # print("Global: {}".format(device_info))
                except Exception as e:
                    print("Error SET:", e)
                    print("Global: {}".format(device_info))
                finally:
                    # Close the connection
                    sock.close()
                    # print("Close the connection")

            elif data["settings"]["command"] == "REMOTEEN":
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "REMOTEEN"
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                try:
                    # Create a socket (SOCK_STREAM means a TCP socket)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        # Connect to server and send data
                        data = "out_mode_05 1"
                        sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))
                        sock.sendall(bytes(data + "\n", "utf-8"))

                        # Receive data from the server and shut down
                        received = str(sock.recv(1024), "utf-8")

                        # print("Sent:{}".format(data))
                        # print("Received:{}".format(received))
                        # print("Global: {}".format(device_info))
                except Exception as e:
                    print("Error REMOTEEN:", e)
                    print("Global: {}".format(device_info))
                finally:
                    # Close the connection
                    sock.close()
                    # print("Close the connection")

            elif (data["settings"]["command"] == "REMOTEDIS") :
                device_info["inUse"] = False
                device_info["remoteEnabled"] = False
                device_info["tele"]["cmnd"] = "REMOTEDIS"
                device_info["tele"]["state"]["state"] = "OFF"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                try:
                    # Create a socket (SOCK_STREAM means a TCP socket)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        # Connect to server and send data
                        data = "out_sp_00 0.0"
                        sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))
                        sock.sendall(bytes(data + "\n", "utf-8"))

                        # Receive data from the server and shut down
                        received = str(sock.recv(1024), "utf-8")

                        # print("Sent:{}".format(data))
                        # print("Received:{}".format(received))
                        # print("Global: {}".format(device_info))
                except Exception as e:
                    print("Error REMTOEDIS:", e)
                    print("Global: {}".format(device_info))
                finally:
                    # Close the connection
                    sock.close()
                    # print("Close the connection")

                try:
                    # Create a socket (SOCK_STREAM means a TCP socket)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        # Connect to server and send data
                        data = "out_mode_05 0"
                        sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))
                        sock.sendall(bytes(data + "\n", "utf-8"))

                        # Receive data from the server and shut down
                        received = str(sock.recv(1024), "utf-8")

                        # print("Sent:{}".format(data))
                        # print("Received:{}".format(received))
                        # print("Global: {}".format(device_info))
                except Exception as e:
                    print("Error REMOTEDIS2:", e)
                    print("Global: {}".format(device_info))
                finally:
                    # Close the connection
                    sock.close()
                    # print("Close the connection")

    except Exception as e:
        print("Error On Msg:", e)
        print("Global: {}".format(device_info))

# Function to start the periodic task for reading real-time data
def read_real_time_data():
    global device_info

    if (device_info["inUse"] == True) :
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))
                # Send a command to request real-time data (adjust as needed)
                data = "in_pv"
                s.sendall(bytes(data + "\n", "utf-8"))
                response = str(s.recv(1024).decode())

                # print("Sent:{}".format(data))
                # print("Received:{}".format(response))

                # Extract the temperature from the response (adjust based on your device's response format)
                temperature = float(response.split()[0])  # Assuming the response is like "in_pv 25.0"

                # Update device_info with the real-time temperature
                device_info["tele"]["state"]["temp"] = temperature
                device_info["tele"]["cmnd"] = "POLL"
                # print("Global: {}".format(device_info))

                # Publish the updated device_info
                client.publish(MQTT_TOPIC_TELE, json.dumps(device_info))
        except Exception as e:
            print("Error reading real-time data:", e)
            print("Global: {}".format(device_info))
        finally:
            # Close the connection
            s.close()
            # print("Close the connection")

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

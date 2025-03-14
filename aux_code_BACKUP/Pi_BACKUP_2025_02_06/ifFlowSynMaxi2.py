# -*- coding: utf-8 -*-� # Use UTF-8 encoding for better compatibility
import paho.mqtt.client as mqtt
import time
import socket
import json
import threading

# Constants
MQTT_TOPIC_CMND = "subflow/flowsynmaxi2/cmnd"
MQTT_TOPIC_TELE = "subflow/flowsynmaxi2/tele"
MQTT_BROKER_ADDRESS = "146.64.91.174"  # Replace with your broker address
MQTT_BROKER_PORT = 1883
DEVICE_IP_ADDRESS = "192.168.1.202"
DEVICE_PORT = 80
DEVICE_RT_POLL_PERIOD = 2

# Global variables
device_info = {
    "deviceName": "flowsynmaxi2",
    "deviceType": "PumpValveHeater",
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
        "settings": {
            "flowRatePumpA" : 0.0, "flowRatePumpB" : 0.0, "flowRatePumpC" : 0.0, "flowRatePumpD" : 0.0,
            "tempReactor1" : 0.0, "tempReactor2" : 0.0, "tempReactor3" : 0.0, "tempReactor4" : 0.0,
            "valveOpenA" : False, "valveOpenB" : False, "valveOpenC" : False, "valveOpenD" : False, 
            "valveOpenCW": False,
            "injValveOpenA" : False, "injValveOpenB" : False, "injValveOpenC" : False, "injValveOpenD" : False,
            "heaterON" : False},
        "state": {
            "pressSystem" : 0.0,
            "pressFlowSynA"  : 0.0, "pressFlowSynB" : 0.0, "pressBinaryC" : 0.0, "pressBinaryD" : 0.0 ,
            "tempReactor1" : 0.0, "tempReactor2" : 0.0, "tempReactor3" : 0.0, "tempReactor4" : 0.0,
            "valveOpenA" : False, "valveOpenB" : False, "valveOpenC" : False, "valveOpenD" : False, 
            "valveOpenCW" : False, 
            "valveInjOpenA" : False, "valveInjOpenB" : False, "valveInjOpenC" : False,"valveInjOpenD" : False,
            "flowRatePumpA" : 0.0, "flowRatePumpB" : 0.0, "flowRatePumpC" : 0.0, "flowRatePumpD" : 0.0,
            "chillerDetected" : False},
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
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                txData = ""

                if (data["settings"]["subDevice"] == "PumpAFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpA"] = value
                    value = value * 1000                                                        # Convert milliliters -> microliters
                    # Convert Value to HEX
                    valueINT = int(value)
                    valueHEX = format(valueINT, 'x')
                    txData = "*j 0 " + str(valueHEX) + str("\r\n")
                elif(data["settings"]["subDevice"] == "PumpBFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpB"] = value
                    value = value * 1000                                                        # Convert milliliters -> microliters
                    # Convert Value to HEX
                    valueINT = int(value)
                    valueHEX = format(valueINT, 'x')
                    txData = "*j 1 " + str(valueHEX) + str("\r\n")
                elif(data["settings"]["subDevice"] == "BinaryPumpCFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpC"] = value
                    value = value * 1000                                                        # Convert milliliters -> microliters
                    # Convert Value to HEX
                    valueINT = int(value)
                    valueHEX = format(valueINT, 'x')
                    txData = "*j 2 " + str(valueHEX) + str("\r\n")
                elif(data["settings"]["subDevice"] == "BinaryPumpDFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpD"] = value
                    value = value * 1000                                                        # Convert milliliters -> microliters
                    # Convert Value to HEX
                    valueINT = int(value)
                    valueHEX = format(valueINT, 'x')
                    txData = "*j 3 " + str(valueHEX) + str("\r\n")

                elif(data["settings"]["subDevice"] == "Reactor1Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor1"] = value
                    reactor2Temp = device_info["tele"]["settings"]["tempReactor2"]
                    reactor3Temp = device_info["tele"]["settings"]["tempReactor3"]
                    reactor4Temp = device_info["tele"]["settings"]["tempReactor4"]
                    # Convert Value to HEX
                    value1HEX = format(int(value), 'x')
                    value2HEX = format(int(reactor2Temp), 'x')
                    value3HEX = format(int(reactor3Temp), 'x')
                    value4HEX = format(int(reactor4Temp), 'x')
                    txData = "*& " + str(value1HEX) + " " + str(value2HEX) + " " + str(value3HEX) + " " + str(value4HEX) + str("\r\n")
                elif(data["settings"]["subDevice"] == "Reactor2Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor2"] = value
                    reactor1Temp = device_info["tele"]["settings"]["tempReactor1"]
                    reactor3Temp = device_info["tele"]["settings"]["tempReactor3"]
                    reactor4Temp = device_info["tele"]["settings"]["tempReactor4"]
                    # Convert Value to HEX
                    value1HEX = format(int(reactor1Temp), 'x')
                    value2HEX = format(int(value), 'x')
                    value3HEX = format(int(reactor3Temp), 'x')
                    value4HEX = format(int(reactor4Temp), 'x')
                    txData = "*& " + str(value1HEX) + " " + str(value2HEX) + " " + str(value3HEX) + " " + str(value4HEX) + str("\r\n")
                elif(data["settings"]["subDevice"] == "Reactor3Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor3"] = value
                    reactor1Temp = device_info["tele"]["settings"]["tempReactor1"]
                    reactor2Temp = device_info["tele"]["settings"]["tempReactor2"]
                    reactor4Temp = device_info["tele"]["settings"]["tempReactor4"]
                    # Convert Value to HEX
                    value1HEX = format(int(reactor1Temp), 'x')
                    value2HEX = format(int(reactor2Temp), 'x')
                    value3HEX = format(int(value), 'x')
                    value4HEX = format(int(reactor4Temp), 'x')
                    txData = "*& " + str(value1HEX) + " " + str(value2HEX) + " " + str(value3HEX) + " " + str(value4HEX) + str("\r\n")
                elif(data["settings"]["subDevice"] == "Reactor4Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor4"] = value
                    reactor1Temp = device_info["tele"]["settings"]["tempReactor1"]
                    reactor2Temp = device_info["tele"]["settings"]["tempReactor2"]
                    reactor3Temp = device_info["tele"]["settings"]["tempReactor3"]
                    # Convert Value to HEX
                    value1HEX = format(int(reactor1Temp), 'x')
                    value2HEX = format(int(reactor2Temp), 'x')
                    value3HEX = format(int(reactor3Temp), 'x')
                    value4HEX = format(int(value), 'x')
                    txData = "*& " + str(value1HEX) + " " + str(value2HEX) + " " + str(value3HEX) + " " + str(value4HEX) + str("\r\n")

                elif(data["settings"]["subDevice"] == "FlowSynValveA"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveOpenA"] = value
                    if (value == True):
                        txData = "*e 0" + str("\r\n")
                    else:
                        txData = "*e 4" + str("\r\n")
                elif(data["settings"]["subDevice"] == "FlowSynValveB"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveOpenB"] = value
                    if (value == True):
                        txData = "*e 1" + str("\r\n")
                    else:
                        txData = "*e 5" + str("\r\n")
                elif(data["settings"]["subDevice"] == "FlowBinaryValveC"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveOpenC"] = value
                    if (value == True):
                        txData = "*e 2" + str("\r\n")
                    else:
                        txData = "*e 6" + str("\r\n")
                elif(data["settings"]["subDevice"] == "FlowBinaryValveD"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveOpenD"] = value
                    if (value == True):
                        txData = "*e 3" + str("\r\n")
                    else:
                        txData = "*e 7" + str("\r\n")

                elif(data["settings"]["subDevice"] == "FlowCWValve"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveOpenCW"] = value
                    if (value == True):
                        txData = "*e 8" + str("\r\n")
                    else:
                        txData = "*e 9" + str("\r\n")

                elif(data["settings"]["subDevice"] == "FlowSynInjValveA"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["injValveOpenA"] = value
                    if (value == True):
                        txData = "*A 0" + str("\r\n")
                    else:
                        txData = "*A 4" + str("\r\n")
                elif(data["settings"]["subDevice"] == "FlowSynInjValveB"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["injValveOpenB"] = value
                    if (value == True):
                        txData = "*A 1" + str("\r\n")
                    else:
                        txData = "*A 5" + str("\r\n")
                elif(data["settings"]["subDevice"] == "FlowBinaryInjValveC"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["injValveOpenC"] = value
                    if (value == True):
                        txData = "*A 2" + str("\r\n")
                    else:
                        txData = "*A 6" + str("\r\n")
                elif(data["settings"]["subDevice"] == "FlowBinaryInjValveD"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["injValveOpenD"] = value
                    if (value == True):
                        txData = "*A 3" + str("\r\n")
                    else:
                        txData = "*A 7" + str("\r\n")

                elif(data["settings"]["subDevice"] == "Heater"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["heaterON"] = value
                    if (value == True):
                        txData = "*E 1" + str("\r\n")
                    else:
                        txData = "*E 0" + str("\r\n")

                try:
                    # Create a socket (SOCK_STREAM means a TCP socket)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        # Connect to server and send data
                        sock.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))
                        sock.sendall(bytes(txData, "utf-8"))

                        # Receive data from the server and shut down
                        received = str(sock.recv(1024), "utf-8")

                        device_info["tele"]["cmndResp"] = received

                        # print("Sent:{}".format(txData))
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

            elif (data["settings"]["command"] == "REMOTEDIS") :
                device_info["inUse"] = False
                device_info["remoteEnabled"] = False
                device_info["tele"]["cmnd"] = "REMOTEDIS"
                device_info["tele"]["state"]["state"] = "OFF"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

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
                data = "*Q 0\r\n"
                s.sendall(bytes(data, "utf-8"))
                response = str(s.recv(2048).decode())                                       # < P Pa Pb Pc Pd T1 T2 T3 T4 >

                # print("Sent:{}".format(data))
                # print("Received:{}".format(response))

                # Extract the values
                systemPressure = float(response.split()[1])         # P
                flowSynAPressure = float(response.split()[2])       # Pa
                flowSynBPressure = float(response.split()[3])       # Pb
                flowBinaryCPressure = float(response.split()[4])    # Pc
                flowBinaryDPressure = float(response.split()[5])    # Pd
                reactor1Temperature = float(response.split()[6])    # T1
                reactor2Temperature = float(response.split()[7])    # T2
                reactor3Temperature = float(response.split()[8])    # T3
                reactor4Temperature = float(response.split()[9])    # T4

                # Update device_info with the real-time temperature
                device_info["tele"]["cmnd"] = "POLL"
                device_info["tele"]["state"]["pressSystem"] = systemPressure
                device_info["tele"]["state"]["pressFlowSynA"] = flowSynAPressure
                device_info["tele"]["state"]["pressFlowSynB"] = flowSynBPressure
                device_info["tele"]["state"]["pressBinaryC"] = flowBinaryCPressure
                device_info["tele"]["state"]["pressBinaryD"] = flowBinaryDPressure

                device_info["tele"]["state"]["tempReactor1"] = reactor1Temperature
                device_info["tele"]["state"]["tempReactor2"] = reactor2Temperature
                device_info["tele"]["state"]["tempReactor3"] = reactor3Temperature
                device_info["tele"]["state"]["tempReactor4"] = reactor4Temperature
                # print("Global: {}".format(device_info))

                # Publish the updated device_info
                client.publish(MQTT_TOPIC_TELE, json.dumps(device_info))
        except Exception as e:
            print("Error reading real-time data Press/Temp:", e)
            print("Global: {}".format(device_info))
        finally:
            # Close the connection
            s.close()
            # print("Close the connection")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((device_info["connDetails"]["ipCom"]["addr"], int(device_info["connDetails"]["ipCom"]["port"])))
                # Send a command to request real-time data (adjust as needed)
                data = "*Q 1\r\n"
                s.sendall(bytes(data, "utf-8"))
                response = str(s.recv(2048).decode())                                       # * Vs Vi F1 F2 F3 F4 C *

                # print("Sent:{}".format(data))
                # print("Received:{}".format(response))

                # Extract the values
                Vs = int(response.split()[1])     # Vs
                Vi = int(response.split()[2])     # Vi
                F1 = float(response.split()[3])   # F1
                F2 = float(response.split()[4])   # F2
                F3 = float(response.split()[5])   # F3
                F4 = float(response.split()[6])   # F4
                C = int(response.split()[7])      # C

                # Update device_info with the real-time temperature
                device_info["tele"]["state"]["flowRatePumpA"] = F1
                device_info["tele"]["state"]["flowRatePumpB"] = F2
                device_info["tele"]["state"]["flowRatePumpC"] = F3
                device_info["tele"]["state"]["flowRatePumpD"] = F4

                if ((Vs & 0x01) == 0x01):
                    device_info["tele"]["state"]["valveOpenA"] = True
                else:
                    device_info["tele"]["state"]["valveOpenA"] = False

                if ((Vs & 0x02) == 0x02):
                    device_info["tele"]["state"]["valveOpenB"] = True
                else:
                    device_info["tele"]["state"]["valveOpenB"] = False

                if ((Vs & 0x04) == 0x04):
                    device_info["tele"]["state"]["valveOpenC"] = True
                else:
                    device_info["tele"]["state"]["valveOpenC"] = False

                if ((Vs & 0x08) == 0x08):
                    device_info["tele"]["state"]["valveOpenD"] = True
                else:
                    device_info["tele"]["state"]["valveOpenD"] = False

                if ((Vs & 0x10) == 0x10):
                    device_info["tele"]["state"]["valveOpenCW"] = True
                else:
                    device_info["tele"]["state"]["valveOpenCW"] = False

                if ((Vi & 0x01) == 0x01):
                    device_info["tele"]["state"]["valveInjOpenA"] = True
                else:
                    device_info["tele"]["state"]["valveInjOpenA"] = False

                if ((Vi & 0x02) == 0x02):
                    device_info["tele"]["state"]["valveInjOpenB"] = True
                else:
                    device_info["tele"]["state"]["valveInjOpenB"] = False

                if ((Vi & 0x04) == 0x04):
                    device_info["tele"]["state"]["valveInjOpenC"] = True
                else:
                    device_info["tele"]["state"]["valveInjOpenC"] = False

                if ((Vi & 0x08) == 0x08):
                    device_info["tele"]["state"]["valveInjOpenD"] = True
                else:
                    device_info["tele"]["state"]["valveInjOpenD"] = False

                if ((C & 0x01) == 0x01):
                    device_info["tele"]["state"]["chillerDetected"] = True
                else:
                    device_info["tele"]["state"]["chillerDetected"] = False

                # print("Global: {}".format(device_info))

                # Publish the updated device_info
                client.publish(MQTT_TOPIC_TELE, json.dumps(device_info))
        except Exception as e:
            print("Error reading real-time data Flow/Valves:", e)
            print("Global: {}".format(device_info))
        finally:
            # Close the connection
            s.close()
            # print("Close the connection")

    threading.Timer(DEVICE_RT_POLL_PERIOD, read_real_time_data).start()

# polling_thread = threading.Thread(target=read_real_time_data)
# polling_thread.start()
threading.Timer(DEVICE_RT_POLL_PERIOD, read_real_time_data).start()
print("Thread started complete...")

# Initialize MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT)
client.subscribe(MQTT_TOPIC_CMND)
print("MQTT Setup complete...")

# Start the MQTT loop
print("MQTT Loop started complete...")
client.loop_forever()

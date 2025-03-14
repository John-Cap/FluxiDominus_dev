# -*- coding: utf-8 -*-  # Use UTF-8 encoding for better compatibility
import paho.mqtt.client as mqtt
import time
import socket
import json
import threading
import serial

# Constants
MQTT_TOPIC_CMND = "subflow/sf10Vapourtec2/cmnd"
MQTT_TOPIC_TELE = "subflow/sf10Vapourtec2/tele"
MQTT_BROKER_ADDRESS = "146.64.91.174"  # Replace with your broker address
MQTT_BROKER_PORT = 1883
DEVICE_COM_PORT = "/dev/ttyUSB1"
DEVICE_COM_PORT_BAUD = 9600
DEVICE_COM_PORT_BYTELENGTH = serial.EIGHTBITS
DEVICE_COM_PORT_PARITY = serial.PARITY_NONE
DEVICE_COM_PORT_STOPBIT = serial.STOPBITS_ONE
DEVICE_RT_POLL_PERIOD = 2

# Global variables
device_info = {
    "deviceName": "sf10Vapourtec2",
    "deviceType": "Pump",
    "inUse": False,
    "remoteEnabled": False,
    "connDetails":{
        "serialCom" : {
            "port": DEVICE_COM_PORT,
            "baud": DEVICE_COM_PORT_BAUD,
            "dataLength": DEVICE_COM_PORT_BYTELENGTH,
            "parity": DEVICE_COM_PORT_PARITY,
            "stopbits": DEVICE_COM_PORT_STOPBIT,
        }
    },
    "tele": {
        "cmnd": "",
        "cmndResp": "",
        "settings": {
            "mode": "FLOW",
            "flowrate": 0.0,
            "pressure": 0.0,
            "dose": 0.0,
            "gasflowrate": 0.0,
            "rampStartRate": 0.0,
            "rampStopRate": 0.0,
            "rampTime": 0.0
        },
        "timestamp": ""
    }
}

# Function to handle MQTT messages
def on_message(client, userdata, message):
    global device_info
    serTx = ""
    serRx = ""

    try:
        payload = message.payload.decode()
        data = json.loads(payload)

        # print("Msg: {}".format(data))

        if (data["deviceName"] == device_info["deviceName"]):
            if data["settings"]["command"] == "REMOTEEN":
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "REMOTEEN"
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["serialCom"]["port"] = data["connDetails"]["serialCom"]["port"]
                device_info["connDetails"]["serialCom"]["baud"] = data["connDetails"]["serialCom"]["baud"]
                device_info["connDetails"]["serialCom"]["dataLength"] = data["connDetails"]["serialCom"]["dataLength"]
                device_info["connDetails"]["serialCom"]["parity"] = data["connDetails"]["serialCom"]["parity"]
                device_info["connDetails"]["serialCom"]["stopbits"] = data["connDetails"]["serialCom"]["stopbits"]
                serTx = "STOP\r\n"

                try:
                    ser = serial.Serial(
                        port = device_info["connDetails"]["serialCom"]["port"],
                        baudrate = device_info["connDetails"]["serialCom"]["baud"],
                        parity = device_info["connDetails"]["serialCom"]["parity"],
                        stopbits = device_info["connDetails"]["serialCom"]["stopbits"],
                        bytesize = device_info["connDetails"]["serialCom"]["dataLength"]
                    )
                    ser.write(serTx.encode())      # write a string
                    time.sleep(0.25)
                    while ser.inWaiting() > 0:
                        serRx += str(ser.read(1))
                
                    # if serRx != '':
                    #     print ("COM port Resp >>" + serRx)

                    ser.close()             # close port

                    device_info["tele"]["cmndResp"] = serRx
                except Exception as e:
                    print("Error REMOTEEN:", e)
                    print("Msg: {}".format(data))
                    print("Global: {}".format(device_info))

            elif (data["settings"]["command"] == "REMOTEDIS") :
                device_info["inUse"] = False
                device_info["remoteEnabled"] = False
                device_info["connDetails"]["serialCom"]["port"] = data["connDetails"]["serialCom"]["port"]
                device_info["connDetails"]["serialCom"]["baud"] = data["connDetails"]["serialCom"]["baud"]
                device_info["connDetails"]["serialCom"]["dataLength"] = data["connDetails"]["serialCom"]["dataLength"]
                device_info["connDetails"]["serialCom"]["parity"] = data["connDetails"]["serialCom"]["parity"]
                device_info["connDetails"]["serialCom"]["stopbits"] = data["connDetails"]["serialCom"]["stopbits"]
                device_info["tele"]["cmnd"] = "REMOTEDIS"
                serTx = "STOP\r\n"

                try:
                    ser = serial.Serial(
                        port = device_info["connDetails"]["serialCom"]["port"],
                        baudrate = device_info["connDetails"]["serialCom"]["baud"],
                        parity = device_info["connDetails"]["serialCom"]["parity"],
                        stopbits = device_info["connDetails"]["serialCom"]["stopbits"],
                        bytesize = device_info["connDetails"]["serialCom"]["dataLength"]
                    )
                    ser.write(serTx.encode())      # write a string
                    time.sleep(0.25)
                    while ser.inWaiting() > 0:
                        serRx += str(ser.read(1))
                
                    # if serRx != '':
                    #     print ("COM port Resp >>" + serRx)

                    ser.close()             # close port

                    device_info["tele"]["cmndResp"] = serRx
                except Exception as e:
                    print("Error REMOTEDIS:", e)
                    print("Msg: {}".format(data))
                    print("Global: {}".format(device_info))

            elif (data["settings"]["command"] == "START") :
                device_info["inUse"] = data["inUse"]
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["serialCom"]["port"] = data["connDetails"]["serialCom"]["port"]
                device_info["connDetails"]["serialCom"]["baud"] = data["connDetails"]["serialCom"]["baud"]
                device_info["connDetails"]["serialCom"]["dataLength"] = data["connDetails"]["serialCom"]["dataLength"]
                device_info["connDetails"]["serialCom"]["parity"] = data["connDetails"]["serialCom"]["parity"]
                device_info["connDetails"]["serialCom"]["stopbits"] = data["connDetails"]["serialCom"]["stopbits"]
                serTx = "START\r\n"
                device_info["tele"]["cmnd"] = serTx

                try:
                    ser = serial.Serial(
                        port = device_info["connDetails"]["serialCom"]["port"],
                        baudrate = device_info["connDetails"]["serialCom"]["baud"],
                        parity = device_info["connDetails"]["serialCom"]["parity"],
                        stopbits = device_info["connDetails"]["serialCom"]["stopbits"],
                        bytesize = device_info["connDetails"]["serialCom"]["dataLength"]
                    )
                    ser.write(serTx.encode())      # write a string
                    time.sleep(0.25)
                    while ser.inWaiting() > 0:
                        serRx += str(ser.read(1))
                
                    # if serRx != '':
                    #     print ("COM port Resp >>" + serRx)

                    ser.close()             # close port

                    device_info["tele"]["cmndResp"] = serRx
                except Exception as e:
                    print("Error START:", e)
                    print("Msg: {}".format(data))
                    print("Global: {}".format(device_info))

            elif (data["settings"]["command"] == "STOP") :
                device_info["inUse"] = data["inUse"]
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["serialCom"]["port"] = data["connDetails"]["serialCom"]["port"]
                device_info["connDetails"]["serialCom"]["baud"] = data["connDetails"]["serialCom"]["baud"]
                device_info["connDetails"]["serialCom"]["dataLength"] = data["connDetails"]["serialCom"]["dataLength"]
                device_info["connDetails"]["serialCom"]["parity"] = data["connDetails"]["serialCom"]["parity"]
                device_info["connDetails"]["serialCom"]["stopbits"] = data["connDetails"]["serialCom"]["stopbits"]
                serTx = "STOP\r\n"
                device_info["tele"]["cmnd"] = serTx

                try:
                    ser = serial.Serial(
                        port = device_info["connDetails"]["serialCom"]["port"],
                        baudrate = device_info["connDetails"]["serialCom"]["baud"],
                        parity = device_info["connDetails"]["serialCom"]["parity"],
                        stopbits = device_info["connDetails"]["serialCom"]["stopbits"],
                        bytesize = device_info["connDetails"]["serialCom"]["dataLength"]
                    )
                    ser.write(serTx.encode())      # write a string
                    time.sleep(0.25)
                    while ser.inWaiting() > 0:
                        serRx += str(ser.read(1))
                
                    # if serRx != '':
                    #     print ("COM port Resp >>" + serRx)

                    ser.close()             # close port

                    device_info["tele"]["cmndResp"] = serRx
                except Exception as e:
                    print("Error STOP:", e)
                    print("Msg: {}".format(data))
                    print("Global: {}".format(device_info))

            elif (data["settings"]["command"] == "VALVE") :
                device_info["inUse"] = data["inUse"]
                device_info["remoteEnabled"] = True
                device_info["serialCom"]["port"] = data["serialCom"]["port"]
                device_info["serialCom"]["baud"] = data["serialCom"]["baud"]
                device_info["serialCom"]["dataLength"] = data["serialCom"]["dataLength"]
                device_info["serialCom"]["parity"] = data["serialCom"]["parity"]
                device_info["serialCom"]["stopbits"] = data["serialCom"]["stopbits"]
                selValve = data["settings"]["valve"]
                device_info["tele"]["state"]["valve"] = selValve
                serTx = "VALVE " + selValve + str("\r\n")
                device_info["tele"]["cmnd"] = serTx

                try:
                    ser = serial.Serial(
                        port = device_info["serialCom"]["port"],
                        baudrate = device_info["serialCom"]["baud"],
                        parity = device_info["serialCom"]["parity"],
                        stopbits = device_info["serialCom"]["stopbits"],
                        bytesize = device_info["serialCom"]["dataLength"]
                    )
                    ser.write(serTx.encode())      # write a string
                    time.sleep(0.25)
                    while ser.inWaiting() > 0:
                        serRx += str(ser.read(1))
                
                    # if serRx != '':
                    #     print ("COM port Resp >>" + serRx)

                    ser.close()             # close port

                    device_info["tele"]["cmndResp"] = serRx
                except Exception as e:
                    print("Error Valve:", e)
                    print("Msg: {}".format(data))
                    print("Global: {}".format(device_info))

            elif (data["settings"]["command"] == "SET") :
                device_info["connDetails"]["serialCom"]["port"] = data["connDetails"]["serialCom"]["port"]
                device_info["connDetails"]["serialCom"]["baud"] = data["connDetails"]["serialCom"]["baud"]
                device_info["connDetails"]["serialCom"]["dataLength"] = data["connDetails"]["serialCom"]["dataLength"]
                device_info["connDetails"]["serialCom"]["parity"] = data["connDetails"]["serialCom"]["parity"]
                device_info["connDetails"]["serialCom"]["stopbits"] = data["connDetails"]["serialCom"]["stopbits"]

                if (data["settings"]["mode"] == "FLOW") :
                    device_info["inUse"] = data["inUse"]
                    device_info["remoteEnabled"] = True
                    flowRate = data["settings"]["flowrate"]
                    device_info["tele"]["settings"]["flowrate"] = flowRate
                    device_info["tele"]["settings"]["pressure"] = 0
                    device_info["tele"]["settings"]["dose"] = 0
                    device_info["tele"]["settings"]["gasflowrate"] = 0
                    device_info["tele"]["settings"]["rampStartRate"] = 0
                    device_info["tele"]["settings"]["rampStopRate"] = 0
                    device_info["tele"]["settings"]["rampTime"] = 0
                    serTx = "SETFLOW " + str(flowRate) + str("\r\n")
                    device_info["tele"]["cmnd"] = serTx

                    try:
                        ser = serial.Serial(
                            port = device_infodevice_info["serialCom"]["serialCom"]["port"],
                            baudrate = device_info["serialCom"]["serialCom"]["baud"],
                            parity = device_infodevice_info["serialCom"]["serialCom"]["parity"],
                            stopbits = device_infodevice_info["serialCom"]["serialCom"]["stopbits"],
                            bytesize = device_infodevice_info["serialCom"]["serialCom"]["dataLength"]
                        )
                        ser.write(serTx.encode())      # write a string
                        time.sleep(0.25)
                        while ser.inWaiting() > 0:
                            serRx += str(ser.read(1))
                    
                        # if serRx != '':
                        #     print ("COM port Resp >>" + serRx)

                        ser.close()             # close port

                        device_info["tele"]["cmndResp"] = serRx
                    except Exception as e:
                        print("Error Set Flow:", e)
                        print("Msg: {}".format(data))
                        print("Global: {}".format(device_info))

                elif (data["settings"]["mode"] == "REG"):
                    device_info["inUse"] = data["inUse"]
                    device_info["remoteEnabled"] = True
                    pressure = data["settings"]["pressure"]
                    device_info["tele"]["settings"]["flowrate"] = 0
                    device_info["tele"]["settings"]["pressure"] = pressure
                    device_info["tele"]["settings"]["dose"] = 0
                    device_info["tele"]["settings"]["gasflowrate"] = 0
                    device_info["tele"]["settings"]["rampStartRate"] = 0
                    device_info["tele"]["settings"]["rampStopRate"] = 0
                    device_info["tele"]["settings"]["rampTime"] = 0
                    serTx = "SETREG " + str(pressure) + str("\r\n")
                    device_info["tele"]["cmnd"] = serTx

                    try:
                        ser = serial.Serial(
                            port = device_info["serialCom"]["serialCom"]["port"],
                            baudrate = device_info["serialCom"]["serialCom"]["baud"],
                            parity = device_info["serialCom"]["serialCom"]["parity"],
                            stopbits = device_info["serialCom"]["serialCom"]["stopbits"],
                            bytesize = device_info["serialCom"]["serialCom"]["dataLength"]
                        )
                        ser.write(serTx.encode())      # write a string
                        time.sleep(0.25)
                        while ser.inWaiting() > 0:
                            serRx += str(ser.read(1))
                    
                        # if serRx != '':
                        #     print ("COM port Resp >>" + serRx)

                        ser.close()             # close port

                        device_info["tele"]["cmndResp"] = serRx
                    except Exception as e:
                        print("Error Set Reg:", e)
                        print("Msg: {}".format(data))
                        print("Global: {}".format(device_info))

                elif (data["settings"]["mode"] == "DOSE"):
                    device_info["inUse"] = data["inUse"]
                    device_info["remoteEnabled"] = True
                    dose = data["settings"]["dose"]
                    device_info["tele"]["settings"]["flowrate"] = 0
                    device_info["tele"]["settings"]["pressure"] = 0
                    device_info["tele"]["settings"]["dose"] = dose
                    device_info["tele"]["settings"]["gasflowrate"] = 0
                    device_info["tele"]["settings"]["rampStartRate"] = 0
                    device_info["tele"]["settings"]["rampStopRate"] = 0
                    device_info["tele"]["settings"]["rampTime"] = 0
                    serTx = "SETDOSE " + str(dose) + str("\r\n")
                    device_info["tele"]["cmnd"] = serTx

                    try:
                        ser = serial.Serial(
                            port = device_info["serialCom"]["serialCom"]["port"],
                            baudrate = device_info["serialCom"]["serialCom"]["baud"],
                            parity = device_info["serialCom"]["serialCom"]["parity"],
                            stopbits = device_info["serialCom"]["serialCom"]["stopbits"],
                            bytesize = device_info["serialCom"]["serialCom"]["dataLength"]
                        )
                        ser.write(serTx.encode())      # write a string
                        time.sleep(0.25)
                        while ser.inWaiting() > 0:
                            serRx += str(ser.read(1))
                    
                        # if serRx != '':
                        #     print ("COM port Resp >>" + serRx)

                        ser.close()             # close port

                        device_info["tele"]["cmndResp"] = serRx
                    except Exception as e:
                        print("Error Set Dose:", e)
                        print("Msg: {}".format(data))
                        print("Global: {}".format(device_info))

                elif (data["settings"]["mode"] == "GAS"):
                    device_info["inUse"] = data["inUse"]
                    device_info["remoteEnabled"] = True
                    gasflowrate = data["settings"]["gasflowrate"]
                    device_info["tele"]["settings"]["flowrate"] = 0
                    device_info["tele"]["settings"]["pressure"] = 0
                    device_info["tele"]["settings"]["dose"] = 0
                    device_info["tele"]["settings"]["gasflowrate"] = gasflowrate
                    device_info["tele"]["settings"]["rampStartRate"] = 0
                    device_info["tele"]["settings"]["rampStopRate"] = 0
                    device_info["tele"]["settings"]["rampTime"] = 0
                    serTx = "SETGASFLOW " + str(gasflowrate) + str("\r\n")
                    device_info["tele"]["cmnd"] = serTx

                    try:
                        ser = serial.Serial(
                            port = device_info["serialCom"]["serialCom"]["port"],
                            baudrate = device_info["serialCom"]["serialCom"]["baud"],
                            parity = device_info["serialCom"]["serialCom"]["parity"],
                            stopbits = device_info["serialCom"]["serialCom"]["stopbits"],
                            bytesize = device_info["serialCom"]["serialCom"]["dataLength"]
                        )
                        ser.write(serTx.encode())      # write a string
                        time.sleep(0.25)
                        while ser.inWaiting() > 0:
                            serRx += str(ser.read(1))
                    
                        # if serRx != '':
                        #     print ("COM port Resp >>" + serRx)

                        ser.close()             # close port

                        device_info["tele"]["cmndResp"] = serRx
                    except Exception as e:
                        print("Error Set Gas:", e)
                        print("Msg: {}".format(data))
                        print("Global: {}".format(device_info))

                elif (data["settings"]["mode"] == "RAMP"):
                    device_info["inUse"] = data["inUse"]
                    device_info["remoteEnabled"] = True
                    startRate = data["settings"]["rampStartSpeed"]
                    stopRate = data["settings"]["rampStopSpeed"]
                    timeRamp = data["settings"]["rampTime"]
                    device_info["tele"]["settings"]["flowrate"] = 0
                    device_info["tele"]["settings"]["pressure"] = 0
                    device_info["tele"]["settings"]["dose"] = 0
                    device_info["tele"]["settings"]["gasflowrate"] = 0
                    device_info["tele"]["settings"]["rampStartRate"] = startRate
                    device_info["tele"]["settings"]["rampStopRate"] = stopRate
                    device_info["tele"]["settings"]["rampTime"] = timeRamp
                    serTx = "SETRAMP " +  str(startRate) + " " + str(stopRate) + " " + str(timeRamp) + str("\r\n")
                    device_info["tele"]["cmnd"] = serTx

                    try:
                        ser = serial.Serial(
                            port = device_info["serialCom"]["serialCom"]["port"],
                            baudrate = device_info["serialCom"]["serialCom"]["baud"],
                            parity = device_info["serialCom"]["serialCom"]["parity"],
                            stopbits = device_info["serialCom"]["serialCom"]["stopbits"],
                            bytesize = device_info["serialCom"]["serialCom"]["dataLength"]
                        )
                        ser.write(serTx.encode())      # write a string
                        time.sleep(0.25)
                        while ser.inWaiting() > 0:
                            serRx += str(ser.read(1))
                    
                        # if serRx != '':
                        #     print ("COM port Resp >>" + serRx)

                        ser.close()             # close port

                        device_info["tele"]["cmndResp"] = str(serRx)
                    except Exception as e:
                        print("Error Set Ramp:", e)
                        print("Msg: {}".format(data))
                        print("Global: {}".format(device_info))

            # print("Tx    : {}".format(serTx))
            # print("Rx    : {}".format(serRx))
            # print("Global: {}".format(device_info))
    except Exception as e:
        print("Error Main:", e)

# Function to start the periodic task for reading real-time data
def read_real_time_data():
    global device_info

    if (device_info["inUse"] == True) :
        try:
            # print("MQTT Pub: {}".format(device_info))

            # Publish the updated device_info
            client.publish(MQTT_TOPIC_TELE, json.dumps(device_info))
        except Exception as e:
            print("Error reading real-time data:", e)
            print("MQTT Pub: {}".format(device_info))

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

# -*- coding: utf-8 -*-� # Use UTF-8 encoding for better compatibility
import paho.mqtt.client as mqtt
import time
import socket
import json
import threading
import rseriesopc as rs

# Constants
MQTT_TOPIC_CMND = "subflow/vapourtecR4P1700/cmnd"
MQTT_TOPIC_TELE = "subflow/vapourtecR4P1700/tele"
MQTT_BROKER_ADDRESS = "146.64.91.174"  # Replace with your broker address
MQTT_BROKER_PORT = 1883
DEVICE_IP_ADDRESS = "192.168.1.170"
DEVICE_PORT = 43344
DEVICE_RT_POLL_PERIOD = 2

# Global variables
device_info = {
    "deviceName": "vapourtecR4P1700",
    "deviceType": "PumpValveHeater",
    "inUse": False,
    "remoteEnabled": False,
    "connDetails":{
        "ipCom" : {
            "addr": DEVICE_IP_ADDRESS,
            "port": DEVICE_PORT
        }
    },
    "tele": {
        "cmnd": "",
        "cmndResp" : "",
        "settings": {
            "valveASR" : False, "valveBSR" : False, "valveCSR" : False, "valveDSR" : False, 
            "valveAIL" : False, "valveBIL" : False, "valveCIL" : False, "valveDIL" : False, 
            "valveWC": False,
            "flowRatePumpA" : 0.0, "flowRatePumpB" : 0.0, "flowRatePumpC" : 0.0, "flowRatePumpD" : 0.0,
            "pressSystem" : 0.0, "pressPumpA" : 0.0, "pressPumpB" : 0.0, "pressSystem2" : 0.0, "pressPumpC" : 0.0, "pressPumpD" : 0.0,
            "tempReactor1" : 0.0, "tempReactor2" : 0.0, "tempReactor3" : 0.0, "tempReactor4" : 0.0
            },
        "state": {
            "valveASR" : False, "valveBSR" : False, "valveCSR" : False, "valveDSR" : False, 
            "valveAIL" : False, "valveBIL" : False, "valveCIL" : False, "valveDIL" : False, 
            "valveWC": False,
            "flowRatePumpA" : 0.0, "flowRatePumpB" : 0.0, "flowRatePumpC" : 0.0, "flowRatePumpD" : 0.0,
            "pressSystem" : 0.0, "pressPumpA" : 0.0, "pressPumpB" : 0.0, "pressSystem2" : 0.0, "pressPumpC" : 0.0, "pressPumpD" : 0.0,
            "tempReactor1" : 0.0, "tempReactor2" : 0.0, "tempReactor3" : 0.0, "tempReactor4" : 0.0
            },
        "timestamp": ""
    }
}

# Function to handle MQTT messages
def on_message(client, userdata, message):
    global device_info

    try:
        payload = message.payload.decode()
        data = json.loads(payload)
        
        if (data["deviceName"] == device_info["deviceName"]):

            if (data["settings"]["command"] == "SET"):
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "SET"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                if (data["settings"]["subDevice"] == "PumpAFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpA"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2prim = manualControl.getModule(0)

                        pumpA = r2prim.getPumps().get("A")
                        pumpA.setFlowRate(value)

                    except Exception as e:
                        print("Error PumpAFlowRate:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "PumpBFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpB"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2prim = manualControl.getModule(0)

                        pumpB = r2prim.getPumps().get("B")
                        pumpB.setFlowRate(value)

                    except Exception as e:
                        print("Error PumpBFlowRate:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "PumpCFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpC"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2secondary = manualControl.getModule(1)

                        pumpC = r2secondary.getPumps().get("A")
                        pumpC.setFlowRate(value)

                    except Exception as e:
                        print("Error PumpCFlowRate:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "PumpDFlowRate"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["flowRatePumpD"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2secondary = manualControl.getModule(1)

                        pumpD = r2secondary.getPumps().get("B")
                        pumpD.setFlowRate(value)

                    except Exception as e:
                        print("Error PumpDFlowRate:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "Reactor1Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor1"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r4 = manualControl.getR4I()

                        reactor1 = r4.getReactors()["1"]
                        reactor1.setTemperature(value)

                    except Exception as e:
                        print("Error Reactor1Temp:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "Reactor2Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor2"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r4 = manualControl.getR4I()

                        reactor2 = r4.getReactors()["2"]
                        reactor2.setTemperature(value)

                    except Exception as e:
                        print("Error Reactor2Temp:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "Reactor3Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor3"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r4 = manualControl.getR4I()

                        reactor3 = r4.getReactors()["3"]
                        reactor3.setTemperature(value)

                    except Exception as e:
                        print("Error Reactor3Temp:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "Reactor4Temp"):
                    value = float(data["settings"]["value"])
                    device_info["tele"]["settings"]["tempReactor4"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r4 = manualControl.getR4I()

                        reactor4 = r4.getReactors()["4"]
                        reactor4.setTemperature(value)

                    except Exception as e:
                        print("Error Reactor4Temp:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveASR"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveASR"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2prim = manualControl.getModule(0)

                        pumpA = r2prim.getPumps().get("A")
                        pumpA.setSRValveState(value)

                    except Exception as e:
                        print("Error valveASR:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveBSR"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveBSR"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2prim = manualControl.getModule(0)

                        pumpB = r2prim.getPumps().get("B")
                        pumpB.setSRValveState(value)

                    except Exception as e:
                        print("Error valveBSR:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveCSR"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveCSR"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2secondary = manualControl.getModule(1)

                        pumpC = r2secondary.getPumps().get("A")
                        pumpC.setSRValveState(value)

                    except Exception as e:
                        print("Error valveCSR:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveDSR"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveDSR"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2secondary = manualControl.getModule(1)

                        pumpD = r2secondary.getPumps().get("B")
                        pumpD.setSRValveState(value)

                    except Exception as e:
                        print("Error valveDSR:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveWC"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveWC"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()

                        manualControl.setWCValveState(value)

                    except Exception as e:
                        print("Error PumpAFlowRate:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveAIL"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveAIL"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2prim = manualControl.getModule(0)

                        pumpA = r2prim.getPumps().get("A")
                        pumpA.setILValveState(value)

                    except Exception as e:
                        print("Error valveAIL:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveBIL"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveBIL"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2prim = manualControl.getModule(0)

                        pumpB = r2prim.getPumps().get("B")
                        pumpB.setILValveState(value)

                    except Exception as e:
                        print("Error valveBIL:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveCIL"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveCIL"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2secondary = manualControl.getModule(1)

                        pumpC = r2secondary.getPumps().get("A")
                        pumpC.setILValveState(value)

                    except Exception as e:
                        print("Error valveCIL:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

                elif(data["settings"]["subDevice"] == "valveDIL"):
                    value = data["settings"]["value"]
                    device_info["tele"]["settings"]["valveDIL"] = value

                    try:
                        clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                        isConnected = clientOPC_Msg.connect()
                        manualControl = clientOPC_Msg.getRSeries().getManualControl()
                        r2secondary = manualControl.getModule(1)

                        pumpD = r2secondary.getPumps().get("B")
                        pumpD.setILValveState(value)

                    except Exception as e:
                        print("Error valveDIL:", e)
                        print("Global: {}".format(device_info))

                    finally:
                        if isConnected:
                            clientOPC_Msg.disconnect()

            elif data["settings"]["command"] == "REMOTEEN":
                device_info["inUse"] = data["inUse"]
                device_info["tele"]["cmnd"] = "REMOTEEN"
                device_info["remoteEnabled"] = True
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                try:
                    clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                    isConnected = clientOPC_Msg.connect()
                    manualControl = clientOPC_Msg.getRSeries().getManualControl()

                    manualControl.startManualControl()

                except Exception as e:
                    print("Error Real Time:", e)

                finally:
                    if isConnected:
                        clientOPC_Msg.disconnect()

            elif (data["settings"]["command"] == "REMOTEDIS") :
                device_info["inUse"] = False
                device_info["remoteEnabled"] = False
                device_info["tele"]["cmnd"] = "REMOTEDIS"
                device_info["tele"]["state"]["state"] = "OFF"
                device_info["connDetails"]["ipCom"]["addr"] = data["connDetails"]["ipCom"]["addr"]
                device_info["connDetails"]["ipCom"]["port"] = data["connDetails"]["ipCom"]["port"]

                try:
                    clientOPC_Msg = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))
                    isConnected = clientOPC_Msg.connect()
                    manualControl = clientOPC_Msg.getRSeries().getManualControl()

                    manualControl.stopAll()

                except Exception as e:
                    print("Error Real TIme:", e)

                finally:
                    if isConnected:
                        clientOPC_Msg.disconnect()

    except Exception as e:
        print("Error On Msg:", e)
        print("Global: {}".format(device_info))


# Function to start the periodic task for reading real-time data
def read_real_time_data():
    global device_info

    if (device_info["inUse"] == True) :
        try:
            clientOPC_RT = rs.RSeriesClient("opc.tcp://" + str(device_info["connDetails"]["ipCom"]["addr"]) +  ":" + str(int(device_info["connDetails"]["ipCom"]["port"])))

            isConnected = clientOPC_RT.connect()

            manualControl = clientOPC_RT.getRSeries().getManualControl()
            r2prim = manualControl.getModule(0)
            r2secondary = manualControl.getModule(1)

            device_info["tele"]["cmnd"] = "POLL"

            valveWC = manualControl.getWCValveState()
            device_info["tele"]["state"]["valveWC"] = valveWC

            "Getting pump A"
            pumpA = r2prim.getPumps().get("A")
            device_info["tele"]["state"]["valveASR"] = pumpA.getSRValveState()
            device_info["tele"]["state"]["valveAIL"] = pumpA.getILValveState()
            device_info["tele"]["state"]["flowRatePumpA"] = pumpA.getFlowRate()

            "Getting pump B"
            pumpB = r2prim.getPumps()["B"]
            device_info["tele"]["state"]["valveBSR"] = pumpB.getSRValveState()
            device_info["tele"]["state"]["valveBIL"] = pumpB.getILValveState()
            device_info["tele"]["state"]["flowRatePumpB"] = pumpB.getFlowRate()

            "Getting pump C"
            pumpC = r2secondary.getPumpA()
            device_info["tele"]["state"]["valveCSR"] = pumpC.getSRValveState()
            device_info["tele"]["state"]["valveCIL"] = pumpC.getILValveState()
            device_info["tele"]["state"]["flowRatePumpC"] = pumpC.getFlowRate()

            "Getting pump D"
            pumpD = r2secondary.getPumps()["B"]
            device_info["tele"]["state"]["valveDSR"] = pumpD.getSRValveState()
            device_info["tele"]["state"]["valveDIL"] = pumpD.getILValveState()
            device_info["tele"]["state"]["flowRatePumpD"] = pumpD.getFlowRate()

            "Getting a R4 Reactor"
            r4 = manualControl.getR4I()

            reactor1 = r4.getReactors()["1"]
            reactor1Temp = reactor1.getTemperature()
            device_info["tele"]["state"]["tempReactor1"] = reactor1Temp

            reactor2 = r4.getReactors()["2"]
            reactor2Temp = reactor2.getTemperature()
            device_info["tele"]["state"]["tempReactor2"] = reactor2Temp

            reactor3 = r4.getReactors()["3"]
            reactor3Temp = reactor3.getTemperature()
            device_info["tele"]["state"]["tempReactor3"] = reactor3Temp

            reactor4 = r4.getReactors()["4"]
            reactor4Temp = reactor4.getTemperature()
            device_info["tele"]["state"]["tempReactor4"] = reactor4Temp

            pressuresInfo = r2prim.getPumpsPressures()
            device_info["tele"]["state"]["pressSystem"] = pressuresInfo[0]
            device_info["tele"]["state"]["pressPumpA"] = pressuresInfo[1]
            device_info["tele"]["state"]["pressPumpB"] = pressuresInfo[2]

            pressuresInfo = r2secondary.getPumpsPressures()
            device_info["tele"]["state"]["pressSystem2"] = pressuresInfo[0]
            device_info["tele"]["state"]["pressPumpC"] = pressuresInfo[1]
            device_info["tele"]["state"]["pressPumpD"] = pressuresInfo[2]

            # Publish the updated device_info
            client.publish(MQTT_TOPIC_TELE, json.dumps(device_info))

        except Exception as e:
            print("Error Real TIme:", e)
            print("Global: {}".format(device_info))

        finally:
            if isConnected:
                clientOPC_RT.disconnect()

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

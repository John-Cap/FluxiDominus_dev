import json
import os
import time
import random
import numpy as np
import pandas as pd
import paho.mqtt.client as mqtt


class FakeReactor:
    def __init__(self, mqtt_host="localhost", data_folder=""):
        # MQTT setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(host=mqtt_host)
        self.mqtt_client.loop_start()

        # Internal states
        self.hotcoil_temp = 25
        self.target_temp = 5
        self.temp_rate = 0.05
        self.flow_rate = 1.0
        self.flow_range = (0.5, 5.0)
        self.pressure_noise = 0.05
        self.pumpAbase=1.2
        self.pumpBbase=0.9

        # Timing
        self.last_temp_switch = time.time()
        self.temp_switch_interval = 120
        self.last_flow_switch = time.time()
        self.flow_switch_interval = 60

        self.publish_interval = {
            "hotcoil1": 1,
            "vapourtecR4P1700": 1,
            "reactIR702L1": 6
        }

        self.last_publish_time = {
            k: time.time() for k in self.publish_interval
        }

        # Load IR data
        self.ir_data = self.load_ir_data(data_folder)

    def load_ir_data(self, folder_path):
        csv_files = [
            "ir_yield_no_resample_averages.csv",
            "ir_yield_no_resample_unaveraged.csv",
            "ir_yield_no_resample_unmasked.csv",
            "ir_yield_training_data.csv",
        ]
        all_data = []
        for file in csv_files:
            file_path = os.path.join(folder_path, file)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df = df.iloc[:, :-1]  # Remove last column
                rows = [row.values.tolist() for _, row in df.iterrows()]
                all_data.extend(rows)
                print(f"{file}: Loaded {len(rows)} rows.")
            else:
                print(f"Warning: {file} not found in {folder_path}")
        return all_data

    def update_temperature(self):
        now = time.time()
        if now - self.last_temp_switch >= self.temp_switch_interval:
            self.target_temp = random.uniform(25, 120)
            self.last_temp_switch = now

        if abs(self.hotcoil_temp - self.target_temp) > self.temp_rate:
            self.hotcoil_temp += (self.temp_rate + random.uniform(-0.05, 0.05)) if self.hotcoil_temp < self.target_temp else -(self.temp_rate + random.uniform(-0.05, 0.05))
        else:
            self.hotcoil_temp = (self.target_temp + random.uniform(-0.05, 0.05))

    def update_flowrate(self):
        now = time.time()
        if now - self.last_flow_switch >= self.flow_switch_interval:
            self.flow_rate = random.uniform(*self.flow_range)
            self.last_flow_switch = now

    def calculate_pressure(self):
        base_pressure = 1 + 0.07 * self.hotcoil_temp + 1.75 * self.flow_rate
        noise = random.uniform(-self.pressure_noise, self.pressure_noise)
        return base_pressure + noise

    def publish_hotcoil(self):
        payload = {
            "deviceName": "hotcoil1",
            "deviceType": "Hotchip",
            "inUse": True,
            "remoteEnabled": True,
            "ipAddr": "192.168.1.213",
            "port": 81,
            "tele": {
                "cmnd": "POLL",
                "settings": {"temp": self.hotcoil_temp},
                "state": {"temp": self.hotcoil_temp, "state": "ON"},
                "timestamp": time.time()
            }
        }
        self.mqtt_client.publish("subflow/hotcoil1/tele", json.dumps(payload))

    def publish_flow_and_pressure(self):
        system_pressure = self.calculate_pressure()
        pump_offset = 0.2 + random.uniform(-0.05, 0.05)
        press_pump_a = 2*((self.pumpAbase + random.uniform(-0.05, 0.05)) + system_pressure + pump_offset)
        press_pump_b = 2*((self.pumpBbase + random.uniform(-0.05, 0.05)) + system_pressure + pump_offset)

        tele = {
            "cmnd": "",
            "cmndResp": "",
            "settings": {
                "flowRatePumpA": self.flow_rate,
                "flowRatePumpB": self.flow_rate,
                "pressSystem": system_pressure,
                "pressPumpA": press_pump_a,
                "pressPumpB": press_pump_b,
                "tempReactor1": self.hotcoil_temp
            },
            "state": {
                "flowRatePumpA": self.flow_rate,
                "flowRatePumpB": self.flow_rate,
                "pressSystem": system_pressure,
                "pressPumpA": press_pump_a,
                "pressPumpB": press_pump_b,
                "tempReactor1": self.hotcoil_temp
            },
            "timestamp": time.time()
        }

        msg = {
            "deviceName": "vapourtecR4P1700",
            "deviceType": "Hotchip",
            "inUse": True,
            "remoteEnabled": True,
            "ipAddr": "192.168.1.53",
            "port": 81,
            "tele": tele
        }

        self.mqtt_client.publish("subflow/vapourtecR4P1700/tele", json.dumps(msg))

    def publish_ir_data(self):
        if not self.ir_data:
            return
        sample = random.choice(self.ir_data)
        payload = {
            "deviceName": "reactIR702L1",
            "deviceType": "IR",
            "inUse": True,
            "remoteEnabled": True,
            "ipAddr": "192.168.1.50",
            "port": 62552,
            "tele": {
                "cmnd": "POLL",
                "settings": {},
                "state": {"data": sample},
                "timestamp": time.time()
            }
        }
        self.mqtt_client.publish("subflow/reactIR702L1/tele", json.dumps(payload))

    def run(self):
        while True:
            now = time.time()
            self.update_temperature()
            self.update_flowrate()

            if now - self.last_publish_time["hotcoil1"] >= self.publish_interval["hotcoil1"]:
                self.publish_hotcoil()
                self.last_publish_time["hotcoil1"] = now

            if now - self.last_publish_time["vapourtecR4P1700"] >= self.publish_interval["vapourtecR4P1700"]:
                self.publish_flow_and_pressure()
                self.last_publish_time["vapourtecR4P1700"] = now

            if now - self.last_publish_time["reactIR702L1"] >= self.publish_interval["reactIR702L1"]:
                self.publish_ir_data()
                self.last_publish_time["reactIR702L1"] = now

            time.sleep(0.1)


if __name__ == "__main__":
    # Replace with the actual path to your CSVs
    reactor = FakeReactor(mqtt_host="172.30.243.138", data_folder="")
    reactor.run()

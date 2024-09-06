
import time
from Core.UI.plutter import MqttService


mqttService=MqttService(orgId="309931")
mqttService.start()
while True:
    time.sleep(0.5)
    pass
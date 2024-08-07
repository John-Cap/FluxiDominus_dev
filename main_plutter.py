
import time
from Core.UI.plutter import MqttService

if __name__ == "__main__":
    MqttService().start()
    while True:
        time.sleep(0.1)
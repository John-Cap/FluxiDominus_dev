import json
import os
import time

from summit_optimizer import SummitOptimizer

if __name__ == "__main__":
    optimizer = SummitOptimizer()
    cont=False
    saidItOnce=False
    
    optimizer.client.connect(host=optimizer.host)
    optimizer.client.loop_forever()
    
    while True:
        time.sleep(1)
        pass
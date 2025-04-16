
import time

from summit_optimizer import SummitOptimizer

if __name__ == "__main__":
    #Soptimizer = SummitOptimizer(host="localhost")
    optimizer = SummitOptimizer(host="172.30.243.138")
    optimizer.client.connect(host=optimizer.host)
    optimizer.client.loop_forever()
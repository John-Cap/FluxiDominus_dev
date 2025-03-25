
import time

from summit_optimizer import SummitOptimizer

if __name__ == "__main__":
    optimizer = SummitOptimizer(host="localhost")
    #optimizer = SummitOptimizer(host="146.64.91.174")
    optimizer.client.connect(host=optimizer.host)
    optimizer.client.loop_forever()
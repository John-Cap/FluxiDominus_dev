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
'''
        while not cont:
            """ Check if goSummit. """
            try:
                with open(optimizer.summitCmndPath, "r") as f:
                    data = json.load(f)

                if data["goSummit"]:
                    cont=True
                else:
                    if not saidItOnce:
                        print("Waiting for goSummit")
                        saidItOnce=True
                    continue
            except:
                pass

            time.sleep(1)
        
        saidItOnce=False
        saidItOnceRecomm=False
        saidItOnceEval=False
        
        while cont:

            try:

                with open(optimizer.summitCmndPath, "r") as f:
                    data = json.load(f)

                if not data["goSummit"]:
                    cont=False
                    continue
            except:
                time.sleep(1)
                continue

            if optimizer.recommending:
                if not saidItOnceRecomm:
                    saidItOnceRecomm=True
                    saidItOnceEval=False
                    print("Summit is recommending...")
                optimizer.recommend()  #Generate new parameters
            else:
                if not saidItOnceEval:
                    saidItOnceEval=True
                    saidItOnceRecomm=False
                    print("Summit is evaluating...")
                optimizer.update()
            
            time.sleep(4)
'''
import time

from summit_optimizer import SummitOptimizer

if __name__ == "__main__":
    optimizer = SummitOptimizer()
    
    while True:
        if optimizer.recommending:
            optimizer.recommend()  #Generate new parameters
        else:
            optimizer.update()
        
        time.sleep(4)
        
import time
from main import SummitOptimizer

if __name__ == "__main__":
    optimizer = SummitOptimizer()
    
    while True:
        if optimizer.recommending:
            optimizer.recommend()  # Gener  ate new parameters
        else:
            optimizer.update()
        
        time.sleep(4)
import time
from main import SummitOptimizer

if __name__ == "__main__":
    optimizer = SummitOptimizer()
    
    while True:
        optimizer.recommend()  # Generate new parameters
        time.sleep(5)  # Wait for evaluator to process
        optimizer.update()  # Get yield score and update optimizer
        time.sleep(5)

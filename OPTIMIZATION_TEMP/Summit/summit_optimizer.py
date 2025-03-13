
# Run optimization loop
import time
from main import SummitOptimizer


if __name__ == "__main__":
    optimizer = SummitOptimizer()
    
    while True:
        optimizer.recommend()
        time.sleep(5)  # Wait for the evaluator to process

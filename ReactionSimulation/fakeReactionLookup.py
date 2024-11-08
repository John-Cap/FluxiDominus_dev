import pandas as pd
from pathlib import Path

class ReactionLookup:
    def __init__(self, filename=r"ReactionSimulation\tables\reaction_lookup_table.csv"):
        # Load the lookup table from the file in the current working directory
        self.file_path = Path(filename)
        if not self.file_path.exists():
            raise FileNotFoundError(f"{filename} not found in the current directory.")
        
        self.lookup_table = pd.read_csv(self.file_path)
        
    def get_yield(self, x, y):
        # Find the closest point in the lookup table to the given (x, y)
        closest_idx = ((self.lookup_table['X'] - x)**2 + (self.lookup_table['Y'] - y)**2).idxmin()
        closest_row = self.lookup_table.iloc[closest_idx]
        
        # Return the Z value at the closest (X, Y) point
        return closest_row['Z']

# Example usage
if __name__ == "__main__":
    _i = 25
    lookup = ReactionLookup()
    _temp=10
    _res=10
    _inc=1
    while _i>0:
        x_target, y_target = _temp, _res
        z_value = lookup.get_yield(x_target, y_target)
        print(f"Yield at closest point to ({x_target}, {y_target}): {z_value*100}")
        _i-=1
        _temp+=_inc
        _temp+=_inc
        
    print("####")
    x_target, y_target = 34, 10
    z_value = lookup.get_yield(x_target, y_target)
    print(f"Yield at closest point to ({x_target}, {y_target}): {z_value*100}")
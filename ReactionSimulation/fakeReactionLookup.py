import threading
from time import sleep
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

class ReactionLookup:
    def __init__(self, filename=r"ReactionSimulation/tables/max_at_34_10_1.csv"):
        # Load the lookup table from the file
        self.file_path = Path(filename)
        if not self.file_path.exists():
            raise FileNotFoundError(f"{filename} not found in the current directory.")
        
        self.lookup_table = pd.read_csv(self.file_path)
        
        self.loopGraphUpdates=True
        self.updateThread=None
        
        self.fig=None
        
        # Create a numpy array from the lookup table data
        self.data = self.lookup_table[['X', 'Y', 'Z']].values

    def get_yield(self, x, y):
        # Find the closest point in the lookup table to the given (x, y)
        closest_idx = ((self.lookup_table['X'] - x)**2 + (self.lookup_table['Y'] - y)**2).idxmin()
        closest_row = self.lookup_table.iloc[closest_idx]
        
        # Return the Z value at the closest (X, Y) point
        return closest_row['Z']

    def plot_surface(self):
        # Extract X, Y, and Z from the data
        x = self.data[:, 0]
        y = self.data[:, 1]
        z = self.data[:, 2]
        
        # Create a grid for X and Y values
        xi = np.linspace(x.min(), x.max(), 100)
        yi = np.linspace(y.min(), y.max(), 100)
        X, Y = np.meshgrid(xi, yi)
        
        # Interpolate Z values on the grid using griddata
        Z = griddata((x, y), z, (X, Y), method='cubic')
        
        # Plotting
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k', alpha=0.7)
        
        # Add color bar and labels
        self.fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label="Yield (Z)")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Yield (Z)')
        ax.set_title('Reaction Yield Surface Plot')
        
        # Print only, without showing the plot
        print("Plot prepared but not displayed.")
    
    def _updateLoop(self):

        plt.pause(1)
        sleep(0.5)
        pass

# Example usage
if __name__ == "__main__":
    lookup = ReactionLookup()
    lookup.plot_surface()        # Prepare the plot (does not display it)
    #lookup.save_figure()
    #lookup.updateThread=threading.Thread(target=lookup._updateLoop) # Save the prepared plot as an image file
    #lookup.updateThread.start()
    while True:
        lookup.plot_surface()
        plt.pause(1)
    print('Here')

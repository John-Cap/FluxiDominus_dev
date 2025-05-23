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
        self.filePath = Path(filename)
        if not self.filePath.exists():
            raise FileNotFoundError(f"{filename} not found in the current directory.")
        
        self.lookupTable = pd.read_csv(self.filePath)
        
        self.loopGraphUpdates=True
        self.updateThread=None
        
        self.fig=None
        
        self.doUpdate=False
        
        # Create a numpy array from the lookup table data
        self.data = self.lookupTable[['X', 'Y', 'Z']].values

    def getYield(self, x, y):
        # Find the closest point in the lookup table to the given (x, y)
        closestIdx = ((self.lookupTable['X'] - x)**2 + (self.lookupTable['Y'] - y)**2).idxmin()
        closestRow = self.lookupTable.iloc[closestIdx]
        
        # Return the Z value at the closest (X, Y) point
        return closestRow['Z']

    def plotSurface(self):
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
        fig = plt.figure()
        self.fig=fig
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k', alpha=0.7)
        
        # Add color bar and labels
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label="Yield (Z)")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Yield (Z)')
        ax.set_title('Reaction Yield Surface Plot')
        
        # Print only, without showing the plot
        print("Plot prepared but not displayed.")
    
    def _updateLoop(self):
        while True:
            self.doUpdate=True
            while not self.doUpdate:
                sleep(0.1)
# Example usage
if __name__ == "__main__": #Max yield at around x: 33, y: 10
    lookup = ReactionLookup()
    print(lookup.get_yield(33,10))
    lookup.plot_surface()
    while True:
        while lookup.doUpdate:
            plt.pause(1)
        #plt.pause(1)
        sleep(1)
    print('Here')

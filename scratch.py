import threading
from time import sleep
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

class ReactionLookup:
    def __init__(self, filename=r"ReactionSimulation\tables\max_at_34_10_1_2.csv"):
        # Load the lookup table from the file
        self.filePath = Path(filename)
        if not self.filePath.exists():
            raise FileNotFoundError(f"{filename} not found in the current directory.")
        
        self.lookupTable = pd.read_csv(self.filePath)
        self.loopGraphUpdates = True
        self.updateThread = None
        self.fig = None
        self.doUpdate = False
        
        # Create a numpy array from the lookup table data
        self.data = self.lookupTable[['X', 'Y', 'Z']].values

    def getYield(self, x, y):
        # Find the closest point in the lookup table to the given (x, y)
        closestIdx = ((self.lookupTable['X'] - x)**2 + (self.lookupTable['Y'] - y)**2).idxmin()
        closestRow = self.lookupTable.iloc[closestIdx]
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
        self.fig = fig
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k', alpha=0.7)
        
        # Add color bar and labels
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label="Yield (Z)")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Yield (Z)')
        ax.set_title('Reaction Yield Surface Plot')
        
        # Print only, without showing the plot
        plt.show()
    def save_scaled_surface(self, x_max=34, y_max=10):
        # Calculate the max distance within domain bounds
        max_dist = np.sqrt((100 - x_max)**2 + (30 - y_max)**2)

        # Compute distance from the max point
        distances = np.sqrt((self.lookupTable['X'] - x_max)**2 + (self.lookupTable['Y'] - y_max)**2)

        # Compute scaling factors
        scale_factors = 2 * (1 - distances / max_dist)

        # Apply scaling to Z
        self.lookupTable['Z'] = self.lookupTable['Z'] * scale_factors

        # Normalize Z values to 0–1
        self.lookupTable['Z'] = (self.lookupTable['Z'] - self.lookupTable['Z'].min()) / (self.lookupTable['Z'].max() - self.lookupTable['Z'].min())

        # Save the modified DataFrame as a new CSV file
        new_path = self.filePath.with_name(self.filePath.stem + "_2.csv")
        self.lookupTable.to_csv(new_path, index=False)
        print(f"Scaled and normalized surface saved to: {new_path}")

    def _updateLoop(self):
        while True:
            self.doUpdate = True
            while not self.doUpdate:
                sleep(0.1)


# Example usage
if __name__ == "__main__":
    lookup = ReactionLookup()
    print(lookup.getYield(34, 10))  # Sample yield lookup
    lookup.plotSurface()
    # lookup.save_scaled_surface()   # Save the scaled surface as CSV

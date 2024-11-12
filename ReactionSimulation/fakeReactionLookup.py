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
        fig = plt.figure()
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
    
    def save_figure(self, filename="surface_plot.png"):
        # Check if plot_surface was called to prepare the figure
        fig = plt.gcf()  # Get the current figure
        if fig.get_axes():  # Check if any plot has been created
            # Save the figure to the current directory
            fig.savefig(filename)
            print(f"Plot saved as {filename} in the current directory.")
        else:
            print("No plot available to save. Please call plot_surface() first.")

# Example usage
if __name__ == "__main__":
    lookup = ReactionLookup()
    lookup.plot_surface()        # Prepare the plot (does not display it)
    lookup.save_figure()          # Save the prepared plot as an image file
    plt.show()

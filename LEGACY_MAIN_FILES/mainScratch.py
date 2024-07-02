import numpy as np
import matplotlib.pyplot as plt

from Core.Control.IR import IRScanner

_IRscanner = IRScanner()
_IRscanner.parseIrData()
_IRscanner.subtractBlanks()
_nems=["Mix","Heated Reaction","Subtracted"]

# Create a figure and axis object
fig, axs = plt.subplots(len(_IRscanner.allAvgArrays), 1)
#fig, axs = plt.subplots(len(_IRscanner.allAvgArrays), 1)

# Iterate over allAvgArrays and plot each array on a separate subplot
for i, _x in enumerate(_IRscanner.allAvgArrays):
    # Generate x values from 0 to 1 with some step size
    x = np.linspace(0, len(_x), len(_x))

    # Your array of values
    your_array = _x  # Use the actual array, not its length

    # Plot on the ith subplot
    axs[i].plot(x, your_array)
    axs[i].set_xlabel('X-axis')
    axs[i].set_ylabel('Y-axis')
    axs[i].set_title(_nems[i])

# Adjust layout to prevent overlapping of subplots
plt.tight_layout(pad=0.5)

# Show the plots
plt.show()

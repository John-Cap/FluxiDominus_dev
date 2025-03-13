
from scipy.interpolate import interp1d, griddata

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class IrStandard:
    def __init__(self, mainDir, smallValueThreshold=0.005, trimLeft=0, trimRight=0, gradientPercentile=85, thresholdDistance=30, minRangeWidth=10):
        """
        Initializes the IR Standard analysis class.

        Parameters:
        - mainDir (str): Directory containing IR data.
        - smallValueThreshold (float): Values below this are set to zero.
        - trimLeft (int): Number of points to trim from the left.
        - trimRight (int): Number of points to trim from the right.
        - gradientPercentile (int): Percentile threshold to detect high-change regions.
        - thresholdDistance (int): Minimum distance to merge high-change ranges.
        - minRangeWidth (int): Minimum width for a range to be considered valid.
        """
        self.mainDir = mainDir
        self.smallValueThreshold = smallValueThreshold
        self.trimLeft = trimLeft
        self.trimRight = trimRight
        self.gradientPercentile = gradientPercentile
        self.thresholdDistance = thresholdDistance
        self.minRangeWidth = minRangeWidth

        self.allWavenumbers = None
        self.allAverages = []
        self.folderLabels = []
        self.X, self.Y, self.Z = None, None, None

    def loadData(self, targetResolution=0.5):
        """Loads and processes IR data, aligning all scans to a common wavenumber grid."""
        folders = sorted([f for f in os.listdir(self.mainDir) if os.path.isdir(os.path.join(self.mainDir, f))], key=self.naturalSortKey)

        # Store all interpolated scans
        interpolatedIntensities = []
        
        # Find global min and max wavenumbers
        minWavenumber, maxWavenumber = float("inf"), float("-inf")

        for folder in folders:
            folderPath = os.path.join(self.mainDir, folder)
            files = [f for f in os.listdir(folderPath) if f.lower().endswith((".csv", ".xlsx", ".xls"))]

            if not files:
                print(f"⚠ Warning: No valid data files found in {folder}")
                continue

            for fileName in files:
                filePath = os.path.join(folderPath, fileName)
                df = pd.read_csv(filePath, header=0) if fileName.lower().endswith(".csv") else pd.read_excel(filePath, header=0)

                if df.shape[1] < 2:
                    print(f"⚠ Warning: {fileName} does not have enough columns")
                    continue

                wavenumbers = pd.to_numeric(df.iloc[:, 0].values, errors="coerce")
                intensities = pd.to_numeric(df.iloc[:, 1].values, errors="coerce")

                mask = ~np.isnan(intensities)
                wavenumbers, intensities = wavenumbers[mask], intensities[mask]

                intensities[np.abs(intensities) < self.smallValueThreshold] = 0

                if len(intensities) == 0:
                    print(f"⚠ Warning: All intensities in {fileName} are NaN or invalid")
                    continue

                # Update min/max wavenumber
                minWavenumber = min(minWavenumber, wavenumbers.min())
                maxWavenumber = max(maxWavenumber, wavenumbers.max())

                interpolatedIntensities.append((wavenumbers, intensities))

        # Create a **common wavenumber grid** across all scans
        self.allWavenumbers = np.arange(minWavenumber, maxWavenumber, targetResolution)

        # Re-grid all scans onto the common wavenumber axis
        regriddedIntensities = []
        
        for wavenumbers, intensities in interpolatedIntensities:
            interpFunc = interp1d(wavenumbers, intensities, kind='linear', bounds_error=False, fill_value=0)
            regriddedIntensities.append(interpFunc(self.allWavenumbers))  # Resample onto common grid

        self.allAverages = np.array(regriddedIntensities)
        self.folderLabels = np.arange(self.allAverages.shape[0])

    def trimData(self):
        """Trims data based on user-defined left and right trim points."""
        if self.trimLeft == 0 and self.trimRight == 0:
            return
        if self.trimLeft + self.trimRight < self.allAverages.shape[1]:
            self.allWavenumbers = self.allWavenumbers[self.trimLeft:-self.trimRight]
            self.allAverages = self.allAverages[:, self.trimLeft:-self.trimRight]
        else:
            print("🚨 Warning: Trimming exceeds data length. Skipping trim operation.")

    def detectHighChangeRegions(self):
        """Detects high-change regions in the IR spectrum."""
        ZGradient = np.abs(np.gradient(self.allAverages, axis=1))
        highChangeThreshold = np.percentile(ZGradient, self.gradientPercentile)
        highChangeIndices = np.where(ZGradient > highChangeThreshold)

        highChangeWavenumbers = self.allWavenumbers[highChangeIndices[1]]
        sortedWavenumbers = np.sort(highChangeWavenumbers)

        groupedRanges = []
        currentRange = [sortedWavenumbers[0]]

        for i in range(1, len(sortedWavenumbers)):
            if sortedWavenumbers[i] - sortedWavenumbers[i - 1] <= self.thresholdDistance:
                currentRange.append(sortedWavenumbers[i])
            else:
                minCurrentRange, maxCurrentRange = min(currentRange), max(currentRange)
                if maxCurrentRange - minCurrentRange > self.minRangeWidth:
                    groupedRanges.append((minCurrentRange, maxCurrentRange))
                currentRange = [sortedWavenumbers[i]]

        if currentRange:
            groupedRanges.append((min(currentRange), max(currentRange)))

        print("Identified high-change wavenumber ranges:")
        for i, (start, end) in enumerate(groupedRanges, 1):
            print(f"Range {i}: {start} - {end} cm⁻¹")

        return groupedRanges

    def filterData(self, groupedRanges):
        """
        Filters intensity values, setting regions outside high-change areas to zero,
        and converts each peak into a triangular shape for alignment.
        
        Parameters:
        - groupedRanges (list of tuples): Identified high-change wavenumber ranges.
        """
        mask = np.zeros_like(self.allAverages, dtype=bool)
        ZTransformed = np.zeros_like(self.allAverages)  # Matrix for storing triangle peaks

        for start, end in groupedRanges:
            rangeMask = (self.allWavenumbers >= start) & (self.allWavenumbers <= end)

            for i in range(self.allAverages.shape[0]):  # Iterate over each scan
                intensities = self.allAverages[i, rangeMask]
                wavenumbers = self.allWavenumbers[rangeMask]

                # Ensure the range is valid
                if len(intensities) < 3:
                    continue  # Skip if not enough points to form a triangle

                # Find peak position (highest intensity in the range)
                peakIndex = np.argmax(intensities)
                peakValue = intensities[peakIndex]

                # Force start and end to be zero
                intensities[0] = 0
                intensities[-1] = 0

                # Create a linear ramp up to the peak, then back down
                leftSlope = np.linspace(0, peakValue, num=peakIndex + 1)
                rightSlope = np.linspace(peakValue, 0, num=len(intensities) - peakIndex)

                # Combine left and right slopes
                triangleShape = np.concatenate([leftSlope[:-1], rightSlope])

                # Apply the transformed shape
                ZTransformed[i, rangeMask] = triangleShape
                mask[i, rangeMask] = True  # Mark processed areas

        # Preserve only values within detected regions
        self.Z = np.where(mask, ZTransformed, 0)
        self.X, self.Y = np.meshgrid(self.allWavenumbers, self.folderLabels)

    def plotSurface(self):
        """Plots the final filtered IR spectra as a 3D surface plot."""
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_proj_type('ortho')

        ax.plot_surface(self.X, self.Y, self.Z, cmap='viridis')

        ax.set_xlabel("Wavenumber (cm⁻¹)")
        ax.set_ylabel("Sample Index")
        ax.set_zlabel("Average Intensity")
        ax.set_title("Averaged IR Spectra Surface Plot (Filtered)")

        plt.show()

    @staticmethod
    def naturalSortKey(folderName):
        """Extracts numbers from folder names for correct numerical sorting."""
        numbers = re.findall(r'\d+', folderName)
        return int(numbers[0]) if numbers else float('inf')

if __name__ == "__main__":
    irAnalysis = IrStandard(mainDir="isovanillin+allylbromide+product",trimLeft=200,trimRight=40)
    irAnalysis.loadData()
    irAnalysis.trimData()
    highChangeRanges = irAnalysis.detectHighChangeRegions()
    irAnalysis.filterData(highChangeRanges)
    irAnalysis.plotSurface()
    
    # plt.plot(irAnalysis.X[0], irAnalysis.allAverages[1], label="Raw Scan 1")
    # plt.xlabel("Wavenumber (cm⁻¹)")
    # plt.ylabel("Intensity")
    # plt.legend()
    # plt.show()


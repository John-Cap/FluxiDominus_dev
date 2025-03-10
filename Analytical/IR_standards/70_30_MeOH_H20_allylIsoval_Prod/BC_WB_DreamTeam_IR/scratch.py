
import copy
from scipy.interpolate import interp1d, griddata
from scipy.stats import pearsonr
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy.interpolate import CubicSpline
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics.pairwise import cosine_similarity

class IrStandard:
    def __init__(self, mainDir, smallValueThreshold=0.015, trimLeft=0, trimRight=0, gradientPercentile=84, thresholdDistance=50, minRangeWidth=50):
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
        
        self.originalSpectra=[]

        self.allWavenumbers = None
        self.allAverages = []
        self.folderLabels = []
        self.X, self.Y, self.Z = None, None, None
        self.highChangeRanges = None

    def loadData(self, targetResolution=0.5):
        """Loads and processes IR data, aligning all scans to a common wavenumber grid and averaging per folder."""
        folders = sorted(
            [f for f in os.listdir(self.mainDir) if os.path.isdir(os.path.join(self.mainDir, f))],
            key=self.naturalSortKey
        )

        allFolderAverages = []  # Stores only averaged spectra per folder
        self.folderLabels = []  # Reset folder labels

        minWavenumber, maxWavenumber = float("inf"), float("-inf")

        for folderIndex, folder in enumerate(folders):
            folderPath = os.path.join(self.mainDir, folder)
            files = [f for f in os.listdir(folderPath) if f.lower().endswith((".csv", ".xlsx", ".xls"))]

            if not files:
                print(f"⚠ Warning: No valid data files found in {folder}")
                continue

            folderIntensities = []  # Store all scans within a folder

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

                # Track wavenumber range
                minWavenumber = min(minWavenumber, wavenumbers.min())
                maxWavenumber = max(maxWavenumber, wavenumbers.max())

                # Interpolate onto common grid
                if self.allWavenumbers is None:
                    self.allWavenumbers = np.arange(minWavenumber, maxWavenumber, targetResolution)

                interpFunc = interp1d(wavenumbers, intensities, kind='linear', bounds_error=False, fill_value=0)
                folderIntensities.append(interpFunc(self.allWavenumbers))  # Resample onto common grid

            # ✅ Average across all scans in the folder
            if len(folderIntensities) > 0:
                avgIntensity = np.mean(folderIntensities, axis=0)
                self.originalSpectra.append(avgIntensity)
                allFolderAverages.append(avgIntensity)
                self.folderLabels.append(folderIndex)

        # Convert to numpy arrays
        self.allAverages = np.array(allFolderAverages)
        self.folderLabels = np.array(self.folderLabels)

        print(f"✅ Loaded {len(self.folderLabels)} averaged IR spectra from {len(folders)} folders")

    def loadDataNoResample(self, output_csv="ir_yield_no_resample.csv"):
        """
        Loads and processes IR data from multiple folders without resampling onto a new grid.
        Saves the averaged intensities along with calculated yields to a CSV file.

        Parameters:
        - output_csv (str): Name of the output CSV file.

        Returns:
        - None (saves processed data to a CSV file).
        """

        folders = sorted(
            [f for f in os.listdir(self.mainDir) if os.path.isdir(os.path.join(self.mainDir, f))],
            key=self.naturalSortKey
        )

        allFolderAverages = []  # Store averaged intensities per folder
        allYields = []  # Store yield values

        for folderIndex, folder in enumerate(folders):
            folderPath = os.path.join(self.mainDir, folder)
            files = [f for f in os.listdir(folderPath) if f.lower().endswith((".csv", ".xlsx", ".xls"))]

            if not files:
                print(f"⚠ Warning: No valid data files found in {folder}")
                continue

            folderIntensities = []  # Store all scans within a folder

            for fileName in files:
                filePath = os.path.join(folderPath, fileName)
                df = pd.read_csv(filePath, header=0) if fileName.lower().endswith(".csv") else pd.read_excel(filePath, header=0)

                if df.shape[1] < 2:
                    print(f"⚠ Warning: {fileName} does not have enough columns")
                    continue

                intensities = pd.to_numeric(df.iloc[:, 1].values, errors="coerce")

                # Remove NaNs and small noise
                intensities[np.abs(intensities) < self.smallValueThreshold] = 0
                if np.isnan(intensities).all():
                    print(f"⚠ Warning: All intensities in {fileName} are NaN or invalid")
                    continue

                folderIntensities.append(intensities)

            # ✅ Compute average intensity per folder
            if len(folderIntensities) > 0:
                avgIntensity = np.mean(folderIntensities, axis=0)
                allFolderAverages.append(avgIntensity)

                # Compute yield: folder index / 10
                yieldValue = folderIndex / 10.0
                allYields.append(yieldValue)

        self.allFolderAverages=allFolderAverages                
        self.trimData()

        # Convert to pandas DataFrame and save
        df = pd.DataFrame(self.allFolderAverages)
        df['Yield'] = allYields
        df.to_csv(output_csv, index=False)

        print(f"✅ Processed and saved {len(allFolderAverages)} averaged IR spectra to {output_csv}")

    def trimDataSingle(self, data_array):
        """
        Trims the given data array based on user-defined left and right trim points.

        Parameters:
        - data_array (np.array or list of lists): The dataset to be trimmed.

        Returns:
        - trimmed_data (np.array): The trimmed version of the input dataset.
        """
        if self.trimLeft == 0 and self.trimRight == 0:
            return np.array(data_array)  # Return unmodified if no trimming needed

        # Ensure input is a NumPy array
        data_array = np.array(data_array)

        # Check if data_array is empty
        if data_array.size == 0:
            print("🚨 Warning: No data available to trim.")
            return data_array  # Return empty array

        # Ensure trimming does not exceed available data length
        scan_length = data_array.shape[1]  # Number of features (columns)
        if self.trimLeft + self.trimRight >= scan_length:
            print("🚨 Warning: Trimming exceeds data length. Skipping trim operation.")
            return data_array  # Return unmodified

        # Apply trimming
        trimmed_data = data_array[:, self.trimLeft:-self.trimRight]

        print(f"✅ Trimmed data: New shape {trimmed_data.shape}")
        return trimmed_data
        
    def trimData(self):
        """Trims each averaged scan in allFolderAverages based on user-defined left and right trim points."""
        if self.trimLeft == 0 and self.trimRight == 0:
            return

        # Check if allFolderAverages is empty
        if not self.allFolderAverages or len(self.allFolderAverages) == 0:
            print("🚨 Warning: No data available to trim.")
            return

        # Ensure trimming does not exceed available data length
        scan_length = len(self.allFolderAverages[0])  # Assuming all scans have the same length
        if self.trimLeft + self.trimRight >= scan_length:
            print("🚨 Warning: Trimming exceeds data length. Skipping trim operation.")
            return

        # Convert to numpy array if not already, then trim each scan
        self.allFolderAverages = np.array(self.allFolderAverages)[:, self.trimLeft:-self.trimRight]

        print(f"✅ Trimmed allFolderAverages: New shape {self.allFolderAverages.shape}")

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
            
        if self.highChangeRanges is None:
            self.highChangeRanges=groupedRanges
        print(f"ranges please: {groupedRanges}")

        return groupedRanges
    
    def filterDataInterpolate(self, groupedRanges, interpolationFactor=5):
        """
        Filters intensity values, setting regions outside high-change areas to zero,
        and interpolates additional scans without applying a triangle transformation.

        Parameters:
        - groupedRanges (list of tuples): Identified high-change wavenumber ranges.
        - interpolationFactor (int): Number of interpolated scans between each standard scan.
        """
        mask = np.zeros_like(self.allAverages, dtype=bool)
        ZFiltered = np.zeros_like(self.allAverages)  # Store filtered intensity values

        for start, end in groupedRanges:
            rangeMask = (self.allWavenumbers >= start) & (self.allWavenumbers <= end)

            for i in range(self.allAverages.shape[0]):  # Iterate over each scan
                intensities = self.allAverages[i, rangeMask]

                if len(intensities) < 3:
                    continue  # Skip if not enough points to process

                # Preserve the original intensity values inside high-change regions
                ZFiltered[i, rangeMask] = intensities
                mask[i, rangeMask] = True  # Mark valid regions

        # Preserve only values within detected regions
        self.Z = np.where(mask, ZFiltered, 0)

        # Original scan indices
        originalIndices = np.arange(self.allAverages.shape[0])

        # Generate new indices with interpolated points
        interpolatedIndices = np.linspace(0, len(originalIndices) - 1, num=len(originalIndices) + (len(originalIndices) - 1) * interpolationFactor)

        # Interpolate additional scans
        ZInterpolated = np.zeros((len(interpolatedIndices), self.allAverages.shape[1]))

        for j in range(self.allAverages.shape[1]):  # Iterate over each wavenumber column
            validPoints = originalIndices[mask[:, j]]  # Get valid scan indices
            validValues = ZFiltered[:, j][mask[:, j]]  # Get corresponding intensity values

            if len(validPoints) > 1:
                interpFunc = interp1d(validPoints, validValues, kind='linear', fill_value="interpolate")  # Linear interpolation
                ZInterpolated[:, j] = interpFunc(interpolatedIndices)
            else:
                ZInterpolated[:, j] = 0  # Keep as zero if no valid data to interpolate

        # Update dataset with interpolated scans
        self.Z = ZInterpolated
        self.X, self.Y = np.meshgrid(self.allWavenumbers, interpolatedIndices)

    def filterDataTriangleInterpolate(self, groupedRanges, interpolationFactor=5):
        """
        Filters intensity values, setting regions outside high-change areas to zero,
        converts each peak into a triangular shape, and interpolates additional scans.

        Parameters:
        - groupedRanges (list of tuples): Identified high-change wavenumber ranges.
        - interpolationFactor (int): Number of interpolated scans between each standard scan.
        """
        mask = np.zeros_like(self.allAverages, dtype=bool)
        ZTransformed = np.zeros_like(self.allAverages)  # Store transformed triangular peaks

        for start, end in groupedRanges:
            rangeMask = (self.allWavenumbers >= start) & (self.allWavenumbers <= end)

            for i in range(self.allAverages.shape[0]):  # Iterate over each scan
                intensities = self.allAverages[i, rangeMask]
                wavenumbers = self.allWavenumbers[rangeMask]

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
        ZFiltered = np.where(mask, ZTransformed, 0)

        # Original scan indices
        originalIndices = np.arange(self.allAverages.shape[0])

        # Generate new indices with interpolated points
        interpolatedIndices = np.linspace(0, len(originalIndices) - 1, num=len(originalIndices) + (len(originalIndices) - 1) * interpolationFactor)

        # Interpolate additional scans
        ZInterpolated = np.zeros((len(interpolatedIndices), self.allAverages.shape[1]))

        for j in range(self.allAverages.shape[1]):  # Iterate over each wavenumber column
            validPoints = originalIndices[mask[:, j]]  # Get valid scan indices
            validValues = ZFiltered[:, j][mask[:, j]]  # Get corresponding intensity values

            if len(validPoints) > 1:
                interpFunc = interp1d(validPoints, validValues, kind='linear', fill_value="extrapolate")  # Linear interpolation
                ZInterpolated[:, j] = interpFunc(interpolatedIndices)
            else:
                ZInterpolated[:, j] = 0  # Keep as zero if no valid data to interpolate

        # Update dataset with interpolated scans
        self.Z = ZInterpolated
        self.X, self.Y = np.meshgrid(self.allWavenumbers, interpolatedIndices)
        
    def filterData(self, groupedRanges):
        """
        Filters intensity values, setting regions outside high-change areas to zero.
        
        Parameters:
        - groupedRanges (list of tuples): Identified high-change wavenumber ranges.
        """
        mask = np.zeros_like(self.allAverages, dtype=bool)
        ZFiltered = np.zeros_like(self.allAverages)  # Store filtered intensity values

        for start, end in groupedRanges:
            rangeMask = (self.allWavenumbers >= start) & (self.allWavenumbers <= end)

            for i in range(self.allAverages.shape[0]):  # Iterate over each scan
                intensities = self.allAverages[i, rangeMask]

                if len(intensities) < 3:
                    continue  # Skip if not enough points to process

                # Preserve the original intensity values inside high-change regions
                ZFiltered[i, rangeMask] = intensities
                mask[i, rangeMask] = True  # Mark valid regions

        # Preserve only values within detected regions
        self.Z = np.where(mask, ZFiltered, 0)

        # Use only standard scans → No interpolation
        self.X, self.Y = np.meshgrid(self.allWavenumbers, self.folderLabels)

    def filterDataTriangle(self, groupedRanges):
        """
        Filters intensity values, setting regions outside high-change areas to zero,
        and converts each peak into a triangular shape.

        Parameters:
        - groupedRanges (list of tuples): Identified high-change wavenumber ranges.
        """
        mask = np.zeros_like(self.allAverages, dtype=bool)
        ZTransformed = np.zeros_like(self.allAverages)  # Store transformed triangular peaks

        for start, end in groupedRanges:
            rangeMask = (self.allWavenumbers >= start) & (self.allWavenumbers <= end)

            for i in range(self.allAverages.shape[0]):  # Iterate over each scan
                intensities = self.allAverages[i, rangeMask]
                wavenumbers = self.allWavenumbers[rangeMask]

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

        # Use only standard scans → No interpolation
        self.X, self.Y = np.meshgrid(self.allWavenumbers, self.folderLabels)
        
    def processRawScan(self, rawWavenumbers, rawIntensities):
        """
        Processes a raw IR scan:
        1. Aligns the scan to the common wavenumber grid.
        2. Mutes values outside pre-detected high-change regions.
        3. Returns the processed scan for comparison.
        """

        # Ensure NumPy arrays
        rawWavenumbers = np.array(rawWavenumbers)
        rawIntensities = np.array(rawIntensities)
        print(f"First, last wavenumber: {[rawWavenumbers[0], rawWavenumbers[-1]]}")

        print(f"🔎 Raw Wavenumbers Shape: {rawWavenumbers.shape}, Raw Intensities Shape: {rawIntensities.shape}")

        # 🔍 Step 1: Ensure matching sizes (Prevent Shape Mismatch)
        if len(rawWavenumbers) > len(rawIntensities):
            interpFunc = interp1d(np.arange(len(rawIntensities)), rawIntensities, kind='linear', bounds_error=False, fill_value=0)
            rawIntensities = interpFunc(np.linspace(0, len(rawIntensities) - 1, num=len(rawWavenumbers)))

        print(f"First, last wavenumber: {[rawWavenumbers[0], rawWavenumbers[-1]]}")

        print(f"🔎 Raw Wavenumbers Shape: {rawWavenumbers.shape}, Raw Intensities Shape: {rawIntensities.shape}")

        # 🔍 Step 2: Remove NaNs
        validMask = ~np.isnan(rawWavenumbers) & ~np.isnan(rawIntensities)
        rawWavenumbers, rawIntensities = rawWavenumbers[validMask], rawIntensities[validMask]

        if len(rawWavenumbers) == 0:
            raise ValueError("❌ Error: rawWavenumbers is empty after NaN removal.")

        # 🔍 Step 3: Interpolate test scan onto **standard wavenumber grid** (`self.allWavenumbers`)
        interpFunc = interp1d(rawWavenumbers, rawIntensities, kind='linear', bounds_error=False, fill_value=0)
        alignedIntensities = interpFunc(self.allWavenumbers)
        print(f"First, last wavenumber: {[self.allWavenumbers[0], self.allWavenumbers[-1]]}")

        print(f"🔍 Interpolated Intensities Shape: {alignedIntensities.shape}")

        # 🔍 Step 4: Apply small value threshold (mute small noise)
        alignedIntensities[np.abs(alignedIntensities) < self.smallValueThreshold] = 0

        # 🔍 Step 5: Mute values outside detected high-change regions
        ZFiltered = np.zeros_like(alignedIntensities)

        for start, end in self.highChangeRanges:
            print(f"Processing range: {start} - {end}")

            # Find indices where `self.allWavenumbers` falls within the range
            rangeMask = (self.allWavenumbers >= start) & (self.allWavenumbers <= end)
            intensities = alignedIntensities[rangeMask]

            #print(f"🔎 Active Points: {np.sum(rangeMask)} | Nonzero Points: {np.sum(intensities != 0)}")

            if len(intensities) < 3 or np.all(intensities == 0):
                #print(f"🚨 Skipping range {start}-{end}: No valid intensities.")
                continue  # Skip empty or zero regions

            # Preserve the original intensity values inside high-change regions
            ZFiltered[rangeMask] = intensities

        return self.allWavenumbers, ZFiltered

    def processRawScanTriangle(self, rawWavenumbers, rawIntensities):
        """
        Processes a raw IR scan:
        1. Aligns the scan to the common wavenumber grid.
        2. Mutes values outside pre-detected high-change regions.
        3. Applies the triangle method to transform peaks.
        4. Returns the processed scan for comparison.
        """

        # Ensure NumPy arrays
        rawWavenumbers = np.array(rawWavenumbers)
        rawIntensities = np.array(rawIntensities)
        print(f"First, last wavenumber: {[rawWavenumbers[0],rawWavenumbers[-1]]}")

        print(f"🔎 Raw Wavenumbers Shape: {rawWavenumbers.shape}, Raw Intensities Shape: {rawIntensities.shape}")

        # 🔍 Step 1: Ensure matching sizes (Prevent Shape Mismatch)
        if len(rawWavenumbers) > len(rawIntensities):
            interpFunc = interp1d(np.arange(len(rawIntensities)), rawIntensities, kind='linear', bounds_error=False, fill_value=0)
            rawIntensities = interpFunc(np.linspace(0, len(rawIntensities) - 1, num=len(rawWavenumbers)))

        print(f"First, last wavenumber: {[rawWavenumbers[0],rawWavenumbers[-1]]}")

        print(f"🔎 Raw Wavenumbers Shape: {rawWavenumbers.shape}, Raw Intensities Shape: {rawIntensities.shape}")

        # 🔍 Step 2: Remove NaNs
        validMask = ~np.isnan(rawWavenumbers) & ~np.isnan(rawIntensities)
        rawWavenumbers, rawIntensities = rawWavenumbers[validMask], rawIntensities[validMask]

        if len(rawWavenumbers) == 0:
            raise ValueError("❌ Error: rawWavenumbers is empty after NaN removal.")

        # 🔍 Step 3: Interpolate test scan onto **standard wavenumber grid** (`self.allWavenumbers`)
        interpFunc = interp1d(rawWavenumbers, rawIntensities, kind='linear', bounds_error=False, fill_value=0)
        alignedIntensities = interpFunc(self.allWavenumbers)
        print(f"First, last wavenumber: {[self.allWavenumbers[0],self.allWavenumbers[-1]]}")

        print(f"🔍 Interpolated Intensities Shape: {alignedIntensities.shape}")

        # 🔍 Step 4: Apply small value threshold (mute small noise)
        alignedIntensities[np.abs(alignedIntensities) < self.smallValueThreshold] = 0

        # 🔍 Step 5: Mute values outside detected high-change regions
        ZTransformed = np.zeros_like(alignedIntensities)

        for start, end in self.highChangeRanges:
            print(f"Processing range: {start} - {end}")

            # Find indices where `self.allWavenumbers` falls within the range
            rangeMask = (self.allWavenumbers >= start) & (self.allWavenumbers <= end)
            intensities = alignedIntensities[rangeMask]

            print(f"🔎 Active Points: {np.sum(rangeMask)} | Nonzero Points: {np.sum(intensities != 0)}")

            if len(intensities) < 3 or np.all(intensities == 0):
                print(f"🚨 Skipping range {start}-{end}: No valid intensities.")
                continue  # Skip empty or zero regions

            # Find peak index & validate it
            peakIndex = np.argmax(intensities)
            peakValue = intensities[peakIndex]

            if peakValue == 0:
                print(f"🚨 Skipping range {start}-{end}: Peak is zero.")
                continue  # Avoid processing a zero peak

            # Force start and end to be zero
            intensities[0] = 0
            intensities[-1] = 0

            # Create a linear ramp up to the peak, then back down
            leftSlope = np.linspace(0, peakValue, num=peakIndex + 1)
            rightSlope = np.linspace(peakValue, 0, num=len(intensities) - peakIndex)

            print(f"Left/Right slope: {[leftSlope, rightSlope]}")

            # Combine slopes
            triangleShape = np.concatenate([leftSlope[:-1], rightSlope])

            # Store the transformed peak back in the output array
            ZTransformed[rangeMask] = triangleShape

        return self.allWavenumbers, ZTransformed

    def plotSurface(self):
        """Plots the final filtered IR spectra as a 3D surface plot."""
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_proj_type('ortho')
        
        print(f"Thebug: {[self.X.shape,self.Y.shape,self.Z.shape]}")

        ax.plot_surface(self.X, self.Y, self.Z, cmap='viridis')

        ax.set_xlabel("Wavenumber (cm⁻¹)")
        ax.set_ylabel("Sample Index")
        ax.set_zlabel("Average Intensity")
        ax.set_title("Averaged IR Spectra Surface Plot (Filtered)")

        plt.show()

    def analyzeNewScanDTW(self, rawWavenumbers, rawIntensities, referenceZ=None):
        """
        Uses Dynamic Time Warping (DTW) to compare a new IR scan against the standard dataset.

        Parameters:
        - rawWavenumbers (np.array): Wavenumber values from the raw IR scan.
        - rawIntensities (np.array): Corresponding intensity values.
        - referenceZ (np.array): Optional. If provided, uses this as the reference dataset.

        Returns:
        - bestMatchIndex (int): The index of the best-matching reference scan.
        - bestScore (float): The DTW similarity score (lower is better).
        - yieldValue (float): Estimated yield, scaled between 0 and 1.
        """
        
        # 🛠 Process the raw spectrum onto the standard grid
        processedScan = self.processRawScan(rawWavenumbers, rawIntensities)

        # 🔍 Ensure test spectrum is a **strict 1D NumPy array**
        testSpectrum = processedScan[1]
        print(f"Test Spectrum Shape: {testSpectrum.shape}")  # Debug

        # Use provided reference dataset or default to self.Z
        if referenceZ is None:
            referenceZ = self.Z  

        # 🔎 Step 1: Compare test spectrum to each reference using DTW
        bestMatchIndex = None
        bestScore = float("inf")  # Lower DTW distance = better match

        for i in range(referenceZ.shape[0]):
            # 🔍 Ensure reference spectrum is **strict 1D**
            refScan = referenceZ[i, :]
            print(f"Ref Scan {i} Shape: {refScan.shape}")  # Debug

            # Compute DTW distance (lower = better match)
            dtw_distance, _ = fastdtw([testSpectrum], [refScan], dist=euclidean)

            if dtw_distance < bestScore:
                bestScore = dtw_distance
                bestMatchIndex = i

        # 🔍 Step 2: Normalize yield based on best match index
        numStandardScans = referenceZ.shape[0]
        yieldValue = bestMatchIndex / (numStandardScans - 1)

        print(f"🔍 Best DTW match: Index {bestMatchIndex} | DTW Distance: {bestScore:.3f}")
        print(f"🌱 Estimated Yield (DTW): {yieldValue:.3f} (0 = first scan, 1 = last scan)")

        return bestMatchIndex, bestScore, yieldValue

    # def analyzeNewScanDTW(self, rawWavenumbers, rawIntensities, referenceZ=None):
    #     """
    #     Uses Dynamic Time Warping (DTW) to compare a new IR scan against the standard dataset.

    #     Parameters:
    #     - rawWavenumbers (np.array): Wavenumber values from the raw IR scan.
    #     - rawIntensities (np.array): Corresponding intensity values.
    #     - referenceZ (np.array): Optional. If provided, uses this as the reference dataset.

    #     Returns:
    #     - bestMatchIndex (int): The index of the best-matching reference scan.
    #     - bestScore (float): The DTW similarity score (lower is better).
    #     - yieldValue (float): Estimated yield, scaled between 0 and 1.
    #     """
        
    #     # 🛠 Process the raw spectrum onto the standard grid
    #     processedScan = self.processRawScan(rawWavenumbers, rawIntensities)
    #     testSpectrum = processedScan[1].flatten()  # Extract processed intensities
    #     print(f"testSpectrum shape: {testSpectrum.shape}")
    #     input()

    #     # Use provided reference dataset or default to self.Z
    #     if referenceZ is None:
    #         referenceZ = self.Z  

    #     # 🔎 Step 1: Compare test spectrum to each reference using DTW
    #     bestMatchIndex = None
    #     bestScore = float("inf")  # Lower DTW distance = better match

    #     for i in range(referenceZ.shape[0]):
    #         refScan = referenceZ[i, :].flatten()
    #         print(f"refScan shape: {refScan.shape}")
    #         input()

    #         # Compute DTW distance (lower = better match)
    #         dtw_distance, _ = fastdtw(testSpectrum, refScan, dist=euclidean)

    #         if dtw_distance < bestScore:
    #             bestScore = dtw_distance
    #             bestMatchIndex = i

    #     # 🔍 Step 2: Normalize yield based on best match index
    #     numStandardScans = referenceZ.shape[0]
    #     yieldValue = bestMatchIndex / (numStandardScans - 1)

    #     print(f"🔍 Best DTW match: Index {bestMatchIndex} | DTW Distance: {bestScore:.3f}")
    #     print(f"🌱 Estimated Yield (DTW): {yieldValue:.3f} (0 = first scan, 1 = last scan)")

    #     return bestMatchIndex, bestScore, yieldValue
    def analyzeNewScanPearson(self, rawWavenumbers, rawIntensities, referenceZ=None):
        """
        Processes a new raw IR scan and compares it against the standard dataset.

        Parameters:
        - rawWavenumbers (np.array): Wavenumber values from the raw IR scan.
        - rawIntensities (np.array): Corresponding intensity values.
        - referenceZ (np.array): Optional. If provided, uses this as the reference dataset.

        Returns:
        - bestMatchIndex (int): The best-matching index along the standard dataset.
        - bestScore (float): The similarity score (correlation).
        - yieldValue (float): Estimated yield, scaled between 0 (first reference scan) and 1 (last reference scan).
        """

        # 🛠 **Process the raw spectrum first!**
        processedScan = self.processRawScan(rawWavenumbers, rawIntensities)

        """
        # Normalize processed scan (0-1 range)
        processedScan -= processedScan.min()
        if processedScan.max() > 0:
            processedScan /= processedScan.max()
        """
        # Use provided reference dataset or default to self.Z
        if referenceZ is None:
            referenceZ = self.Z  # Default to full dataset

        # Compare to existing standard scans
        bestMatchIndex = None
        bestScore = float("-inf")  # Higher score = better match

        for i in range(referenceZ.shape[0]):
            refScan = referenceZ[i, :]

            # Compute similarity using Pearson correlation
            corr, _ = pearsonr(processedScan[1], refScan)

            if corr > bestScore:
                bestScore = corr
                bestMatchIndex = i

        # Calculate yield as a normalized value between 0 and 1
        numStandardScans = referenceZ.shape[0] + 1  # Total reference scans
        print(f"Num: {numStandardScans}")
        yieldValue = bestMatchIndex / numStandardScans  # Normalize index

        print(f"🔍 Best match found at index {bestMatchIndex} with similarity: {bestScore:.3f}")
        print(f"🌱 Estimated Yield: {yieldValue:.3f} (0 = first scan, 1 = last scan)")

        return bestMatchIndex, bestScore, yieldValue

    def analyzeNewScan(self, rawWavenumbers, rawIntensities, referenceZ=None):
        """
        Processes a new raw IR scan and compares it against the standard dataset.

        Parameters:
        - rawWavenumbers (np.array): Wavenumber values from the raw IR scan.
        - rawIntensities (np.array): Corresponding intensity values.
        - referenceZ (np.array): Optional. If provided, uses this as the reference dataset.

        Returns:
        - bestMatchIndex (int): The best-matching index along the standard dataset.
        - bestScore (float): The similarity score (correlation).
        - yieldValue (float): Estimated yield, scaled between 0 (first reference scan) and 1 (last reference scan).
        """

        # # 🛠 **Process the raw spectrum first!**
        # rawIntensities -= rawIntensities.min()
        # if rawIntensities.max() > 0:
        #     rawIntensities /= rawIntensities.max()

        # print([rawWavenumbers.shape,processedScan[0].shape,processedScan[1].shape])
        # plt.figure(figsize=(10, 5))
        # plt.plot( processedScan[0], processedScan[1], label="Processed Scan", color="blue", alpha=0.7)
        # plt.xlabel("Wavenumber (cm⁻¹)")
        # plt.ylabel("Processed Intensity")
        # plt.title("Processed IR Scan after Filtering & Triangle Transformation")
        # plt.legend()
        # plt.grid(True)
        # plt.show()
        # Normalize processed scan (0-1 range)

        # Use provided reference dataset or default to self.Z
        if referenceZ is None:
            referenceZ = self.Z  # Default to full dataset
            
        processedScan = self.processRawScan(rawWavenumbers, rawIntensities)
        if processedScan[1].shape != self.Z[1].shape:
            print(f"🚨 Shape mismatch! Expected {(self.Z.shape[1],)} but got {processedScan[1].shape}")

        # Compare to existing standard scans
        bestMatchIndex = None
        bestScore = float("-inf")  # Higher score = better match

        if not np.allclose(processedScan[0], self.allWavenumbers):
            print("🚨 Processed scan wavenumbers do NOT match standard dataset wavenumbers!")
            print(f"First 5 wavenumbers: {processedScan[0][:5]} vs {self.allWavenumbers[:5]}")

        for i in range(referenceZ.shape[0]):
            refScan = referenceZ[i, :]

            # Compute similarity using Pearson correlation
            scan=processedScan[1].flatten()
            ref=refScan.flatten()
            
            bestMatchIndex = None
            bestScore = float("-inf")  # Higher = better match

            processedScanNorm = processedScan[1].reshape(1, -1)  # Ensure 2D
            for i in range(self.Z.shape[0]):
                refScanNorm = self.Z[i, :].reshape(1, -1)
                
                # Compute cosine similarity
                score = cosine_similarity(processedScanNorm, refScanNorm)[0, 0]

                if score > bestScore:
                    bestScore = score
                    bestMatchIndex = i

        # Calculate yield as a normalized value between 0 and 1
        numStandardScans = referenceZ.shape[0]  # Total reference scans
        print(f"Num: {numStandardScans},shape: {referenceZ.shape}")
        yieldValue = bestMatchIndex / (numStandardScans - 1)  # Normalize index

        print(f"🔍 Best match found at index {bestMatchIndex} with similarity: {bestScore:.3f}")
        print(f"🌱 Estimated Yield: {yieldValue:.3f} (0 = first scan, 1 = last scan)")

        return bestMatchIndex, bestScore, yieldValue

    def generateInterpolatedSpectraLinear(self, numInterpolated=5):
        """
        Generates interpolated test spectra between existing scans.

        Parameters:
        - numInterpolated (int): Number of interpolated spectra to generate between each pair.

        Returns:
        - interpolatedZ (np.array): New interpolated intensity dataset.
        - interpolatedY (np.array): Updated sample indices including interpolated points.
        """
        originalY = self.folderLabels  # Existing sample indices
        interpolatedZ = [self.Z[0, :]]  # Start with the first scan

        newY = [originalY[0]]

        for i in range(len(originalY) - 1):
            scan1 = self.Z[i, :]
            scan2 = self.Z[i + 1, :]

            for j in range(1, numInterpolated + 1):
                weight = j / (numInterpolated + 1)
                interpolatedScan = (1 - weight) * scan1 + weight * scan2  # Linear interpolation
                interpolatedZ.append(interpolatedScan)
                newY.append(originalY[i] + weight)  # Position between existing scans

            interpolatedZ.append(scan2)
            newY.append(originalY[i + 1])

        interpolatedZ = np.array(interpolatedZ)
        interpolatedY = np.array(newY)

        print(f"✅ Generated {numInterpolated} interpolated spectra per pair. New total scans: {len(interpolatedY)}")

        return interpolatedZ, interpolatedY
    
    def generateInterpolatedSpectraSpline(self, numInterpolated=5, method='cubic'):
        """
        Generates interpolated test spectra between existing scans.

        Parameters:
        - numInterpolated (int): Number of interpolated spectra to generate between each pair.
        - method (str): Interpolation method ('linear', 'cubic', 'quadratic').

        Returns:
        - interpolatedZ (np.array): New interpolated intensity dataset.
        - interpolatedY (np.array): Updated sample indices including interpolated points.
        """
        originalY = self.folderLabels  # Existing sample indices
        interpolatedZ = [self.Z[0, :]]  # Start with the first scan
        newY = [originalY[0]]

        for i in range(len(originalY) - 1):
            scan1 = self.Z[i, :]
            scan2 = self.Z[i + 1, :]

            for j in range(1, numInterpolated + 1):
                weight = j / (numInterpolated + 1)

                if method == 'linear':
                    interpolatedScan = (1 - weight) * scan1 + weight * scan2  # Linear interpolation
                elif method == 'cubic':
                    cs = CubicSpline([0, 1], np.vstack([scan1, scan2]), axis=0)  # Cubic spline interpolation
                    interpolatedScan = cs(weight)
                elif method == 'quadratic':
                    interpFunc = interp1d([0, 1], np.vstack([scan1, scan2]), kind='quadratic', axis=0, fill_value="extrapolate")
                    interpolatedScan = interpFunc(weight)
                else:
                    raise ValueError("Unsupported interpolation method. Choose 'linear', 'cubic', or 'quadratic'.")

                interpolatedZ.append(interpolatedScan)
                newY.append(originalY[i] + weight)  # Position between existing scans

            interpolatedZ.append(scan2)
            newY.append(originalY[i + 1])

        interpolatedZ = np.array(interpolatedZ)
        interpolatedY = np.array(newY)

        print(f"✅ Generated {numInterpolated} interpolated spectra per pair using {method} interpolation. New total scans: {len(interpolatedY)}")

        # 🛠️ **Fix meshgrid for plotting**
        self.Z = interpolatedZ
        self.Y = interpolatedY
        self.X, self.Y = np.meshgrid(self.allWavenumbers, self.Y)  # 🔥 Ensure correct shape!

        return self.Z, self.Y
    
    def normalizeSpectrum(intensities):
        return (intensities - np.mean(intensities)) / np.std(intensities)

    @staticmethod
    def naturalSortKey(folderName):
        """Extracts numbers from folder names for correct numerical sorting."""
        numbers = re.findall(r'\d+', folderName)
        return int(numbers[0]) if numbers else float('inf')
    
if __name__ == "__main__":
    # Step 1: Initialize and process the standard curve
    irAnalysis = IrStandard(mainDir="isovanillin+allylbromide+product", trimLeft=200, trimRight=40)
    irAnalysis.originalSpectra = []  # Store raw spectra for later testing

    irAnalysis.loadDataNoResample()

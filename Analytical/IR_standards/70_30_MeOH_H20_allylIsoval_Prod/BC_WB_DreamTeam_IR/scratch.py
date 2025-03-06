
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

    irAnalysis.loadData()
    irAnalysis.trimData()
    highChangeRanges = irAnalysis.detectHighChangeRegions()
    print(f"Ranges: {highChangeRanges}")
    #exit()
    irAnalysis.filterDataInterpolate(highChangeRanges,interpolationFactor=3)

    # Step 2: Convert original raw spectra to test cases
    #Middle
    test_cases = copy.deepcopy(irAnalysis.Z) #[[-0.000920472, -0.001037177, -0.001142116, -0.001162132, -0.001098506, -0.001056892, -0.001097379, -0.001112349, -0.000964116, -0.000712267, -0.000560399, -0.000577375, -0.000614591, -0.000521822, -0.000348506, -0.000238255, -0.000222526, -0.000225397, -0.00020954, -0.000221646, -0.000309547, -0.000464161, -0.000650133, -0.000827587, -0.000924879, -0.000892768, -0.000810557, -0.000782827, -0.000803771, -0.000821716, -0.000853951, -0.000946713, -0.001066015, -0.001138114, -0.001180775, -0.001259979, -0.00132822, -0.00127308, -0.001138607, -0.00106131, -0.001028431, -0.000934929, -0.000828669, -0.000856943, -0.000970179, -0.000948848, -0.000744216, -0.000590923, -0.000571521, -0.000485172, -0.000224139, -7.81E-05, -0.000288939, -0.000682144, -0.000907439, -0.000822567, -0.00062649, -0.00054253, -0.000579795, -0.000622268, -0.000599954, -0.000509404, -0.00038913, -0.000366754, -0.000566256, -0.000900248, -0.001104194, -0.000932327, -0.000394129, 0.000195361, 0.000447261, 0.0002131, -0.000225876, -0.000394663, -0.0001934, 3.1643251032672E-05, 1.56582797997437E-05, -0.000170259, -0.000313857, -0.000370548, -0.000468484, -0.000714161, -0.001113867, -0.001507949, -0.001689592, -0.001598015, -0.001246198, -0.000623253, 0.000313609, 0.001523619, 0.00280702, 0.003986387, 0.005133507, 0.006441188, 0.00775227, 0.008649359, 0.009194343, 0.00993352, 0.011052952, 0.012103147, 0.012835793, 0.013479278, 0.01411734, 0.014475916, 0.014609999, 0.014958973, 0.01547429, 0.015590206, 0.015233841, 0.015231585, 0.016028331, 0.016799727, 0.016730053, 0.016005374, 0.015340305, 0.01517724, 0.015558784, 0.016379317, 0.016973897, 0.016311105, 0.01446388, 0.012634979, 0.01163075, 0.010967642, 0.009750983, 0.00807274, 0.006664332, 0.005665376, 0.004733578, 0.003934132, 0.003375156, 0.002400099, 0.000447726, -0.001744639, -0.002786246, -0.002585399, -0.002558475, -0.003249393, -0.003644834, -0.00325837, -0.003041707, -0.003555948, -0.004229116, -0.004784773, -0.005869505, -0.007812536, -0.009973085, -0.011581277, -0.012502645, -0.01256167, -0.011810276, -0.012039613, -0.01540623, -0.021315201, -0.026055301, -0.026867562, -0.025482625, -0.024864634, -0.025983724, -0.028616249, -0.032380765, -0.036056296, -0.037891572, -0.038030955, -0.038455329, -0.039249773, -0.038404767, -0.035982497, -0.034681696, -0.035245754, -0.035197384, -0.033152659, -0.031258273, -0.03117346, -0.031718428, -0.031667327, -0.031950505, -0.033503448, -0.035100958, -0.035168082, -0.034199017, -0.033152042, -0.031997725, -0.031337178, -0.032683871, -0.035825911, -0.038253373, -0.038413303, -0.03766322, -0.037297112, -0.036815291, -0.036154998, -0.036719249, -0.038853754, -0.040676259, -0.040844792, -0.040674122, -0.041687548, -0.043424755, -0.044865005, -0.046030932, -0.046889157, -0.046683851, -0.045481952, -0.044588443, -0.04447916, -0.044086333, -0.042766893, -0.041248149, -0.03995666, -0.038165666, -0.035556735, -0.033154366, -0.03184529, -0.03127885, -0.030690062, -0.029963271, -0.029233485, -0.028271562, -0.026993926, -0.025917533, -0.02552152, -0.025554835, -0.025333697, -0.024501824, -0.023176992, -0.021651911, -0.020214207, -0.019027565, -0.018106052, -0.017493329, -0.017388614, -0.017878178, -0.018610536, -0.018999, -0.018776207, -0.018155983, -0.017468397, -0.016930296, -0.01670068, -0.016835716, -0.01717695, -0.017487151, -0.017712305, -0.01798421, -0.018511475, -0.019750385, -0.022482262, -0.02723466, -0.033505315, -0.039865165, -0.045356892, -0.050622436, -0.056692551, -0.062955366, -0.067300733, -0.068375336, -0.066451997, -0.06243624, -0.057639466, -0.053488076, -0.050304579, -0.047101253, -0.043175481, -0.039234449, -0.036257848, -0.034326196, -0.033044442, -0.032185882, -0.031559104, -0.030843643, -0.029970663, -0.029232902, -0.02879838, -0.028594954, -0.028684103, -0.029222263, -0.029945642, -0.030088475, -0.029081444, -0.027113902, -0.024782351, -0.022542779, -0.020614256, -0.019010182, -0.017572763, -0.016284646, -0.015640882, -0.01638715, -0.018646963, -0.0213402, -0.02270916, -0.02193002, -0.019866718, -0.017877268, -0.016622447, -0.015967457, -0.015437301, -0.014706725, -0.013813596, -0.01294326, -0.012101391, -0.011136275, -0.01000084, -0.008798908, -0.007600727, -0.006399696, -0.005239598, -0.004226498, -0.003408976, -0.002756589, -0.002243364, -0.001860756, -0.001567149, -0.001307252, -0.001064115, -0.000835536, -0.000610458, -0.000436201, -0.000437201, -0.000662108, -0.000964777, -0.001145245, -0.001179472, -0.001203992, -0.001297077, -0.001398221, -0.001436972, -0.001428355, -0.001424736, -0.001461414, -0.001565972, -0.001746884, -0.001960866, -0.002149939, -0.002308974, -0.002461773, -0.002580306, -0.002597176, -0.002508122, -0.002381903, -0.002251211, -0.002096862, -0.001953932, -0.001904194, -0.001953565, -0.002058413, -0.002248937, -0.002560722, -0.002894747, -0.003161328, -0.003508348, -0.004094127, -0.004721086, -0.005084676, -0.005328835, -0.005943784, -0.007102278, -0.008524357, -0.009958871, -0.011373966, -0.012685032, -0.013788415, -0.014895549, -0.016250022, -0.017530413, -0.018058172, -0.017592266, -0.016435613, -0.014818604, -0.01290567, -0.011223074, -0.010166217, -0.009367895, -0.008336213, -0.007358807, -0.00700709, -0.007105801, -0.00707692, -0.006952658, -0.007149303, -0.007477821, -0.0072829, -0.006449685, -0.005497477, -0.004738002, -0.00412327, -0.00372006, -0.003562919, -0.003200554, -0.002224322, -0.001160921, -0.000891578, -0.001347359, -0.00169541, -0.001571987, -0.001365103, -0.001350802, -0.001334035, -0.001153787, -0.000950998, -0.000873056, -0.000916775, -0.000989354, -0.000876163, -0.000282283, 0.000858886, 0.002143006, 0.003063045, 0.003509918, 0.003544458, 0.003167661, 0.002628281, 0.002363735, 0.002527836, 0.002766341, 0.002639442, 0.002265475, 0.002010129, 0.001812349, 0.001317153, 0.000519609, -0.000123255, -0.000447377, -0.000756083, -0.001049603, -0.001093368, -0.001374131, -0.002861234, -0.005341679, -0.007101655, -0.007440785, -0.008127815, -0.010099481, -0.011700433, -0.012037686, -0.012786926, -0.014270437, -0.013707662, -0.010637964, -0.009306783, -0.012088566, -0.016726211, -0.018174312, -0.015830522, -0.01069223, -0.00168911, 0.005121458, 0.003254947, -0.004732051, -0.010564126, -0.011843844, -0.013318009, -0.016428174, -0.016847652, -0.01705181, -0.020166553, -0.01997, -0.00668067, 0.007642256, 0.012253121, 0.008677204, 0.003414669, -0.000283022, 0.000327306, 0.002933175, 0.010828142, 0.016071819, 0.013406271, 0.007978943, 0.005027665, 0.005136112, 0.004890513, 0.003332555, 0.003053923, 0.004724198, 0.005487878, 0.004896435, 0.005231038, 0.006642984, 0.007147983, 0.007357765, 0.009681423, 0.01135048, 0.00758292, 0.000745758, -0.001623899, 0.004046783, 0.00865091, 0.006043417, -0.000564405, -0.003506615, -0.009137173, -0.020612624, -0.024207413, -0.014262148, -0.010498645, -0.014103738, -0.011898092, -0.003898671, -0.002731963, -0.003600963, 0.005270824, 0.018303169, 0.022706695, 0.026032029, 0.034999421, 0.033412475, 0.023664289, 0.015400431, 0.012391556, 0.010316012, 0.003080341, -0.005751585, -0.007400288, -0.002838715, -0.002327581, -0.005392381, -0.005119721, -0.000889424, 0.001295802, 0.000594861, 0.00049348, 0.00190345, 0.002423178, 0.001788547, 0.001884581, 0.002688334, 0.00230001, 0.00102548, 0.000822299, 0.001669827, 0.001583868, 0.000291917, -0.000379529, 0.000167279, 0.000572081, 0.000441519, 0.000625256, 0.001101529, 0.000880754, 0.000200596, 0.000198632, 0.000749417, 0.000582552, -0.000249555, -0.00054857, -0.000234071, -0.000330767, -0.001059432, -0.001537501, -0.001299777, -0.001065828, -0.001339928, -0.001694411, -0.001944928, -0.002686819, -0.004178749, -0.005680847, -0.006746428, -0.008026807, -0.009885436, -0.011548673, -0.012320437, -0.012803985, -0.013281645, -0.012613897, -0.010566981, -0.008980515, -0.008494852, -0.00753579, -0.004813186, -0.001383307, 0.002416674, 0.009732937, 0.023933269, 0.042506795, 0.060986747, 0.080201618, 0.100257939, 0.1147315, 0.117227386, 0.1076776, 0.090096094, 0.071178486, 0.056157734, 0.045648442, 0.037879281, 0.031756106, 0.027526583, 0.025019126, 0.023168501, 0.021138968, 0.019362687, 0.018605234, 0.018941501, 0.021285393, 0.02898645, 0.045256388, 0.069031409, 0.094319041, 0.113976725, 0.123917972, 0.123339031, 0.111966878, 0.089622232, 0.060879773, 0.036323663, 0.022057863, 0.014800133, 0.009636332, 0.006089957, 0.005114219, 0.004881777, 0.004052402, 0.004249418, 0.007150885, 0.011864273, 0.020260105, 0.039031436, 0.070612634, 0.102451636, 0.116116877, 0.101341018, 0.067711015, 0.037366796, 0.018330851, 0.006694902, -0.000548084, -0.003750773, -0.003896304, -0.002056529, 0.001823475, 0.006709608, 0.009579535, 0.008889825, 0.008283429, 0.015445141, 0.031530235, 0.049881081, 0.061601053, 0.060371736, 0.049361835, 0.036008676, 0.023563649, 0.012779802, 0.005245126, 0.001980214, 0.001647124, 0.001563612, -0.00032664, -0.00430726, -0.009376057, -0.01443449, -0.018601911, -0.020781524, -0.020137823, -0.017399073, -0.014349725, -0.011652356, -0.008358088, -0.003359214, 0.003460035, 0.011171648, 0.017703362, 0.020438661, 0.018810652, 0.015336017, 0.012814002, 0.011908939, 0.011595195, 0.011015238, 0.010530175, 0.011287181, 0.014470501, 0.021048134, 0.031790629, 0.047923175, 0.072543797, 0.110408274, 0.163602895, 0.224812124, 0.273834259, 0.285177788, 0.250382814, 0.189979596, 0.132443287, 0.094201918, 0.079035289, 0.081104068, 0.087270878, 0.084343151, 0.069023513, 0.048906857, 0.03242268, 0.021951645, 0.015892842, 0.012515021, 0.010913477, 0.010536281, 0.011176263, 0.012589235, 0.01359595, 0.01286115, 0.011454256, 0.013338379, 0.021608333, 0.03437647, 0.044988499, 0.047036617, 0.040063029, 0.030388698, 0.027535486, 0.039184861, 0.065723754, 0.096998154, 0.115770893, 0.111175196, 0.08916999, 0.063356686, 0.04170476, 0.025489943, 0.014302376, 0.007902927, 0.00483947, 0.002754777, 0.000542521, -0.001405694, -0.002873958, -0.004349443, -0.005953419, -0.007048192, -0.00719802, -0.00675091, -0.006177009, -0.005526341, -0.004937639, -0.005046075, -0.006416092, -0.008980125, -0.012393308, -0.01687082, -0.02366906, -0.033831052, -0.04377404, -0.045020063, -0.040516734, -0.029896484, -0.00960882, 0.009080586, 0.021378871, 0.028014686, 0.02960603, 0.026928686, 0.021651452, 0.015531377, 0.009537844, 0.004113054, -0.000134648, -0.002425905, -0.002311276, 0.000252125, 0.005260274, 0.012471564, 0.020536118, 0.027130939, 0.030741357, 0.031489123, 0.029856182, 0.026025548, 0.020843591, 0.015998848, 0.012590377, 0.01020966, 0.008015323, 0.006128455, 0.005119484, 0.004747048, 0.004400347, 0.004484817, 0.005999233, 0.008837121, 0.011716843, 0.013584975, 0.01365933, 0.011047836, 0.006120075, 0.001071196, -0.002034163, -0.003277532, -0.003800067, -0.002840366, 0.001621257, 0.008825623, 0.015645834, 0.021222839, 0.024719542, 0.022771516, 0.016260878, 0.011925927, 0.012607652, 0.009844558, -0.001834886, -0.012349108, -0.008823205, 0.004210111, 0.006155242, -0.003706873, -0.008107415, -0.000589765, 0.001126657, -0.009430217, -0.018629792, -0.011329238, -0.020217515, -0.03482597, -0.026575661, 0.001762308, 0.050646186, 0.052769343, 0.030418818, 0.020130991, 0.011994198, -0.027340096, -0.059415674, -0.041469977, -0.015536203, -0.023801729, -0.031440204, -0.005445265, 0.012890134, 0.000951528, -0.001758116, 0.015946043, 0.024235539, 0.004098743, -0.01174373, -0.043953606, -0.046385025]]
    test_ref = copy.deepcopy(irAnalysis.Z)
    
    print(f"✅ Created {len(test_cases)} test cases from original raw spectra.")

    # Step 3: Iterate through raw spectra, process, and analyze
    problemScans = 0
    results = []
    rawWavenumbers = irAnalysis.allWavenumbers  # Assume original wavenumbers match common grid
    noramlized=[]

    # Step 6: Visualize the result
    irAnalysis.plotSurface()

    for i, testSpectrum in enumerate(test_cases):
        rawIntensities = (np.array(testSpectrum))  # Convert back to array
        print(f"Raw Wavenumbers Shape: {rawWavenumbers.shape}, Raw Intensities Shape: {rawIntensities.shape}")

        # plt.plot(rawWavenumbers, rawIntensities, label=f"Raw Scan {i}")
        # plt.xlabel("Wavenumber (cm⁻¹)")
        # plt.ylabel("Intensity")
        # plt.legend()
        # plt.show()

        # 🛠 Apply jitter (±5% random variation)
        jitterFactor = 0.05  # Max 5% variation
        noise = 0#(np.random.rand(*rawIntensities.shape) - 0.5) * 2 * jitterFactor
        jitteredTestSpectrum = np.clip(rawIntensities + rawIntensities * noise, 0, 1)

        print(f"\n🔬 Testing raw spectrum {i + 1}/{len(test_cases)} with jitter:")

        # Step 4: Compare test spectrum **against original standard scans only**
        bestMatchIndex, bestScore, yieldValue = irAnalysis.analyzeNewScan(rawWavenumbers,jitteredTestSpectrum,referenceZ=test_ref)
        noramlized.append(yieldValue)

        # Compute true yield from test spectrum position
        trueYield = i/((len(irAnalysis.Z)))  # Normalize to range 0-1
        error = abs(trueYield - yieldValue) * 100

        if error > 5:
            results.append(f"🚨 {i}: [Yield={yieldValue:.3f}, True={trueYield:.3f}, Index={bestMatchIndex}, Error={error:.2f}%]")
            reference_intensities = irAnalysis.Z[bestMatchIndex]

            plt.figure(figsize=(10, 5))
            plt.plot(rawWavenumbers, rawIntensities, label=f"Test Scan {i + 1}", color="blue", alpha=0.7)
            plt.plot(rawWavenumbers, reference_intensities, label=f"Matched Ref {bestMatchIndex + 1}", color="red", linestyle="dashed", alpha=0.7)

            # Plot difference spectrum
            plt.fill_between(rawWavenumbers, rawIntensities - reference_intensities, color="gray", alpha=0.3, label="Difference (Test - Ref)")

            plt.xlabel("Wavenumber (cm⁻¹)")
            plt.ylabel("Intensity")
            plt.title(f"Test Scan {i + 1} vs. Matched Reference {bestMatchIndex + 1}")
            plt.legend()
            plt.grid()
            plt.show()
            
            problemScans += 1
        else:
            results.append(f"✅ {i}: [Yield={yieldValue:.3f}, True={trueYield:.3f}, Index={bestMatchIndex}]")

    # Step 5: Print results
    print("\n📊 Yield Estimation Results:")
    for result in results:
        print(result)
        
    minMax=[min(noramlized),max(noramlized)]
    noramlized=np.array(noramlized)
    noramlized -= minMax[0]
    if minMax[1] > 0:
        noramlized /= minMax[1]
    print(noramlized)
    diff=[]
    for _i, _x in enumerate(noramlized):
        if _i == 0:
            diff.append(0)
            continue
        diff.append(noramlized[_i] - noramlized[_i - 1])

    print(diff)
    print(f"\n🚨 {problemScans}/{len(test_cases)} ({(problemScans / len(test_cases)) * 100:.1f}%) scans had >5% error.")

    print("Folder Labels (Scan Indices):", irAnalysis.folderLabels)
    print("Differences:", np.diff(irAnalysis.folderLabels))

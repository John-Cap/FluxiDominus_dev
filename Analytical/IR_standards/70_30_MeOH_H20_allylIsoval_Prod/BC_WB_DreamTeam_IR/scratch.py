
from scipy.interpolate import interp1d, griddata
from scipy.stats import pearsonr
from scipy.interpolate import CubicSpline
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

        return groupedRanges

    def filterDataInterpolate(self, groupedRanges, interpolationFactor=5):
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

        ax.plot_surface(self.X, self.Y, self.Z, cmap='viridis')

        ax.set_xlabel("Wavenumber (cm⁻¹)")
        ax.set_ylabel("Sample Index")
        ax.set_zlabel("Average Intensity")
        ax.set_title("Averaged IR Spectra Surface Plot (Filtered)")

        plt.show()

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

        # 🛠 **Process the raw spectrum first!**
        processedScan = self.processRawScan(rawWavenumbers, rawIntensities)
        print([rawWavenumbers.shape,processedScan[0].shape,processedScan[1].shape])
        plt.figure(figsize=(10, 5))
        plt.plot( processedScan[0], processedScan[1], label="Processed Scan", color="blue", alpha=0.7)
        plt.xlabel("Wavenumber (cm⁻¹)")
        plt.ylabel("Processed Intensity")
        plt.title("Processed IR Scan after Filtering & Triangle Transformation")
        plt.legend()
        plt.grid(True)
        plt.show()
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
    irAnalysis.filterData(highChangeRanges)

    # 📌 Save **original standard dataset** before interpolating!
    standardZ = np.copy(irAnalysis.Z)
    standardY = np.copy(irAnalysis.Y)

    # Step 2: Convert original raw spectra to test cases
    test_cases = [standardZ[5]]#[[-0.000765229, -0.000631024, -0.000406328, -0.000277366, -0.000342414, -0.000489882, -0.0005686, -0.000582964, -0.00061246, -0.000638055, -0.00057614, -0.0004305, -0.00029901, -0.000258768, -0.00031067, -0.000416124, -0.000515383, -0.000542117, -0.000485989, -0.000396112, -0.000289828, -0.000133674, 3.36E-05, 4.40E-05, -0.000259888, -0.000760621, -0.001099375, -0.001106067, -0.000884317, -0.000636504, -0.000531978, -0.000592617, -0.000690222, -0.000674666, -0.000548081, -0.000449749, -0.000463356, -0.000538476, -0.000595354, -0.000618405, -0.000576119, -0.000407845, -0.000181444, -5.18E-05, -3.07E-05, -1.69E-05, -1.17E-05, -0.000137088, -0.000369093, -0.000464341, -0.000222747, 0.000148517, 0.000315876, 0.000238742, 6.77E-05, -4.03E-05, -8.05E-06, 0.000148716, 0.00029419, 0.000246443, 6.02E-06, -0.000236519, -0.00035202, -0.000419864, -0.000483495, -0.000326818, 0.000130971, 0.000509745, 0.000410396, -4.37E-05, -0.000466399, -0.00066984, -0.000655477, -0.000411183, -1.42E-05, 0.00023652, 9.97E-05, -0.000287386, -0.000485403, -0.000309119, -3.09E-05, 0.000113616, 0.000202762, 0.0004175, 0.000757314, 0.001158675, 0.001641152, 0.00223794, 0.002883542, 0.003461851, 0.003945666, 0.00439703, 0.004954653, 0.005663103, 0.006212899, 0.00626543, 0.006092253, 0.00637071, 0.007284866, 0.008255455, 0.008918512, 0.009557203, 0.010334727, 0.010812653, 0.010705959, 0.010435674, 0.010377402, 0.010389207, 0.010334319, 0.010534884, 0.011069602, 0.011275482, 0.010732656, 0.009940812, 0.009597541, 0.009511394, 0.009022837, 0.008250404, 0.007961755, 0.008352806, 0.008780908, 0.008763011, 0.008241591, 0.007223753, 0.005887974, 0.004740038, 0.004092699, 0.003540384, 0.002798095, 0.0024831, 0.00301856, 0.003357329, 0.002271915, 0.000304331, -0.00108586, -0.001682382, -0.002475777, -0.003372734, -0.003348316, -0.003052974, -0.004435659, -0.007234667, -0.008984206, -0.008645102, -0.008184391, -0.009248378, -0.010688728, -0.011103205, -0.01139949, -0.012485765, -0.013350674, -0.013558896, -0.015144294, -0.019288627, -0.023402885, -0.024334946, -0.023206017, -0.022764291, -0.02301981, -0.022648554, -0.022424556, -0.023885726, -0.026395289, -0.027903268, -0.028107226, -0.027893875, -0.027188063, -0.025789789, -0.02455091, -0.024090603, -0.023678632, -0.022751256, -0.022476174, -0.023985013, -0.026425115, -0.027933927, -0.028114072, -0.027880875, -0.027611321, -0.02729048, -0.027294661, -0.027817849, -0.02841607, -0.028736488, -0.029274031, -0.030574086, -0.032299481, -0.03381632, -0.034809875, -0.034823709, -0.033581275, -0.032182561, -0.032244552, -0.033570034, -0.034290555, -0.033519431, -0.032408781, -0.03197816, -0.031927432, -0.031924799, -0.032382814, -0.033345835, -0.033997679, -0.033809663, -0.033189947, -0.032459899, -0.031368014, -0.029884236, -0.028337654, -0.026716343, -0.024827726, -0.023087177, -0.022161173, -0.021880318, -0.021402937, -0.020469128, -0.019670634, -0.019396425, -0.019314806, -0.018929676, -0.018144115, -0.017087166, -0.015904249, -0.014818756, -0.013932576, -0.01306264, -0.01211445, -0.011399667, -0.011164871, -0.011089136, -0.01071585, -0.010176515, -0.010001684, -0.010273554, -0.010498146, -0.010329561, -0.009985663, -0.009822629, -0.00990282, -0.01010724, -0.01033618, -0.010462685, -0.010342107, -0.010029654, -0.009836286, -0.010122315, -0.01121468, -0.013413492, -0.016747734, -0.020674188, -0.024299394, -0.02728324, -0.030309015, -0.034017192, -0.037798254, -0.040269278, -0.040868247, -0.040097049, -0.038486974, -0.036420992, -0.034301185, -0.032181471, -0.029763604, -0.02718753, -0.025199605, -0.0241039, -0.023387623, -0.022533409, -0.021572307, -0.020753053, -0.020184248, -0.01989953, -0.019834907, -0.019713249, -0.019326601, -0.018922261, -0.018932469, -0.01931652, -0.019509935, -0.019067066, -0.018040743, -0.016649747, -0.015007816, -0.013297586, -0.011813316, -0.010697521, -0.00995108, -0.009781878, -0.010594643, -0.012388575, -0.01428798, -0.01502823, -0.014216735, -0.012624732, -0.011120577, -0.010059847, -0.009477065, -0.009253143, -0.009128409, -0.008803258, -0.008113796, -0.007100523, -0.005952371, -0.004901627, -0.004077882, -0.003424098, -0.002779349, -0.002035542, -0.001201994, -0.000358252, 0.000402285, 0.001010972, 0.001464126, 0.001808096, 0.002069624, 0.002243789, 0.002346456, 0.002409421, 0.00240969, 0.00228869, 0.00207961, 0.001924185, 0.001905309, 0.001939785, 0.001905981, 0.001802943, 0.001698061, 0.001593371, 0.001448762, 0.00128388, 0.001145927, 0.001012813, 0.000840254, 0.000675062, 0.000606493, 0.000617721, 0.000590352, 0.000470681, 0.000347303, 0.000321215, 0.000362678, 0.000364998, 0.000274475, 0.00010607, -0.00010143, -0.000293096, -0.000418844, -0.000473215, -0.000447261, -0.000320808, -0.000266432, -0.000694072, -0.001750844, -0.002926957, -0.003557119, -0.003705556, -0.004131185, -0.005302176, -0.006971984, -0.008724079, -0.010317886, -0.011371585, -0.011436067, -0.010783744, -0.010375166, -0.01061213, -0.010873223, -0.010549274, -0.009924091, -0.00950384, -0.009202782, -0.008721168, -0.008098983, -0.007419105, -0.006545945, -0.005605285, -0.005109021, -0.005147265, -0.005044318, -0.004276692, -0.003313541, -0.002987026, -0.003406477, -0.0038381, -0.003666097, -0.003042861, -0.00249927, -0.002309219, -0.002263589, -0.002055057, -0.001718562, -0.001466631, -0.001240539, -0.000811027, -0.000278257, -6.98E-05, -0.000282491, -0.000478769, -0.000307596, -1.79E-05, -3.84E-05, -0.000342796, -0.000572788, -0.000531342, -0.000296695, 5.87E-05, 0.00058362, 0.001303458, 0.002101074, 0.002734916, 0.002927127, 0.002630122, 0.002142559, 0.001756779, 0.001539189, 0.001425498, 0.001386422, 0.001414331, 0.001361813, 0.001008443, 0.000385518, -7.68E-05, -5.32E-05, 8.90E-05, -0.00015962, -0.000622354, -0.000803417, -0.000823193, -0.001360014, -0.0026763, -0.004356682, -0.006146134, -0.008261874, -0.010412786, -0.011994082, -0.013204674, -0.013888301, -0.012187693, -0.006930014, -0.001961435, -0.001723918, -0.004559292, -0.005627259, -0.003404158, -0.000941296, 0.000703993, 0.002596896, 0.004912884, 0.006038696, 0.007164761, 0.009617097, 0.006025511, -0.006489116, -0.021753201, -0.029130449, -0.024650635, -0.020300617, -0.019686353, -0.013838476, -0.003438628, 0.001396028, -0.001692989, -0.002185887, 0.004803681, 0.007657933, 0.007175354, 0.009810322, 0.011656834, 0.008383878, 0.00346841, 0.001436093, 0.002479187, 0.003515412, 0.003227641, 0.002791609, 0.003208684, 0.003856567, 0.005359106, 0.00852022, 0.010813509, 0.009268221, 0.004998765, 0.001675442, 0.000528214, -0.001821219, -0.005015032, -0.00370943, 0.002756203, 0.0072801, 0.007904009, 0.009146565, 0.011040271, 0.004849528, -0.008306671, -0.016219399, -0.009999109, -0.003387095, -0.001113189, 0.002737517, 0.006656492, 0.005830251, 0.004282886, 0.008359657, 0.014840538, 0.0119423, 0.002406246, -0.005125449, -0.005646685, -0.008371156, -0.013494896, -0.010861491, -0.00254226, -0.00171215, -0.005740686, -0.006184342, -0.002915238, -0.00253164, -0.004029027, -0.002727906, 0.001204438, 0.003014075, 0.002114524, 0.001378148, 0.001976082, 0.002159593, 0.001363556, 0.000796325, 0.000941255, 0.000851989, 0.000388969, 0.000450646, 0.001013633, 0.001068463, 0.000603766, 0.000649334, 0.001260032, 0.00140277, 0.000878793, 0.000467221, 0.00053865, 0.000553198, 0.000376541, 0.000456285, 0.000719855, 0.000586044, 0.000195717, 0.000230129, 0.000642705, 0.000746152, 0.000336922, -0.00014651, -0.000418799, -0.000725471, -0.001153308, -0.001375363, -0.001392708, -0.001761346, -0.002770692, -0.003929475, -0.004785584, -0.005637383, -0.006753282, -0.007750413, -0.008244787, -0.008571703, -0.008857553, -0.008406406, -0.007135516, -0.006198132, -0.0059174, -0.005242872, -0.003412159, -0.001195567, 0.001306284, 0.006502841, 0.016995318, 0.031115956, 0.045673943, 0.061209469, 0.07745357, 0.088956427, 0.090444179, 0.082081626, 0.067760916, 0.053141146, 0.04179033, 0.033499169, 0.027070595, 0.022581147, 0.020148616, 0.018822819, 0.017739334, 0.016818716, 0.016606018, 0.017857816, 0.021438469, 0.028039896, 0.03763891, 0.049338828, 0.061599101, 0.072879807, 0.081983216, 0.087197188, 0.086096255, 0.077104762, 0.060680858, 0.040673203, 0.023986906, 0.014281135, 0.009345263, 0.006086827, 0.00409169, 0.003738182, 0.003983847, 0.00436712, 0.006042765, 0.009438332, 0.013426111, 0.019325722, 0.031537903, 0.051453886, 0.071081768, 0.079129135, 0.069082986, 0.046601542, 0.026190204, 0.013498161, 0.00575322, 0.00078464, -0.001383106, -0.001193624, 0.000598935, 0.004101606, 0.008758956, 0.012344789, 0.013533766, 0.014904489, 0.021872906, 0.034263474, 0.045588054, 0.048748018, 0.041595984, 0.02989615, 0.019646196, 0.011979139, 0.00634001, 0.003004702, 0.001903068, 0.001778569, 0.001236027, -0.000412103, -0.00318446, -0.00657677, -0.009710658, -0.011884822, -0.012729099, -0.012003747, -0.009870694, -0.007031843, -0.004121575, -0.001217503, 0.001990641, 0.005684149, 0.009554151, 0.012744289, 0.014264544, 0.013947188, 0.012770946, 0.011965259, 0.0120541, 0.012679093, 0.013383452, 0.014676406, 0.017893361, 0.023896465, 0.03269393, 0.044784939, 0.062377968, 0.088151937, 0.121869424, 0.157936593, 0.1871057, 0.201223664, 0.19566342, 0.170573156, 0.133686003, 0.097507, 0.071500139, 0.058514608, 0.055468189, 0.055813934, 0.053607816, 0.047258726, 0.039655896, 0.034079567, 0.030742328, 0.027635002, 0.023505117, 0.019070675, 0.015681647, 0.013968219, 0.013692535, 0.013984785, 0.013815563, 0.013179819, 0.013983712, 0.018612383, 0.026890745, 0.034869448, 0.037533106, 0.033393062, 0.026005902, 0.021710072, 0.026348713, 0.041788549, 0.06315657, 0.079449804, 0.080886258, 0.068207191, 0.050668363, 0.035765116, 0.024787167, 0.016350133, 0.010302647, 0.006906751, 0.005043825, 0.003328301, 0.001646975, 0.000461624, -0.000376424, -0.001254534, -0.001979638, -0.002172097, -0.002028124, -0.001999184, -0.002107578, -0.002253232, -0.002842482, -0.004480407, -0.007224545, -0.010580455, -0.014288445, -0.019193842, -0.026402797, -0.03240176, -0.030413093, -0.029143549, -0.027819434, -0.016232993, -0.002670157, 0.006960306, 0.013020929, 0.01627095, 0.016860487, 0.015114899, 0.011788083, 0.007765974, 0.003947186, 0.001238429, 0.000232485, 0.00084135, 0.002599936, 0.005531613, 0.010171181, 0.016230183, 0.02185476, 0.025065795, 0.025404722, 0.023508176, 0.02006638, 0.015866373, 0.01197519, 0.009058557, 0.006827291, 0.004839406, 0.003556622, 0.003718617, 0.004943922, 0.006108592, 0.00699847, 0.008226477, 0.009640362, 0.010183873, 0.009346206, 0.00738631, 0.004519946, 0.001232791, -0.001118752, -0.001562845, -0.001312777, -0.002325813, -0.003731777, -0.00251308, 0.002001936, 0.007439321, 0.012780138, 0.017644018, 0.018644676, 0.014590967, 0.010672458, 0.012071293, 0.015425284, 0.014533294, 0.012858265, 0.013752969, 0.010388139, -0.002661241, -0.016537054, -0.015228051, 0.00163469, 0.008242254, -0.000690595, -0.012243444, -0.019147651, -0.024148504, -0.030326522, -0.025590527, -0.021086869, -0.01865256, -0.002037424, 0.030943944, 0.029378488, 0.038843221, 0.031237379, 0.06208283, 0.093284753, 0.089312685, 0.058580572, 0.031936195, 0.002436384, 0.000891063, 0.019247309, 0.025669845, 0.017029781, 0.000380139, -0.022304266, -0.055422328, -0.059591914, -0.020058919]]  # Convert to simple list format
    #test_cases[0]=test_cases[0][::-1]
    print(f"✅ Created {len(test_cases)} test cases from original raw spectra.")

    # Step 3: Iterate through raw spectra, process, and analyze
    problemScans = 0
    results = []
    rawWavenumbers = irAnalysis.allWavenumbers  # Assume original wavenumbers match common grid

    for i, testSpectrum in enumerate(test_cases):
        rawIntensities = np.array(testSpectrum)  # Convert back to array
        print(f"Raw Wavenumbers Shape: {rawWavenumbers.shape}, Raw Intensities Shape: {rawIntensities.shape}")

        # plt.plot(rawWavenumbers, rawIntensities, label="Raw Scan 1")
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
        bestMatchIndex, bestScore, yieldValue = irAnalysis.analyzeNewScan(rawWavenumbers, jitteredTestSpectrum, referenceZ=standardZ)

        # Compute true yield from test spectrum position
        trueYield = 0.5  # Normalize to range 0-1
        error = abs(trueYield - yieldValue) * 100

        if error > 5:
            results.append(f"🚨 {i}: [Yield={yieldValue:.3f}, True={trueYield:.3f}, Index={bestMatchIndex}, Error={error:.2f}%]")
            problemScans += 1
        else:
            results.append(f"✅ {i}: [Yield={yieldValue:.3f}, True={trueYield:.3f}, Index={bestMatchIndex}]")

    # Step 5: Print results
    print("\n📊 Yield Estimation Results:")
    for result in results:
        print(result)

    print(f"\n🚨 {problemScans}/{len(test_cases)} ({(problemScans / len(test_cases)) * 100:.1f}%) scans had >5% error.")

    # Step 6: Visualize the result
    irAnalysis.plotSurface()

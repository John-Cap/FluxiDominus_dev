
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
        # print([rawWavenumbers.shape,processedScan[0].shape,processedScan[1].shape])
        # plt.figure(figsize=(10, 5))
        # plt.plot( processedScan[0], processedScan[1], label="Processed Scan", color="blue", alpha=0.7)
        # plt.xlabel("Wavenumber (cm⁻¹)")
        # plt.ylabel("Processed Intensity")
        # plt.title("Processed IR Scan after Filtering & Triangle Transformation")
        # plt.legend()
        # plt.grid(True)
        # plt.show()
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
    irAnalysis.filterDataInterpolate(highChangeRanges)

    # Step 2: Convert original raw spectra to test cases
    test_cases = irAnalysis.Z#[[-0.000900477, -0.000951372, -0.000921264, -0.000834431, -0.000767489, -0.000743001, -0.000712284, -0.00065138, -0.000591286, -0.000551343, -0.000516933, -0.000489566, -0.000490627, -0.000500177, -0.000454129, -0.000329481, -0.000182077, -8.65E-05, -6.53E-05, -9.21E-05, -0.000136952, -0.000189327, -0.000259969, -0.000364754, -0.000510269, -0.0006822, -0.000841393, -0.000927798, -0.000885882, -0.000761779, -0.00073366, -0.000900771, -0.00112294, -0.00117612, -0.001049897, -0.000910306, -0.000811223, -0.000705638, -0.00066263, -0.000773608, -0.000901175, -0.000779175, -0.00045025, -0.00028412, -0.000430685, -0.000674558, -0.000749538, -0.000700316, -0.000672476, -0.0006084, -0.000410912, -0.000207697, -0.000135973, -0.000115646, -3.11E-05, 8.99E-05, 0.000163495, 0.000185832, 0.000138461, -5.78E-05, -0.000340575, -0.000434677, -0.000134634, 0.000321109, 0.000488922, 0.000381772, 0.000242711, 5.49E-05, -0.000240805, -0.000383515, -5.22E-05, 0.000659394, 0.001233104, 0.001262547, 0.000903414, 0.000577338, 0.000477649, 0.000511397, 0.000450991, 0.000209949, 2.36E-05, 0.000206598, 0.000683297, 0.000908122, 0.000765444, 0.000707699, 0.001010375, 0.001462166, 0.00174297, 0.002099563, 0.002852937, 0.003790508, 0.004600553, 0.005423968, 0.006555762, 0.007691968, 0.008264464, 0.008357735, 0.008620434, 0.009265387, 0.009860439, 0.010102844, 0.010094088, 0.010027317, 0.010019018, 0.010236989, 0.010751122, 0.011213012, 0.0110401, 0.010272576, 0.009818943, 0.010213396, 0.010901745, 0.011000813, 0.010323429, 0.009569415, 0.009233175, 0.009037434, 0.008615492, 0.008195244, 0.008151032, 0.008189145, 0.007549604, 0.006134371, 0.004884492, 0.004551565, 0.004763154, 0.004639714, 0.004016529, 0.003248235, 0.002222659, 0.000488146, -0.001642261, -0.003027178, -0.003047725, -0.002652621, -0.003069654, -0.004123585, -0.004807292, -0.004788035, -0.004579467, -0.004262738, -0.00379669, -0.003928106, -0.005284154, -0.007241534, -0.008585759, -0.009108648, -0.009435051, -0.009449516, -0.009152491, -0.010046276, -0.013257132, -0.01737184, -0.019754768, -0.01994222, -0.019989229, -0.020951832, -0.022277231, -0.024013543, -0.026721892, -0.029218275, -0.029411224, -0.027715583, -0.026633593, -0.026594889, -0.02570548, -0.023563907, -0.022198317, -0.022499685, -0.022834004, -0.021991963, -0.021151772, -0.021363655, -0.021958645, -0.022075146, -0.022025279, -0.022272996, -0.02277232, -0.023963124, -0.02648914, -0.029656242, -0.031428695, -0.030596911, -0.027850722, -0.024231858, -0.020961104, -0.01997844, -0.022061738, -0.025234828, -0.026599082, -0.025894011, -0.025499864, -0.026736458, -0.028736561, -0.030538082, -0.03226132, -0.033649428, -0.033800193, -0.033160303, -0.0333741, -0.034590048, -0.035217581, -0.034519885, -0.033559071, -0.033108125, -0.03260464, -0.031419467, -0.029653817, -0.027407452, -0.024750649, -0.022399555, -0.021127051, -0.02070511, -0.020365221, -0.020019185, -0.019998678, -0.019955145, -0.019140245, -0.01769231, -0.016529863, -0.015925683, -0.015366978, -0.01458269, -0.013820286, -0.013157245, -0.012366294, -0.011517958, -0.010954434, -0.010627855, -0.010184414, -0.009665628, -0.00946687, -0.009594771, -0.009610771, -0.009368645, -0.00921601, -0.009354831, -0.009584224, -0.009764721, -0.009998471, -0.010224585, -0.010156417, -0.009821045, -0.009693984, -0.010146006, -0.011241723, -0.013141037, -0.016149149, -0.020067778, -0.023916399, -0.026960365, -0.029773294, -0.033288866, -0.037132805, -0.039844084, -0.040649491, -0.039918245, -0.038195384, -0.036065928, -0.034226325, -0.032737464, -0.030848301, -0.028269587, -0.025902413, -0.024492481, -0.02366063, -0.022815361, -0.022018356, -0.021488601, -0.021020223, -0.020428919, -0.019977967, -0.019859234, -0.019827986, -0.019688719, -0.019628681, -0.019751304, -0.019682876, -0.018991235, -0.017730072, -0.016216534, -0.014598776, -0.012954046, -0.01151705, -0.010540516, -0.010129418, -0.010382297, -0.011484813, -0.013355794, -0.015190002, -0.015778467, -0.014748902, -0.012972708, -0.011438775, -0.010469313, -0.009913681, -0.00950885, -0.009065795, -0.008551909, -0.008028744, -0.007480004, -0.006780893, -0.005865357, -0.004812602, -0.003726558, -0.002648438, -0.001626146, -0.000742709, -1.41E-05, 0.000640618, 0.001261623, 0.001764933, 0.002062307, 0.002196977, 0.00228873, 0.002380678, 0.002421846, 0.002385844, 0.002320196, 0.00226276, 0.002177134, 0.002015348, 0.001812963, 0.001672024, 0.001641751, 0.001644429, 0.001551339, 0.001334891, 0.001103999, 0.000969979, 0.000919802, 0.000867134, 0.000792719, 0.000757277, 0.000782142, 0.000789327, 0.000684936, 0.000464977, 0.000213601, 1.88E-05, -7.36E-05, -4.71E-05, 8.07E-05, 0.000238281, 0.000313731, 0.000178116, -0.000259642, -0.000925604, -0.001536512, -0.001806684, -0.001762843, -0.001750174, -0.002073485, -0.002779181, -0.00375818, -0.004880722, -0.006020381, -0.00710345, -0.008232638, -0.009532076, -0.010779614, -0.011493173, -0.011537021, -0.011316765, -0.011164652, -0.010947896, -0.010421778, -0.009644907, -0.008858073, -0.008220503, -0.007778171, -0.00745609, -0.007036274, -0.006348665, -0.005544022, -0.004930071, -0.00461199, -0.004517179, -0.004573898, -0.004611625, -0.004323142, -0.003627237, -0.002915465, -0.002566399, -0.002452058, -0.002283899, -0.00212355, -0.00215871, -0.002191644, -0.001893881, -0.001444043, -0.001306807, -0.001534617, -0.001818823, -0.001999288, -0.002079774, -0.001866773, -0.001157227, -0.000271915, 0.000208518, 0.000185733, 3.48E-05, 7.44E-05, 0.000366441, 0.000935907, 0.001797082, 0.002708048, 0.00324729, 0.003251487, 0.002893529, 0.002368938, 0.001782513, 0.001267785, 0.000987527, 0.000977058, 0.001043498, 0.000980159, 0.000792542, 0.000589731, 0.000438909, 0.000350083, 0.000249587, -3.76E-05, -0.00059333, -0.001211639, -0.001561008, -0.001576702, -0.001557647, -0.001812715, -0.002575081, -0.004250218, -0.006908091, -0.009677672, -0.011191864, -0.011071816, -0.010180401, -0.008269244, -0.004189305, 0.000427178, 0.002125723, 0.000566682, -0.001359962, -0.001224303, -0.000718999, -0.004001596, -0.012095248, -0.018983575, -0.021457213, -0.02082295, -0.01811259, -0.016025169, -0.013662941, -0.007814854, -0.000356691, 0.001732856, -0.00024643, -0.005925682, -0.01358824, -0.012922017, -0.009136892, -0.004597095, 0.006849369, 0.018263473, 0.01501746, 0.00596533, 0.004017437, 0.007522008, 0.008686569, 0.007497413, 0.00601557, 0.00480474, 0.003554736, 0.002874226, 0.003879281, 0.005393747, 0.005460799, 0.004956618, 0.005290134, 0.00596739, 0.006080141, 0.006688996, 0.009103738, 0.010973489, 0.009566954, 0.007479011, 0.008967759, 0.013265214, 0.013936436, 0.009367627, 0.00330106, 0.00095621, -0.005878084, -0.015858065, -0.009825515, 0.007359288, 0.013432772, 0.007861753, 0.001238808, 0.005792076, 0.01287916, 0.020913713, 0.028859661, 0.024119505, 0.009647157, -0.005870251, -0.012664315, -0.002772261, 0.006437074, 0.010718597, 0.013553515, 0.011435051, 0.006675514, 0.000890898, -0.003454572, -0.003874167, -0.002296042, -0.000110866, 0.002643322, 0.003885023, 0.002628021, 0.001231312, 0.00198583, 0.003453213, 0.003151369, 0.001802529, 0.001543787, 0.002305179, 0.002143076, 0.000923173, 0.000192185, 0.000468946, 0.000702902, 0.000560471, 0.000810109, 0.00143169, 0.001463748, 0.000740313, 8.08E-05, -1.71E-05, -3.44E-05, -0.00019475, -0.000121518, 0.000183152, 0.000226427, 6.55E-05, 0.000209249, 0.000585855, 0.000646877, 0.000272305, -0.000162435, -0.000456774, -0.000821455, -0.001277968, -0.00154249, -0.001676988, -0.002150453, -0.003068732, -0.003932169, -0.00455231, -0.005426457, -0.00676686, -0.007993312, -0.008567148, -0.008861621, -0.00911294, -0.008637636, -0.007295167, -0.006234977, -0.005835836, -0.00510899, -0.003323053, -0.001203057, 0.001212003, 0.006337973, 0.016763588, 0.030847202, 0.045456635, 0.061180347, 0.077730253, 0.089485127, 0.090957855, 0.082328341, 0.067741408, 0.053081634, 0.04188955, 0.033733199, 0.027180387, 0.022384262, 0.019817007, 0.018640619, 0.017786987, 0.01690969, 0.016534569, 0.017646004, 0.021282261, 0.028056108, 0.037742705, 0.049396683, 0.061585627, 0.072847604, 0.081959451, 0.087180141, 0.086114121, 0.077176167, 0.060729674, 0.040587814, 0.023793889, 0.014147591, 0.009390616, 0.006245315, 0.004194546, 0.003765511, 0.004050203, 0.004539936, 0.006262215, 0.009592006, 0.013471844, 0.019263382, 0.031383079, 0.051286394, 0.071012663, 0.079179597, 0.069176706, 0.046679673, 0.02626023, 0.013568405, 0.005817136, 0.000863988, -0.00124974, -0.001024481, 0.000718652, 0.004117782, 0.008739347, 0.01238381, 0.013651857, 0.015098164, 0.022174977, 0.034677807, 0.046044351, 0.04916683, 0.041966722, 0.03023915, 0.019921474, 0.012107985, 0.006316904, 0.00293266, 0.001889029, 0.001859538, 0.001386281, -0.000260242, -0.003100422, -0.006565646, -0.009719322, -0.011885256, -0.012727784, -0.01197283, -0.009748823, -0.006827595, -0.003935102, -0.001104414, 0.002118199, 0.005946676, 0.0099459, 0.013139129, 0.014555875, 0.014129485, 0.012868716, 0.011971695, 0.011977449, 0.012584289, 0.013341743, 0.014697673, 0.017941129, 0.023946451, 0.032752005, 0.044874762, 0.062541685, 0.088453649, 0.122369357, 0.158643085, 0.187948297, 0.202076828, 0.196404169, 0.171147871, 0.134134602, 0.097896334, 0.071852576, 0.058818744, 0.055735028, 0.056086443, 0.053900089, 0.047519477, 0.039829214, 0.034175104, 0.030815841, 0.027722291, 0.023597473, 0.019148161, 0.015748288, 0.014056131, 0.013845908, 0.01423377, 0.014150225, 0.013547877, 0.014325898, 0.018902448, 0.027139034, 0.035101017, 0.037769807, 0.033642878, 0.026256955, 0.021941211, 0.026556452, 0.042004018, 0.063437696, 0.079857092, 0.081444841, 0.068870428, 0.051319132, 0.036276818, 0.025126004, 0.016611036, 0.01061098, 0.00731124, 0.00551697, 0.003821236, 0.002107846, 0.000830158, -0.000151457, -0.001196121, -0.002089268, -0.00242792, -0.002363693, -0.002323392, -0.002376397, -0.002497124, -0.003091398, -0.004674333, -0.007224787, -0.010271667, -0.013673688, -0.018374629, -0.02547658, -0.031921748, -0.032062899, -0.032639511, -0.030022532, -0.016625562, -0.002676276, 0.006820208, 0.012881097, 0.016315828, 0.017090695, 0.015393717, 0.012025092, 0.008027151, 0.004374804, 0.00186443, 0.000914488, 0.001430101, 0.003147266, 0.006235097, 0.011075072, 0.017089963, 0.022409989, 0.025384466, 0.025777038, 0.024018793, 0.020451644, 0.015854233, 0.011631542, 0.008755252, 0.006969837, 0.005635604, 0.004899248, 0.005170413, 0.005974782, 0.00652423, 0.0070707, 0.008320634, 0.009870734, 0.010622362, 0.010334533, 0.009264291, 0.007044256, 0.003656871, 0.000609182, -0.000739713, -0.001453347, -0.003187331, -0.004471065, -0.002075087, 0.003812329, 0.00981789, 0.0150969, 0.020061909, 0.02077339, 0.014503629, 0.00782037, 0.009303739, 0.015615105, 0.015204307, 0.007919722, 0.001755926, -0.001206942, -0.00591747, -0.01149228, -0.007667755, 0.005019566, 0.00749325, -0.001621395, -0.008250724, -0.009478637, -0.024824133, -0.045036565, -0.03272844, 0.012745027, 0.022120615, -0.000788573, -0.000529745, -0.00508596, -0.033132922, -0.055090009, -0.029720735, -0.036899926, -0.013508268, -0.020739706, -0.027332081, -0.000537603, 0.010550929, 0.01435759, 0.005577916, -0.015627662, -0.021109093, -0.005525047, -0.014070425, -0.040633743, -0.004508937]]
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
        bestMatchIndex, bestScore, yieldValue = irAnalysis.analyzeNewScan(rawWavenumbers, jitteredTestSpectrum)

        # Compute true yield from test spectrum position
        trueYield = i/(len(irAnalysis.Z))  # Normalize to range 0-1
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

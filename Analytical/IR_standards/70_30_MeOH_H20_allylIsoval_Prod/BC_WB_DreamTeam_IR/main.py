
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
        
    def analyzeNewScan(self, newScanIntensities, referenceZ=None):
        """
        Processes a new IR scan (given as an array) and compares it against standard spectra.

        Parameters:
        - newScanIntensities (np.array): 1D array of intensity values, aligned to self.allWavenumbers.
        - referenceZ (np.array): Optional. If provided, uses this as the reference dataset.

        Returns:
        - bestMatchIndex (int): The best-matching index along the standard dataset.
        - bestScore (float): The similarity score (correlation).
        - yieldValue (float): Estimated yield, scaled between 0 (first reference scan) and 1 (last reference scan).
        """
        if len(newScanIntensities) != len(self.allWavenumbers):
            raise ValueError(f"New scan length ({len(newScanIntensities)}) must match reference length ({len(self.allWavenumbers)}).")

        # Normalize new scan (0-1 range)
        newScanIntensities = np.array(newScanIntensities)
        newScanIntensities -= newScanIntensities.min()
        if newScanIntensities.max() > 0:
            newScanIntensities /= newScanIntensities.max()

        # Use provided reference dataset or default to self.Z
        if referenceZ is None:
            referenceZ = self.Z  # Default to the full dataset

        # Compare to existing standard scans
        bestMatchIndex = None
        bestScore = float("-inf")  # Higher score = better match

        for i in range(referenceZ.shape[0]):
            refScan = referenceZ[i, :]

            # Compute similarity using Pearson correlation
            corr, _ = pearsonr(newScanIntensities, refScan)

            if corr > bestScore:
                bestScore = corr
                bestMatchIndex = i

        # Calculate yield as a normalized value between 0 and 1
        numStandardScans = referenceZ.shape[0] - 1  # Total reference scans
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
    irAnalysis.loadData()
    irAnalysis.trimData()
    highChangeRanges = irAnalysis.detectHighChangeRegions()
    irAnalysis.filterData(highChangeRanges)

    # 📌 Save **original standard dataset** before interpolating!
    standardZ = np.copy(irAnalysis.Z)
    standardY = np.copy(irAnalysis.Y)

    # Step 2: Interpolate a few test spectra
    numInterpolatedSpectra = 3  # Number of test spectra to generate
    interpolatedZ, interpolatedY = irAnalysis.generateInterpolatedSpectraSpline(numInterpolated=numInterpolatedSpectra, method='cubic')

    # Convert one interpolated spectrum to a simple array [intensities...]
    testSpectraIndex = 45  # Choose an interpolated spectrum to test
    cnt=len(interpolatedZ)
    i=0
    vals=[]
    problemAreas=[]
    problemScans=0
    while i < cnt:
        testSpectraIndex=i
        testSpectrum = interpolatedZ[testSpectraIndex, :]  # Extract the spectrum

        # 🛠 Apply jitter (±5% random variation)
        jitterFactor = 0.05  # Max 5% variation
        noise = (np.random.rand(*testSpectrum.shape) - 0.5) * 2 * jitterFactor  # Random values from -5% to +5%
        jitteredTestSpectrum = np.clip(testSpectrum + testSpectrum * noise, 0, 1)  # Ensure values stay in 0-1 range

        print("\n🔬 Testing interpolated spectrum (converted to simple array) with jitter:")
        print(jitteredTestSpectrum)

        # Step 3: Compare test spectrum **against original standard scans only**
        bestMatchIndex, bestScore, yieldValue = irAnalysis.analyzeNewScan(jitteredTestSpectrum, referenceZ=standardZ)
        
        # Compute true yield from interpolation position
        trueYield = testSpectraIndex / (len(interpolatedY) - 1)
        error = abs(trueYield - yieldValue)*100
        if error > 5:
            vals.append(f"{i}:{[yieldValue,trueYield,bestMatchIndex,error]}")
            problemScans+=1
        else:
            vals.append(f"{i}:{[yieldValue,trueYield,bestMatchIndex]}")
        i+=1
    for _x in vals:
        print(_x)
    print(f"{(problemScans/cnt)*100} of scans are problematic")
    exit()
    print(f"\n🎯 Best matching standard scan index: {bestMatchIndex}")
    print(f"📊 Similarity score: {bestScore:.3f}")
    print(f"🌱 Estimated Yield: {yieldValue:.2%}")
    print(f"✅ True Yield of Test Spectrum: {trueYield:.2%}")

    # Optional: Compute absolute error
    print(f"📏 Yield Estimation Error: {error:.3%}")

    # Step 5: Visualize the result
    irAnalysis.plotSurface()

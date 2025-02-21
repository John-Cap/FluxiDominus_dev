import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Set the main directory containing the subfolders
main_dir = r"isovanillin+allylbromide+product"  # UPDATE THIS

# Define a small-value threshold
SMALL_VALUE_THRESHOLD = 0.005  # Snap values below this to 0

# Get the list of subdirectories (each representing a sample)
folders = [f for f in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, f))]

# Sort folders numerically
def natural_sort_key(folder_name):
    """Extracts numbers from folder names for correct numerical sorting."""
    numbers = re.findall(r'\d+', folder_name)  # Extract numbers from folder name
    return int(numbers[0]) if numbers else float('inf')  # Convert to integer

folders = sorted(folders, key=natural_sort_key)  # Sort numerically

# Initialize lists to store data
all_wavenumbers = None  # Common wavenumbers
all_averages = []  # Averaged intensity per folder
folder_labels = []  # Sample index

for folder_index, folder in enumerate(folders):
    folder_path = os.path.join(main_dir, folder)
    files = [f for f in os.listdir(folder_path) if f.lower().endswith((".csv", ".xlsx", ".xls"))]  # Handle uppercase extensions

    intensity_list = []  # Store intensity values for averaging

    if not files:
        print(f"⚠ Warning: No valid data files found in {folder}")
        continue  # Skip if no files are found

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        print(f"📂 Reading file: {file_path}")

        # Read Excel or CSV appropriately
        if file_name.lower().endswith(".csv"):
            df = pd.read_csv(file_path, header=0)  # CSV files have headers
        elif file_name.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path, header=0)  # Read Excel files

        if df.shape[1] < 2:
            print(f"⚠ Warning: {file_name} does not have enough columns")
            continue  # Skip if structure is wrong

        # Extract columns (A1 = Wavenumber, B1 = Intensity)
        wavenumbers = pd.to_numeric(df.iloc[:, 0].values, errors="coerce")
        intensities = pd.to_numeric(df.iloc[:, 1].values, errors="coerce")

        # Remove NaN values
        mask = ~np.isnan(intensities)
        wavenumbers = wavenumbers[mask]
        intensities = intensities[mask]

        # Snap small values to 0
        intensities[np.abs(intensities) < SMALL_VALUE_THRESHOLD] = 0

        if len(intensities) == 0:
            print(f"⚠ Warning: All intensities in {file_name} are NaN or invalid")
            continue  # Skip invalid data

        if all_wavenumbers is None:
            all_wavenumbers = wavenumbers  # Set wavenumber reference

        intensity_list.append(intensities)

    # Convert to NumPy array and compute the average intensity
    intensity_array = np.array(intensity_list)

    if intensity_array.shape[0] == 0:
        print(f"❌ Skipping {folder} because no valid data was found.")
        continue

    avg_intensity = np.nanmean(intensity_array, axis=0)  # Use nanmean to ignore NaNs

    # Store data for plotting
    all_averages.append(avg_intensity)
    folder_labels.append(folder_index)

# Convert lists to NumPy arrays
all_averages = np.array(all_averages)
folder_labels = np.array(folder_labels)

# Ensure 2D meshgrid
X, Y = np.meshgrid(all_wavenumbers, folder_labels)
Z = np.array(all_averages)
Z = np.nan_to_num(Z)  # Replace NaNs with zero

# Define number of points to remove from each side
trim_left = 10  # Snip 'x' points from the left
trim_right = 200  # Snip 'y' points from the right

# Ensure we do not over-trim
if trim_left + trim_right < X.shape[1]:  
    X = X[:, trim_left:-trim_right]  # Trim wavenumber axis
    Z = Z[:, trim_left:-trim_right]  # Adjust intensity values accordingly
    Y = Y[:, trim_left:-trim_right]  # 🔹 Trim Y to match X & Z
    all_wavenumbers = all_wavenumbers[trim_left:-trim_right]  # Trim wavenumber reference
else:
    print("🚨 Warning: Trimming exceeds data length. Skipping trim operation.")

# Debug: Print new shapes
print(f"✅ Trimmed X shape: {X.shape}, Y shape: {Y.shape}, Z shape: {Z.shape}")


# Compute the first derivative along the wavenumber axis
Z_gradient = np.abs(np.gradient(Z, axis=1))  # Derivative along wavenumber axis

# Find the wavenumber regions with the highest changes
high_change_threshold = np.percentile(Z_gradient, 75)  # Get the top 25% of changes
high_change_indices = np.where(Z_gradient > high_change_threshold)

# Get the corresponding wavenumber values
high_change_wavenumbers = all_wavenumbers[high_change_indices[1]]

# Define a threshold distance between consecutive high-change wavenumbers
threshold_distance = 20  # Adjust based on your data resolution
minRangeWidth = 30  # Minimum width of a detected range

# Sort high-change wavenumbers
sorted_wavenumbers = np.sort(high_change_wavenumbers)

# Initialize variables
grouped_ranges = []
current_range = [sorted_wavenumbers[0]]

# Iterate through sorted wavenumbers
for i in range(1, len(sorted_wavenumbers)):
    if sorted_wavenumbers[i] - sorted_wavenumbers[i - 1] <= threshold_distance:
        current_range.append(sorted_wavenumbers[i])
    else:
        minCurrentRange = min(current_range)
        maxCurrentRange = max(current_range)
        if maxCurrentRange - minCurrentRange > minRangeWidth:
            grouped_ranges.append((minCurrentRange, maxCurrentRange))
        current_range = [sorted_wavenumbers[i]]

# Add the last range if valid
if current_range:
    grouped_ranges.append((min(current_range), max(current_range)))

# Print the identified high-change wavenumber ranges
print("Identified high-change wavenumber ranges:")
for i, (start, end) in enumerate(grouped_ranges, 1):
    print(f"Range {i}: {start} - {end} cm⁻¹")

# **Apply Mask to Zero Out Intensity Values Outside of High-Change Ranges**
mask = np.zeros_like(Z, dtype=bool)  # Initialize a mask (default: all zero)

for start, end in grouped_ranges:
    range_mask = (all_wavenumbers >= start) & (all_wavenumbers <= end)
    mask[:, range_mask] = True  # Mark valid wavenumber indices

# Set intensities outside the identified ranges to zero
Z_filtered = np.where(mask, Z, 0)

# Debug print
print(f"✅ Wavenumbers shape: {all_wavenumbers.shape}")
print(f"✅ Filtered Intensity shape: {Z_filtered.shape}")

# Update Z for plotting
Z = Z_filtered  # Use the filtered data

# Debug: Check final array shapes
print(f"✅ Final Shapes -> X: {X.shape}, Y: {Y.shape}, Z: {Z.shape}")

# Create the surface plot
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.set_proj_type('ortho')  # Switch to orthographic projection

ax.plot_surface(X, Y, Z, cmap='viridis')

# Labels
ax.set_xlabel("Wavenumber (cm⁻¹)")
ax.set_ylabel("Sample Index")
ax.set_zlabel("Average Intensity")
ax.set_title("Averaged IR Spectra Surface Plot (Filtered)")

plt.show()

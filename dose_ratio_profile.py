#!/usr/bin/env python3
"""
Horizontal profile of dose ratio to extract conversion factors
Ratio = dose_hetero / dose_homo for different materials
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

# ===== MODIFY THESE =====
file1 = "brachytherapy_Lung_Homo_200m.root"
file2 = "brachytherapy_Bone_Homo.root"
title = "Dose Ratio: Lung Homo / Bone Homo"
material1 = "lung"   # File 1 material
material2 = "bone"   # File 2 material
# =======================

# Material densities (g/cm³)
densities = {
    "water": 1.0,
    "bone": 1.92,
    "lung": 0.26
}

# Voxel parameters
voxel_size_x_mm = 1.0
voxel_size_y_mm = 1.0
voxel_size_z_mm = 10.0
voxel_volume_cm3 = (voxel_size_x_mm * voxel_size_y_mm * voxel_size_z_mm) / 1000.0

# Conversion factors
keV_to_J = 1.602e-13
density1 = densities[material1]
density2 = densities[material2]

conversion1 = keV_to_J / (voxel_volume_cm3 * density1 / 1000.0)
conversion2 = keV_to_J / (voxel_volume_cm3 * density2 / 1000.0)

print(f"File 1 Material: {material1} (ρ={density1} g/cm³)")
print(f"File 2 Material: {material2} (ρ={density2} g/cm³)")
print(f"Conversion file1: {conversion1:.6e} Gy/keV")
print(f"Conversion file2: {conversion2:.6e} Gy/keV")
print(f"Ratio (conv1/conv2): {conversion1/conversion2:.6f}\n")

# Open files
h1 = uproot.open(file1)["h20;1"]
h2 = uproot.open(file2)["h20;1"]

vals1_keV = h1.values()
vals2_keV = h2.values()

# Get axes
x_edges = h1.axis(0).edges()
y_edges = h1.axis(1).edges()
x_centers = (x_edges[:-1] + x_edges[1:]) / 2
y_centers = (y_edges[:-1] + y_edges[1:]) / 2

# Create regional mask
x_hetero_min, x_hetero_max = 10.0, 70.0
y_hetero_min, y_hetero_max = -30.0, 30.0

x_mesh, y_mesh = np.meshgrid(x_centers, y_centers, indexing='ij')
mask_hetero = ((x_mesh >= x_hetero_min) & (x_mesh <= x_hetero_max) &
               (y_mesh >= y_hetero_min) & (y_mesh <= y_hetero_max))
mask_water = ~mask_hetero

# Convert to Gy (simple, both homogeneous)
vals1_Gy = vals1_keV * conversion1
vals2_Gy = vals2_keV * conversion2

# Calculate horizontal profile (integrated over Y)
dose1_x = np.sum(vals1_Gy, axis=1)
dose2_x = np.sum(vals2_Gy, axis=1)

# Calculate ratio (avoid division by zero)
ratio = np.divide(dose1_x, dose2_x, 
                  out=np.ones_like(dose1_x),
                  where=dose2_x != 0)

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Plot 1: Doses
ax1.plot(x_centers, dose1_x, 'r-', linewidth=2, label='File 1 (Hetero)')
ax1.plot(x_centers, dose2_x, 'b-', linewidth=2, label='File 2 (Homo)')
ax1.axvline(x=x_hetero_min, color='yellow', linestyle='--', linewidth=2, alpha=0.7, label='Hetero region')
ax1.axvline(x=x_hetero_max, color=f'yellow', linestyle='--', linewidth=2, alpha=0.7)
ax1.set_ylabel('Integrated Dose (Gy)')
ax1.set_title(f'{title} - X Profile')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_yscale('log')

# Plot 2: Ratio
ax2.plot(x_centers, ratio, 'g-', linewidth=2, label='Ratio (File1/File2)')
ax2.axhline(y=1.0, color='k', linestyle='-', alpha=0.3)
ax2.axvline(x=x_hetero_min, color='yellow', linestyle='--', linewidth=2, alpha=0.7, label='Hetero region')
ax2.axvline(x=x_hetero_max, color='yellow', linestyle='--', linewidth=2, alpha=0.7)
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Dose Ratio')
ax2.set_title('Dose Ratio Profile')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Print statistics for different regions
print("=" * 70)
print("RATIO STATISTICS BY REGION")
print("=" * 70)

mask_water_profile = x_centers < x_hetero_min
mask_hetero_profile = (x_centers >= x_hetero_min) & (x_centers <= x_hetero_max)
mask_water_profile2 = x_centers > x_hetero_max

if np.sum(mask_water_profile) > 0:
    mean_ratio_water1 = np.mean(ratio[mask_water_profile])
    print(f"Water (X < {x_hetero_min}mm): Mean ratio = {mean_ratio_water1:.6f}")

if np.sum(mask_hetero_profile) > 0:
    mean_ratio_hetero = np.mean(ratio[mask_hetero_profile])
    print(f"{material1.upper()}/{material2.upper()} (X in [{x_hetero_min}, {x_hetero_max}]mm): Mean ratio = {mean_ratio_hetero:.6f}")

if np.sum(mask_water_profile2) > 0:
    mean_ratio_water2 = np.mean(ratio[mask_water_profile2])
    print(f"Water (X > {x_hetero_max}mm): Mean ratio = {mean_ratio_water2:.6f}")

print("\n" + "=" * 70)
print("INTERPRETATION:")
print("=" * 70)
print(f"If ratio ≈ 1.0: Both have similar dose (same material)")
print(f"If ratio > 1.0: File1 has MORE dose (lower density in hetero)")
print(f"If ratio < 1.0: File1 has LESS dose (higher density in hetero)")

# Add cursor display
def on_move(event):
    if event.inaxes == ax2:
        x = event.xdata
        if x is not None:
            ix = np.argmin(np.abs(x_centers - x))
            ax2.set_title(f'Dose Ratio Profile | X={x:.1f}mm → Ratio={ratio[ix]:.6f}')
            fig.canvas.draw_idle()

fig.canvas.mpl_connect('motion_notify_event', on_move)
plt.tight_layout()
plt.show()

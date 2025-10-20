#!/usr/bin/env python3
"""
Subtract two 2D histograms from ROOT files and convert to dose (Gy)
Divides by voxel mass based on material density
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm

# ===== MODIFY THESE =====
file1 = "brachytherapy_lung_hetero50m.root"
file2 = "brachytherapy_water_homo_50m.root"
title = "Dose: Lung Hetero - Water Homo"
hetero_material = "lung"  # "bone", "lung" - material DENTRO del heterogeneity
# =======================

# Material densities (g/cm³)
densities = {
    "water": 1.0,
    "bone": 1.92,
    "lung": 0.26
}

# Voxel parameters from macro
# /score/mesh/boxSize 150.0 150.0 5.0 mm  (half-dimensions)
# /score/mesh/nBin 300 300 1
voxel_size_x_mm = 300.0 / 300  # 1 mm
voxel_size_y_mm = 300.0 / 300  # 1 mm
voxel_size_z_mm = 10.0         # 2 * 5.0 mm

voxel_volume_mm3 = voxel_size_x_mm * voxel_size_y_mm * voxel_size_z_mm
voxel_volume_cm3 = voxel_volume_mm3 / 1000.0

# Densities for regional conversion
density_water = densities["water"]
density_hetero = densities[hetero_material]

# Conversion factors: keV -> Gy
keV_to_J = 1.602e-13
conversion_water = keV_to_J / (voxel_volume_cm3 * density_water / 1000.0)
conversion_hetero = keV_to_J / (voxel_volume_cm3 * density_hetero / 1000.0)

print(f"Voxel: {voxel_size_x_mm:.3f} × {voxel_size_y_mm:.3f} × {voxel_size_z_mm:.1f} mm")
print(f"Volume: {voxel_volume_cm3:.6f} cm³")
print(f"Water (ρ={density_water} g/cm³): 1 keV = {conversion_water:.6e} Gy")
print(f"{hetero_material.upper()} (ρ={density_hetero} g/cm³): 1 keV = {conversion_hetero:.6e} Gy\n")

# Heterogeneity region: 6×6×6 cm cube centered at X=40mm
x_hetero_min, x_hetero_max = 10.0, 70.0
y_hetero_min, y_hetero_max = -30.0, 30.0

# Open files and get histograms
h1 = uproot.open(file1)["h20;1"]
h2 = uproot.open(file2)["h20;1"]

# Get values in keV
vals1_keV = h1.values()
vals2_keV = h2.values()

# Get axes
x_edges = h1.axis(0).edges()
y_edges = h1.axis(1).edges()
x_centers = (x_edges[:-1] + x_edges[1:]) / 2
y_centers = (y_edges[:-1] + y_edges[1:]) / 2

# Create regional mask for heterogeneity
x_mesh, y_mesh = np.meshgrid(x_centers, y_centers, indexing='ij')
mask_hetero = ((x_mesh >= x_hetero_min) & (x_mesh <= x_hetero_max) &
               (y_mesh >= y_hetero_min) & (y_mesh <= y_hetero_max))
mask_water = ~mask_hetero

# Convert to Gy with regional densities
vals1_Gy = np.zeros_like(vals1_keV, dtype=float)
vals1_Gy[mask_hetero] = vals1_keV[mask_hetero] * conversion_hetero
vals1_Gy[mask_water] = vals1_keV[mask_water] * conversion_water

vals2_Gy = np.zeros_like(vals2_keV, dtype=float)
vals2_Gy[mask_hetero] = vals2_keV[mask_hetero] * conversion_hetero
vals2_Gy[mask_water] = vals2_keV[mask_water] * conversion_water

# Subtract (doses in Gy)
difference_Gy = vals1_Gy - vals2_Gy

print(f"Total dose file1: {vals1_Gy.sum():.3e} Gy")
print(f"Total dose file2: {vals2_Gy.sum():.3e} Gy")
print(f"Difference: {difference_Gy.sum():.3e} Gy\n")

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
vmax = np.max(np.abs(difference_Gy))
norm = SymLogNorm(linthresh=1e-6, vmin=-vmax, vmax=vmax)
im = ax.pcolormesh(x_centers, y_centers, difference_Gy.T, cmap='RdBu_r', norm=norm, shading='auto')
cbar = plt.colorbar(im, ax=ax, label='Dose Difference (Gy) - Log Scale')
ax.set_title(title)
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')

# Mark heterogeneity region
rect = plt.Rectangle((x_hetero_min, y_hetero_min), 
                      x_hetero_max - x_hetero_min, 
                      y_hetero_max - y_hetero_min,
                      fill=False, edgecolor='yellow', linewidth=2, linestyle='--',
                      label=f'{hetero_material.upper()} region')
ax.add_patch(rect)
ax.legend(loc='upper right')

# Add cursor value display
def on_move(event):
    if event.inaxes != ax:
        return
    x, y = event.xdata, event.ydata
    if x is None or y is None:
        return
    
    # Find closest bin
    ix = np.argmin(np.abs(x_centers - x))
    iy = np.argmin(np.abs(y_centers - y))
    
    value = difference_Gy[ix, iy]
    ax.set_title(f"{title} | X={x:.1f}mm, Y={y:.1f}mm → {value:.3e} Gy")
    fig.canvas.draw_idle()

fig.canvas.mpl_connect('motion_notify_event', on_move)
plt.show()

#!/usr/bin/env python3
"""
Convert EDEP to dose and compare heterogeneity vs homogeneous
EDEP [keV] -> Dose [Gy]

For 1mm x 1mm x 10mm voxels in water:
- Volume = 0.01 cm³ = 10 mm³
- Mass = 0.01 g (ρ=1 g/cm³ for water)
- Conversion: 1 keV = 1.602e-13 J
- Dose [Gy] = Energy [J] / Mass [kg] = EDEP [keV] * 1.602e-13 / 0.00001 kg
           = EDEP [keV] * 1.602e-8 Gy/keV
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LogNorm

# Open ROOT files
file_hetero = uproot.open("brachytherapy_Bone_Hetero.root")
file_homo = uproot.open("brachytherapy_Water_Homo.root")

# Get histograms
h_hetero = file_hetero["h20"]
h_homo = file_homo["h20"]

# Get bin values in keV
values_hetero_keV = h_hetero.values()
values_homo_keV = h_homo.values()

# Get bin edges
x_edges = h_hetero.axis(0).edges()
y_edges = h_hetero.axis(1).edges()
x_centers = (x_edges[:-1] + x_edges[1:]) / 2
y_centers = (y_edges[:-1] + y_edges[1:]) / 2

# Calculate voxel volume and mass
# From macro: /score/mesh/boxSize 150.0 150.0 5.0 mm
# /score/mesh/nBin 300 300 1
voxel_size_x_mm = (x_edges[1] - x_edges[0])  # ~1 mm
voxel_size_y_mm = (y_edges[1] - y_edges[0])  # ~1 mm
voxel_size_z_mm = 10.0  # Half-width 5.0mm -> full 10mm

voxel_volume_mm3 = voxel_size_x_mm * voxel_size_y_mm * voxel_size_z_mm
voxel_volume_cm3 = voxel_volume_mm3 / 1000.0  # 1 cm³ = 1000 mm³
voxel_mass_g = voxel_volume_cm3 * 1.0  # ρ_water = 1 g/cm³
voxel_mass_kg = voxel_mass_g / 1000.0

# Conversion factor: keV -> Gy
# 1 keV = 1.602e-13 J
# Dose [Gy] = Energy [J] / Mass [kg]
keV_to_J = 1.602e-13
conversion_keV_to_Gy = keV_to_J / voxel_mass_kg

print("=" * 60)
print("VOXEL PARAMETERS:")
print(f"  Size: {voxel_size_x_mm:.3f} x {voxel_size_y_mm:.3f} x {voxel_size_z_mm:.1f} mm")
print(f"  Volume: {voxel_volume_mm3:.2f} mm³ = {voxel_volume_cm3:.5f} cm³")
print(f"  Mass: {voxel_mass_g:.6f} g = {voxel_mass_kg:.9f} kg")
print(f"  Conversion: 1 keV = {conversion_keV_to_Gy:.6e} Gy")
print("=" * 60)

# Convert to Gy
values_hetero_Gy = values_hetero_keV * conversion_keV_to_Gy
values_homo_Gy = values_homo_keV * conversion_keV_to_Gy

# Calculate difference and ratio
difference_Gy = values_hetero_Gy - values_homo_Gy
ratio = np.divide(values_hetero_Gy, values_homo_Gy,
                  out=np.ones_like(values_hetero_Gy),
                  where=values_homo_Gy!=0)

# Percent difference
percent_diff = np.divide(100.0 * (values_hetero_Gy - values_homo_Gy), values_homo_Gy,
                        out=np.zeros_like(values_hetero_Gy),
                        where=values_homo_Gy!=0)

print("\n=== DOSE COMPARISON: HETEROGENEITY vs HOMOGENEOUS ===")
print(f"232003 (Hetero) total:  {np.sum(values_hetero_Gy):.6e} Gy")
print(f"233210 (Homo) total:    {np.sum(values_homo_Gy):.6e} Gy")
print(f"Difference (H-Ho):      {np.sum(difference_Gy):.6e} Gy")
print(f"Percent difference:     {100.0*np.sum(difference_Gy)/np.sum(values_homo_Gy):.2f}%")
print(f"\nStatistics:")
print(f"Max difference:         {np.max(difference_Gy):.6e} Gy")
print(f"Min difference:         {np.min(difference_Gy):.6e} Gy")
print(f"Mean difference:        {np.mean(difference_Gy):.6e} Gy")
print(f"Std difference:         {np.std(difference_Gy):.6e} Gy")

# Regional analysis - HETEROGENEITY AT X=40mm, EXTENDS ±30mm
print(f"\n=== REGIONAL ANALYSIS (Hetero centered at X=40mm, size 6cm) ===")
x_idx_10 = np.argmin(np.abs(x_centers - 10.0))   # Near edge
x_idx_40 = np.argmin(np.abs(x_centers - 40.0))   # Center
x_idx_70 = np.argmin(np.abs(x_centers - 70.0))   # Far edge

sum_hetero_10 = np.sum(values_hetero_Gy[x_idx_10, :])
sum_homo_10 = np.sum(values_homo_Gy[x_idx_10, :])
sum_hetero_40 = np.sum(values_hetero_Gy[x_idx_40, :])
sum_homo_40 = np.sum(values_homo_Gy[x_idx_40, :])
sum_hetero_70 = np.sum(values_hetero_Gy[x_idx_70, :])
sum_homo_70 = np.sum(values_homo_Gy[x_idx_70, :])

print(f"X=10mm (borde cercano):")
print(f"  Hetero: {sum_hetero_10:.6e} Gy, Homo: {sum_homo_10:.6e} Gy")
print(f"  Ratio: {sum_hetero_10/sum_homo_10:.4f}, Change: {100.0*(sum_hetero_10-sum_homo_10)/sum_homo_10:.2f}%")
print(f"X=40mm (centro hetero):")
print(f"  Hetero: {sum_hetero_40:.6e} Gy, Homo: {sum_homo_40:.6e} Gy")
print(f"  Ratio: {sum_hetero_40/sum_homo_40:.4f}, Change: {100.0*(sum_hetero_40-sum_homo_40)/sum_homo_40:.2f}%")
print(f"X=70mm (borde lejano):")
print(f"  Hetero: {sum_hetero_70:.6e} Gy, Homo: {sum_homo_70:.6e} Gy")
print(f"  Ratio: {sum_hetero_70/sum_homo_70:.4f}, Change: {100.0*(sum_hetero_70-sum_homo_70)/sum_homo_70:.2f}%")

# Create figure
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Plot 1: Heterogeneity dose map
im1 = axes[0, 0].pcolormesh(x_centers, y_centers, values_hetero_Gy.T,
                             cmap='hot', norm=LogNorm())
axes[0, 0].set_title('WITH Heterogeneity (Bone)', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('X [mm]')
axes[0, 0].set_ylabel('Y [mm]')
axes[0, 0].axvline(x=40, color='cyan', linestyle='--', linewidth=2, label='Hetero center')
axes[0, 0].axvline(x=10, color='cyan', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 0].axvline(x=70, color='cyan', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 0].axhline(y=30, color='cyan', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 0].axhline(y=-30, color='cyan', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 0].legend()
cbar1 = plt.colorbar(im1, ax=axes[0, 0], label='Dose [Gy]')

# Plot 2: Homogeneous dose map
im2 = axes[0, 1].pcolormesh(x_centers, y_centers, values_homo_Gy.T,
                             cmap='hot', norm=LogNorm())
axes[0, 1].set_title('Homogeneous Water Only', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('X [mm]')
axes[0, 1].set_ylabel('Y [mm]')
cbar2 = plt.colorbar(im2, ax=axes[0, 1], label='Dose [Gy]')

# Plot 3: Absolute difference
vmax = max(abs(np.nanmin(difference_Gy)), abs(np.nanmax(difference_Gy)))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
im3 = axes[0, 2].pcolormesh(x_centers, y_centers, difference_Gy.T,
                             cmap='RdBu_r', norm=norm)
axes[0, 2].set_title('Difference (Hetero - Homo)', fontsize=14, fontweight='bold')
axes[0, 2].set_xlabel('X [mm]')
axes[0, 2].set_ylabel('Y [mm]')
axes[0, 2].axvline(x=40, color='black', linestyle='--', linewidth=2)
axes[0, 2].axvline(x=10, color='black', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 2].axvline(x=70, color='black', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 2].add_patch(plt.Rectangle((10, -30), 60, 60, fill=False,
                                   edgecolor='yellow', linewidth=2, linestyle='--'))
cbar3 = plt.colorbar(im3, ax=axes[0, 2], label='Difference [Gy]')

# Plot 4: Ratio
im4 = axes[1, 0].pcolormesh(x_centers, y_centers, ratio.T,
                             cmap='RdYlBu_r', vmin=0.8, vmax=1.5)
axes[1, 0].set_title('Ratio (Hetero / Homo)', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('X [mm]')
axes[1, 0].set_ylabel('Y [mm]')
axes[1, 0].axvline(x=40, color='black', linestyle='--', linewidth=2)
axes[1, 0].add_patch(plt.Rectangle((10, -30), 60, 60, fill=False,
                                   edgecolor='yellow', linewidth=2, linestyle='--'))
cbar4 = plt.colorbar(im4, ax=axes[1, 0], label='Ratio')

# Plot 5: Percent difference
im5 = axes[1, 1].pcolormesh(x_centers, y_centers, percent_diff.T,
                             cmap='RdBu_r', vmin=-50, vmax=50)
axes[1, 1].set_title('Percent Change (%)', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('X [mm]')
axes[1, 1].set_ylabel('Y [mm]')
axes[1, 1].axvline(x=40, color='black', linestyle='--', linewidth=2)
axes[1, 1].add_patch(plt.Rectangle((10, -30), 60, 60, fill=False,
                                   edgecolor='yellow', linewidth=2, linestyle='--'))
cbar5 = plt.colorbar(im5, ax=axes[1, 1], label='% Change')

# Plot 6: 1D profiles along X-axis at Y=0
y_bin_center = np.argmin(np.abs(y_centers - 0))
profile_hetero = values_hetero_Gy[:, y_bin_center]
profile_homo = values_homo_Gy[:, y_bin_center]
profile_diff = difference_Gy[:, y_bin_center]

ax6 = axes[1, 2]
ax6.plot(x_centers, profile_hetero, 'r-', linewidth=2.5, label='Hetero', marker='o', markersize=2, markevery=30)
ax6.plot(x_centers, profile_homo, 'b-', linewidth=2.5, label='Homo', marker='s', markersize=2, markevery=30)
ax6.set_xlabel('X [mm]', fontsize=11)
ax6.set_ylabel('Dose [Gy]', color='k', fontsize=11)
ax6.set_title('1D Profile at Y=0', fontsize=14, fontweight='bold')
ax6.legend(loc='upper right', fontsize=11)
ax6.set_yscale('log')
ax6.grid(True, alpha=0.3)
ax6.axvline(x=40, color='gray', linestyle='--', linewidth=2, alpha=0.5)
ax6.axvline(x=10, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax6.axvline(x=70, color='gray', linestyle=':', linewidth=1, alpha=0.5)

ax6_twin = ax6.twinx()
ax6_twin.plot(x_centers, profile_diff, 'g-', linewidth=2, alpha=0.7, label='Difference', marker='^', markersize=2, markevery=30)
ax6_twin.set_ylabel('Difference [Gy]', color='g', fontsize=11)
ax6_twin.tick_params(axis='y', labelcolor='g')
ax6_twin.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

plt.tight_layout()
plt.savefig('heterogeneity_dose_comparison_Gy.png', dpi=300, bbox_inches='tight')
print("\n" + "=" * 60)
print("==> Plot saved as: heterogeneity_dose_comparison_Gy.png")
print("=" * 60)
print("\nHeterogeneity region marked with YELLOW RECTANGLE in plots")
print("(X: 10-70mm, Y: ±30mm)")
print("\nColumn colors in plots:")
print("  RED: With bone heterogeneity")
print("  BLUE: Homogeneous water (control)")
print("  CYAN/BLACK: Marks heterogeneity boundaries")

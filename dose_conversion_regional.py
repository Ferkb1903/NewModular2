#!/usr/bin/env python3
"""
Convert EDEP to dose by REGION
Different regions may have different materials/densities

Regions:
1. WATER: ρ = 1.0 g/cm³ (outside heterogeneity)
2. BONE: ρ = 1.92 g/cm³ (G4_BONE_COMPACT_ICRU, inside heterogeneity at X=10-70mm, Y=±30mm)
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LogNorm

# Open ROOT files
file_homo = uproot.open("brachytherapy_20251019_001546.root")
file_hetero = uproot.open("brachytherapy_20251019_001606.root")
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

# Calculate voxel volume
# From macro: /score/mesh/boxSize 150.0 150.0 5.0 mm (half-dimensions)
# /score/mesh/nBin 300 300 1
voxel_size_x_mm = (x_edges[1] - x_edges[0])
voxel_size_y_mm = (y_edges[1] - y_edges[0])
voxel_size_z_mm = 10.0  # Full depth (half-width 5.0mm each side)

voxel_volume_mm3 = voxel_size_x_mm * voxel_size_y_mm * voxel_size_z_mm
voxel_volume_cm3 = voxel_volume_mm3 / 1000.0

print("=" * 70)
print("REGIONAL DOSE CONVERSION")
print("=" * 70)
print(f"\nVoxel dimensions: {voxel_size_x_mm:.3f} × {voxel_size_y_mm:.3f} × {voxel_size_z_mm:.1f} mm")
print(f"Voxel volume: {voxel_volume_cm3:.6f} cm³")

# Define regions
# HETEROGENEITY: X ∈ [10, 70]mm, Y ∈ [-30, 30]mm (6cm cube centered at X=40mm)
x_hetero_min, x_hetero_max = 10.0, 70.0
y_hetero_min, y_hetero_max = -30.0, 30.0

# Create regional masks
x_mesh, y_mesh = np.meshgrid(x_centers, y_centers, indexing='ij')
mask_hetero = ((x_mesh >= x_hetero_min) & (x_mesh <= x_hetero_max) &
               (y_mesh >= y_hetero_min) & (y_mesh <= y_hetero_max))
mask_water = ~mask_hetero

print(f"\nREGION DEFINITIONS:")
print(f"  HETEROGENEITY (Bone): X=[{x_hetero_min}, {x_hetero_max}]mm, Y=[{y_hetero_min}, {y_hetero_max}]mm")
print(f"  WATER (surroundings): Everything else")
print(f"\nRegion sizes:")
print(f"  Bone region voxels: {np.sum(mask_hetero)}")
print(f"  Water region voxels: {np.sum(mask_water)}")

# Densities and conversion factors
density_water = 1.0  # g/cm³
density_bone = 1.92  # g/cm³ (G4_BONE_COMPACT_ICRU)

mass_water_kg = voxel_volume_cm3 * density_water / 1000.0
mass_bone_kg = voxel_volume_cm3 * density_bone / 1000.0

keV_to_J = 1.602e-13
conversion_water_keV_to_Gy = keV_to_J / mass_water_kg
conversion_bone_keV_to_Gy = keV_to_J / mass_bone_kg

print(f"\nCONVERSION FACTORS:")
print(f"  Water mass: {mass_water_kg:.6e} kg → 1 keV = {conversion_water_keV_to_Gy:.6e} Gy")
print(f"  Bone mass: {mass_bone_kg:.6e} kg → 1 keV = {conversion_bone_keV_to_Gy:.6e} Gy")
print(f"  Ratio (bone/water): {conversion_bone_keV_to_Gy/conversion_water_keV_to_Gy:.3f}x")

# Convert to Gy with regional factors
values_hetero_Gy = np.zeros_like(values_hetero_keV, dtype=float)
values_homo_Gy = np.zeros_like(values_homo_keV, dtype=float)

# Apply correct conversion based on region
# Heterogeneity file: hetero region uses bone density, rest uses water
values_hetero_Gy[mask_hetero] = values_hetero_keV[mask_hetero] * conversion_bone_keV_to_Gy
values_hetero_Gy[mask_water] = values_hetero_keV[mask_water] * conversion_water_keV_to_Gy

# Homogeneous file: everything is water
values_homo_Gy = values_homo_keV * conversion_water_keV_to_Gy

# Calculate differences
difference_Gy = values_hetero_Gy - values_homo_Gy
percent_diff = np.divide(100.0 * (values_hetero_Gy - values_homo_Gy), values_homo_Gy,
                        out=np.zeros_like(values_hetero_Gy),
                        where=values_homo_Gy!=0)

print("\n" + "=" * 70)
print("TOTAL DOSE COMPARISON")
print("=" * 70)
total_hetero = np.sum(values_hetero_Gy)
total_homo = np.sum(values_homo_Gy)
print(f"WITH Heterogeneity:  {total_hetero:.6e} Gy")
print(f"Homogeneous (water): {total_homo:.6e} Gy")
print(f"Difference:          {(total_hetero - total_homo):.6e} Gy (+{100.0*(total_hetero-total_homo)/total_homo:.2f}%)")

print("\n" + "=" * 70)
print("DOSE BY REGION")
print("=" * 70)

# Heterogeneity file - dose in bone region
dose_hetero_bone = np.sum(values_hetero_Gy[mask_hetero])
dose_hetero_water = np.sum(values_hetero_Gy[mask_water])

# Homogeneous file - dose where heterogeneity would be (still water)
dose_homo_hetero_region = np.sum(values_homo_Gy[mask_hetero])
dose_homo_water_region = np.sum(values_homo_Gy[mask_water])

print(f"\nIN HETEROGENEITY REGION (X=[{x_hetero_min}, {x_hetero_max}], Y=[{y_hetero_min}, {y_hetero_max}]):")
print(f"  WITH Bone:        {dose_hetero_bone:.6e} Gy")
print(f"  Water only:       {dose_homo_hetero_region:.6e} Gy")
print(f"  Difference:       {(dose_hetero_bone - dose_homo_hetero_region):.6e} Gy")
print(f"  Change:           {100.0*(dose_hetero_bone - dose_homo_hetero_region)/dose_homo_hetero_region:+.2f}%")

print(f"\nOUTSIDE HETEROGENEITY REGION:")
print(f"  WITH surrounding: {dose_hetero_water:.6e} Gy")
print(f"  Homogeneous:      {dose_homo_water_region:.6e} Gy")
print(f"  Difference:       {(dose_hetero_water - dose_homo_water_region):.6e} Gy")
print(f"  Change:           {100.0*(dose_hetero_water - dose_homo_water_region)/dose_homo_water_region:+.2f}%")

# X-profile analysis
print(f"\n" + "=" * 70)
print("X-PROFILE ANALYSIS (integrated over Y)")
print("=" * 70)

dose_hetero_x = np.sum(values_hetero_Gy, axis=1)
dose_homo_x = np.sum(values_homo_Gy, axis=1)
difference_x = dose_hetero_x - dose_homo_x

# Specific X positions
x_positions = [10, 25, 40, 55, 70]  # mm
print(f"\n{'X (mm)':<10} {'With Hetero':<20} {'Homogeneous':<20} {'Difference':<20} {'Change %':<10}")
print("-" * 80)
for x_pos in x_positions:
    idx = np.argmin(np.abs(x_centers - x_pos))
    d_het = dose_hetero_x[idx]
    d_homo = dose_homo_x[idx]
    diff = d_het - d_homo
    pct = 100.0 * diff / d_homo if d_homo != 0 else 0
    
    # Determine which material region
    in_hetero = x_hetero_min <= x_pos <= x_hetero_max
    material = "BONE" if in_hetero else "WATER"
    
    print(f"{x_pos:<10.0f} {d_het:<20.6e} {d_homo:<20.6e} {diff:<20.6e} {pct:+.2f}% ({material})")

# Create visualization
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Plot 1: Heterogeneity dose map (with bone)
im1 = axes[0, 0].pcolormesh(x_centers, y_centers, values_hetero_Gy.T,
                             cmap='hot', norm=LogNorm())
axes[0, 0].set_title('WITH Heterogeneity\n(Bone with ρ=1.92 g/cm³)', 
                     fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('X [mm]')
axes[0, 0].set_ylabel('Y [mm]')
axes[0, 0].add_patch(plt.Rectangle((x_hetero_min, y_hetero_min), 
                                   x_hetero_max-x_hetero_min, 
                                   y_hetero_max-y_hetero_min, 
                                   fill=False, edgecolor='cyan', 
                                   linewidth=2, linestyle='--', label='Bone region'))
axes[0, 0].legend()
cbar1 = plt.colorbar(im1, ax=axes[0, 0], label='Dose [Gy]')

# Plot 2: Homogeneous dose map (all water)
im2 = axes[0, 1].pcolormesh(x_centers, y_centers, values_homo_Gy.T,
                             cmap='hot', norm=LogNorm())
axes[0, 1].set_title('Homogeneous Water\n(ρ=1.0 g/cm³)', 
                     fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('X [mm]')
axes[0, 1].set_ylabel('Y [mm]')
axes[0, 1].add_patch(plt.Rectangle((x_hetero_min, y_hetero_min), 
                                   x_hetero_max-x_hetero_min, 
                                   y_hetero_max-y_hetero_min, 
                                   fill=False, edgecolor='yellow', 
                                   linewidth=2, linestyle='--', alpha=0.7))
cbar2 = plt.colorbar(im2, ax=axes[0, 1], label='Dose [Gy]')

# Plot 3: Absolute difference
vmax = max(abs(np.nanmin(difference_Gy)), abs(np.nanmax(difference_Gy)))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
im3 = axes[0, 2].pcolormesh(x_centers, y_centers, difference_Gy.T,
                             cmap='RdBu_r', norm=norm)
axes[0, 2].set_title('Difference (Hetero - Homo)\n[Gy]', 
                     fontsize=14, fontweight='bold')
axes[0, 2].set_xlabel('X [mm]')
axes[0, 2].set_ylabel('Y [mm]')
axes[0, 2].add_patch(plt.Rectangle((x_hetero_min, y_hetero_min), 
                                   x_hetero_max-x_hetero_min, 
                                   y_hetero_max-y_hetero_min, 
                                   fill=False, edgecolor='black', 
                                   linewidth=2, linestyle='--'))
cbar3 = plt.colorbar(im3, ax=axes[0, 2], label='Difference [Gy]')

# Plot 4: Percent difference
percent_diff_clipped = np.clip(percent_diff, -100, 100)
mask_valid = (values_homo_Gy > 0)
im4 = axes[1, 0].pcolormesh(x_centers, y_centers, 
                             np.where(mask_valid.T, percent_diff.T, np.nan),
                             cmap='RdBu_r', vmin=-100, vmax=100)
axes[1, 0].set_title('Percent Difference\n[(Hetero-Homo)/Homo × 100%]', 
                     fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('X [mm]')
axes[1, 0].set_ylabel('Y [mm]')
axes[1, 0].add_patch(plt.Rectangle((x_hetero_min, y_hetero_min), 
                                   x_hetero_max-x_hetero_min, 
                                   y_hetero_max-y_hetero_min, 
                                   fill=False, edgecolor='black', 
                                   linewidth=2, linestyle='--'))
cbar4 = plt.colorbar(im4, ax=axes[1, 0], label='Percent [%]')

# Plot 5: X-profile
axes[1, 1].plot(x_centers, dose_hetero_x, 'r-', linewidth=2, label='With Heterogeneity')
axes[1, 1].plot(x_centers, dose_homo_x, 'b-', linewidth=2, label='Homogeneous')
axes[1, 1].axvline(x=x_hetero_min, color='cyan', linestyle='--', alpha=0.5, label='Hetero bounds')
axes[1, 1].axvline(x=x_hetero_max, color='cyan', linestyle='--', alpha=0.5)
axes[1, 1].set_xlabel('X [mm]')
axes[1, 1].set_ylabel('Integrated Dose [Gy]')
axes[1, 1].set_title('X-Profile (integrated over Y)', fontsize=14, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_yscale('log')

# Plot 6: X-profile difference
axes[1, 2].plot(x_centers, difference_x, 'g-', linewidth=2, label='Difference')
axes[1, 2].axvline(x=x_hetero_min, color='cyan', linestyle='--', alpha=0.5)
axes[1, 2].axvline(x=x_hetero_max, color='cyan', linestyle='--', alpha=0.5)
axes[1, 2].axhline(y=0, color='k', linestyle='-', alpha=0.3)
axes[1, 2].set_xlabel('X [mm]')
axes[1, 2].set_ylabel('Dose Difference [Gy]')
axes[1, 2].set_title('X-Profile Difference', fontsize=14, fontweight='bold')
axes[1, 2].legend()
axes[1, 2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('dose_regional_comparison.png', dpi=150, bbox_inches='tight')
print(f"\n{'=' * 70}")
print(f"Plot saved as: dose_regional_comparison.png")
print(f"{'=' * 70}")

plt.close()

# Create a detailed statistics file
with open('regional_dose_analysis.txt', 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("REGIONAL DOSE ANALYSIS - HETEROGENEITY vs HOMOGENEOUS\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("MATERIAL PROPERTIES:\n")
    f.write(f"  Water: ρ = 1.0 g/cm³\n")
    f.write(f"  Bone (G4_BONE_COMPACT_ICRU): ρ = 1.92 g/cm³\n\n")
    
    f.write(f"VOXEL PARAMETERS:\n")
    f.write(f"  Size: {voxel_size_x_mm:.3f} × {voxel_size_y_mm:.3f} × {voxel_size_z_mm:.1f} mm\n")
    f.write(f"  Volume: {voxel_volume_cm3:.6f} cm³\n")
    f.write(f"  Mass (water): {mass_water_kg:.6e} kg\n")
    f.write(f"  Mass (bone): {mass_bone_kg:.6e} kg\n\n")
    
    f.write(f"CONVERSION FACTORS:\n")
    f.write(f"  Water: 1 keV = {conversion_water_keV_to_Gy:.6e} Gy\n")
    f.write(f"  Bone: 1 keV = {conversion_bone_keV_to_Gy:.6e} Gy\n")
    f.write(f"  Ratio (bone/water): {conversion_bone_keV_to_Gy/conversion_water_keV_to_Gy:.3f}x\n\n")
    
    f.write("=" * 70 + "\n")
    f.write("TOTAL DOSE COMPARISON\n")
    f.write("=" * 70 + "\n")
    f.write(f"WITH Heterogeneity:  {total_hetero:.6e} Gy\n")
    f.write(f"Homogeneous (water): {total_homo:.6e} Gy\n")
    f.write(f"Difference:          {(total_hetero - total_homo):.6e} Gy\n")
    f.write(f"Change:              +{100.0*(total_hetero-total_homo)/total_homo:.2f}%\n\n")
    
    f.write("=" * 70 + "\n")
    f.write("DOSE BY REGION\n")
    f.write("=" * 70 + "\n")
    f.write(f"\nIN HETEROGENEITY REGION (Bone):\n")
    f.write(f"  Hetero (with bone):  {dose_hetero_bone:.6e} Gy\n")
    f.write(f"  Homo (water equiv):  {dose_homo_hetero_region:.6e} Gy\n")
    f.write(f"  Difference:          {(dose_hetero_bone - dose_homo_hetero_region):.6e} Gy\n")
    f.write(f"  Change:              +{100.0*(dose_hetero_bone - dose_homo_hetero_region)/dose_homo_hetero_region:.2f}%\n")
    
    f.write(f"\nOUTSIDE HETEROGENEITY REGION (Water):\n")
    f.write(f"  Hetero (water):      {dose_hetero_water:.6e} Gy\n")
    f.write(f"  Homo (water):        {dose_homo_water_region:.6e} Gy\n")
    f.write(f"  Difference:          {(dose_hetero_water - dose_homo_water_region):.6e} Gy\n")
    f.write(f"  Change:              {100.0*(dose_hetero_water - dose_homo_water_region)/dose_homo_water_region:+.2f}%\n")

print("\nStatistics file saved as: regional_dose_analysis.txt")

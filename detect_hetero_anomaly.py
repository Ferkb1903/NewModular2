#!/usr/bin/env python3
"""
Detect which file has heterogeneity anomaly.
Compare two homogeneous files and identify where the unexpected difference is.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THESE =====
file1 = "brachytherapy_Water_Homo.root"
file2 = "brachytherapy_Lung_Homo_200m.root"
hetero_region = (10.0, 70.0)  # (x_min, x_max) in mm where anomaly appears
# =======================


def load_histogram(file_path):
    """Load h20;1 histogram from ROOT file."""
    print(f"  Loading: {file_path}")
    f = uproot.open(file_path)
    h = f["h20;1"]
    vals = h.values()
    x_edges = h.axis(0).edges()
    y_edges = h.axis(1).edges()
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    
    print(f"    Shape: {vals.shape}")
    print(f"    Total EDEP: {np.sum(vals):.6e} keV")
    print(f"    Min: {np.min(vals):.6e}, Max: {np.max(vals):.6e}")
    
    return vals, x_centers, y_centers


print("Loading homogeneous files...\n")
vals1, x_centers, y_centers = load_histogram(file1)
vals2, _, _ = load_histogram(file2)

print("\n" + "="*80)
print("REGIONAL ANALYSIS")
print("="*80)

# Define regions
x_min, x_max = hetero_region
inside_mask = (x_centers >= x_min) & (x_centers <= x_max)
outside_mask = ~inside_mask

# Extract regional data
edep1_inside = vals1[inside_mask, :]
edep1_outside = vals1[outside_mask, :]
edep2_inside = vals2[inside_mask, :]
edep2_outside = vals2[outside_mask, :]

# Calculate statistics
print(f"\nInside hetero region ({x_min}-{x_max} mm):")
print(f"\n  File 1 ({file1}):")
print(f"    Total EDEP: {np.sum(edep1_inside):.6e} keV")
print(f"    Mean per voxel: {np.mean(edep1_inside):.6e} keV")
print(f"    Std dev: {np.std(edep1_inside):.6e} keV")
print(f"    Min: {np.min(edep1_inside):.6e}, Max: {np.max(edep1_inside):.6e}")

print(f"\n  File 2 ({file2}):")
print(f"    Total EDEP: {np.sum(edep2_inside):.6e} keV")
print(f"    Mean per voxel: {np.mean(edep2_inside):.6e} keV")
print(f"    Std dev: {np.std(edep2_inside):.6e} keV")
print(f"    Min: {np.min(edep2_inside):.6e}, Max: {np.max(edep2_inside):.6e}")

ratio_inside = np.sum(edep2_inside) / np.sum(edep1_inside) if np.sum(edep1_inside) > 0 else 0
print(f"\n  Ratio (File2/File1) inside: {ratio_inside:.6f}")

print(f"\n\nOutside hetero region (X < {x_min} or X > {x_max} mm):")
print(f"\n  File 1 ({file1}):")
print(f"    Total EDEP: {np.sum(edep1_outside):.6e} keV")
print(f"    Mean per voxel: {np.mean(edep1_outside):.6e} keV")
print(f"    Std dev: {np.std(edep1_outside):.6e} keV")
print(f"    Min: {np.min(edep1_outside):.6e}, Max: {np.max(edep1_outside):.6e}")

print(f"\n  File 2 ({file2}):")
print(f"    Total EDEP: {np.sum(edep2_outside):.6e} keV")
print(f"    Mean per voxel: {np.mean(edep2_outside):.6e} keV")
print(f"    Std dev: {np.std(edep2_outside):.6e} keV")
print(f"    Min: {np.min(edep2_outside):.6e}, Max: {np.max(edep2_outside):.6e}")

ratio_outside = np.sum(edep2_outside) / np.sum(edep1_outside) if np.sum(edep1_outside) > 0 else 0
print(f"\n  Ratio (File2/File1) outside: {ratio_outside:.6f}")

print("\n" + "="*80)
print("DIAGNOSIS")
print("="*80)

if abs(ratio_inside - ratio_outside) > 0.1:
    print(f"\n⚠️  SIGNIFICANT DIFFERENCE DETECTED between inside and outside regions!")
    print(f"   Inside ratio: {ratio_inside:.6f}")
    print(f"   Outside ratio: {ratio_outside:.6f}")
    print(f"   Difference: {abs(ratio_inside - ratio_outside):.6f}")
    
    if ratio_inside > ratio_outside:
        print(f"\n   → File 2 ({file2}) has HIGHER dose INSIDE the suspected hetero region")
        print(f"     This suggests File 2 might have a LOWER-DENSITY heterogeneity")
        print(f"     (less interaction, more particles reach beyond)")
    else:
        print(f"\n   → File 1 ({file1}) has HIGHER dose INSIDE the suspected hetero region")
        print(f"     This suggests File 1 might have a LOWER-DENSITY heterogeneity")
        print(f"     (less interaction, more particles reach beyond)")
else:
    print("\n✓ Ratios are similar inside and outside.")
    print("  The difference is likely just due to different materials (Water vs Lung),")
    print("  not due to heterogeneity artifacts.")

# Create detailed visualization
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

# Top row: Full maps
ax1 = fig.add_subplot(gs[0, 0])
vmax1 = np.max(np.abs(vals1))
im1 = ax1.pcolormesh(x_centers, y_centers, vals1.T, cmap='viridis', vmax=vmax1, shading='auto')
ax1.set_title(f'File 1: {file1}', fontsize=11, fontweight='bold')
ax1.set_ylabel('Y (mm)')
x_min_val, x_max_val = hetero_region
rect = plt.Rectangle((x_min_val, -30), x_max_val - x_min_val, 60, 
                      linewidth=2, edgecolor='yellow', facecolor='none')
ax1.add_patch(rect)
plt.colorbar(im1, ax=ax1, label='EDEP (keV)')

ax2 = fig.add_subplot(gs[0, 1])
vmax2 = np.max(np.abs(vals2))
im2 = ax2.pcolormesh(x_centers, y_centers, vals2.T, cmap='viridis', vmax=vmax2, shading='auto')
ax2.set_title(f'File 2: {file2}', fontsize=11, fontweight='bold')
rect = plt.Rectangle((x_min_val, -30), x_max_val - x_min_val, 60, 
                      linewidth=2, edgecolor='yellow', facecolor='none')
ax2.add_patch(rect)
plt.colorbar(im2, ax=ax2, label='EDEP (keV)')

ax3 = fig.add_subplot(gs[0, 2])
diff = vals2 - vals1
vmax_diff = np.max(np.abs(diff))
norm = SymLogNorm(linthresh=max(vmax_diff * 0.01, 1.0), vmin=-vmax_diff, vmax=vmax_diff)
im3 = ax3.pcolormesh(x_centers, y_centers, diff.T, cmap='RdBu_r', norm=norm, shading='auto')
ax3.set_title('Difference (File2 - File1)', fontsize=11, fontweight='bold')
rect = plt.Rectangle((x_min_val, -30), x_max_val - x_min_val, 60, 
                      linewidth=2, edgecolor='yellow', facecolor='none')
ax3.add_patch(rect)
plt.colorbar(im3, ax=ax3, label='Difference (keV)')

# Zoom into hetero region
hetero_slice_1 = vals1[inside_mask, :]
hetero_slice_2 = vals2[inside_mask, :]
x_hetero = x_centers[inside_mask]

ax4 = fig.add_subplot(gs[1, 0])
y_prof_1 = np.mean(hetero_slice_1, axis=1)
y_prof_2 = np.mean(hetero_slice_2, axis=1)
ax4.plot(x_hetero, y_prof_1, 'o-', label=file1, linewidth=2, markersize=4)
ax4.plot(x_hetero, y_prof_2, 's-', label=file2, linewidth=2, markersize=4)
ax4.set_xlabel('X (mm)')
ax4.set_ylabel('Mean Dose (keV)')
ax4.set_title('Y-averaged profiles (inside hetero region)', fontsize=10, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend(fontsize=9)
ax4.set_yscale('log')

# Horizontal profiles
ax5 = fig.add_subplot(gs[1, 1])
profile1 = np.sum(vals1, axis=1)
profile2 = np.sum(vals2, axis=1)
ax5.plot(x_centers, profile1, 'o-', label=file1, linewidth=2, markersize=3, alpha=0.7)
ax5.plot(x_centers, profile2, 's-', label=file2, linewidth=2, markersize=3, alpha=0.7)
ax5.axvspan(x_min_val, x_max_val, alpha=0.15, color='red')
ax5.set_xlabel('X (mm)')
ax5.set_ylabel('Total Dose per X bin (keV)')
ax5.set_title('Horizontal profiles', fontsize=10, fontweight='bold')
ax5.grid(True, alpha=0.3)
ax5.legend(fontsize=9)
ax5.set_yscale('log')

# Ratio plot
ax6 = fig.add_subplot(gs[1, 2])
profile1_safe = np.where(profile1 > 0, profile1, np.nan)
ratio_profile = profile2 / profile1_safe
valid = ~np.isnan(ratio_profile)
ax6.plot(x_centers[valid], ratio_profile[valid], 'o-', linewidth=2, markersize=3, color='purple')
ax6.axhline(1.0, color='black', linestyle='--', linewidth=1, alpha=0.7)
ax6.axvspan(x_min_val, x_max_val, alpha=0.15, color='red')
ax6.set_xlabel('X (mm)')
ax6.set_ylabel('Ratio (File2/File1)')
ax6.set_title('Dose ratio profile', fontsize=10, fontweight='bold')
ax6.grid(True, alpha=0.3)
ax6.set_yscale('log')

# Statistics bars
ax7 = fig.add_subplot(gs[2, :])
regions = ['Inside\nhetero', 'Outside\nhetero']
ratio1_data = [ratio_inside, ratio_outside]
colors = ['orange' if abs(r - 1.0) > 0.1 else 'green' for r in ratio1_data]
bars = ax7.bar(regions, ratio1_data, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
ax7.axhline(1.0, color='red', linestyle='--', linewidth=2, label='Expected (ratio=1.0)')
ax7.set_ylabel('Dose Ratio (File2/File1)', fontsize=11)
ax7.set_title('Regional Dose Ratio Comparison', fontsize=12, fontweight='bold')
ax7.set_ylim([0, max(ratio1_data) * 1.2])
ax7.grid(True, alpha=0.3, axis='y')
ax7.legend(fontsize=10)

# Add value labels on bars
for bar, val in zip(bars, ratio1_data):
    height = bar.get_height()
    ax7.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.savefig("hetero_detection.png", dpi=150, bbox_inches='tight')
print(f"\nSaved: hetero_detection.png\n")

plt.show()

#!/usr/bin/env python3
"""
Compare two homogeneous files by subtracting their dose maps.
Shows differences that should NOT exist if both are truly homogeneous.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THESE =====
file1 = "brachytherapy_Water_Homo.root"     # Reference
file2 = "brachytherapy_Lung_Homo_200m.root" # Test
hetero_region = (10.0, 70.0)  # (x_min, x_max) in mm where hetero SHOULD be (but isn't in homo)
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


print("Loading histograms...")
vals1, x_centers1, y_centers1 = load_histogram(file1)
vals2, x_centers2, y_centers2 = load_histogram(file2)

# Subtract
print("\nSubtracting: File2 - File1")
difference = vals2 - vals1

print(f"\nDifference statistics:")
print(f"  Min: {np.min(difference):.6e}")
print(f"  Max: {np.max(difference):.6e}")
print(f"  Mean: {np.mean(difference):.6e}")
print(f"  Std: {np.std(difference):.6e}")
print(f"  Total: {np.sum(difference):.6e} keV")

# Create figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# ===== Plot 1: File 1 =====
ax = axes[0]
vmax1 = np.max(np.abs(vals1))
im1 = ax.pcolormesh(x_centers1, y_centers1, vals1.T, cmap='viridis', vmax=vmax1, shading='auto')
ax.set_title(f'File 1: {file1}', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
if hetero_region:
    x_min, x_max = hetero_region
    rect = plt.Rectangle((x_min, -30), x_max - x_min, 60, linewidth=2, edgecolor='yellow', facecolor='none')
    ax.add_patch(rect)
plt.colorbar(im1, ax=ax, label='EDEP (keV)')

# ===== Plot 2: File 2 =====
ax = axes[1]
vmax2 = np.max(np.abs(vals2))
im2 = ax.pcolormesh(x_centers2, y_centers2, vals2.T, cmap='viridis', vmax=vmax2, shading='auto')
ax.set_title(f'File 2: {file2}', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
if hetero_region:
    x_min, x_max = hetero_region
    rect = plt.Rectangle((x_min, -30), x_max - x_min, 60, linewidth=2, edgecolor='yellow', facecolor='none')
    ax.add_patch(rect)
plt.colorbar(im2, ax=ax, label='EDEP (keV)')

# ===== Plot 3: Difference (with SymLogNorm) =====
ax = axes[2]
vmax_diff = np.max(np.abs(difference))
norm = SymLogNorm(linthresh=max(vmax_diff * 0.01, 1.0), vmin=-vmax_diff, vmax=vmax_diff)
im_diff = ax.pcolormesh(x_centers1, y_centers1, difference.T, cmap='RdBu_r', norm=norm, shading='auto')
ax.set_title(f'Difference (File2 - File1)\n(SymLog scale)', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
if hetero_region:
    x_min, x_max = hetero_region
    rect = plt.Rectangle((x_min, -30), x_max - x_min, 60, linewidth=2, edgecolor='yellow', facecolor='none')
    ax.add_patch(rect)
plt.colorbar(im_diff, ax=ax, label='Difference (keV)')

plt.tight_layout()
plt.savefig("compare_homo_files.png", dpi=150, bbox_inches='tight')
print(f"\nSaved: compare_homo_files.png")

# Compute horizontal profiles for more detail
print("\n" + "="*80)
print("HORIZONTAL PROFILE COMPARISON")
print("="*80)

profile1 = np.sum(vals1, axis=1)
profile2 = np.sum(vals2, axis=1)
profile_diff = profile2 - profile1

print(f"\nFile 1 profile: min={np.min(profile1):.6e}, max={np.max(profile1):.6e}, mean={np.mean(profile1):.6e}")
print(f"File 2 profile: min={np.min(profile2):.6e}, max={np.max(profile2):.6e}, mean={np.mean(profile2):.6e}")
print(f"Difference: min={np.min(profile_diff):.6e}, max={np.max(profile_diff):.6e}, mean={np.mean(profile_diff):.6e}")

# Analyze by region
if hetero_region:
    x_min, x_max = hetero_region
    hetero_mask = (x_centers1 >= x_min) & (x_centers1 <= x_max)
    outside_mask = ~hetero_mask
    
    if np.any(hetero_mask):
        print(f"\nInside hetero region ({x_min}-{x_max} mm):")
        diff_hetero = profile_diff[hetero_mask]
        print(f"  Mean difference: {np.mean(diff_hetero):.6e}")
        print(f"  Std dev: {np.std(diff_hetero):.6e}")
        print(f"  Max |diff|: {np.max(np.abs(diff_hetero)):.6e}")
    
    if np.any(outside_mask):
        print(f"\nOutside hetero region (X < {x_min} or X > {x_max} mm):")
        diff_outside = profile_diff[outside_mask]
        print(f"  Mean difference: {np.mean(diff_outside):.6e}")
        print(f"  Std dev: {np.std(diff_outside):.6e}")
        print(f"  Max |diff|: {np.max(np.abs(diff_outside)):.6e}")

print("\n" + "="*80)
print("INTERPRETATION:")
print("="*80)
print("If these are both HOMOGENEOUS (same material everywhere),")
print("the difference should be close to zero everywhere.")
print("Non-zero differences indicate:")
print("  1. Different materials used (Water vs Lung)")
print("  2. Or different simulation statistics/noise")
print("  3. Or one file actually contains a heterogeneity")
print("="*80 + "\n")

# Create horizontal profile comparison plot
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

x = x_centers1

# Plot 1: Profiles
ax = axes[0]
ax.plot(x, profile1, 'o-', label=file1, linewidth=2, markersize=3, alpha=0.8)
ax.plot(x, profile2, 's-', label=file2, linewidth=2, markersize=3, alpha=0.8)
ax.set_ylabel('Dose (keV)')
ax.set_title('Horizontal Profiles Comparison', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_yscale('log')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red', label='Hetero region (should be empty here)')

# Plot 2: Difference
ax = axes[1]
ax.plot(x, profile_diff, 'o-', linewidth=2, markersize=4, color='purple')
ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.7)
ax.set_ylabel('Difference (keV)')
ax.set_title('Difference Profile (File2 - File1)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, which='both')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red')

# Plot 3: Ratio
profile1_safe = np.where(profile1 > 0, profile1, np.nan)
ratio = profile2 / profile1_safe
valid_mask = ~np.isnan(ratio)
ax = axes[2]
ax.plot(x[valid_mask], ratio[valid_mask], 'o-', linewidth=2, markersize=4, color='green')
ax.axhline(1.0, color='black', linestyle='--', linewidth=1, alpha=0.7, label='Ratio = 1.0 (identical)')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Ratio (File2 / File1)')
ax.set_title('Dose Ratio Profile', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, which='both')
ax.legend()
ax.set_yscale('log')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red')

plt.tight_layout()
plt.savefig("homo_profile_comparison.png", dpi=150, bbox_inches='tight')
print(f"Saved: homo_profile_comparison.png\n")

plt.show()

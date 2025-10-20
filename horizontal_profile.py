#!/usr/bin/env python3
"""
Simple horizontal profile analysis with left/right ratio.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THESE =====
file1 = "brachytherapy_Water_Homo200m.root"   # Homogeneous reference
file2 = "brachytherapy_water_homo_50m.root" # Potentially heterogeneous
hetero_region = (10.0, 70.0)  # (x_min, x_max) in mm
# =======================


def load_histogram(file_path):
    """Load h20;1 histogram from ROOT file."""
    f = uproot.open(file_path)
    h = f["h20;1"]
    vals = h.values()
    x_edges = h.axis(0).edges()
    y_edges = h.axis(1).edges()
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    return vals, x_centers, y_centers


def compute_horizontal_profile(hist_2d, x_centers, y_centers):
    """Compute horizontal dose profile by integrating over Y."""
    profile = np.sum(hist_2d, axis=1)
    return profile, x_centers


# Load histograms
print("Loading histograms...")
vals1, x_centers1, y_centers1 = load_histogram(file1)
vals2, x_centers2, y_centers2 = load_histogram(file2)

# Compute profiles
print("Computing horizontal profiles...")
profile1, x1 = compute_horizontal_profile(vals1, x_centers1, y_centers1)
profile2, x2 = compute_horizontal_profile(vals2, x_centers2, y_centers2)

# Find center index
center_idx = np.argmin(np.abs(x1))
center_x = x1[center_idx]

print(f"\nProfile 1 ({file1}):")
print(f"  Min X: {x1.min():.2f} mm, Max X: {x1.max():.2f} mm")
print(f"  Center X: {center_x:.2f} mm")
print(f"  Min dose: {profile1.min():.6e}, Max dose: {profile1.max():.6e}")

print(f"\nProfile 2 ({file2}):")
print(f"  Min X: {x2.min():.2f} mm, Max X: {x2.max():.2f} mm")
print(f"  Min dose: {profile2.min():.6e}, Max dose: {profile2.max():.6e}")

# Create figure with 2 subplots
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# ===== Plot 1: Both profiles =====
ax = axes[0]
ax.plot(x1, profile1, 'o-', label=file1, linewidth=2, markersize=3, alpha=0.7)
ax.plot(x2, profile2, 's-', label=file2, linewidth=2, markersize=3, alpha=0.7)
ax.axvline(center_x, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Center (X=0)')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red', label=f'Hetero region ({x_min:.0f}-{x_max:.0f} mm)')
ax.set_xlabel('X (mm)', fontsize=12)
ax.set_ylabel('Dose (keV)', fontsize=12)
ax.set_title('Horizontal Dose Profiles', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.set_yscale('log')

# ===== Plot 2: Ratio Profile2 / Profile1 =====
ax = axes[1]
# Avoid division by zero
profile1_safe = np.where(profile1 > 0, profile1, np.nan)
ratio = profile2 / profile1_safe

# Plot ratio only where profile1 is not zero
valid_mask = ~np.isnan(ratio)
ax.plot(x1[valid_mask], ratio[valid_mask], 'o-', linewidth=2, markersize=4, color='purple', label=f'{file2.split("/")[-1]} / {file1.split("/")[-1]}')
ax.axhline(1.0, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Ratio = 1.0 (identical)')
ax.axvline(center_x, color='gray', linestyle='--', linewidth=1, alpha=0.5)
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red', label=f'Hetero region ({x_min:.0f}-{x_max:.0f} mm)')
ax.set_xlabel('X (mm)', fontsize=12)
ax.set_ylabel('Ratio (File2 / File1)', fontsize=12)
ax.set_title('Dose Ratio Profile (left/right analysis)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, which='both')
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig("horizontal_profile_ratio.png", dpi=150, bbox_inches='tight')
print("\nSaved: horizontal_profile_ratio.png")

# Print regional statistics
print("\n" + "="*80)
print("RATIO STATISTICS BY REGION")
print("="*80)

# Left side (X < center)
left_mask = x1 < center_x
if np.any(left_mask):
    left_ratio = ratio[left_mask]
    valid_left = left_ratio[~np.isnan(left_ratio)]
    if len(valid_left) > 0:
        print(f"\nLeft side (X < {center_x:.1f} mm):")
        print(f"  Mean ratio: {np.mean(valid_left):.6f}")
        print(f"  Std dev: {np.std(valid_left):.6f}")
        print(f"  Min: {np.min(valid_left):.6f}, Max: {np.max(valid_left):.6f}")

# Right side (X > center)
right_mask = x1 > center_x
if np.any(right_mask):
    right_ratio = ratio[right_mask]
    valid_right = right_ratio[~np.isnan(right_ratio)]
    if len(valid_right) > 0:
        print(f"\nRight side (X > {center_x:.1f} mm):")
        print(f"  Mean ratio: {np.mean(valid_right):.6f}")
        print(f"  Std dev: {np.std(valid_right):.6f}")
        print(f"  Min: {np.min(valid_right):.6f}, Max: {np.max(valid_right):.6f}")

# Hetero region
if hetero_region:
    x_min, x_max = hetero_region
    hetero_mask = (x1 >= x_min) & (x1 <= x_max)
    if np.any(hetero_mask):
        hetero_ratio = ratio[hetero_mask]
        valid_hetero = hetero_ratio[~np.isnan(hetero_ratio)]
        if len(valid_hetero) > 0:
            print(f"\nHetero region ({x_min:.1f} - {x_max:.1f} mm):")
            print(f"  Mean ratio: {np.mean(valid_hetero):.6f}")
            print(f"  Std dev: {np.std(valid_hetero):.6f}")
            print(f"  Min: {np.min(valid_hetero):.6f}, Max: {np.max(valid_hetero):.6f}")

# Outside hetero region
if hetero_region:
    x_min, x_max = hetero_region
    outside_mask = (x1 < x_min) | (x1 > x_max)
    if np.any(outside_mask):
        outside_ratio = ratio[outside_mask]
        valid_outside = outside_ratio[~np.isnan(outside_ratio)]
        if len(valid_outside) > 0:
            print(f"\nOutside hetero region (X < {x_min:.1f} or X > {x_max:.1f} mm):")
            print(f"  Mean ratio: {np.mean(valid_outside):.6f}")
            print(f"  Std dev: {np.std(valid_outside):.6f}")
            print(f"  Min: {np.min(valid_outside):.6f}, Max: {np.max(valid_outside):.6f}")

print("="*80 + "\n")

plt.show()

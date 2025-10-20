#!/usr/bin/env python3
"""
Analyze horizontal profile symmetry for a SINGLE file.
Plots the full profile and computes ratio of right side / left side (mirrored).
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THIS =====
file_path = "brachytherapy_Water_Homo200m.root"
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


# Load histogram
print(f"Loading histogram from: {file_path}")
vals, x_centers, y_centers = load_histogram(file_path)

# Compute profile
print("Computing horizontal profile...")
profile, x = compute_horizontal_profile(vals, x_centers, y_centers)

# Find center (X=0)
center_idx = np.argmin(np.abs(x))
center_x = x[center_idx]

print(f"\nProfile Statistics:")
print(f"  X range: {x.min():.2f} to {x.max():.2f} mm")
print(f"  Center at X = {center_x:.2f} mm (index {center_idx})")
print(f"  Dose range: {profile.min():.6e} to {profile.max():.6e} keV")

# Split into left (X < center) and right (X > center)
left_mask = x < center_x
right_mask = x > center_x

left_x = x[left_mask]
left_profile = profile[left_mask]
right_x = x[right_mask]
right_profile = profile[right_mask]

print(f"\nLeft side (X < {center_x:.2f}):")
print(f"  Points: {len(left_x)}")
print(f"  X range: {left_x.min():.2f} to {left_x.max():.2f} mm")

print(f"\nRight side (X > {center_x:.2f}):")
print(f"  Points: {len(right_x)}")
print(f"  X range: {right_x.min():.2f} to {right_x.max():.2f} mm")

# Mirror left side to compare with right
# Reverse left profile and x coordinates
left_profile_mirrored = left_profile[::-1]
left_x_mirrored = -left_x[::-1]

# Make same length for comparison
min_len = min(len(left_profile_mirrored), len(right_profile))
left_profile_mirrored = left_profile_mirrored[-min_len:]
left_x_mirrored = left_x_mirrored[-min_len:]
right_profile = right_profile[:min_len]
right_x = right_x[:min_len]

# Compute ratio (right / left_mirrored)
left_safe = np.where(left_profile_mirrored > 0, left_profile_mirrored, np.nan)
ratio = right_profile / left_safe

# Create figure with 3 subplots
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# ===== Plot 1: Full horizontal profile =====
ax = axes[0]
ax.plot(x, profile, 'o-', linewidth=2, markersize=3, label='Full profile', color='blue', alpha=0.8)
ax.axvline(center_x, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Center (X={center_x:.1f} mm)')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red', label=f'Hetero region ({x_min:.0f}-{x_max:.0f} mm)')
ax.set_xlabel('X (mm)', fontsize=12)
ax.set_ylabel('Dose (keV)', fontsize=12)
ax.set_title(f'Horizontal Dose Profile: {file_path}', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.set_yscale('log')

# ===== Plot 2: Left vs Right (mirrored) =====
ax = axes[1]
x_index = np.arange(min_len)
ax.plot(x_index, left_profile_mirrored, 'o-', linewidth=2, markersize=4, label='Left side (mirrored)', alpha=0.8, color='green')
ax.plot(x_index, right_profile, 's-', linewidth=2, markersize=4, label='Right side', alpha=0.8, color='orange')
ax.set_xlabel('Position index (from center outward)', fontsize=12)
ax.set_ylabel('Dose (keV)', fontsize=12)
ax.set_title('Left (Mirrored) vs Right Side Comparison', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.set_yscale('log')

# ===== Plot 3: Ratio Right / Left (mirrored) =====
ax = axes[2]
valid_mask = ~np.isnan(ratio)
ax.plot(x_index[valid_mask], ratio[valid_mask], 'o-', linewidth=2, markersize=4, 
        label='Right / Left (mirrored)', color='purple', alpha=0.8)
ax.axhline(1.0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Ratio = 1.0 (perfect symmetry)')
ax.set_xlabel('Position index (from center outward)', fontsize=12)
ax.set_ylabel('Ratio (Right / Left)', fontsize=12)
ax.set_title('Asymmetry Profile (Right/Left Ratio)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, which='both')
ax.legend(fontsize=10)
ax.set_yscale('log')

plt.tight_layout()
plt.savefig("profile_symmetry.png", dpi=150, bbox_inches='tight')
print(f"\nSaved: profile_symmetry.png")

# Print statistics
print("\n" + "="*80)
print("SYMMETRY STATISTICS")
print("="*80)

valid_ratio = ratio[valid_mask]
if len(valid_ratio) > 0:
    print(f"\nRatio statistics (Right / Left mirrored):")
    print(f"  Mean: {np.mean(valid_ratio):.6f}")
    print(f"  Median: {np.median(valid_ratio):.6f}")
    print(f"  Std dev: {np.std(valid_ratio):.6f}")
    print(f"  Min: {np.min(valid_ratio):.6f}")
    print(f"  Max: {np.max(valid_ratio):.6f}")
    
    # Deviation from perfect symmetry
    deviation = np.abs(np.log10(valid_ratio))  # Log-space deviation
    print(f"\n  Log-space deviation from symmetry (|log10(ratio)|):")
    print(f"    Mean: {np.mean(deviation):.6f}")
    print(f"    Median: {np.median(deviation):.6f}")
    print(f"    Max: {np.max(deviation):.6f}")

print("\n" + "="*80 + "\n")

plt.show()

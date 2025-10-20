#!/usr/bin/env python3
"""
Compare SAME material with and without heterogeneity.
This shows the PURE effect of heterogeneity on dose distribution.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THESE =====
file_homo = "brachytherapy_bone_homo50m.root"   # Same material, NO hetero
file_hetero = "brachytherapy_bone_hetero50m.root" # SAME material, WITH hetero
hetero_region = (10.0, 70.0)  # (x_min, x_max) in mm where hetero IS placed
material_name = "Bone"
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


print(f"Comparing {material_name} Homo vs Hetero effects\n")
print("Loading histograms...")
vals_homo, x_centers, y_centers = load_histogram(file_homo)
vals_hetero, _, _ = load_histogram(file_hetero)

# Subtract (Hetero - Homo shows the EFFECT of heterogeneity)
print("\nSubtracting: Hetero - Homo (to see heterogeneity effect)")
difference = vals_hetero - vals_homo

print(f"\nDifference statistics:")
print(f"  Min: {np.min(difference):.6e}")
print(f"  Max: {np.max(difference):.6e}")
print(f"  Mean: {np.mean(difference):.6e}")
print(f"  Total: {np.sum(difference):.6e} keV")

# Create figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# ===== Plot 1: Homo =====
ax = axes[0]
vmax_homo = np.max(np.abs(vals_homo))
im1 = ax.pcolormesh(x_centers, y_centers, vals_homo.T, cmap='viridis', vmax=vmax_homo, shading='auto')
ax.set_title(f'{material_name} Homo (no hetero)', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
if hetero_region:
    x_min, x_max = hetero_region
    rect = plt.Rectangle((x_min, -30), x_max - x_min, 60, linewidth=2, edgecolor='yellow', facecolor='none')
    ax.add_patch(rect)
plt.colorbar(im1, ax=ax, label='EDEP (keV)')

# ===== Plot 2: Hetero =====
ax = axes[1]
vmax_hetero = np.max(np.abs(vals_hetero))
im2 = ax.pcolormesh(x_centers, y_centers, vals_hetero.T, cmap='viridis', vmax=vmax_hetero, shading='auto')
ax.set_title(f'{material_name} Hetero (WITH hetero)', fontsize=12, fontweight='bold')
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
im_diff = ax.pcolormesh(x_centers, y_centers, difference.T, cmap='RdBu_r', norm=norm, shading='auto')
ax.set_title(f'Heterogeneity Effect\n(Hetero - Homo)', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
if hetero_region:
    x_min, x_max = hetero_region
    rect = plt.Rectangle((x_min, -30), x_max - x_min, 60, linewidth=2, edgecolor='yellow', facecolor='none', label='Hetero placement')
    ax.add_patch(rect)
plt.colorbar(im_diff, ax=ax, label='Difference (keV)')

plt.tight_layout()
plt.savefig(f"{material_name.lower()}_hetero_effect.png", dpi=150, bbox_inches='tight')
print(f"\nSaved: {material_name.lower()}_hetero_effect.png")

# Compute horizontal profiles for more detail
print("\n" + "="*80)
print("HORIZONTAL PROFILE ANALYSIS")
print("="*80)

profile_homo = np.sum(vals_homo, axis=1)
profile_hetero = np.sum(vals_hetero, axis=1)
profile_diff = profile_hetero - profile_homo

print(f"\nHomo profile: min={np.min(profile_homo):.6e}, max={np.max(profile_homo):.6e}, mean={np.mean(profile_homo):.6e}")
print(f"Hetero profile: min={np.min(profile_hetero):.6e}, max={np.max(profile_hetero):.6e}, mean={np.mean(profile_hetero):.6e}")
print(f"Difference: min={np.min(profile_diff):.6e}, max={np.max(profile_diff):.6e}, mean={np.mean(profile_diff):.6e}")

# Analyze by region
if hetero_region:
    x_min, x_max = hetero_region
    hetero_mask = (x_centers >= x_min) & (x_centers <= x_max)
    outside_mask = ~hetero_mask
    
    if np.any(hetero_mask):
        print(f"\nINSIDE hetero region ({x_min}-{x_max} mm):")
        diff_hetero = profile_diff[hetero_mask]
        print(f"  Mean difference: {np.mean(diff_hetero):.6e} keV")
        print(f"  Std dev: {np.std(diff_hetero):.6e} keV")
        print(f"  Max |diff|: {np.max(np.abs(diff_hetero)):.6e} keV")
        print(f"  % change: {100 * np.mean(diff_hetero) / np.mean(profile_homo[hetero_mask]):.2f}%")
    
    if np.any(outside_mask):
        print(f"\nOUTSIDE hetero region (X < {x_min} or X > {x_max} mm):")
        diff_outside = profile_diff[outside_mask]
        print(f"  Mean difference: {np.mean(diff_outside):.6e} keV")
        print(f"  Std dev: {np.std(diff_outside):.6e} keV")
        print(f"  Max |diff|: {np.max(np.abs(diff_outside)):.6e} keV")
        if np.mean(profile_homo[outside_mask]) != 0:
            print(f"  % change: {100 * np.mean(diff_outside) / np.mean(profile_homo[outside_mask]):.2f}%")

print("\n" + "="*80)
print("INTERPRETATION:")
print("="*80)
print(f"If heterogeneity is CORRECTLY placed at X={x_min}-{x_max} mm:")
print(f"  - Inside region: should see LARGE changes (dose modified by hetero)")
print(f"  - Outside region: should see SMALL changes (unaffected by hetero)")
print("="*80 + "\n")

# Create horizontal profile comparison plot
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

x = x_centers

# Plot 1: Profiles
ax = axes[0]
ax.plot(x, profile_homo, 'o-', label=f'{material_name} Homo', linewidth=2, markersize=3, alpha=0.8)
ax.plot(x, profile_hetero, 's-', label=f'{material_name} Hetero', linewidth=2, markersize=3, alpha=0.8)
ax.set_ylabel('Dose (keV)', fontsize=11)
ax.set_title(f'{material_name}: Homo vs Hetero Horizontal Profiles', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.set_yscale('log')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red', label='Hetero region')

# Plot 2: Absolute Difference
ax = axes[1]
ax.plot(x, profile_diff, 'o-', linewidth=2, markersize=4, color='purple', label='Hetero - Homo')
ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.7)
ax.set_ylabel('Difference (keV)', fontsize=11)
ax.set_title('Heterogeneity Effect on Dose', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, which='both')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red')
ax.legend(fontsize=10)

# Plot 3: Relative % Change
profile_homo_safe = np.where(profile_homo > 0, profile_homo, np.nan)
pct_change = 100 * profile_diff / profile_homo_safe
valid_mask = ~np.isnan(pct_change)
ax = axes[2]
ax.plot(x[valid_mask], pct_change[valid_mask], 'o-', linewidth=2, markersize=4, color='green', label='% change')
ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.7)
ax.set_xlabel('X (mm)', fontsize=11)
ax.set_ylabel('% Change [(Hetero - Homo) / Homo × 100]', fontsize=11)
ax.set_title('Relative Change Due to Heterogeneity', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, which='both')
if hetero_region:
    x_min, x_max = hetero_region
    ax.axvspan(x_min, x_max, alpha=0.15, color='red')
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig(f"{material_name.lower()}_hetero_profile.png", dpi=150, bbox_inches='tight')
print(f"Saved: {material_name.lower()}_hetero_profile.png\n")

plt.show()

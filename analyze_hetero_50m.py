#!/usr/bin/env python3
"""
Heterogeneity Analysis at 50m
1. Compare hetero vs homo for each material (water as reference)
2. Compare homo materials against each other
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== FILES =====
# Water reference (homo only)
water_homo = "brachytherapy_water_homo_50m.root"

# Hetero versions (water with different materials)
bone_hetero = "brachytherapy_bone_hetero50m.root"
lung_hetero = "brachytherapy_lung_hetero50m.root"

# Homo versions (pure materials)
bone_homo = "brachytherapy_bone_homo50m.root"
lung_homo = "brachytherapy_Lung_Homo50m.root"

hetero_region = (10.0, 70.0, -30.0, 30.0)  # (x_min, x_max, y_min, y_max) in mm
# ==================


def load_hist(file_path):
    """Load histogram h20;1 from ROOT file."""
    f = uproot.open(file_path)
    h = f["h20;1"]
    vals = h.values()
    x_edges = h.axis(0).edges()
    y_edges = h.axis(1).edges()
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    return vals, x_centers, y_centers


def extract_regions(vals, x_centers, y_centers, hetero_region):
    """Extract inside and outside heterogeneity region."""
    x_min, x_max, y_min, y_max = hetero_region
    
    x_mask = (x_centers >= x_min) & (x_centers <= x_max)
    y_mask = (y_centers >= y_min) & (y_centers <= y_max)
    
    inside = vals[x_mask, :][:, y_mask]
    inside_sum = np.sum(inside)
    outside_sum = np.sum(vals) - inside_sum
    
    return inside_sum, outside_sum


print("\n" + "="*70)
print("HETEROGENEITY ANALYSIS AT 50m")
print("="*70)

# Load all files
print("\nLoading files...")
print(f"  Water Homo: {water_homo}")
water_h, x_c, y_c = load_hist(water_homo)
water_total = np.sum(water_h)
print(f"    Total EDEP: {water_total:.6e} keV\n")

print(f"  Bone Homo: {bone_homo}")
bone_h, _, _ = load_hist(bone_homo)
bone_total = np.sum(bone_h)
print(f"    Total EDEP: {bone_total:.6e} keV")

print(f"  Bone Hetero: {bone_hetero}")
bone_het, _, _ = load_hist(bone_hetero)
bone_het_total = np.sum(bone_het)
print(f"    Total EDEP: {bone_het_total:.6e} keV\n")

print(f"  Lung Homo: {lung_homo}")
lung_h, _, _ = load_hist(lung_homo)
lung_total = np.sum(lung_h)
print(f"    Total EDEP: {lung_total:.6e} keV")

print(f"  Lung Hetero: {lung_hetero}")
lung_het, _, _ = load_hist(lung_hetero)
lung_het_total = np.sum(lung_het)
print(f"    Total EDEP: {lung_het_total:.6e} keV")

# ============================================================
# PART 1: HETERO EFFECT (hetero - homo water)
# ============================================================

print("\n" + "="*70)
print("PART 1: HETEROGENEITY EFFECT (Material Hetero - Water Homo)")
print("="*70)

# Bone hetero effect
print("\nBone Heterogeneity Effect:")
bone_effect = bone_het - water_h
bone_effect_pct = (bone_effect / water_h) * 100.0
print(f"  Difference range: [{np.min(bone_effect):.6e}, {np.max(bone_effect):.6e}] keV")
print(f"  Percentage range: [{np.min(bone_effect_pct):.2f}%, {np.max(bone_effect_pct):.2f}%]")

inside_hetero, outside_hetero = extract_regions(bone_het, x_c, y_c, hetero_region)
inside_water, outside_water = extract_regions(water_h, x_c, y_c, hetero_region)
print(f"  Inside hetero region: {inside_hetero:.6e} vs water {inside_water:.6e} keV")
print(f"    Change: {((inside_hetero - inside_water) / inside_water * 100):.2f}%")
print(f"  Outside hetero region: {outside_hetero:.6e} vs water {outside_water:.6e} keV")
print(f"    Change: {((outside_hetero - outside_water) / outside_water * 100):.2f}%")

# Lung hetero effect
print("\nLung Heterogeneity Effect:")
lung_effect = lung_het - water_h
lung_effect_pct = (lung_effect / water_h) * 100.0
print(f"  Difference range: [{np.min(lung_effect):.6e}, {np.max(lung_effect):.6e}] keV")
print(f"  Percentage range: [{np.min(lung_effect_pct):.2f}%, {np.max(lung_effect_pct):.2f}%]")

inside_hetero_l, outside_hetero_l = extract_regions(lung_het, x_c, y_c, hetero_region)
print(f"  Inside hetero region: {inside_hetero_l:.6e} vs water {inside_water:.6e} keV")
print(f"    Change: {((inside_hetero_l - inside_water) / inside_water * 100):.2f}%")
print(f"  Outside hetero region: {outside_hetero_l:.6e} vs water {outside_water:.6e} keV")
print(f"    Change: {((outside_hetero_l - outside_water) / outside_water * 100):.2f}%")

# ============================================================
# PART 2: HOMO COMPARISON (homo materials vs each other)
# ============================================================

print("\n" + "="*70)
print("PART 2: HOMOGENEOUS MATERIAL COMPARISON")
print("="*70)

# Bone homo vs Water homo
print("\nBone Homo vs Water Homo:")
bone_vs_water = bone_h - water_h
bone_vs_water_pct = (bone_vs_water / water_h) * 100.0
print(f"  Difference range: [{np.min(bone_vs_water):.6e}, {np.max(bone_vs_water):.6e}] keV")
print(f"  Percentage range: [{np.min(bone_vs_water_pct):.2f}%, {np.max(bone_vs_water_pct):.2f}%]")

inside_bone, outside_bone = extract_regions(bone_h, x_c, y_c, hetero_region)
print(f"  Inside region: {inside_bone:.6e} vs water {inside_water:.6e} keV")
print(f"    Change: {((inside_bone - inside_water) / inside_water * 100):.2f}%")
print(f"  Outside region: {outside_bone:.6e} vs water {outside_water:.6e} keV")
print(f"    Change: {((outside_bone - outside_water) / outside_water * 100):.2f}%")

# Lung homo vs Water homo
print("\nLung Homo vs Water Homo:")
lung_vs_water = lung_h - water_h
lung_vs_water_pct = (lung_vs_water / water_h) * 100.0
print(f"  Difference range: [{np.min(lung_vs_water):.6e}, {np.max(lung_vs_water):.6e}] keV")
print(f"  Percentage range: [{np.min(lung_vs_water_pct):.2f}%, {np.max(lung_vs_water_pct):.2f}%]")

inside_lung, outside_lung = extract_regions(lung_h, x_c, y_c, hetero_region)
print(f"  Inside region: {inside_lung:.6e} vs water {inside_water:.6e} keV")
print(f"    Change: {((inside_lung - inside_water) / inside_water * 100):.2f}%")
print(f"  Outside region: {outside_lung:.6e} vs water {outside_water:.6e} keV")
print(f"    Change: {((outside_lung - outside_water) / outside_water * 100):.2f}%")

# Bone homo vs Lung homo
print("\nBone Homo vs Lung Homo:")
bone_vs_lung = bone_h - lung_h
bone_vs_lung_pct = (bone_vs_lung / lung_h) * 100.0
print(f"  Difference range: [{np.min(bone_vs_lung):.6e}, {np.max(bone_vs_lung):.6e}] keV")
print(f"  Percentage range: [{np.min(bone_vs_lung_pct):.2f}%, {np.max(bone_vs_lung_pct):.2f}%]")

print(f"  Inside region: {inside_bone:.6e} vs lung {inside_lung:.6e} keV")
print(f"    Change: {((inside_bone - inside_lung) / inside_lung * 100):.2f}%")
print(f"  Outside region: {outside_bone:.6e} vs lung {outside_lung:.6e} keV")
print(f"    Change: {((outside_bone - outside_lung) / outside_lung * 100):.2f}%")

# ============================================================
# PLOTTING: 2 ROWS x 3 COLUMNS
# Row 1: Hetero Effects (Bone, Lung, and their %)
# Row 2: Homo Comparisons (Bone vs Water, Lung vs Water, Bone vs Lung)
# ============================================================

print("\n" + "="*70)
print("GENERATING VISUALIZATION")
print("="*70)

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

def add_hetero_rect(ax):
    """Add heterogeneity region rectangle."""
    x_min, x_max, y_min, y_max = hetero_region
    rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                         linewidth=2, edgecolor='yellow', facecolor='none', linestyle='--')
    ax.add_patch(rect)

# ROW 1: HETERO EFFECTS
# Column 0: Bone hetero effect (keV)
vmax_bone = np.nanmax(np.abs(bone_effect))
norm_bone = SymLogNorm(linthresh=max(vmax_bone * 0.001, 1.0), vmin=-vmax_bone, vmax=vmax_bone)
im = axes[0, 0].pcolormesh(x_c, y_c, bone_effect.T, cmap='RdBu_r', norm=norm_bone, shading='auto')
axes[0, 0].set_title('Bone Hetero - Water Homo\n(keV)', fontsize=11, fontweight='bold')
axes[0, 0].set_xlabel('X (mm)')
axes[0, 0].set_ylabel('Y (mm)')
plt.colorbar(im, ax=axes[0, 0])
add_hetero_rect(axes[0, 0])

# Column 1: Lung hetero effect (keV)
vmax_lung = np.nanmax(np.abs(lung_effect))
norm_lung = SymLogNorm(linthresh=max(vmax_lung * 0.001, 1.0), vmin=-vmax_lung, vmax=vmax_lung)
im = axes[0, 1].pcolormesh(x_c, y_c, lung_effect.T, cmap='RdBu_r', norm=norm_lung, shading='auto')
axes[0, 1].set_title('Lung Hetero - Water Homo\n(keV)', fontsize=11, fontweight='bold')
axes[0, 1].set_xlabel('X (mm)')
axes[0, 1].set_ylabel('Y (mm)')
plt.colorbar(im, ax=axes[0, 1])
add_hetero_rect(axes[0, 1])

# Column 2: Hetero effects percentage comparison
im = axes[0, 2].pcolormesh(x_c, y_c, lung_effect_pct.T, cmap='RdBu_r', 
                          vmin=-50, vmax=50, shading='auto')
axes[0, 2].set_title('Lung Hetero Effect\n(%)', fontsize=11, fontweight='bold')
axes[0, 2].set_xlabel('X (mm)')
axes[0, 2].set_ylabel('Y (mm)')
plt.colorbar(im, ax=axes[0, 2])
add_hetero_rect(axes[0, 2])

# ROW 2: HOMO COMPARISONS
# Column 0: Bone homo vs Water homo
vmax_bw = np.nanmax(np.abs(bone_vs_water))
norm_bw = SymLogNorm(linthresh=max(vmax_bw * 0.001, 1.0), vmin=-vmax_bw, vmax=vmax_bw)
im = axes[1, 0].pcolormesh(x_c, y_c, bone_vs_water.T, cmap='RdBu_r', norm=norm_bw, shading='auto')
axes[1, 0].set_title('Bone Homo - Water Homo\n(keV)', fontsize=11, fontweight='bold')
axes[1, 0].set_xlabel('X (mm)')
axes[1, 0].set_ylabel('Y (mm)')
plt.colorbar(im, ax=axes[1, 0])
add_hetero_rect(axes[1, 0])

# Column 1: Lung homo vs Water homo
vmax_lw = np.nanmax(np.abs(lung_vs_water))
norm_lw = SymLogNorm(linthresh=max(vmax_lw * 0.001, 1.0), vmin=-vmax_lw, vmax=vmax_lw)
im = axes[1, 1].pcolormesh(x_c, y_c, lung_vs_water.T, cmap='RdBu_r', norm=norm_lw, shading='auto')
axes[1, 1].set_title('Lung Homo - Water Homo\n(keV)', fontsize=11, fontweight='bold')
axes[1, 1].set_xlabel('X (mm)')
axes[1, 1].set_ylabel('Y (mm)')
plt.colorbar(im, ax=axes[1, 1])
add_hetero_rect(axes[1, 1])

# Column 2: Bone homo vs Lung homo
vmax_bl = np.nanmax(np.abs(bone_vs_lung))
norm_bl = SymLogNorm(linthresh=max(vmax_bl * 0.001, 1.0), vmin=-vmax_bl, vmax=vmax_bl)
im = axes[1, 2].pcolormesh(x_c, y_c, bone_vs_lung.T, cmap='RdBu_r', norm=norm_bl, shading='auto')
axes[1, 2].set_title('Bone Homo - Lung Homo\n(keV)', fontsize=11, fontweight='bold')
axes[1, 2].set_xlabel('X (mm)')
axes[1, 2].set_ylabel('Y (mm)')
plt.colorbar(im, ax=axes[1, 2])
add_hetero_rect(axes[1, 2])

plt.tight_layout()
plt.savefig("analyze_hetero_50m.png", dpi=150, bbox_inches='tight')
print("\nSaved: analyze_hetero_50m.png\n")

plt.show()

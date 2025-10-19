#!/usr/bin/env python3
"""
Compare heterogeneity effect across different radiation sources
Different sources = different energy spectra = different interaction cross-sections

Physical basis:
- Low energy (35 keV I-125): Dominated by photoelectric effect (~Z³)
  → Bone (Z~7.64) vs Water (Z~7.42) shows BIG difference
  
- High energy (60-370 keV Ir-192): Mixed Compton + photoelectric
  → Bone vs Water shows SMALLER difference (Compton ~weak Z dependence)
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LogNorm
import os

# Check which simulations exist
sim_dir = "simulation_results"
if not os.path.exists(sim_dir):
    print(f"ERROR: {sim_dir}/ directory not found!")
    print("Run: bash run_source_comparison.sh")
    exit(1)

# Find available ROOT files
available_sims = {}
for fname in os.listdir(sim_dir):
    if fname.endswith('.root'):
        label = fname.replace('.root', '')
        available_sims[label] = os.path.join(sim_dir, fname)

print("=" * 70)
print("AVAILABLE SIMULATIONS:")
print("=" * 70)
for label, path in sorted(available_sims.items()):
    size = os.path.getsize(path) / 1024 / 1024
    print(f"  {label:<30} {size:.1f} MB")

# Helper function to load and convert dose
def load_dose_regional(filepath):
    """Load simulation and convert EDEP to Gy with regional densities"""
    try:
        f = uproot.open(filepath)
        h = f["h20"]
    except:
        print(f"ERROR: Could not open {filepath}")
        return None
    
    values_keV = h.values()
    x_edges = h.axis(0).edges()
    y_edges = h.axis(1).edges()
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    
    # Voxel parameters
    voxel_size_x_mm = x_edges[1] - x_edges[0]
    voxel_size_y_mm = y_edges[1] - y_edges[0]
    voxel_size_z_mm = 10.0
    voxel_volume_cm3 = (voxel_size_x_mm * voxel_size_y_mm * voxel_size_z_mm) / 1000.0
    
    # Heterogeneity region mask
    x_hetero_min, x_hetero_max = 10.0, 70.0
    y_hetero_min, y_hetero_max = -30.0, 30.0
    x_mesh, y_mesh = np.meshgrid(x_centers, y_centers, indexing='ij')
    mask_hetero = ((x_mesh >= x_hetero_min) & (x_mesh <= x_hetero_max) &
                   (y_mesh >= y_hetero_min) & (y_mesh <= y_hetero_max))
    
    # Conversion factors
    keV_to_J = 1.602e-13
    conversion_water = keV_to_J / (voxel_volume_cm3 * 1.0 / 1000.0)
    conversion_bone = keV_to_J / (voxel_volume_cm3 * 1.92 / 1000.0)
    
    # Convert with regional densities
    values_Gy = np.zeros_like(values_keV, dtype=float)
    
    # Try to detect if this is heterogeneity simulation
    # (If bone region has significant dose, it's WITH heterogeneity)
    values_Gy[mask_hetero] = values_keV[mask_hetero] * conversion_bone
    values_Gy[~mask_hetero] = values_keV[~mask_hetero] * conversion_water
    
    return {
        'values': values_Gy,
        'x_centers': x_centers,
        'y_centers': y_centers,
        'mask_hetero': mask_hetero,
        'total_dose': np.sum(values_Gy),
        'dose_hetero_region': np.sum(values_Gy[mask_hetero]),
        'dose_other_region': np.sum(values_Gy[~mask_hetero])
    }

# Analyze each source pair
print("\n" + "=" * 70)
print("HETEROGENEITY EFFECT BY SOURCE")
print("=" * 70)

sources = ['I125', 'Ir192', 'Leipzig']

results = {}

for source in sources:
    homo_key = f"{source}_Homogeneous"
    hetero_key = f"{source}_WithBone"
    
    if homo_key not in available_sims or hetero_key not in available_sims:
        print(f"\nSkipping {source}: incomplete simulation pair")
        continue
    
    print(f"\n{source.upper()} SOURCE:")
    print("-" * 70)
    
    homo = load_dose_regional(available_sims[homo_key])
    hetero = load_dose_regional(available_sims[hetero_key])
    
    if homo is None or hetero is None:
        print(f"  ERROR loading data for {source}")
        continue
    
    total_homo = homo['total_dose']
    total_hetero = hetero['total_dose']
    
    dose_homo_bone = homo['dose_hetero_region']
    dose_hetero_bone = hetero['dose_hetero_region']
    
    print(f"  Total dose - Homogeneous:    {total_homo:.6e} Gy")
    print(f"  Total dose - With Bone:      {total_hetero:.6e} Gy")
    print(f"  Total difference:            {(total_hetero - total_homo):.6e} Gy ({100.0*(total_hetero-total_homo)/total_homo:+.2f}%)")
    
    print(f"\n  IN BONE REGION:")
    print(f"    Homogeneous (equiv water): {dose_homo_bone:.6e} Gy")
    print(f"    With bone heterogeneity:   {dose_hetero_bone:.6e} Gy")
    print(f"    Difference:                {(dose_hetero_bone - dose_homo_bone):.6e} Gy")
    print(f"    Effect:                    {100.0*(dose_hetero_bone - dose_homo_bone)/dose_homo_bone:+.2f}%")
    
    results[source] = {
        'homo': homo,
        'hetero': hetero,
        'total_change_pct': 100.0*(total_hetero - total_homo)/total_homo,
        'bone_region_change_pct': 100.0*(dose_hetero_bone - dose_homo_bone)/dose_homo_bone
    }

# Create comparison figure
if len(results) > 0:
    fig, axes = plt.subplots(len(results), 3, figsize=(16, 5*len(results)))
    
    if len(results) == 1:
        axes = axes.reshape(1, -1)
    
    for idx, (source, data) in enumerate(sorted(results.items())):
        homo = data['homo']
        hetero = data['hetero']
        
        x_centers = homo['x_centers']
        y_centers = homo['y_centers']
        mask_hetero = homo['mask_hetero']
        
        # Difference map
        diff = hetero['values'] - homo['values']
        vmax = max(abs(np.nanmin(diff)), abs(np.nanmax(diff)))
        norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
        
        # Plot 1: Homo dose
        im0 = axes[idx, 0].pcolormesh(x_centers, y_centers, homo['values'].T,
                                      cmap='hot', norm=LogNorm())
        axes[idx, 0].set_title(f'{source.upper()}: Homogeneous Water\n(Total: {homo["total_dose"]:.4e} Gy)',
                              fontsize=12, fontweight='bold')
        axes[idx, 0].set_xlabel('X [mm]')
        axes[idx, 0].set_ylabel('Y [mm]')
        axes[idx, 0].add_patch(plt.Rectangle((10, -30), 60, 60, fill=False,
                                            edgecolor='cyan', linewidth=2, linestyle='--'))
        plt.colorbar(im0, ax=axes[idx, 0], label='Dose [Gy]')
        
        # Plot 2: Hetero dose
        im1 = axes[idx, 1].pcolormesh(x_centers, y_centers, hetero['values'].T,
                                      cmap='hot', norm=LogNorm())
        axes[idx, 1].set_title(f'{source.upper()}: With Bone Heterogeneity\n(Total: {hetero["total_dose"]:.4e} Gy)',
                              fontsize=12, fontweight='bold')
        axes[idx, 1].set_xlabel('X [mm]')
        axes[idx, 1].set_ylabel('Y [mm]')
        axes[idx, 1].add_patch(plt.Rectangle((10, -30), 60, 60, fill=False,
                                            edgecolor='yellow', linewidth=2, linestyle='--'))
        plt.colorbar(im1, ax=axes[idx, 1], label='Dose [Gy]')
        
        # Plot 3: Difference
        im2 = axes[idx, 2].pcolormesh(x_centers, y_centers, diff.T,
                                      cmap='RdBu_r', norm=norm)
        effect = data['bone_region_change_pct']
        axes[idx, 2].set_title(f'{source.upper()}: Difference (Hetero - Homo)\n(Bone region: {effect:+.2f}%)',
                              fontsize=12, fontweight='bold')
        axes[idx, 2].set_xlabel('X [mm]')
        axes[idx, 2].set_ylabel('Y [mm]')
        axes[idx, 2].add_patch(plt.Rectangle((10, -30), 60, 60, fill=False,
                                            edgecolor='black', linewidth=2, linestyle='--'))
        plt.colorbar(im2, ax=axes[idx, 2], label='Difference [Gy]')
    
    plt.tight_layout()
    plt.savefig('dose_comparison_by_source.png', dpi=150, bbox_inches='tight')
    print("\n" + "=" * 70)
    print("Plot saved: dose_comparison_by_source.png")
    print("=" * 70)
    
    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY: HETEROGENEITY EFFECT BY SOURCE")
    print("=" * 70)
    print(f"\n{'Source':<15} {'Total Change':<20} {'Bone Region Effect':<20}")
    print("-" * 70)
    for source in sorted(results.keys()):
        total_change = results[source]['total_change_pct']
        bone_effect = results[source]['bone_region_change_pct']
        print(f"{source.upper():<15} {total_change:+.2f}% {'':>14} {bone_effect:+.2f}%")

print("\nDone!")

#!/usr/bin/env python3
"""
Compare two brachytherapy ROOT files and visualize dose difference
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

# Open ROOT files
file_hetero = uproot.open("brachytherapy_20251019_000420.root")
file_water = uproot.open("brachytherapy_20251019_000633.root")

# Get histograms
h_hetero = file_hetero["h20"]
h_water = file_water["h20"]

# Get bin values
values_hetero = h_hetero.values()
values_water = h_water.values()

# Get bin edges
x_edges = h_hetero.axis(0).edges()
y_edges = h_hetero.axis(1).edges()

# Calculate centers for plotting
x_centers = (x_edges[:-1] + x_edges[1:]) / 2
y_centers = (y_edges[:-1] + y_edges[1:]) / 2

# Calculate difference and ratio
difference = values_hetero - values_water
ratio = np.divide(values_hetero, values_water, 
                  out=np.ones_like(values_hetero), 
                  where=values_water!=0)

# Percent difference
percent_diff = np.divide(100.0 * (values_hetero - values_water), values_water,
                        out=np.zeros_like(values_hetero),
                        where=values_water!=0)

print("=== DOSE COMPARISON STATISTICS ===")
print(f"Hetero total integral: {np.sum(values_hetero):.6e}")
print(f"Water total integral:  {np.sum(values_water):.6e}")
print(f"Difference integral:   {np.sum(difference):.6e}")
print(f"Max difference: {np.max(difference):.2f}")
print(f"Min difference: {np.min(difference):.2f}")
print(f"Mean difference: {np.mean(difference):.2f}")
print(f"Std difference: {np.std(difference):.2f}")

# Create figure with subplots
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Plot 1: Heterogeneity dose map
im1 = axes[0, 0].pcolormesh(x_centers, y_centers, values_hetero.T, 
                             cmap='hot', norm=plt.matplotlib.colors.LogNorm())
axes[0, 0].set_title('With Bone Heterogeneity', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('X [mm]')
axes[0, 0].set_ylabel('Y [mm]')
axes[0, 0].axhline(y=40, color='cyan', linestyle='--', linewidth=2, label='Hetero center')
axes[0, 0].axhline(y=10, color='cyan', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 0].axhline(y=70, color='cyan', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 0].legend()
plt.colorbar(im1, ax=axes[0, 0], label='Energy Deposition [MeV]')

# Plot 2: Water only dose map
im2 = axes[0, 1].pcolormesh(x_centers, y_centers, values_water.T, 
                             cmap='hot', norm=plt.matplotlib.colors.LogNorm())
axes[0, 1].set_title('Water Only (Control)', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('X [mm]')
axes[0, 1].set_ylabel('Y [mm]')
plt.colorbar(im2, ax=axes[0, 1], label='Energy Deposition [MeV]')

# Plot 3: Absolute difference (Hetero - Water)
# Use diverging colormap centered at zero
vmax = max(abs(np.min(difference)), abs(np.max(difference)))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
im3 = axes[0, 2].pcolormesh(x_centers, y_centers, difference.T, 
                             cmap='RdBu_r', norm=norm)
axes[0, 2].set_title('Difference (Bone - Water)', fontsize=14, fontweight='bold')
axes[0, 2].set_xlabel('X [mm]')
axes[0, 2].set_ylabel('Y [mm]')
axes[0, 2].axhline(y=40, color='black', linestyle='--', linewidth=2, label='Hetero center')
axes[0, 2].axhline(y=10, color='black', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 2].axhline(y=70, color='black', linestyle=':', linewidth=1, alpha=0.5)
axes[0, 2].legend()
plt.colorbar(im3, ax=axes[0, 2], label='Difference [MeV]')

# Plot 4: Ratio (Hetero / Water)
im4 = axes[1, 0].pcolormesh(x_centers, y_centers, ratio.T, 
                             cmap='RdYlBu_r', vmin=0.5, vmax=1.5)
axes[1, 0].set_title('Ratio (Bone / Water)', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('X [mm]')
axes[1, 0].set_ylabel('Y [mm]')
axes[1, 0].axhline(y=40, color='black', linestyle='--', linewidth=2)
axes[1, 0].axhline(y=10, color='black', linestyle=':', linewidth=1, alpha=0.5)
axes[1, 0].axhline(y=70, color='black', linestyle=':', linewidth=1, alpha=0.5)
plt.colorbar(im4, ax=axes[1, 0], label='Ratio')

# Plot 5: Percent difference
im5 = axes[1, 1].pcolormesh(x_centers, y_centers, percent_diff.T, 
                             cmap='RdBu_r', vmin=-50, vmax=50)
axes[1, 1].set_title('Percent Change', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('X [mm]')
axes[1, 1].set_ylabel('Y [mm]')
axes[1, 1].axhline(y=40, color='black', linestyle='--', linewidth=2)
axes[1, 1].axhline(y=10, color='black', linestyle=':', linewidth=1, alpha=0.5)
axes[1, 1].axhline(y=70, color='black', linestyle=':', linewidth=1, alpha=0.5)
plt.colorbar(im5, ax=axes[1, 1], label='% Change')

# Plot 6: 1D profiles along Y-axis (X=0)
x_bin_center = np.argmin(np.abs(x_centers - 0))
profile_hetero = values_hetero[x_bin_center, :]
profile_water = values_water[x_bin_center, :]
profile_diff = difference[x_bin_center, :]

ax6 = axes[1, 2]
ax6.plot(y_centers, profile_hetero, 'r-', linewidth=2, label='Bone')
ax6.plot(y_centers, profile_water, 'b-', linewidth=2, label='Water')
ax6.set_xlabel('Y [mm]')
ax6.set_ylabel('Energy Deposition [MeV]', color='k')
ax6.set_title('1D Profile at X=0', fontsize=14, fontweight='bold')
ax6.legend(loc='upper right')
ax6.set_yscale('log')
ax6.grid(True, alpha=0.3)
ax6.axvline(x=40, color='gray', linestyle='--', linewidth=2, alpha=0.5)
ax6.axvline(x=10, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax6.axvline(x=70, color='gray', linestyle=':', linewidth=1, alpha=0.5)

# Add difference on secondary y-axis
ax6_twin = ax6.twinx()
ax6_twin.plot(y_centers, profile_diff, 'g-', linewidth=2, alpha=0.7, label='Difference')
ax6_twin.set_ylabel('Difference [MeV]', color='g')
ax6_twin.tick_params(axis='y', labelcolor='g')
ax6_twin.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax6_twin.legend(loc='upper left')

plt.tight_layout()
plt.savefig('dose_comparison_2d.png', dpi=300, bbox_inches='tight')
print("\n==> Plot saved as: dose_comparison_2d.png")
plt.show()

# Additional: zoomed view on heterogeneity region
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))

# Set limits to heterogeneity region
xlim = [-50, 50]
ylim = [-10, 80]

# Find indices
x_mask = (x_centers >= xlim[0]) & (x_centers <= xlim[1])
y_mask = (y_centers >= ylim[0]) & (y_centers <= ylim[1])

# Plot zoomed difference
im1 = axes2[0].pcolormesh(x_centers[x_mask], y_centers[y_mask], 
                          difference[x_mask, :][:, y_mask].T, 
                          cmap='RdBu_r', norm=norm)
axes2[0].set_title('Difference (Zoomed)', fontsize=14, fontweight='bold')
axes2[0].set_xlabel('X [mm]')
axes2[0].set_ylabel('Y [mm]')
axes2[0].axhline(y=40, color='black', linestyle='--', linewidth=2)
axes2[0].add_patch(plt.Rectangle((-30, 10), 60, 60, fill=False, 
                                 edgecolor='yellow', linewidth=2, linestyle='--'))
plt.colorbar(im1, ax=axes2[0], label='Difference [MeV]')

# Plot zoomed ratio
im2 = axes2[1].pcolormesh(x_centers[x_mask], y_centers[y_mask], 
                          ratio[x_mask, :][:, y_mask].T, 
                          cmap='RdYlBu_r', vmin=0.8, vmax=1.5)
axes2[1].set_title('Ratio (Zoomed)', fontsize=14, fontweight='bold')
axes2[1].set_xlabel('X [mm]')
axes2[1].set_ylabel('Y [mm]')
axes2[1].axhline(y=40, color='black', linestyle='--', linewidth=2)
axes2[1].add_patch(plt.Rectangle((-30, 10), 60, 60, fill=False, 
                                 edgecolor='yellow', linewidth=2, linestyle='--'))
plt.colorbar(im2, ax=axes2[1], label='Ratio')

# Plot zoomed percent change
im3 = axes2[2].pcolormesh(x_centers[x_mask], y_centers[y_mask], 
                          percent_diff[x_mask, :][:, y_mask].T, 
                          cmap='RdBu_r', vmin=-50, vmax=100)
axes2[2].set_title('Percent Change (Zoomed)', fontsize=14, fontweight='bold')
axes2[2].set_xlabel('X [mm]')
axes2[2].set_ylabel('Y [mm]')
axes2[2].axhline(y=40, color='black', linestyle='--', linewidth=2)
axes2[2].add_patch(plt.Rectangle((-30, 10), 60, 60, fill=False, 
                                 edgecolor='yellow', linewidth=2, linestyle='--'))
plt.colorbar(im3, ax=axes2[2], label='% Change')

plt.tight_layout()
plt.savefig('dose_comparison_2d_zoomed.png', dpi=300, bbox_inches='tight')
print("==> Zoomed plot saved as: dose_comparison_2d_zoomed.png")
plt.show()

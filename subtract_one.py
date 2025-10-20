#!/usr/bin/env python3
"""
Compare two groups of file pairs in side-by-side panels.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THESE =====
# Pair A (left panel)
file1_a = "brachytherapy_Lung_Hetero200m.root"
file2_a = "brachytherapy_Bone_Hetero200m.root"
title_a = "Lung_Hetero200m - Bone_Hetero200m"

# Pair B (right panel)
file1_b = "brachytherapy_lung_hetero50m.root"
file2_b = "brachytherapy_bone_hetero50m.root"
title_b = "lung_hetero50m - bone_hetero50m"

hetero_region = (10.0, 70.0, -30.0, 30.0)  # (x_min, x_max, y_min, y_max) in mm
# =======================

def load_hist(file_path):
    """Load histogram h20;1 from ROOT file."""
    print(f"  Loading: {file_path}")
    f = uproot.open(file_path)
    h = f["h20;1"]
    vals = h.values()
    x_edges = h.axis(0).edges()
    y_edges = h.axis(1).edges()
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    print(f"    Total: {np.sum(vals):.6e} keV")
    return vals, x_centers, y_centers


# Load first pair
print("\nPair A:")
vals1_a, x_centers, y_centers = load_hist(file1_a)
vals2_a, _, _ = load_hist(file2_a)
diff_a = vals1_a - vals2_a

print(f"  Difference range: [{np.min(diff_a):.6e}, {np.max(diff_a):.6e}] keV")

# Load second pair
print("\nPair B:")
vals1_b, _, _ = load_hist(file1_b)
vals2_b, _, _ = load_hist(file2_b)
diff_b = vals1_b - vals2_b

print(f"  Difference range: [{np.min(diff_b):.6e}, {np.max(diff_b):.6e}] keV")

# Compute shared colorbar range (independent per panel is better, but let's compute max for ref)
vmax_a = np.nanmax(np.abs(diff_a))
vmax_b = np.nanmax(np.abs(diff_b))

print(f"\nColor scales:")
print(f"  Pair A: vmax={vmax_a:.6e}")
print(f"  Pair B: vmax={vmax_b:.6e}")

# Create plot with 2 panels
print("\nPlotting...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Panel A
norm_a = SymLogNorm(linthresh=max(vmax_a * 0.001, 1.0), vmin=-vmax_a, vmax=vmax_a)
im1 = ax1.pcolormesh(x_centers, y_centers, diff_a.T, cmap='RdBu_r', norm=norm_a, shading='auto')
ax1.set_title(title_a, fontsize=12, fontweight='bold')
ax1.set_xlabel('X (mm)', fontsize=11)
ax1.set_ylabel('Y (mm)', fontsize=11)
cbar1 = plt.colorbar(im1, ax=ax1, label='Difference (keV)')

# Draw hetero rectangle on panel A
if hetero_region is not None:
    x_min, x_max, y_min, y_max = hetero_region
    rect1 = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                          linewidth=2, edgecolor='yellow', facecolor='none', label='Hetero region')
    ax1.add_patch(rect1)
    ax1.legend(loc='upper right')

# Panel B
norm_b = SymLogNorm(linthresh=max(vmax_b * 0.001, 1.0), vmin=-vmax_b, vmax=vmax_b)
im2 = ax2.pcolormesh(x_centers, y_centers, diff_b.T, cmap='RdBu_r', norm=norm_b, shading='auto')
ax2.set_title(title_b, fontsize=12, fontweight='bold')
ax2.set_xlabel('X (mm)', fontsize=11)
ax2.set_ylabel('Y (mm)', fontsize=11)
cbar2 = plt.colorbar(im2, ax=ax2, label='Difference (keV)')

# Draw hetero rectangle on panel B
if hetero_region is not None:
    x_min, x_max, y_min, y_max = hetero_region
    rect2 = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                          linewidth=2, edgecolor='yellow', facecolor='none', label='Hetero region')
    ax2.add_patch(rect2)
    ax2.legend(loc='upper right')

# Interactive cursor for both panels
def on_move_a(event):
    """Show value at cursor position in panel A."""
    if event.inaxes != ax1:
        return
    x, y = event.xdata, event.ydata
    if x is None or y is None:
        return
    ix = np.argmin(np.abs(x_centers - x))
    iy = np.argmin(np.abs(y_centers - y))
    value = diff_a[ix, iy]
    ax1.set_title(f"{title_a}\nX={x:.1f}mm, Y={y:.1f}mm → {value:.3e} keV", fontsize=12, fontweight='bold')
    fig.canvas.draw_idle()

def on_move_b(event):
    """Show value at cursor position in panel B."""
    if event.inaxes != ax2:
        return
    x, y = event.xdata, event.ydata
    if x is None or y is None:
        return
    ix = np.argmin(np.abs(x_centers - x))
    iy = np.argmin(np.abs(y_centers - y))
    value = diff_b[ix, iy]
    ax2.set_title(f"{title_b}\nX={x:.1f}mm, Y={y:.1f}mm → {value:.3e} keV", fontsize=12, fontweight='bold')
    fig.canvas.draw_idle()

fig.canvas.mpl_connect('motion_notify_event', on_move_a)
fig.canvas.mpl_connect('motion_notify_event', on_move_b)

plt.tight_layout()
plt.savefig("subtract_two_pairs.png", dpi=150, bbox_inches='tight')
print("Saved: subtract_two_pairs.png\n")

plt.show()


#!/usr/bin/env python3
"""
Simple script to subtract two 2D histograms from ROOT files.
No conversion, no regional analysis, just simple subtraction.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import os

os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THESE =====
# Pair A: fileA1 - fileA2
fileA1 = "brachytherapy_Lung_Homo_200m.root"
fileA2 = "brachytherapy_Water_Homo.root"
titleA = "Lung_Homo_200m - Water_Homo"

# Pair B: fileB1 - fileB2 (can be same as A or different)
fileB1 = "brachytherapy_Water_Homo.root"
fileB2 = "brachytherapy_Lung_Homo_200m.root"
titleB = "Water_Homo - Lung_Homo_200m (inverted)"

# Optionally draw a rectangle marking the heterogeneity region (set to None to skip)
hetero_region = (10.0, 70.0, -30.0, 30.0)  # (x_min, x_max, y_min, y_max) in mm
# =======================


def load_hist(file_path):
    """Load histogram h20;1 from ROOT file."""
    print(f"Loading: {file_path}")
    f = uproot.open(file_path)
    h = f["h20;1"]
    vals = h.values()
    x_edges = h.axis(0).edges()
    y_edges = h.axis(1).edges()
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    print(f"  Shape: {vals.shape}, Total: {np.sum(vals):.6e}")
    return vals, x_centers, y_centers


# Load histograms
print("Loading histograms...\n")
valsA1, x_centers, y_centers = load_hist(fileA1)
valsA2, _, _ = load_hist(fileA2)
valsB1, _, _ = load_hist(fileB1)
valsB2, _, _ = load_hist(fileB2)

print("\nComputing differences...")

# Compute differences
diffA = valsA1 - valsA2
diffB = valsB1 - valsB2

print(f"Pair A: min={np.min(diffA):.6e}, max={np.max(diffA):.6e}")
print(f"Pair B: min={np.min(diffB):.6e}, max={np.max(diffB):.6e}")

# Create norms for each difference separately (NOT shared)
vmaxA = np.nanmax(np.abs(diffA))
vmaxB = np.nanmax(np.abs(diffB))
normA = SymLogNorm(linthresh=max(vmaxA * 0.001, 1.0), vmin=-vmaxA, vmax=vmaxA)
normB = SymLogNorm(linthresh=max(vmaxB * 0.001, 1.0), vmin=-vmaxB, vmax=vmaxB)

print(f"Norm A linthresh: {max(vmaxA * 0.001, 1.0):.6e}")
print(f"Norm B linthresh: {max(vmaxB * 0.001, 1.0):.6e}")

# Create 2-panel plot
fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=True, sharey=True)

print("\nPlotting...")

for ax, diff, norm, title in zip(axes, (diffA, diffB), (normA, normB), (titleA, titleB)):
    im = ax.pcolormesh(x_centers, y_centers, diff.T, cmap='RdBu_r', norm=norm, shading='auto')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('X (mm)', fontsize=11)
    ax.set_ylabel('Y (mm)', fontsize=11)
    # Individual colorbars for each
    plt.colorbar(im, ax=ax, label='Difference (keV)')

# Optionally draw heterogeneity rectangle
if hetero_region is not None:
    x_min, x_max, y_min, y_max = hetero_region
    for ax in axes:
        rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                             linewidth=2, edgecolor='yellow', facecolor='none', label='Hetero region')
        ax.add_patch(rect)


# Interactive cursor showing values for active panel
active_ax_idx = 0

def on_click(event):
    """Switch active panel when user clicks inside an axes."""
    global active_ax_idx
    for i, ax in enumerate(axes):
        if event.inaxes == ax:
            active_ax_idx = i
            fig.suptitle(f"Active panel: {['A', 'B'][active_ax_idx]}", fontsize=11)
            fig.canvas.draw_idle()
            return


def on_move(event):
    """Show value at cursor position."""
    if event.inaxes not in axes:
        return
    x, y = event.xdata, event.ydata
    if x is None or y is None:
        return

    # Find closest bin
    ix = np.argmin(np.abs(x_centers - x))
    iy = np.argmin(np.abs(y_centers - y))

    if event.inaxes == axes[0]:
        value = diffA[ix, iy]
        title = titleA
    else:
        value = diffB[ix, iy]
        title = titleB

    event.inaxes.set_title(f"{title} | X={x:.1f}mm, Y={y:.1f}mm → Value: {value:.3e} keV")
    fig.canvas.draw_idle()


fig.canvas.mpl_connect('motion_notify_event', on_move)
fig.canvas.mpl_connect('button_press_event', on_click)

plt.tight_layout()
plt.savefig("subtract_simple.png", dpi=150, bbox_inches='tight')
print("Saved: subtract_simple.png\n")

plt.show()

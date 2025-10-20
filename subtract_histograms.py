#!/usr/bin/env python3
"""
Simple script to subtract two 2D histograms from ROOT files
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm

# ===== MODIFY THESE =====
# Declare two pairs of files to subtract. Each pair will be shown in one panel.
# Pair A: fileA1 - fileA2
# Pair B: fileB1 - fileB2
fileA1 = "brachytherapy_bone_hetero50m.root"
fileA2 = "brachytherapy_water_homo_50m.root"
titleA = "A: Bone_Hetero - Water_Homo"

fileB1 = "brachytherapy_Lung_Homo_200m.root"
fileB2 = "brachytherapy_Water_Homo200m.root"
titleB = "B: Lung_Hetero - Bone_Hetero"

# Optionally draw a rectangle marking the heterogeneity region (set to None to skip)
# Format: (x_min, x_max, y_min, y_max) in the same units as the histogram axes (mm)
hetero_region = (10.0, 70.0, -30.0, 30.0)
# =======================

# Open files and get histograms
def load_hist(file_path):
    f = uproot.open(file_path)
    h = f["h20;1"]
    vals = h.values()
    x_edges = h.axis(0).edges()
    y_edges = h.axis(1).edges()
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    return vals, x_centers, y_centers


# Load both pairs
valsA1, x_centers, y_centers = load_hist(fileA1)
valsA2, _, _ = load_hist(fileA2)
valsB1, _, _ = load_hist(fileB1)
valsB2, _, _ = load_hist(fileB2)

# Compute differences
diffA = valsA1 - valsA2
diffB = valsB1 - valsB2

# Shared colormap limits based on max abs value across both diffs
vmax = max(np.nanmax(np.abs(diffA)), np.nanmax(np.abs(diffB)))
norm = SymLogNorm(linthresh=1.0, vmin=-vmax, vmax=vmax)

# Create 2-panel plot
fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=True, sharey=True)
ims = []
for ax, diff, title in zip(axes, (diffA, diffB), (titleA, titleB)):
    im = ax.pcolormesh(x_centers, y_centers, diff.T, cmap='RdBu_r', norm=norm, shading='auto')
    ax.set_title(title)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ims.append(im)

# Single colorbar for both
#cbar = fig.colorbar(ims[0], ax=axes.ravel().tolist(), label='Difference (keV) - SymLog')

# Optionally draw heterogeneity rectangle
if hetero_region is not None:
    x_min, x_max, y_min, y_max = hetero_region
    for ax in axes:
        rect = plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                             linewidth=2, edgecolor='yellow', facecolor='none')
        ax.add_patch(rect)


# Interactive cursor showing values for active panel
active_ax_idx = 0

def on_click(event):
    # Switch active panel when user clicks inside an axes
    global active_ax_idx
    for i, ax in enumerate(axes):
        if event.inaxes == ax:
            active_ax_idx = i
            fig.suptitle(f"Active panel: {['A', 'B'][active_ax_idx]}")
            fig.canvas.draw_idle()
            return


def on_move(event):
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
        panel = 'A'
        title = titleA
    else:
        value = diffB[ix, iy]
        panel = 'B'
        title = titleB

    event.inaxes.set_title(f"{title} | X={x:.1f}mm, Y={y:.1f}mm → Value: {value:.3e} keV")
    fig.canvas.draw_idle()


fig.canvas.mpl_connect('motion_notify_event', on_move)
fig.canvas.mpl_connect('button_press_event', on_click)

plt.tight_layout()
plt.show()

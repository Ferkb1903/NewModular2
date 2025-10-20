#!/usr/bin/env python3
"""
Analyze horizontal profile symmetry to detect heterogeneities.
Compares left vs right sides of the X-profile to find asymmetries
that indicate the presence of heterogeneous inclusions.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

# Change to workspace directory
os.chdir("/home/fer/fer/newbrachy")

# ===== MODIFY THESE =====
file1 = "brachytherapy_water_homo_50m.root"   # Homogeneous reference
file2 = "brachytherapy_bone_hetero50m.root" # Potentially heterogeneous
hetero_region = (10.0, 70.0)  # (x_min, x_max) in mm for heterogeneity

# Analysis parameters
symmetry_threshold = 0.15  # Flag asymmetry if abs(ratio_left - ratio_right) > threshold
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
    """
    Compute horizontal dose profile by integrating over Y (voxel-wise).
    Returns profile (1D array) and x_centers.
    """
    # Integrate histogram over Y axis (sum across rows)
    profile = np.sum(hist_2d, axis=1)
    return profile, x_centers


def analyze_symmetry(profile, x_centers, hetero_region=None):
    """
    Analyze symmetry of horizontal profile.
    
    Returns dict with:
    - center_x: center position (X=0 in histogram coords)
    - left_profile, right_profile: profiles for X<0 and X>0
    - left_mean, right_mean: mean values
    - asymmetry_ratio: abs(left_mean - right_mean) / ((left_mean + right_mean)/2)
    - hetero_region: marked region
    """
    
    # Find center (X=0 in histogram space)
    center_idx = np.argmin(np.abs(x_centers))
    center_x = x_centers[center_idx]
    
    # Split into left (X <= 0) and right (X >= 0)
    left_mask = x_centers <= center_x
    right_mask = x_centers >= center_x
    
    left_profile = profile[left_mask]
    right_profile = profile[right_mask]
    left_x = x_centers[left_mask]
    right_x = x_centers[right_mask]
    
    # Make them same length for comparison (mirror around center)
    min_len = min(len(left_profile), len(right_profile))
    left_profile = left_profile[-min_len:]  # Last min_len from left
    right_profile = right_profile[:min_len]  # First min_len from right
    left_x = left_x[-min_len:]
    right_x = right_x[:min_len]
    
    # Compute statistics
    left_mean = np.mean(left_profile)
    right_mean = np.mean(right_profile)
    left_std = np.std(left_profile)
    right_std = np.std(right_profile)
    
    # Asymmetry ratio (relative to average)
    avg_mean = (left_mean + right_mean) / 2.0
    if avg_mean > 0:
        asymmetry_ratio = abs(left_mean - right_mean) / avg_mean
    else:
        asymmetry_ratio = 0.0
    
    # Correlation between left and right
    correlation = np.corrcoef(left_profile, right_profile)[0, 1]
    if np.isnan(correlation):
        correlation = 0.0
    
    # Analyze hetero region specifically
    hetero_stats = None
    if hetero_region:
        x_min, x_max = hetero_region
        # Find indices in hetero region
        hetero_mask = (x_centers >= x_min) & (x_centers <= x_max)
        if np.any(hetero_mask):
            hetero_profile = profile[hetero_mask]
            hetero_x = x_centers[hetero_mask]
            hetero_mean = np.mean(hetero_profile)
            hetero_std = np.std(hetero_profile)
            hetero_stats = {
                "mean": hetero_mean,
                "std": hetero_std,
                "max": np.max(hetero_profile),
                "min": np.min(hetero_profile),
            }
    
    return {
        "center_x": center_x,
        "left_profile": left_profile,
        "right_profile": right_profile,
        "left_x": left_x,
        "right_x": right_x,
        "left_mean": left_mean,
        "right_mean": right_mean,
        "left_std": left_std,
        "right_std": right_std,
        "asymmetry_ratio": asymmetry_ratio,
        "correlation": correlation,
        "hetero_region": hetero_region,
        "hetero_stats": hetero_stats,
    }


def plot_symmetry_analysis(file1, file2, analysis1, analysis2, hetero_region):
    """Create a 2x2 subplot figure showing symmetry analysis."""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # --- Plot 1: Profiles (file1 - homogeneous reference) ---
    ax = axes[0, 0]
    profile1 = analysis1["left_profile"]
    x1 = analysis1["left_x"]
    ax.plot(x1, profile1, 'o-', label="File 1 (reference)", linewidth=2, markersize=4)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Dose (keV)")
    ax.set_title(f"{file1}\nAsymmetry: {analysis1['asymmetry_ratio']:.4f}, Corr: {analysis1['correlation']:.4f}")
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # --- Plot 2: Profiles (file2 - potentially heterogeneous) ---
    ax = axes[0, 1]
    profile2 = analysis2["left_profile"]
    x2 = analysis2["left_x"]
    ax.plot(x2, profile2, 's-', label="File 2 (test)", linewidth=2, markersize=4, color='orange')
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Dose (keV)")
    ax.set_title(f"{file2}\nAsymmetry: {analysis2['asymmetry_ratio']:.4f}, Corr: {analysis2['correlation']:.4f}")
    ax.grid(True, alpha=0.3)
    if hetero_region:
        x_min, x_max = hetero_region
        ax.axvspan(x_min, x_max, alpha=0.2, color='red', label=f'Hetero region ({x_min:.0f}-{x_max:.0f} mm)')
        ax.legend()
    
    # --- Plot 3: Left vs Right comparison (file1) ---
    ax = axes[1, 0]
    x_mirror = np.arange(len(profile1))
    ax.plot(x_mirror, profile1, 'o-', label="Left side", linewidth=2, markersize=5, color='blue')
    ax.plot(x_mirror, analysis1["right_profile"], 's--', label="Right side (mirrored)", linewidth=2, markersize=5, color='green')
    ax.set_xlabel("Position index")
    ax.set_ylabel("Dose (keV)")
    ax.set_title(f"File 1: Left vs Right Symmetry\nL-mean={analysis1['left_mean']:.2e}, R-mean={analysis1['right_mean']:.2e}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # --- Plot 4: Left vs Right comparison (file2) ---
    ax = axes[1, 1]
    x_mirror = np.arange(len(profile2))
    ax.plot(x_mirror, profile2, 'o-', label="Left side", linewidth=2, markersize=5, color='blue')
    ax.plot(x_mirror, analysis2["right_profile"], 's--', label="Right side (mirrored)", linewidth=2, markersize=5, color='green')
    ax.set_xlabel("Position index")
    ax.set_ylabel("Dose (keV)")
    ax.set_title(f"File 2: Left vs Right Symmetry\nL-mean={analysis2['left_mean']:.2e}, R-mean={analysis2['right_mean']:.2e}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def print_summary(file1, file2, analysis1, analysis2, threshold):
    """Print text summary of symmetry analysis."""
    print("\n" + "="*80)
    print("HORIZONTAL PROFILE SYMMETRY ANALYSIS")
    print("="*80)
    
    print(f"\nFile 1 (Reference): {file1}")
    print(f"  Asymmetry Ratio: {analysis1['asymmetry_ratio']:.6f}")
    print(f"  Correlation (Left vs Right): {analysis1['correlation']:.6f}")
    print(f"  Left side mean dose: {analysis1['left_mean']:.6e} keV")
    print(f"  Right side mean dose: {analysis1['right_mean']:.6e} keV")
    print(f"  Std Dev (L/R): {analysis1['left_std']:.6e} / {analysis1['right_std']:.6e}")
    if analysis1['hetero_stats']:
        h = analysis1['hetero_stats']
        print(f"  Hetero Region: mean={h['mean']:.6e}, std={h['std']:.6e}, max={h['max']:.6e}, min={h['min']:.6e}")
    
    print(f"\nFile 2 (Test): {file2}")
    print(f"  Asymmetry Ratio: {analysis2['asymmetry_ratio']:.6f}")
    print(f"  Correlation (Left vs Right): {analysis2['correlation']:.6f}")
    print(f"  Left side mean dose: {analysis2['left_mean']:.6e} keV")
    print(f"  Right side mean dose: {analysis2['right_mean']:.6e} keV")
    print(f"  Std Dev (L/R): {analysis2['left_std']:.6e} / {analysis2['right_std']:.6e}")
    if analysis2['hetero_stats']:
        h = analysis2['hetero_stats']
        print(f"  Hetero Region: mean={h['mean']:.6e}, std={h['std']:.6e}, max={h['max']:.6e}, min={h['min']:.6e}")
    
    print(f"\nAsymmetry Threshold: {threshold:.6f}")
    print("-"*80)
    
    if analysis1['asymmetry_ratio'] > threshold:
        print(f"⚠️  FILE 1: ASYMMETRY DETECTED (ratio={analysis1['asymmetry_ratio']:.6f} > {threshold})")
    else:
        print(f"✓ FILE 1: Symmetric (ratio={analysis1['asymmetry_ratio']:.6f} ≤ {threshold})")
    
    if analysis2['asymmetry_ratio'] > threshold:
        print(f"⚠️  FILE 2: ASYMMETRY DETECTED (ratio={analysis2['asymmetry_ratio']:.6f} > {threshold})")
    else:
        print(f"✓ FILE 2: Symmetric (ratio={analysis2['asymmetry_ratio']:.6f} ≤ {threshold})")
    
    print("\nInterpretation:")
    if analysis1['asymmetry_ratio'] < threshold and analysis2['asymmetry_ratio'] > threshold:
        print("→ FILE 2 shows MORE asymmetry than FILE 1: HETEROGENEITY likely present in FILE 2")
    elif analysis2['asymmetry_ratio'] < threshold and analysis1['asymmetry_ratio'] > threshold:
        print("→ FILE 1 shows MORE asymmetry than FILE 2: HETEROGENEITY likely present in FILE 1")
    else:
        print("→ Both files show similar symmetry: Heterogeneity effect might be SUBTLE or ABSENT")
    
    print("\nCorrelation Analysis:")
    print(f"  File 1 L-R correlation: {analysis1['correlation']:.6f} (perfect=1.0, random=0.0)")
    print(f"  File 2 L-R correlation: {analysis2['correlation']:.6f}")
    if analysis1['correlation'] > analysis2['correlation']:
        print(f"  → File 1 is MORE symmetric (higher L-R correlation)")
    else:
        print(f"  → File 2 is MORE symmetric (higher L-R correlation)")
    
    # Regional analysis
    if analysis1['hetero_stats'] and analysis2['hetero_stats']:
        h1 = analysis1['hetero_stats']
        h2 = analysis2['hetero_stats']
        print("\nRegional Analysis (Hetero Zone):")
        print(f"  File 1 hetero region mean: {h1['mean']:.6e} keV")
        print(f"  File 2 hetero region mean: {h2['mean']:.6e} keV")
        if h1['mean'] > 0:
            ratio = h2['mean'] / h1['mean']
            print(f"  Ratio (File2/File1): {ratio:.6f}")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    print("Loading histograms...")
    vals1, x_centers1, y_centers1 = load_histogram(file1)
    vals2, x_centers2, y_centers2 = load_histogram(file2)
    
    print(f"File 1 shape: {vals1.shape}")
    print(f"File 2 shape: {vals2.shape}")
    
    print("\nComputing horizontal profiles...")
    profile1, x1 = compute_horizontal_profile(vals1, x_centers1, y_centers1)
    profile2, x2 = compute_horizontal_profile(vals2, x_centers2, y_centers2)
    
    print("\nAnalyzing symmetry...")
    analysis1 = analyze_symmetry(profile1, x1, hetero_region)
    analysis2 = analyze_symmetry(profile2, x2, hetero_region)
    
    print_summary(file1, file2, analysis1, analysis2, symmetry_threshold)
    
    print("Creating plots...")
    fig = plot_symmetry_analysis(file1, file2, analysis1, analysis2, hetero_region)
    plt.savefig("symmetry_analysis.png", dpi=150, bbox_inches='tight')
    print("Saved: symmetry_analysis.png")
    
    plt.show()

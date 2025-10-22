#!/usr/bin/env python3
"""Resumen inicial de la campaña Ir-192 (200M eventos).
Carga los histogramas h20 (plano Y=0) para agua homogénea y hueso heterogéneo,
convierte edep a Gy considerando la heterogeneidad centrada sobre el eje X,
y produce una figura 2x2 con mapas logarítmicos, diferencia y ratio.
También imprime estadísticas básicas dentro y fuera de la heterogeneidad."""

import os
import matplotlib.colors as colors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import uproot
from typing import Tuple

DATA_DIR = "/home/fer/fer/newbrachy/200M_IR192"
WATER_FILE = "200m_water_homogeneous.root"
BONE_HETERO_FILE = "200m_heterogeneous_bone.root"

HETERO_SIZE_MM = 60.0
HETERO_POS_X_MM = 40.0
HETERO_POS_Y_MM = 0.0

BIN_THICKNESS_MM = 0.125  # espesor axial asociado al mapa 2D
MEV_TO_GY = 1.602e-10

DENSITY_WATER = 1.0
DENSITY_BONE = 1.85


def load_histogram(filepath: str, hist_name: str = "h20") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Devuelve valores y ejes del histograma solicitado."""
    with uproot.open(filepath) as root_file:
        if hist_name not in root_file:
            raise KeyError(f"Histograma {hist_name} no encontrado en {filepath}")
        hist = root_file[hist_name]
        values = hist.values()
        x_edges = hist.axes[0].edges()
        y_edges = hist.axes[1].edges()
        return values, x_edges, y_edges


def bin_centers(edges: np.ndarray) -> np.ndarray:
    return 0.5 * (edges[:-1] + edges[1:])


def heterogeneity_mask(x_centers: np.ndarray, y_centers: np.ndarray) -> np.ndarray:
    """Máscara booleana para la región 60×60 mm centrada en (40, 0) sobre el eje X."""
    x_min = HETERO_POS_X_MM - HETERO_SIZE_MM / 2.0
    x_max = HETERO_POS_X_MM + HETERO_SIZE_MM / 2.0
    y_min = HETERO_POS_Y_MM - HETERO_SIZE_MM / 2.0
    y_max = HETERO_POS_Y_MM + HETERO_SIZE_MM / 2.0

    xx, yy = np.meshgrid(x_centers, y_centers, indexing="ij")
    return (xx >= x_min) & (xx <= x_max) & (yy >= y_min) & (yy <= y_max)


def build_density_map(mask: np.ndarray, inside_density: float, outside_density: float) -> np.ndarray:
    density = np.full(mask.shape, outside_density, dtype=float)
    density[mask] = inside_density
    return density


def edep_to_dose(values: np.ndarray, density_map: np.ndarray, bin_size_mm: float) -> np.ndarray:
    """Convierte edep (MeV) a Gy empleando la densidad local."""
    bin_volume_cm3 = (bin_size_mm / 10.0) ** 2 * (BIN_THICKNESS_MM / 10.0)
    dose = np.zeros_like(values, dtype=float)
    valid = density_map > 0
    dose[valid] = values[valid] * MEV_TO_GY / (bin_volume_cm3 * density_map[valid])
    return dose


def add_hetero_outline(ax: plt.Axes) -> None:
    rect = patches.Rectangle(
        (HETERO_POS_X_MM - HETERO_SIZE_MM / 2.0, HETERO_POS_Y_MM - HETERO_SIZE_MM / 2.0),
        HETERO_SIZE_MM,
        HETERO_SIZE_MM,
        linewidth=1.5,
        edgecolor="white",
        facecolor="none",
        linestyle="--",
    )
    ax.add_patch(rect)


def print_stats(name: str, dose: np.ndarray, mask: np.ndarray) -> None:
    inside = dose[mask]
    outside = dose[~mask]
    inside_positive = inside[inside > 0]
    outside_positive = outside[outside > 0]

    print(f"\n{name}:")
    if inside_positive.size:
        print(f"  Heterogeneidad -> mean {inside_positive.mean():.3e} Gy | max {inside_positive.max():.3e} Gy")
    if outside_positive.size:
        print(f"  Agua exterior -> mean {outside_positive.mean():.3e} Gy | max {outside_positive.max():.3e} Gy")


def main() -> None:
    water_path = os.path.join(DATA_DIR, WATER_FILE)
    bone_path = os.path.join(DATA_DIR, BONE_HETERO_FILE)

    water_values, water_x_edges, water_y_edges = load_histogram(water_path)
    bone_values_raw, bone_x_edges, bone_y_edges = load_histogram(bone_path)

    if bone_values_raw.shape != water_values.shape:
        step_mm = bone_x_edges[1] - bone_x_edges[0]
        start_x = int(round((water_x_edges[0] - bone_x_edges[0]) / step_mm))
        start_y = int(round((water_y_edges[0] - bone_y_edges[0]) / step_mm))
        end_x = start_x + water_values.shape[0]
        end_y = start_y + water_values.shape[1]
        bone_values = bone_values_raw[start_x:end_x, start_y:end_y]
    else:
        bone_values = bone_values_raw

    x_cent = bin_centers(water_x_edges)
    y_cent = bin_centers(water_y_edges)
    mask = heterogeneity_mask(x_cent, y_cent)
    bin_size_mm = water_x_edges[1] - water_x_edges[0]

    water_density = np.full_like(water_values, DENSITY_WATER, dtype=float)
    bone_density = build_density_map(mask, DENSITY_BONE, DENSITY_WATER)

    water_dose = edep_to_dose(water_values, water_density, bin_size_mm)
    bone_dose = edep_to_dose(bone_values, bone_density, bin_size_mm)

    diff_dose = bone_dose - water_dose
    ratio = np.ones_like(bone_dose)
    np.divide(bone_dose, water_dose, out=ratio, where=water_dose > 0)

    print("Resumen estadístico (Ir-192, 200M eventos)")
    print_stats("Water homogéneo", water_dose, mask)
    print_stats("Bone heterogéneo", bone_dose, mask)

    extent = [water_x_edges[0], water_x_edges[-1], water_y_edges[0], water_y_edges[-1]]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Ir-192 200M | Agua vs Hueso (Plano Y=0)", fontsize=16, fontweight="bold")

    # Agua homogénea (log)
    water_plot = water_dose.copy()
    positive_water = water_plot[water_plot > 0]
    if positive_water.size:
        water_plot[water_plot <= 0] = positive_water.min() * 0.1
        im0 = axes[0, 0].imshow(
            water_plot.T,
            origin="lower",
            extent=extent,
            cmap="viridis",
            norm=colors.LogNorm(vmin=positive_water.min() * 0.1, vmax=positive_water.max()),
        )
        plt.colorbar(im0, ax=axes[0, 0], label="Dosis (Gy)")
    axes[0, 0].set_title("Water Homogéneo (log)")
    axes[0, 0].set_xlabel("X (mm)")
    axes[0, 0].set_ylabel("Y (mm)")
    add_hetero_outline(axes[0, 0])

    # Bone heterogéneo (log)
    bone_plot = bone_dose.copy()
    positive_bone = bone_plot[bone_plot > 0]
    if positive_bone.size:
        bone_plot[bone_plot <= 0] = positive_bone.min() * 0.1
        im1 = axes[0, 1].imshow(
            bone_plot.T,
            origin="lower",
            extent=extent,
            cmap="viridis",
            norm=colors.LogNorm(vmin=positive_bone.min() * 0.1, vmax=positive_bone.max()),
        )
        plt.colorbar(im1, ax=axes[0, 1], label="Dosis (Gy)")
    axes[0, 1].set_title("Bone Heterogéneo (log)")
    axes[0, 1].set_xlabel("X (mm)")
    axes[0, 1].set_ylabel("Y (mm)")
    add_hetero_outline(axes[0, 1])

    # Diferencia lineal
    vmax_diff = np.max(np.abs(diff_dose))
    im2 = axes[1, 0].imshow(
        diff_dose.T,
        origin="lower",
        extent=extent,
        cmap="RdBu_r",
        vmin=-vmax_diff,
        vmax=vmax_diff,
    )
    plt.colorbar(im2, ax=axes[1, 0], label="ΔDosis (Gy)")
    axes[1, 0].set_title("Diferencia: Bone - Water")
    axes[1, 0].set_xlabel("X (mm)")
    axes[1, 0].set_ylabel("Y (mm)")
    add_hetero_outline(axes[1, 0])

    # Ratio
    im3 = axes[1, 1].imshow(
        ratio.T,
        origin="lower",
        extent=extent,
        cmap="magma",
        vmin=0.5,
        vmax=1.5,
    )
    plt.colorbar(im3, ax=axes[1, 1], label="Ratio (Bone/Water)")
    axes[1, 1].set_title("Ratio Bone / Water")
    axes[1, 1].set_xlabel("X (mm)")
    axes[1, 1].set_ylabel("Y (mm)")
    add_hetero_outline(axes[1, 1])

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    output_path = os.path.join(DATA_DIR, "ir192_overview_water_vs_bone.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\nFigura guardada en: {output_path}")


if __name__ == "__main__":
    main()


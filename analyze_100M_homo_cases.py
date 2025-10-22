#!/usr/bin/env python3
"""
Análisis de casos homogéneos I-125 100M: Lung MIRD vs Bone vs Water
Layout 2×3: Dosis | Diferencia | Perfil+Ratio
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import uproot

# Constantes
MEV_TO_GY = 1.602e-10
BIN_SIZE_MM = 1.0
BIN_THICKNESS_MM = 0.125

# Densidades (g/cm³)
DENSITIES = {
    "water": 1.0,
    "lung": 0.2958,
    "bone": 1.85,
}

# Mapeo de archivos ROOT
FILE_MAP = {
    "water": "brachytherapy_homo_water100m.root",
    "lung": "brachytherapy_homo_lung100m.root",
    "bone": "brachytherapy_homo_bone100m.root",
}

DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"


def load_histogram(case_name: str) -> np.ndarray:
    """Cargar histogram h20 del archivo ROOT"""
    try:
        filepath = f"{DATA_DIR}/{FILE_MAP[case_name]}"
        with uproot.open(filepath) as file:
            for key_name in file.keys():
                if "h20" in key_name:
                    hist = file[key_name].to_numpy()
                    return hist[0]
    except Exception as e:
        print(f"⚠️ Error cargando {case_name}: {e}")
    return None


def edep_to_dose(edep: np.ndarray, density: float) -> np.ndarray:
    """Convertir energía depositada a dosis en Gy"""
    bin_volume_cm3 = (BIN_SIZE_MM / 10.0) ** 2 * (BIN_THICKNESS_MM / 10.0)
    dose_gy = edep * MEV_TO_GY / (bin_volume_cm3 * density)
    return dose_gy


def get_horizontal_profile(dose_map: np.ndarray) -> tuple:
    """Extraer perfil horizontal en Y=0 (índice central), eliminando ±2mm de la fuente"""
    center_idx = dose_map.shape[1] // 2
    center_x_idx = dose_map.shape[0] // 2
    
    # Eliminar ±2mm alrededor de la fuente (2 bins)
    profile = dose_map[:, center_idx].copy()
    profile[center_x_idx - 2:center_x_idx + 2] = 0  # Marcar como 0 (se ignorará en gráficos)
    
    x_mm = np.linspace(-150, 150, len(profile))
    return x_mm, profile


def get_profile_3bins(dose_map: np.ndarray) -> tuple:
    """Extraer 3 bins centrados en el origen, fuera de ±2mm"""
    center_idx = dose_map.shape[1] // 2
    center_x_idx = dose_map.shape[0] // 2
    
    # 3 bins en -3, -2, +2, +3 (saltando ±2mm) - tomamos +2, +3, +4
    # Mejor: usar bins en -3, 0, +3 para claridad
    bin_left = center_x_idx - 3
    bin_center = center_x_idx
    bin_right = center_x_idx + 3
    
    profile_3bins = np.array([
        dose_map[bin_left, center_idx],
        dose_map[bin_center, center_idx],
        dose_map[bin_right, center_idx]
    ])
    x_pos = np.array([-3, 0, 3])  # posiciones en bins
    
    return x_pos, profile_3bins


def main():
    print("=" * 80)
    print("ANÁLISIS DE CASOS HOMOGÉNEOS - I-125 100M")
    print("=" * 80)
    print()
    
    # Cargar datos
    print("Cargando datos...")
    dose_data = {}
    for case_key in ["water", "lung", "bone"]:
        edep = load_histogram(case_key)
        if edep is None:
            print(f"❌ No se pudo cargar {case_key}")
            return
        dose_data[case_key] = edep_to_dose(edep, DENSITIES[case_key])
        print(f"  {case_key:6s}... ✓ (shape: {dose_data[case_key].shape})")
    
    print()
    
    # Preparar datos
    dose_water = dose_data["water"].copy()
    dose_lung = dose_data["lung"].copy()
    dose_bone = dose_data["bone"].copy()
    
    # Reemplazar ceros para escala log
    vmin_ref = np.min(dose_water[dose_water > 0]) * 0.1
    dose_water[dose_water <= 0] = vmin_ref
    dose_lung[dose_lung <= 0] = vmin_ref
    dose_bone[dose_bone <= 0] = vmin_ref
    
    vmax_water = np.max(dose_water)
    vmax_lung = np.max(dose_lung)
    vmax_bone = np.max(dose_bone)
    
    # Crear figura 2×3
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "Análisis Homogéneo I-125 100M: Lung MIRD vs Bone\n"
        "Plano Y=0 mm | Dosis, Diferencia, Perfil+Ratio (3 bins centrales)",
        fontsize=14,
        fontweight="bold",
        y=0.98
    )
    
    x_mm = np.linspace(-150, 150, dose_lung.shape[0])
    
    # Crear máscaras para eliminar ±2mm de la fuente
    center_x_idx = dose_lung.shape[0] // 2
    mask_source = np.ones(dose_lung.shape, dtype=bool)
    mask_source[center_x_idx - 2:center_x_idx + 2, :] = False  # Eliminar ±2mm en X
    
    # Aplicar máscaras
    dose_lung_masked = dose_lung.copy()
    dose_lung_masked[~mask_source] = vmin_ref
    
    dose_bone_masked = dose_bone.copy()
    dose_bone_masked[~mask_source] = vmin_ref
    
    dose_water_masked = dose_water.copy()
    dose_water_masked[~mask_source] = vmin_ref
    
    # ============================================================================
    # FILA 1: LUNG MIRD
    # ============================================================================
    
    # [0,0] Dosis Lung MIRD
    im1 = axes[0, 0].imshow(
        dose_lung_masked.T,
        aspect="auto",
        origin="lower",
        cmap="viridis",
        norm=colors.LogNorm(vmin=vmin_ref, vmax=vmax_lung),
        extent=[-150, 150, -150, 150]
    )
    axes[0, 0].set_title("Lung MIRD Homogéneo\nDosis (Gy, escala log)", fontweight="bold")
    axes[0, 0].set_xlabel("X (mm)")
    axes[0, 0].set_ylabel("Z (mm)")
    plt.colorbar(im1, ax=axes[0, 0], label="Gy")
    
    # [0,1] Diferencia Lung - Water
    diff_lung = dose_lung_masked - dose_water_masked
    vmax_diff_lung = np.max(np.abs(diff_lung))
    im2 = axes[0, 1].imshow(
        diff_lung.T,
        aspect="auto",
        origin="lower",
        cmap="RdBu_r",
        vmin=-vmax_diff_lung,
        vmax=vmax_diff_lung,
        extent=[-150, 150, -150, 150]
    )
    axes[0, 1].set_title("Lung MIRD - Water\nDiferencia (Gy, lineal)", fontweight="bold")
    axes[0, 1].set_xlabel("X (mm)")
    axes[0, 1].set_ylabel("Z (mm)")
    plt.colorbar(im2, ax=axes[0, 1], label="ΔGy")
    
    # [0,2] Perfil horizontal + Ratio (3 bins)
    x_prof, prof_lung = get_horizontal_profile(dose_lung)
    _, prof_water = get_horizontal_profile(dose_water)
    x_3bins, vals_lung_3bins = get_profile_3bins(dose_lung)
    _, vals_water_3bins = get_profile_3bins(dose_water)
    
    ax2_1 = axes[0, 2]
    ax2_2 = ax2_1.twinx()
    
    # Perfil línea (filtrar ceros de la fuente)
    mask_plot = prof_lung > 0
    line1 = ax2_1.plot(x_prof[mask_plot], prof_lung[mask_plot], "o-", color="orange", linewidth=2, markersize=3, 
                       label="Lung MIRD", alpha=0.7)
    line2 = ax2_1.plot(x_prof[mask_plot], prof_water[mask_plot], "s-", color="blue", linewidth=2, markersize=3, 
                       label="Water", alpha=0.7)
    ax2_1.set_xlabel("X (mm)", fontsize=10)
    ax2_1.set_ylabel("Dosis (Gy)", fontsize=10, color="black")
    ax2_1.tick_params(axis="y", labelcolor="black")
    ax2_1.grid(True, alpha=0.3)
    ax2_1.set_xlim([-150, 150])
    
    # Ratio (3 bins)
    ratio_lung_3bins = np.divide(vals_lung_3bins, vals_water_3bins, 
                                  out=np.ones_like(vals_lung_3bins), 
                                  where=vals_water_3bins > 0)
    line3 = ax2_2.scatter(x_3bins, ratio_lung_3bins, s=200, c="orange", 
                         marker="o", edgecolors="darkorange", linewidths=2, 
                         label="Ratio (3 bins)", zorder=5, alpha=0.8)
    ax2_2.axhline(y=1.0, color="k", linestyle="--", linewidth=1.5, alpha=0.5)
    ax2_2.set_ylabel("Ratio (Lung/Water)", fontsize=10, color="orange")
    ax2_2.tick_params(axis="y", labelcolor="orange")
    ax2_2.set_ylim([0.5, 3.5])
    
    ax2_1.set_title("Perfil Horizontal (Y=0)\n+ Ratio 3 bins", fontweight="bold", fontsize=10)
    lines = line1 + line2 + [line3]
    labels = ["Lung MIRD (perfil)", "Water (perfil)", "Ratio 3bins"]
    ax2_1.legend(lines, labels, loc="upper right", fontsize=9)
    
    # ============================================================================
    # FILA 2: BONE
    # ============================================================================
    
    # [1,0] Dosis Bone
    im3 = axes[1, 0].imshow(
        dose_bone_masked.T,
        aspect="auto",
        origin="lower",
        cmap="viridis",
        norm=colors.LogNorm(vmin=vmin_ref, vmax=vmax_bone),
        extent=[-150, 150, -150, 150]
    )
    axes[1, 0].set_title("Bone Homogéneo\nDosis (Gy, escala log)", fontweight="bold")
    axes[1, 0].set_xlabel("X (mm)")
    axes[1, 0].set_ylabel("Z (mm)")
    plt.colorbar(im3, ax=axes[1, 0], label="Gy")
    
    # [1,1] Diferencia Bone - Water
    diff_bone = dose_bone_masked - dose_water_masked
    vmax_diff_bone = np.max(np.abs(diff_bone))
    im4 = axes[1, 1].imshow(
        diff_bone.T,
        aspect="auto",
        origin="lower",
        cmap="RdBu_r",
        vmin=-vmax_diff_bone,
        vmax=vmax_diff_bone,
        extent=[-150, 150, -150, 150]
    )
    axes[1, 1].set_title("Bone - Water\nDiferencia (Gy, lineal)", fontweight="bold")
    axes[1, 1].set_xlabel("X (mm)")
    axes[1, 1].set_ylabel("Z (mm)")
    plt.colorbar(im4, ax=axes[1, 1], label="ΔGy")
    
    # [1,2] Perfil horizontal + Ratio (3 bins)
    _, prof_bone = get_horizontal_profile(dose_bone)
    _, vals_bone_3bins = get_profile_3bins(dose_bone)
    
    ax3_1 = axes[1, 2]
    ax3_2 = ax3_1.twinx()
    
    # Perfil línea (filtrar ceros de la fuente)
    line1b = ax3_1.plot(x_prof[mask_plot], prof_bone[mask_plot], "o-", color="red", linewidth=2, markersize=3, 
                        label="Bone", alpha=0.7)
    line2b = ax3_1.plot(x_prof[mask_plot], prof_water[mask_plot], "s-", color="blue", linewidth=2, markersize=3, 
                        label="Water", alpha=0.7)
    ax3_1.set_xlabel("X (mm)", fontsize=10)
    ax3_1.set_ylabel("Dosis (Gy)", fontsize=10, color="black")
    ax3_1.tick_params(axis="y", labelcolor="black")
    ax3_1.grid(True, alpha=0.3)
    ax3_1.set_xlim([-150, 150])
    
    # Ratio (3 bins)
    ratio_bone_3bins = np.divide(vals_bone_3bins, vals_water_3bins, 
                                 out=np.ones_like(vals_bone_3bins), 
                                 where=vals_water_3bins > 0)
    line3b = ax3_2.scatter(x_3bins, ratio_bone_3bins, s=200, c="red", 
                          marker="o", edgecolors="darkred", linewidths=2, 
                          label="Ratio (3 bins)", zorder=5, alpha=0.8)
    ax3_2.axhline(y=1.0, color="k", linestyle="--", linewidth=1.5, alpha=0.5)
    ax3_2.set_ylabel("Ratio (Bone/Water)", fontsize=10, color="red")
    ax3_2.tick_params(axis="y", labelcolor="red")
    ax3_2.set_ylim([0.5, 3.5])
    
    ax3_1.set_title("Perfil Horizontal (Y=0)\n+ Ratio 3 bins", fontweight="bold", fontsize=10)
    lines = line1b + line2b + [line3b]
    labels = ["Bone (perfil)", "Water (perfil)", "Ratio 3bins"]
    ax3_1.legend(lines, labels, loc="upper right", fontsize=9)
    
    plt.tight_layout()
    
    # Guardar figura
    output_path = f"{DATA_DIR}/homo_analysis_2x3_complete.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Figura guardada: {output_path}")
    print()
    
    # Estadísticas
    print("=" * 80)
    print("ESTADÍSTICAS (3 BINS CENTRALES)")
    print("=" * 80)
    print()
    print(f"Lung MIRD (3 bins): {vals_lung_3bins}")
    print(f"Water (3 bins):     {vals_water_3bins}")
    print(f"Ratio Lung/Water:   {ratio_lung_3bins}")
    print()
    print(f"Bone (3 bins):      {vals_bone_3bins}")
    print(f"Ratio Bone/Water:   {ratio_bone_3bins}")
    print()


if __name__ == "__main__":
    main()

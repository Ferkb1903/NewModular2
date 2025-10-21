#!/usr/bin/env python3
"""
Resta de Mapas de Dosis Convertida por Secciones
Braquiterapia I125 (200M)
Bone_Hetero - Water_Homo y Lung_Hetero - Water_Homo
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/200M_I125"
HISTOGRAM_NAME = "h20;1"

# Parámetros de heterogeneidad (del macro)
HETERO_SIZE = 60.0  # mm (6.0 cm)
HETERO_POS_X = 40.0  # mm (posición en X)
HETERO_POS_Y = 0.0   # mm (posición en Y)

# Casos de simulación
CASES = {
    "Water_Homo": "brachytherapy_water_homo200m.root",
    "Bone_Hetero": "brachytherapy_Bone_Hetero200m.root",
    "Lung_Hetero": "brachytherapy_Lung_Hetero200m.root"
}

# Densidades base
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 1.05  # 64_LUNG_ICRP

# Tamaño de bins
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

def load_histogram(filepath, hist_name):
    """Carga un histograma 2D de un archivo ROOT"""
    try:
        with uproot.open(filepath) as file:
            if hist_name in file:
                hist = file[hist_name]
                return hist
            else:
                print(f"❌ Histograma {hist_name} no encontrado en {filepath}")
                return None
    except Exception as e:
        print(f"❌ Error abriendo {filepath}: {e}")
        return None

def create_density_map(shape, case_name):
    """
    Crea un mapa de densidad considerando la región de heterogeneidad
    """
    density_map = np.ones(shape, dtype=float) * DENSITY_WATER
    
    if case_name == "Bone_Hetero":
        hetero_density = DENSITY_BONE
    elif case_name == "Lung_Hetero":
        hetero_density = DENSITY_LUNG
    else:  # Water_Homo
        return density_map
    
    # Calcular índices de la región de heterogeneidad
    x_min = HETERO_POS_X - HETERO_SIZE / 2
    x_max = HETERO_POS_X + HETERO_SIZE / 2
    y_min = HETERO_POS_Y - HETERO_SIZE / 2
    y_max = HETERO_POS_Y + HETERO_SIZE / 2
    
    # Convertir de mm a índices de bins
    scale_factor = 300 / 301.0
    offset = -150.5
    
    x_min_bin = int((x_min - offset) * scale_factor)
    x_max_bin = int((x_max - offset) * scale_factor)
    y_min_bin = int((y_min - offset) * scale_factor)
    y_max_bin = int((y_max - offset) * scale_factor)
    
    # Asegurar que están dentro de los límites
    x_min_bin = max(0, min(x_min_bin, shape[0]))
    x_max_bin = max(0, min(x_max_bin, shape[0]))
    y_min_bin = max(0, min(y_min_bin, shape[1]))
    y_max_bin = max(0, min(y_max_bin, shape[1]))
    
    # Aplicar densidad de heterogeneidad
    density_map[x_min_bin:x_max_bin, y_min_bin:y_max_bin] = hetero_density
    
    return density_map

def edep_to_dose_sectional(edep_values, case_name):
    """
    Convierte edep a dosis por secciones
    Aplica densidades diferentes dentro y fuera de la heterogeneidad
    """
    density_map = create_density_map(edep_values.shape, case_name)
    
    # Evitar división por cero
    density_map[density_map == 0] = DENSITY_WATER
    
    # Convertir: Dosis (mGy) = edep * 1.602e-4 / (volumen * densidad)
    dose_mgy = edep_values * 1.602e-4 / (BIN_VOLUME * density_map)
    
    return dose_mgy

def draw_heterogeneity(ax):
    """Dibuja un rectángulo que marca la región de heterogeneidad"""
    x_min = HETERO_POS_X - HETERO_SIZE / 2
    x_max = HETERO_POS_X + HETERO_SIZE / 2
    y_min = HETERO_POS_Y - HETERO_SIZE / 2
    y_max = HETERO_POS_Y + HETERO_SIZE / 2
    
    scale_factor = 300 / 301.0
    
    x_min_bin = (x_min - (-150.5)) * scale_factor
    x_max_bin = (x_max - (-150.5)) * scale_factor
    y_min_bin = (y_min - (-150.5)) * scale_factor
    y_max_bin = (y_max - (-150.5)) * scale_factor
    
    rect = patches.Rectangle(
        (x_min_bin, y_min_bin),
        x_max_bin - x_min_bin,
        y_max_bin - y_min_bin,
        linewidth=1.5,
        edgecolor='white',
        facecolor='none',
        linestyle='--'
    )
    ax.add_patch(rect)

def plot_dose_difference():
    """Crea visualización de diferencias de dosis convertida"""
    
    fig = plt.figure(figsize=(14, 5))
    
    # Cargar todos los histogramas
    histograms = {}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Procesando: {case_name}...", end=" ")
        
        hist = load_histogram(filepath, HISTOGRAM_NAME)
        if hist is None:
            print("❌ Error")
            continue
        
        histograms[case_name] = hist.values()
        print("✅")
    
    # Convertir a dosis por secciones
    print("\nConvirtiendo a dosis...", end=" ")
    dose_water = edep_to_dose_sectional(histograms["Water_Homo"], "Water_Homo")
    dose_bone = edep_to_dose_sectional(histograms["Bone_Hetero"], "Bone_Hetero")
    dose_lung = edep_to_dose_sectional(histograms["Lung_Hetero"], "Lung_Hetero")
    print("✅")
    
    # Calcular diferencias
    diff_bone = dose_bone - dose_water
    diff_lung = dose_lung - dose_water
    
    # Fila: Diferencias
    # Resta 1: Bone_Hetero - Water_Homo
    ax_bone = plt.subplot(1, 2, 1)
    
    im_bone = ax_bone.imshow(
        diff_bone.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=colors.SymLogNorm(linthresh=1e2, vmin=diff_bone.min(), vmax=diff_bone.max())
    )
    
    ax_bone.set_title('Bone_Hetero - Water_Homo\n(SymLog)', fontsize=12, fontweight='bold')
    ax_bone.set_xlabel('X (bins)')
    ax_bone.set_ylabel('Y (bins)')
    plt.colorbar(im_bone, ax=ax_bone, label='Diferencia (mGy)')
    draw_heterogeneity(ax_bone)
    
    # Resta 2: Lung_Hetero - Water_Homo
    ax_lung = plt.subplot(1, 2, 2)
    
    im_lung = ax_lung.imshow(
        diff_lung.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=colors.SymLogNorm(linthresh=1e2, vmin=diff_lung.min(), vmax=diff_lung.max())
    )
    
    ax_lung.set_title('Lung_Hetero - Water_Homo\n(SymLog)', fontsize=12, fontweight='bold')
    ax_lung.set_xlabel('X (bins)')
    ax_lung.set_ylabel('Y (bins)')
    plt.colorbar(im_lung, ax=ax_lung, label='Diferencia (mGy)')
    draw_heterogeneity(ax_lung)
    
    plt.suptitle('Diferencias de Dosis Convertida - I125 200M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '2D_dose_difference_sectional.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    
    # Estadísticas de diferencias
    print("\n" + "="*70)
    print("ESTADÍSTICAS DE DIFERENCIAS DE DOSIS")
    print("="*70)
    
    print("\nBone_Hetero - Water_Homo:")
    print(f"  Diferencia mínima:  {np.min(diff_bone):.6e} mGy")
    print(f"  Diferencia máxima:  {np.max(diff_bone):.6e} mGy")
    print(f"  Diferencia media:   {np.mean(diff_bone):.6e} mGy")
    print(f"  Desv. estándar:     {np.std(diff_bone):.6e} mGy")
    
    diff_bone_pos = diff_bone[diff_bone > 0]
    diff_bone_neg = diff_bone[diff_bone < 0]
    if len(diff_bone_pos) > 0:
        print(f"  Diferencia media (positiva): {np.mean(diff_bone_pos):.6e} mGy")
    if len(diff_bone_neg) > 0:
        print(f"  Diferencia media (negativa): {np.mean(diff_bone_neg):.6e} mGy")
    
    print("\nLung_Hetero - Water_Homo:")
    print(f"  Diferencia mínima:  {np.min(diff_lung):.6e} mGy")
    print(f"  Diferencia máxima:  {np.max(diff_lung):.6e} mGy")
    print(f"  Diferencia media:   {np.mean(diff_lung):.6e} mGy")
    print(f"  Desv. estándar:     {np.std(diff_lung):.6e} mGy")
    
    diff_lung_pos = diff_lung[diff_lung > 0]
    diff_lung_neg = diff_lung[diff_lung < 0]
    if len(diff_lung_pos) > 0:
        print(f"  Diferencia media (positiva): {np.mean(diff_lung_pos):.6e} mGy")
    if len(diff_lung_neg) > 0:
        print(f"  Diferencia media (negativa): {np.mean(diff_lung_neg):.6e} mGy")
    
    print("="*70 + "\n")
    plt.show()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("RESTA DE MAPAS DE DOSIS CONVERTIDA - I125 200M")
    print("="*70 + "\n")
    plot_dose_difference()

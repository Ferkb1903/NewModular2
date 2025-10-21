#!/usr/bin/env python3
"""
Visualización y Resta de Mapas de Dosis Convertida por Secciones
Braquiterapia I125 (200M)
Rango limitado a región central de interés
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

# Parámetros de heterogeneidad
HETERO_SIZE = 60.0  # mm
HETERO_POS_X = 40.0  # mm
HETERO_POS_Y = 0.0   # mm

# Casos de simulación
CASES = {
    "Water_Homo": "brachytherapy_water_homo200m.root",
    "Bone_Hetero": "brachytherapy_Bone_Hetero200m.root",
    "Lung_Hetero": "brachytherapy_Lung_Hetero200m.root"
}

# Densidades
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
    """Crea un mapa de densidad considerando la región de heterogeneidad"""
    density_map = np.ones(shape, dtype=float) * DENSITY_WATER
    
    if case_name == "Bone_Hetero":
        hetero_density = DENSITY_BONE
    elif case_name == "Lung_Hetero":
        hetero_density = DENSITY_LUNG
    else:
        return density_map
    
    x_min = HETERO_POS_X - HETERO_SIZE / 2
    x_max = HETERO_POS_X + HETERO_SIZE / 2
    y_min = HETERO_POS_Y - HETERO_SIZE / 2
    y_max = HETERO_POS_Y + HETERO_SIZE / 2
    
    scale_factor = 300 / 301.0
    offset = -150.5
    
    x_min_bin = int((x_min - offset) * scale_factor)
    x_max_bin = int((x_max - offset) * scale_factor)
    y_min_bin = int((y_min - offset) * scale_factor)
    y_max_bin = int((y_max - offset) * scale_factor)
    
    x_min_bin = max(0, min(x_min_bin, shape[0]))
    x_max_bin = max(0, min(x_max_bin, shape[0]))
    y_min_bin = max(0, min(y_min_bin, shape[1]))
    y_max_bin = max(0, min(y_max_bin, shape[1]))
    
    density_map[x_min_bin:x_max_bin, y_min_bin:y_max_bin] = hetero_density
    
    return density_map

def edep_to_dose_sectional(edep_values, case_name):
    """Convierte edep a dosis por secciones"""
    density_map = create_density_map(edep_values.shape, case_name)
    density_map[density_map == 0] = DENSITY_WATER
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

def get_cropped_region(data_2d, x_range=120, y_range=120):
    """
    Extrae la región central del mapa 2D
    x_range e y_range en mm desde el centro
    """
    # El mapa va de -150.5 a 150.5 mm en 300 bins
    # Centro en índice 150
    center_idx = 150
    
    # Convertir mm a índices (escala ~1mm/bin)
    bin_range_x = int(x_range)
    bin_range_y = int(y_range)
    
    x_min_idx = max(0, center_idx - bin_range_x)
    x_max_idx = min(300, center_idx + bin_range_x)
    y_min_idx = max(0, center_idx - bin_range_y)
    y_max_idx = min(300, center_idx + bin_range_y)
    
    return data_2d[x_min_idx:x_max_idx, y_min_idx:y_max_idx]

def plot_dose_maps_and_difference():
    """Crea visualización de mapas de dosis convertida y sus diferencias"""
    
    fig = plt.figure(figsize=(18, 10))
    
    # Cargar histogramas
    histograms = {}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Cargando: {case_name}...", end=" ")
        
        hist = load_histogram(filepath, HISTOGRAM_NAME)
        if hist is None:
            print("❌")
            continue
        
        histograms[case_name] = hist.values()
        print("✅")
    
    # Convertir a dosis
    print("Convirtiendo a dosis...", end=" ")
    dose_maps = {}
    for case_name in CASES.keys():
        if case_name in histograms:
            dose_maps[case_name] = edep_to_dose_sectional(histograms[case_name], case_name)
    print("✅")
    
    # Extraer región central (±120 mm)
    print("Extrayendo región central...", end=" ")
    dose_maps_cropped = {}
    for case_name, dose_map in dose_maps.items():
        dose_maps_cropped[case_name] = get_cropped_region(dose_map, x_range=120, y_range=120)
    print("✅")
    
    # Densidades por caso
    densities = {
        "Water_Homo": DENSITY_WATER,
        "Bone_Hetero": DENSITY_BONE,
        "Lung_Hetero": DENSITY_LUNG
    }
    
    # Fila 1: Mapas de dosis convertida
    for idx, case_name in enumerate(CASES.keys()):
        ax = plt.subplot(2, 3, idx + 1)
        
        if case_name not in dose_maps_cropped:
            continue
        
        values_dose = dose_maps_cropped[case_name]
        
        # Escala log
        values_log = np.copy(values_dose).astype(float)
        values_log[values_log <= 0] = np.min(values_log[values_log > 0]) / 10
        
        im = ax.imshow(
            values_log.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=values_log.min(), vmax=values_log.max())
        )
        
        ax.set_title(f'{case_name}\n(ρ={densities[case_name]} g/cm³)', 
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='Dosis (mGy)')
    
    # Fila 2: Diferencias
    # Resta 1: Bone_Hetero - Water_Homo
    ax_bone = plt.subplot(2, 3, 4)
    diff_bone = dose_maps_cropped['Bone_Hetero'] - dose_maps_cropped['Water_Homo']
    
    im_bone = ax_bone.imshow(
        diff_bone.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=colors.SymLogNorm(linthresh=1e2, vmin=diff_bone.min(), vmax=diff_bone.max())
    )
    
    ax_bone.set_title('Bone_Hetero - Water_Homo\n(SymLog)', fontsize=11, fontweight='bold')
    ax_bone.set_xlabel('X (bins)')
    ax_bone.set_ylabel('Y (bins)')
    plt.colorbar(im_bone, ax=ax_bone, label='Diferencia (mGy)')
    
    # Resta 2: Lung_Hetero - Water_Homo
    ax_lung = plt.subplot(2, 3, 5)
    diff_lung = dose_maps_cropped['Lung_Hetero'] - dose_maps_cropped['Water_Homo']
    
    im_lung = ax_lung.imshow(
        diff_lung.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=colors.SymLogNorm(linthresh=1e2, vmin=diff_lung.min(), vmax=diff_lung.max())
    )
    
    ax_lung.set_title('Lung_Hetero - Water_Homo\n(SymLog)', fontsize=11, fontweight='bold')
    ax_lung.set_xlabel('X (bins)')
    ax_lung.set_ylabel('Y (bins)')
    plt.colorbar(im_lung, ax=ax_lung, label='Diferencia (mGy)')
    
    # Panel vacío para simetría
    ax_empty = plt.subplot(2, 3, 6)
    ax_empty.axis('off')
    
    plt.suptitle('Mapas de Dosis Convertida y Diferencias (Región Central ±120mm) - I125 200M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, 'dose_maps_and_difference_central.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    
    # Estadísticas
    print("\n" + "="*70)
    print("ESTADÍSTICAS DE MAPAS DE DOSIS (REGIÓN CENTRAL ±120mm)")
    print("="*70)
    
    for case_name, dose_map_cropped in dose_maps_cropped.items():
        dose_pos = dose_map_cropped[dose_map_cropped > 0]
        print(f"\n{case_name}:")
        print(f"  Dosis mínima (>0):  {np.min(dose_pos):.6e} mGy")
        print(f"  Dosis máxima:       {np.max(dose_pos):.6e} mGy")
        print(f"  Dosis media:        {np.mean(dose_pos):.6e} mGy")
    
    print("\n" + "="*70)
    print("ESTADÍSTICAS DE DIFERENCIAS (REGIÓN CENTRAL ±120mm)")
    print("="*70)
    
    print(f"\nBone_Hetero - Water_Homo:")
    print(f"  Diferencia mínima:  {np.min(diff_bone):.6e} mGy")
    print(f"  Diferencia máxima:  {np.max(diff_bone):.6e} mGy")
    print(f"  Diferencia media:   {np.mean(diff_bone):.6e} mGy")
    
    print(f"\nLung_Hetero - Water_Homo:")
    print(f"  Diferencia mínima:  {np.min(diff_lung):.6e} mGy")
    print(f"  Diferencia máxima:  {np.max(diff_lung):.6e} mGy")
    print(f"  Diferencia media:   {np.mean(diff_lung):.6e} mGy")
    
    print("\n" + "="*70 + "\n")
    plt.show()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MAPAS DE DOSIS CONVERTIDA Y DIFERENCIAS (REGIÓN CENTRAL) - I125 200M")
    print("="*70 + "\n")
    plot_dose_maps_and_difference()

#!/usr/bin/env python3
"""
Conversión de edep a Dosis por Secciones
Braquiterapia I125 (200M)
Aplica densidades diferentes dentro y fuera de la heterogeneidad
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
DENSITY_LUNG = 1.05

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
    
    Para Water_Homo: todo agua (1.0 g/cm³)
    Para Bone_Hetero: agua (1.0) fuera, hueso (1.85) dentro
    Para Lung_Hetero: agua (1.0) fuera, pulmón (0.26) dentro
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
    
    return dose_mgy, density_map

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

def plot_dose_sectional():
    """Crea visualización de dosis convertida por secciones"""
    
    fig = plt.figure(figsize=(18, 5))
    
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
    
    # Mapas de dosis convertida por secciones
    densities_info = {
        "Water_Homo": "Agua: 1.0 g/cm³",
        "Bone_Hetero": "Agua: 1.0 | Hueso: 1.85 g/cm³",
        "Lung_Hetero": "Agua: 1.0 | Pulmón: 0.26 g/cm³"
    }
    
    for idx, case_name in enumerate(CASES.keys()):
        ax = plt.subplot(1, 3, idx + 1)
        
        if case_name not in histograms:
            continue
        
        values_edep = histograms[case_name]
        
        # Convertir a dosis por secciones
        values_dose, density_map = edep_to_dose_sectional(values_edep, case_name)
        
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
        
        ax.set_title(f'{case_name}\n{densities_info[case_name]}', 
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='Dosis (mGy)')
        draw_heterogeneity(ax)
    
    plt.suptitle('Mapas de Dosis (Conversión por Secciones) - I125 200M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '2D_dose_maps_sectional.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    
    # Estadísticas
    print("\n" + "="*70)
    print("ESTADÍSTICAS DE DOSIS POR SECCIONES")
    print("="*70)
    
    for case_name in CASES.keys():
        if case_name not in histograms:
            continue
        
        values_dose, density_map = edep_to_dose_sectional(histograms[case_name], case_name)
        values_dose_positive = values_dose[values_dose > 0]
        
        # Separar dentro y fuera de heterogeneidad (si aplica)
        if case_name != "Water_Homo":
            hetero_mask = density_map != DENSITY_WATER
            dose_hetero = values_dose[hetero_mask]
            dose_water = values_dose[~hetero_mask]
            
            dose_hetero_pos = dose_hetero[dose_hetero > 0]
            dose_water_pos = dose_water[dose_water > 0]
            
            print(f"\n{case_name}:")
            print(f"  Dosis total:")
            print(f"    Media:   {np.mean(values_dose_positive):.6e} mGy")
            print(f"    Máximo:  {np.max(values_dose_positive):.6e} mGy")
            print(f"  En heterogeneidad:")
            if len(dose_hetero_pos) > 0:
                print(f"    Media:   {np.mean(dose_hetero_pos):.6e} mGy")
                print(f"    Máximo:  {np.max(dose_hetero_pos):.6e} mGy")
            print(f"  En agua (fuera):")
            if len(dose_water_pos) > 0:
                print(f"    Media:   {np.mean(dose_water_pos):.6e} mGy")
                print(f"    Máximo:  {np.max(dose_water_pos):.6e} mGy")
        else:
            print(f"\n{case_name}:")
            print(f"  Dosis total (agua homogénea):")
            print(f"    Media:   {np.mean(values_dose_positive):.6e} mGy")
            print(f"    Máximo:  {np.max(values_dose_positive):.6e} mGy")
    
    print("="*70 + "\n")
    plt.show()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CONVERSIÓN DE DOSIS POR SECCIONES - I125 200M")
    print("="*70 + "\n")
    plot_dose_sectional()

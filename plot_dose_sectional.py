#!/usr/bin/env python3
"""
Conversión de edep a Dosis por Secciones
Braquiterapia I125 (100M)
Aplica densidades diferentes dentro y fuera de la heterogeneidad
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
HISTOGRAM_NAME = "h20"

# Parámetros de heterogeneidad (del macro)
HETERO_SIZE = 60.0  # mm (6.0 cm)
HETERO_POS_X = 40.0  # mm (posición en X)
HETERO_POS_Y = 0.0   # mm (posición en Y)

# Casos de simulación
CASES = {
    "Water_Homo": "brachytherapy_homo_water100m.root",
    "Lung_ICRP_Hetero": "brachytherapy_hetero_lung100m.root",
    "Lung_Hueco_Hetero": "brachytherapy_hetero_lunghueco100m.root",
    "Bone_Hetero": "brachytherapy_hetero_bone100m.root",
    "Lung_Hueco_Homo": "brachytherapy_lunghueco_homo100m.root",
    "Lung_ICRP_Homo": "brachytherapy_homo_lung100m.root"
}

# Densidades base (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG_ICRP = 1.05  # Lung compacto (ICRP)
DENSITY_LUNG_MIRD = 0.2958  # Lung inflado con aire (MIRD)

# Tamaño de bins (plano XY de 1 mm y espesor axial de 0.125 mm)
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0

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
    Para Lung_ICRP_Hetero: agua (1.0) fuera, pulmón ICRP (1.05) dentro
    Para Lung_Hueco_Hetero: agua (1.0) fuera, pulmón MIRD (0.2958) dentro
    Para Lung_ICRP_Homo: todo pulmón ICRP (1.05)
    Para Lung_Hueco_Homo: todo pulmón MIRD (0.2958)
    """
    
    # Determinar densidad de la región principal
    if "Homo" in case_name and "Lung_ICRP" in case_name:
        # Todo es pulmón ICRP
        return np.ones(shape, dtype=float) * DENSITY_LUNG_ICRP
    elif "Homo" in case_name and "Lung_Hueco" in case_name:
        # Todo es pulmón MIRD (hueco)
        return np.ones(shape, dtype=float) * DENSITY_LUNG_MIRD
    elif case_name == "Water_Homo":
        # Todo es agua
        return np.ones(shape, dtype=float) * DENSITY_WATER
    
    # Para casos heterogéneos, empezar con agua
    density_map = np.ones(shape, dtype=float) * DENSITY_WATER
    
    # Determinar densidad de heterogeneidad
    if "Bone" in case_name:
        hetero_density = DENSITY_BONE
    elif "Lung_ICRP" in case_name:
        hetero_density = DENSITY_LUNG_ICRP
    elif "Lung_Hueco" in case_name:
        hetero_density = DENSITY_LUNG_MIRD
    else:
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
    
    Conversión: Dosis (Gy) = edep (MeV) * 1.602e-10 / (volumen_cm³ * densidad_g/cm³)
    """
    density_map = create_density_map(edep_values.shape, case_name)
    
    # Evitar división por cero
    density_map[density_map == 0] = DENSITY_WATER
    
    # Volumen por bin: 1 mm x 1 mm x 0.125 mm = 0.125 mm³ = 0.125e-3 cm³
    bin_volume_cm3 = (BIN_SIZE_MM / 10) ** 2 * 0.0125  # 0.125 mm grosor = 0.0125 cm
    
    # Convertir: Dosis (Gy) = edep * 1.602e-10 / (volumen * densidad)
    dose_gy = edep_values * 1.602e-10 / (bin_volume_cm3 * density_map)
    
    return dose_gy, density_map

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
    
    fig = plt.figure(figsize=(20, 12))
    
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
        "Lung_ICRP_Hetero": "Agua: 1.0 | Pulmón ICRP: 1.05 g/cm³",
        "Lung_Hueco_Hetero": "Agua: 1.0 | Pulmón MIRD: 0.2958 g/cm³",
        "Lung_ICRP_Homo": "Pulmón ICRP: 1.05 g/cm³ (todo)",
        "Lung_Hueco_Homo": "Pulmón MIRD: 0.2958 g/cm³ (todo)"
    }
    
    # Organizar en subplots (3x2)
    num_cases = len(histograms)
    n_rows = 3
    n_cols = 2
    
    for plot_idx, case_name in enumerate(histograms.keys()):
        ax = plt.subplot(n_rows, n_cols, plot_idx + 1)
        
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
        
        ax.set_title(f'{case_name}\n{densities_info.get(case_name, "")}', 
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='Dosis (Gy)', format='%.1e')
        draw_heterogeneity(ax)
    
    plt.suptitle('Mapas de Dosis (Conversión por Secciones) - I125 100M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, 'dose_maps_sectional_3x2.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    
    # Estadísticas
    print("\n" + "="*80)
    print("ESTADÍSTICAS DE DOSIS POR SECCIONES - 100M")
    print("="*80)
    
    for case_name in histograms.keys():
        values_dose, density_map = edep_to_dose_sectional(histograms[case_name], case_name)
        values_dose_positive = values_dose[values_dose > 0]
        
        # Separar dentro y fuera de heterogeneidad (si aplica)
        if case_name != "Water_Homo" and ("Hetero" in case_name):
            hetero_mask = density_map != DENSITY_WATER
            dose_hetero = values_dose[hetero_mask]
            dose_water = values_dose[~hetero_mask]
            
            dose_hetero_pos = dose_hetero[dose_hetero > 0]
            dose_water_pos = dose_water[dose_water > 0]
            
            print(f"\n{case_name}:")
            print(f"  Dosis total:")
            print(f"    Media:   {np.mean(values_dose_positive):.6e} Gy")
            print(f"    Máximo:  {np.max(values_dose_positive):.6e} Gy")
            print(f"  En heterogeneidad:")
            if len(dose_hetero_pos) > 0:
                print(f"    Media:   {np.mean(dose_hetero_pos):.6e} Gy")
                print(f"    Máximo:  {np.max(dose_hetero_pos):.6e} Gy")
            print(f"  En agua (fuera):")
            if len(dose_water_pos) > 0:
                print(f"    Media:   {np.mean(dose_water_pos):.6e} Gy")
                print(f"    Máximo:  {np.max(dose_water_pos):.6e} Gy")
        else:
            print(f"\n{case_name}:")
            print(f"  Dosis total:")
            print(f"    Media:   {np.mean(values_dose_positive):.6e} Gy")
            print(f"    Máximo:  {np.max(values_dose_positive):.6e} Gy")
    
    print("="*80 + "\n")
    plt.show()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CONVERSIÓN DE DOSIS POR SECCIONES - I125 100M")
    print("="*80 + "\n")
    plot_dose_sectional()

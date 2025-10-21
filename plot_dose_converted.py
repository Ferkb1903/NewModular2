#!/usr/bin/env python3
"""
Visualización de Dosis Convertida
Braquiterapia I125 (200M)
Solo muestra mapas 2D de dosis (sin edep)
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

# Parámetros de conversión edep -> dosis
# Densidades (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85  # típico para hueso
DENSITY_LUNG = 1.05  # 64_LUNG_ICRP (comprimido, con aire residual)

# Masa por bin (aproximado, asumiendo bins de 1mm x 1mm x 1mm)
BIN_SIZE_MM = 1.0  # mm
BIN_SIZE_CM = BIN_SIZE_MM / 10.0  # cm
BIN_VOLUME = BIN_SIZE_CM ** 3  # cm³

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

def edep_to_dose(edep_values, density):
    """
    Convierte energía depositada (MeV) a dosis (mGy)
    Dosis (mGy) = edep (MeV) * 1.602e-4 / (volumen cm³ * densidad g/cm³)
    """
    mass_g = BIN_VOLUME * density
    dose_mgy = edep_values * 1.602e-4 / mass_g
    return dose_mgy

def plot_dose_maps():
    """Crea visualización de dosis convertida (sin edep)"""
    
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
    
    # Densidades por caso
    densities = {
        "Water_Homo": DENSITY_WATER,
        "Bone_Hetero": DENSITY_BONE,
        "Lung_Hetero": DENSITY_LUNG
    }
    
    # Mapas de dosis convertida (escala log)
    for idx, case_name in enumerate(CASES.keys()):
        ax = plt.subplot(1, 3, idx + 1)
        
        if case_name not in histograms:
            continue
        
        values_edep = histograms[case_name]
        density = densities[case_name]
        
        # Convertir a dosis
        values_dose = edep_to_dose(values_edep, density)
        
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
        
        ax.set_title(f'{case_name}\n(ρ={density} g/cm³)', 
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='Dosis (mGy)')
        draw_heterogeneity(ax)
    
    plt.suptitle('Mapas de Dosis Convertida - I125 200M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '2D_dose_maps_converted.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    plt.show()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MAPAS DE DOSIS CONVERTIDA - I125 200M")
    print("="*60 + "\n")
    plot_dose_maps()
    print("\n" + "="*60 + "\n")

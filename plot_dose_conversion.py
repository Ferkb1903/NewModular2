#!/usr/bin/env python3
"""
Conversión de Energía Depositada (edep) a Dosis
Braquiterapia I125 (200M)
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
DENSITY_LUNG = 0.26  # típico para tejido pulmonar

# Número de eventos simulados
NUM_EVENTS = 200e6

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
    Convierte energía depositada (MeV) a dosis (Gy)
    
    Dosis (Gy) = edep (MeV) * (1.602e-13 J/MeV) / (masa en kg)
    
    Para simplificar:
    Dosis (mGy) = edep (MeV) * 1.602e-7 / (volumen cm³ * densidad g/cm³ * 1e-3)
    Dosis (mGy) = edep (MeV) * 1.602e-4 / (volumen cm³ * densidad g/cm³)
    """
    
    # Masa del bin en gramos
    mass_g = BIN_VOLUME * density
    
    # Convertir edep a dosis
    # 1 MeV en 1 gramo = 1.602e-7 Gy = 1.602e-4 mGy
    dose_mgy = edep_values * 1.602e-4 / mass_g
    
    return dose_mgy

def plot_dose_comparison():
    """Crea visualización de dosis convertida de edep"""
    
    fig = plt.figure(figsize=(18, 10))
    
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
    
    # Fila 1: Edep original (escala log)
    for idx, case_name in enumerate(CASES.keys()):
        ax = plt.subplot(2, 3, idx + 1)
        
        if case_name not in histograms:
            continue
        
        values_edep = histograms[case_name]
        
        # Escala log
        values_log = np.copy(values_edep).astype(float)
        values_log[values_log <= 0] = np.min(values_log[values_log > 0]) / 10
        
        im = ax.imshow(
            values_log.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=values_log.min(), vmax=values_log.max())
        )
        
        ax.set_title(f'{case_name}\n(edep)', fontsize=11, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='edep (MeV)')
        draw_heterogeneity(ax)
    
    # Fila 2: Dosis convertida (escala log)
    for idx, case_name in enumerate(CASES.keys()):
        ax = plt.subplot(2, 3, idx + 4)
        
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
        
        ax.set_title(f'{case_name}\n(dosis, ρ={density} g/cm³)', 
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='Dosis (mGy)')
        draw_heterogeneity(ax)
    
    plt.suptitle('Conversión de edep a Dosis - I125 200M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '2D_dose_maps_edep_to_dose.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    
    # Imprimir información de conversión
    print("\n" + "="*60)
    print("INFORMACIÓN DE CONVERSIÓN")
    print("="*60)
    print(f"Tamaño bin: {BIN_SIZE_MM} mm × {BIN_SIZE_MM} mm × {BIN_SIZE_MM} mm")
    print(f"Volumen bin: {BIN_VOLUME:.6f} cm³")
    print(f"Factor de conversión: 1 MeV en 1g = {1.602e-4:.6e} mGy")
    print(f"\nDensidades utilizadas:")
    print(f"  Water:  {DENSITY_WATER} g/cm³")
    print(f"  Bone:   {DENSITY_BONE} g/cm³")
    print(f"  Lung:   {DENSITY_LUNG} g/cm³")
    print("="*60 + "\n")
    
    plt.show()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CONVERSIÓN DE ENERGÍA DEPOSITADA A DOSIS")
    print("="*60 + "\n")
    plot_dose_comparison()

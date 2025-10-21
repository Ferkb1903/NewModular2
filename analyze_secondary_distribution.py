#!/usr/bin/env python3
"""
Análisis de la distribución espacial de secundarias
Verifica si toda la energía de secundarias está concentrada en los primeros 2mm
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"

HOMO_CASES = {
    "Lung_Hueco_Homo": {
        "secondary": "brachytherapy_eDepSecondary_lunghueco_homo100m.root",
        "density": 0.2958,
    },
    "Bone_Homo": {
        "secondary": "brachytherapy_eDepSecondary_homo_ bone100m.root",
        "density": 1.85,
    },
    "Water_Homo": {
        "secondary": "brachytherapy_eDepSecondary_homo_water100m.root",
        "density": 1.0,
    },
}

SOURCE_CENTER_X = 150.0  # bins
SOURCE_CENTER_Y = 150.0  # bins
BIN_SIZE_MM = 1.0

def load_histogram(filename, hist_name):
    """Cargar histograma específico de archivo ROOT"""
    try:
        filepath = os.path.join(DATA_DIR, filename) if filename else None
        if not filepath or not os.path.exists(filepath):
            return None
        
        with uproot.open(filepath) as f:
            if hist_name in f:
                hist = f[hist_name]
                edep = hist.values()
                return edep
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def calculate_radial_distance(x, y, source_x, source_y):
    """Calcula distancia radial en mm desde la fuente"""
    dx_mm = (x - source_x) * BIN_SIZE_MM
    dy_mm = (y - source_y) * BIN_SIZE_MM
    distance_mm = np.sqrt(dx_mm**2 + dy_mm**2)
    return distance_mm

def analyze_secondary_distribution():
    """Analiza distribución radial de secundarias"""
    
    print("=" * 90)
    print("ANÁLISIS DE DISTRIBUCIÓN DE SECUNDARIAS")
    print("=" * 90)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Distribución Radial de Secundarias desde la Fuente', fontsize=14, fontweight='bold')
    
    for idx, (case_name, files) in enumerate(HOMO_CASES.items()):
        print(f"\n{case_name}:")
        print("-" * 90)
        
        edep_secondary = load_histogram(files["secondary"], "h2_eDepSecondary")
        
        if edep_secondary is None:
            print("  ❌ No se pudo cargar")
            continue
        
        # Crear matriz de distancias radiales
        nx, ny = edep_secondary.shape
        x_coords, y_coords = np.meshgrid(np.arange(nx), np.arange(ny), indexing='ij')
        radial_distances = calculate_radial_distance(x_coords, y_coords, SOURCE_CENTER_X, SOURCE_CENTER_Y)
        
        # Agrupar energía por distancia radial
        max_radius = int(np.max(radial_distances)) + 1
        radius_bins = np.arange(0, min(max_radius, 50), 1)  # Hasta 50 mm
        
        energy_by_radius = []
        cumulative_energy = []
        total_energy = np.nansum(edep_secondary)
        cumsum = 0
        
        for r_min, r_max in zip(radius_bins[:-1], radius_bins[1:]):
            mask = (radial_distances >= r_min) & (radial_distances < r_max)
            energy_in_ring = np.nansum(edep_secondary[mask])
            energy_by_radius.append(energy_in_ring)
            cumsum += energy_in_ring
            cumulative_energy.append(100.0 * cumsum / total_energy if total_energy > 0 else 0)
        
        # Plotear distribución
        ax = axes[idx]
        center_radii = (radius_bins[:-1] + radius_bins[1:]) / 2
        ax.bar(center_radii, energy_by_radius, width=0.9, alpha=0.7, color='#ff7f0e', label='Energía por anillo')
        
        # Añadir línea de acumulado
        ax2 = ax.twinx()
        ax2.plot(center_radii, cumulative_energy, 'r-o', linewidth=2, markersize=4, label='Acumulado %')
        ax2.set_ylabel('Energía Acumulada (%)', fontsize=10, color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        ax2.set_ylim(0, 105)
        
        material_label = "Lung MIRD" if "Lung" in case_name else ("Bone" if "Bone" in case_name else "Water")
        ax.set_title(f'{material_label}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Distancia Radial (mm)', fontsize=10)
        ax.set_ylabel('Energía por Anillo (MeV)', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_xlim(0, 30)
        
        # Estadísticas clave
        mask_2mm = radial_distances < 2.0
        energy_within_2mm = np.nansum(edep_secondary[mask_2mm])
        pct_2mm = 100.0 * energy_within_2mm / total_energy if total_energy > 0 else 0
        
        mask_5mm = radial_distances < 5.0
        energy_within_5mm = np.nansum(edep_secondary[mask_5mm])
        pct_5mm = 100.0 * energy_within_5mm / total_energy if total_energy > 0 else 0
        
        print(f"\n  RESUMEN:")
        print(f"    Energía total: {total_energy:.2e} MeV")
        print(f"    Dentro de 2mm: {energy_within_2mm:.2e} MeV ({pct_2mm:.2f}%)")
        print(f"    Dentro de 5mm: {energy_within_5mm:.2e} MeV ({pct_5mm:.2f}%)")
        print(f"    Fuera de 5mm: {total_energy - energy_within_5mm:.2e} MeV ({100-pct_5mm:.2f}%)")
    
    plt.tight_layout()
    output_file = os.path.join(DATA_DIR, 'secondary_distribution_analysis.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    analyze_secondary_distribution()

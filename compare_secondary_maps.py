#!/usr/bin/env python3
"""
Comparar mapas de energía depositada por partículas secundarias
Tres casos homogéneos a la misma escala, excluyendo los primeros 2mm desde la fuente
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Circle
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"

# Casos a comparar: Solo secundarias de casos homogéneos
CASES = {
    "Lung MIRD\n(0.2958 g/cm³)": {
        "file": "brachytherapy_eDepSecondary_lunghueco_homo100m.root",
        "hist": "h2_eDepSecondary",
    },
    "Bone\n(1.85 g/cm³)": {
        "file": "brachytherapy_eDepSecondary_homo_ bone100m.root",
        "hist": "h2_eDepSecondary",
    },
    "Water\n(1.0 g/cm³)": {
        "file": "brachytherapy_eDepSecondary_homo_water100m.root",
        "hist": "h2_eDepSecondary",
    },
}

# Parámetros
SOURCE_CENTER_X = 150.0  # bins
SOURCE_CENTER_Y = 150.0  # bins
BIN_SIZE_MM = 1.0
EXCLUDE_RADIUS_MM = 2.0  # Excluir primeros 2mm

def load_histogram(filename, hist_name):
    """Cargar histograma de archivo ROOT"""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  ❌ Archivo no existe: {filepath}")
        return None
    
    try:
        with uproot.open(filepath) as f:
            if hist_name in f:
                hist = f[hist_name]
                edep = hist.values()
                return edep
    except Exception as e:
        print(f"  ❌ Error cargando {hist_name}: {e}")
    
    return None

def mask_inner_region(data, exclude_radius_mm):
    """Crear máscara para excluir región interior"""
    nx, ny = data.shape
    x_coords, y_coords = np.meshgrid(np.arange(nx), np.arange(ny), indexing='ij')
    
    # Distancia radial en mm desde la fuente
    dx_mm = (x_coords - SOURCE_CENTER_X) * BIN_SIZE_MM
    dy_mm = (y_coords - SOURCE_CENTER_Y) * BIN_SIZE_MM
    radial_distance = np.sqrt(dx_mm**2 + dy_mm**2)
    
    # Máscara: mantener solo puntos fuera del radio de exclusión
    mask = radial_distance > exclude_radius_mm
    return mask

def main():
    print("=" * 80)
    print("COMPARACIÓN DE MAPAS DE SECUNDARIAS (sin primeros 2mm)")
    print("=" * 80)
    
    # Cargar datos
    data_maps = {}
    for case_label, case_info in CASES.items():
        print(f"\nCargando {case_label.replace(chr(10), '')}...")
        edep = load_histogram(case_info["file"], case_info["hist"])
        
        if edep is None:
            print(f"  ❌ No se pudo cargar")
            continue
        
        # Aplicar máscara para excluir primeros 2mm
        mask = mask_inner_region(edep, EXCLUDE_RADIUS_MM)
        edep_masked = edep.copy()
        edep_masked[~mask] = 0  # Poner a cero la región interior
        
        data_maps[case_label] = edep_masked
        print(f"  ✓ Cargado exitosamente")
        print(f"    - Rango original: {np.min(edep[edep>0]):.2e} - {np.max(edep):.2e} MeV")
        print(f"    - Rango sin 2mm: {np.min(edep_masked[edep_masked>0]):.2e} - {np.max(edep_masked):.2e} MeV")
    
    if len(data_maps) < 3:
        print("\n❌ No se pudieron cargar los 3 casos")
        return
    
    # Encontrar escala común (máximo global)
    max_vals = [np.max(data) for data in data_maps.values()]
    global_max = np.max(max_vals)
    print(f"\nValor máximo global: {global_max:.2e} MeV")
    
    # Crear visualización
    create_comparison_plot(data_maps, global_max)

def create_comparison_plot(data_maps, global_max):
    """Crear figura con 3 mapas de secundarias a escala común"""
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Mapas de Energía Depositada por Partículas Secundarias\n(excluyendo primeros 2mm)', 
                 fontsize=14, fontweight='bold')
    
    case_order = list(data_maps.keys())
    
    for ax, case_label in zip(axes, case_order):
        data = data_maps[case_label]
        
        # Usar escala logarítmica normalizada
        im = ax.imshow(data.T, origin='lower', cmap='rainbow', 
                       norm=colors.LogNorm(vmin=1e-3 * global_max, vmax=global_max),
                       extent=[0, 300, 0, 300], aspect='auto')
        
        # Dibujar círculo de exclusión (2mm)
        exclude_radius_bins = EXCLUDE_RADIUS_MM / BIN_SIZE_MM
        circle = Circle((SOURCE_CENTER_X, SOURCE_CENTER_Y), exclude_radius_bins,
                       fill=False, edgecolor='white', linewidth=2, linestyle='--', label='2mm limit')
        ax.add_patch(circle)
        
        # Punto de la fuente
        ax.plot(SOURCE_CENTER_X, SOURCE_CENTER_Y, 'w+', markersize=15, markeredgewidth=2)
        
        ax.set_xlabel('X (mm)', fontsize=11)
        ax.set_ylabel('Y (mm)', fontsize=11)
        ax.set_title(case_label, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.2, linestyle=':')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax, label='Energía (MeV)')
    
    plt.tight_layout()
    
    output_file = '/home/fer/fer/newbrachy/secondary_maps_comparison_no2mm.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    
    plt.show()

if __name__ == "__main__":
    main()

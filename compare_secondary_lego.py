#!/usr/bin/env python3
"""
Mapas de energía depositada por partículas secundarias en formato LEGO 3D
Tres casos homogéneos comparados, excluyendo los primeros 2mm desde la fuente
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
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

def subsample_data(data, factor=2):
    """Submuestrear datos para reducir ruido visual"""
    return data[::factor, ::factor]

def main():
    print("=" * 80)
    print("MAPAS 3D LEGO DE SECUNDARIAS (sin primeros 2mm)")
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
        print(f"    - Rango sin 2mm: {np.min(edep_masked[edep_masked>0]):.2e} - {np.max(edep_masked):.2e} MeV")
    
    if len(data_maps) < 3:
        print("\n❌ No se pudieron cargar los 3 casos")
        return
    
    # Encontrar escala común (máximo global)
    max_vals = [np.max(data) for data in data_maps.values()]
    global_max = np.max(max_vals)
    print(f"\nValor máximo global: {global_max:.2e} MeV")
    
    # Crear visualización 3D individual para cada caso
    create_lego_plots(data_maps, global_max)
    
    # Crear visualización comparativa
    create_lego_comparison(data_maps, global_max)

def create_lego_plots(data_maps, global_max):
    """Crear un lego plot individual para cada caso"""
    
    case_order = list(data_maps.keys())
    
    # Calcular escala logarítmica global (mínimo = log(1) = 0)
    log_min_global = 0.0  # log₁₀(1) = 0
    log_max_global = np.log10(global_max)
    
    for idx, case_label in enumerate(case_order):
        print(f"\nGenerando lego plot para {case_label.replace(chr(10), '')}...")
        
        data = data_maps[case_label]
        
        # Submuestrear para mejor visualización
        data_sub = subsample_data(data, factor=3)
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Crear coordenadas
        ny, nx = data_sub.shape
        xpos = np.arange(nx)
        ypos = np.arange(ny)
        xposn, yposn = np.meshgrid(xpos, ypos, indexing='ij')
        
        # Flatten para bar3d
        xpos_flat = xposn.flatten()
        ypos_flat = yposn.flatten()
        dx = 0.8 * np.ones_like(xpos_flat)
        dy = 0.8 * np.ones_like(xpos_flat)
        dz = data_sub.flatten()
        
        # Convertir alturas a escala logarítmica
        dz_log = np.where(dz > 0, np.log10(np.maximum(dz, 1e-10)), log_min_global)
        # Asegurar que todas las alturas sean positivas (mínimo 0)
        dz_log = np.maximum(dz_log, log_min_global)
        
        # Posición base en Z (todas las barras parten desde z=0)
        zpos = np.zeros_like(xpos_flat)
        
        # Normalizar colores en escala logarítmica GLOBAL
        colors_normalized = (dz_log - log_min_global) / (log_max_global - log_min_global)
        colors_normalized = np.clip(colors_normalized, 0, 1)
        
        # Mapear colores
        cmap = cm.get_cmap('rainbow')
        colors_list = cmap(colors_normalized)
        
        # Crear barras 3D con ALTURA EN ESCALA LOGARÍTMICA (solo hacia arriba desde z=0)
        ax.bar3d(xpos_flat, ypos_flat, zpos, dx, dy, dz_log, 
                color=colors_list, zsort='average', shade=True)
        
        ax.set_xlabel('X (bins × 3)', fontsize=11)
        ax.set_ylabel('Y (bins × 3)', fontsize=11)
        ax.set_zlabel('log₁₀(Energía depositada [MeV])', fontsize=11)
        ax.set_title(f'Mapa LEGO 3D: {case_label}', fontsize=13, fontweight='bold')
        ax.text2D(0.05, 0.95, f'Escala log: {10**log_min_global:.2e} - {global_max:.2e} MeV', 
                  transform=ax.transAxes, fontsize=10, verticalalignment='top',
                  bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Ajustar vista
        ax.view_init(elev=25, azim=45)
        
        plt.tight_layout()
        
        # Guardar
        output_file = f'/home/fer/fer/newbrachy/lego_secondary_{idx+1}_{case_label.split(chr(10))[0].replace(" ", "_").lower()}.png'
        plt.savefig(output_file, dpi=120, bbox_inches='tight')
        print(f"  ✓ Guardado: {output_file}")
        print(f"    Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")

def create_lego_comparison(data_maps, global_max):
    """Crear figura comparativa con 3 lego plots en subgráficas"""
    
    print(f"\nGenerando comparación de 3 lego plots...")
    
    # Calcular escala logarítmica global (mínimo = log(1) = 0)
    log_min_global = 0.0  # log₁₀(1) = 0
    log_max_global = np.log10(global_max)
    
    fig = plt.figure(figsize=(20, 6))
    fig.suptitle('Comparación de Mapas 3D LEGO: Energía por Secundarias (sin 2mm)\nEscala logarítmica común: {:.2e} - {:.2e} MeV'.format(10**log_min_global, global_max), 
                 fontsize=14, fontweight='bold')
    
    case_order = list(data_maps.keys())
    
    for plot_idx, case_label in enumerate(case_order):
        ax = fig.add_subplot(1, 3, plot_idx+1, projection='3d')
        
        data = data_maps[case_label]
        
        # Submuestrear
        data_sub = subsample_data(data, factor=3)
        
        # Crear coordenadas
        ny, nx = data_sub.shape
        xpos = np.arange(nx)
        ypos = np.arange(ny)
        xposn, yposn = np.meshgrid(xpos, ypos, indexing='ij')
        
        # Flatten
        xpos_flat = xposn.flatten()
        ypos_flat = yposn.flatten()
        dx = 0.8 * np.ones_like(xpos_flat)
        dy = 0.8 * np.ones_like(xpos_flat)
        dz = data_sub.flatten()
        
        # Convertir alturas a escala logarítmica
        dz_log = np.where(dz > 0, np.log10(np.maximum(dz, 1e-10)), log_min_global)
        # Asegurar que todas las alturas sean positivas (mínimo 0)
        dz_log = np.maximum(dz_log, log_min_global)
        
        # Posición base en Z (todas las barras parten desde z=0)
        zpos = np.zeros_like(xpos_flat)
        
        # Normalizar colores con escala logarítmica GLOBAL
        colors_normalized = (dz_log - log_min_global) / (log_max_global - log_min_global)
        colors_normalized = np.clip(colors_normalized, 0, 1)
        
        # Mapear colores
        cmap = cm.get_cmap('rainbow')
        colors_list = cmap(colors_normalized)
        
        # Barras 3D con ALTURA EN ESCALA LOGARÍTMICA (solo hacia arriba desde z=0)
        ax.bar3d(xpos_flat, ypos_flat, zpos, dx, dy, dz_log, 
                color=colors_list, zsort='average', shade=True)
        
        ax.set_xlabel('X (×3)', fontsize=10)
        ax.set_ylabel('Y (×3)', fontsize=10)
        ax.set_zlabel('log₁₀(E) [MeV]', fontsize=10)
        ax.set_title(case_label, fontsize=11, fontweight='bold')
        
        # Misma vista para todos
        ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    
    output_file = '/home/fer/fer/newbrachy/lego_secondary_comparison.png'
    plt.savefig(output_file, dpi=120, bbox_inches='tight')
    print(f"  ✓ Guardado: {output_file}")
    print(f"    Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")

if __name__ == "__main__":
    main()

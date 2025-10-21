#!/usr/bin/env python3
"""
Mapas de energía depositada: primarias ENCIMA de secundarias en formato LEGO 3D
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

# Casos a comparar: Primarias y secundarias de casos homogéneos
CASES = {
    "Lung MIRD\n(0.2958 g/cm³)": {
        "primary": "brachytherapy_eDepPrimary_lunghueco_homo100m.root",
        "secondary": "brachytherapy_eDepSecondary_lunghueco_homo100m.root",
    },
    "Bone\n(1.85 g/cm³)": {
        "primary": "brachytherapy_eDepPrimary_homo_bone100m.root",
        "secondary": "brachytherapy_eDepSecondary_homo_ bone100m.root",
    },
    "Water\n(1.0 g/cm³)": {
        "primary": "brachytherapy_eDepPrimary_homo_water100m.root",
        "secondary": "brachytherapy_eDepSecondary_homo_water100m.root",
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
    print("MAPAS 3D LEGO: PRIMARIAS ENCIMA DE SECUNDARIAS (sin primeros 2mm)")
    print("=" * 80)
    
    # Cargar datos
    data_maps = {}
    for case_label, case_info in CASES.items():
        print(f"\nCargando {case_label.replace(chr(10), '')}...")
        
        edep_primary = load_histogram(case_info["primary"], "h2_eDepPrimary")
        edep_secondary = load_histogram(case_info["secondary"], "h2_eDepSecondary")
        
        if edep_primary is None or edep_secondary is None:
            print(f"  ❌ No se pudo cargar")
            continue
        
        # Aplicar máscara para excluir primeros 2mm
        mask = mask_inner_region(edep_primary, EXCLUDE_RADIUS_MM)
        edep_primary_masked = edep_primary.copy()
        edep_primary_masked[~mask] = 0
        
        mask = mask_inner_region(edep_secondary, EXCLUDE_RADIUS_MM)
        edep_secondary_masked = edep_secondary.copy()
        edep_secondary_masked[~mask] = 0
        
        data_maps[case_label] = {
            'primary': edep_primary_masked,
            'secondary': edep_secondary_masked,
        }
        print(f"  ✓ Cargado exitosamente")
        print(f"    - Primarias: {np.min(edep_primary_masked[edep_primary_masked>0]):.2e} - {np.max(edep_primary_masked):.2e} MeV")
        print(f"    - Secundarias: {np.min(edep_secondary_masked[edep_secondary_masked>0]):.2e} - {np.max(edep_secondary_masked):.2e} MeV")
    
    if len(data_maps) < 3:
        print("\n❌ No se pudieron cargar los 3 casos")
        return
    
    # Encontrar escala común (máximo global)
    max_primary = max(np.max(data['primary']) for data in data_maps.values())
    max_secondary = max(np.max(data['secondary']) for data in data_maps.values())
    global_max = max(max_primary, max_secondary)
    print(f"\nValor máximo global: {global_max:.2e} MeV")
    
    # Crear visualizaciones
    create_stacked_lego_plots(data_maps, global_max)
    create_stacked_lego_comparison(data_maps, global_max)

def create_stacked_lego_plots(data_maps, global_max):
    """Crear un lego plot individual con primarias + secundarias apiladas"""
    
    case_order = list(data_maps.keys())
    
    # Calcular escala logarítmica global
    log_min_global = 0.0  # log₁₀(1) = 0
    log_max_global = np.log10(global_max)
    
    for idx, case_label in enumerate(case_order):
        print(f"\nGenerando lego stacked para {case_label.replace(chr(10), '')}...")
        
        fig = plt.figure(figsize=(13, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        primary = data_maps[case_label]['primary']
        secondary = data_maps[case_label]['secondary']
        
        # Submuestrear
        primary_sub = subsample_data(primary, factor=3)
        secondary_sub = subsample_data(secondary, factor=3)
        
        # Crear coordenadas
        ny, nx = primary_sub.shape
        xpos = np.arange(nx)
        ypos = np.arange(ny)
        xposn, yposn = np.meshgrid(xpos, ypos, indexing='ij')
        
        xpos_flat = xposn.flatten()
        ypos_flat = yposn.flatten()
        dx = 0.8 * np.ones_like(xpos_flat)
        dy = 0.8 * np.ones_like(xpos_flat)
        
        # ===== BARRAS DE SECUNDARIAS =====
        dz_sec = secondary_sub.flatten()
        dz_sec_log = np.where(dz_sec > 0, np.log10(np.maximum(dz_sec, 1e-10)), log_min_global)
        dz_sec_log = np.maximum(dz_sec_log, log_min_global)
        
        zpos_sec = np.zeros_like(xpos_flat)
        colors_norm_sec = (dz_sec_log - log_min_global) / (log_max_global - log_min_global)
        colors_norm_sec = np.clip(colors_norm_sec, 0, 1)
        
        cmap = cm.get_cmap('Blues')
        colors_sec = cmap(colors_norm_sec * 0.7 + 0.2)  # Escala de azules
        
        ax.bar3d(xpos_flat, ypos_flat, zpos_sec, dx, dy, dz_sec_log, 
                color=colors_sec, zsort='average', shade=True, alpha=0.7, label='Secundarias')
        
        # ===== BARRAS DE PRIMARIAS (ENCIMA) =====
        dz_prim = primary_sub.flatten()
        dz_prim_log = np.where(dz_prim > 0, np.log10(np.maximum(dz_prim, 1e-10)), log_min_global)
        dz_prim_log = np.maximum(dz_prim_log, log_min_global)
        
        # Posición base = altura de secundarias
        zpos_prim = dz_sec_log
        
        colors_norm_prim = (dz_prim_log - log_min_global) / (log_max_global - log_min_global)
        colors_norm_prim = np.clip(colors_norm_prim, 0, 1)
        
        cmap_prim = cm.get_cmap('Reds')
        colors_prim = cmap_prim(colors_norm_prim * 0.7 + 0.2)  # Escala de rojos
        
        ax.bar3d(xpos_flat, ypos_flat, zpos_prim, dx, dy, dz_prim_log, 
                color=colors_prim, zsort='average', shade=True, alpha=0.7, label='Primarias')
        
        ax.set_xlabel('X (bins × 3)', fontsize=11)
        ax.set_ylabel('Y (bins × 3)', fontsize=11)
        ax.set_zlabel('log₁₀(Energía depositada [MeV])', fontsize=11)
        ax.set_title(f'Primarias + Secundarias: {case_label}', fontsize=13, fontweight='bold')
        ax.text2D(0.05, 0.95, f'Azul (abajo)=Secundarias\nRojo (arriba)=Primarias\nEscala: {10**log_min_global:.2e}-{global_max:.2e} MeV', 
                  transform=ax.transAxes, fontsize=10, verticalalignment='top',
                  bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.view_init(elev=25, azim=45)
        
        plt.tight_layout()
        
        output_file = f'/home/fer/fer/newbrachy/lego_stacked_{idx+1}_{case_label.split(chr(10))[0].replace(" ", "_").lower()}.png'
        plt.savefig(output_file, dpi=120, bbox_inches='tight')
        print(f"  ✓ Guardado: {output_file}")
        print(f"    Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
        plt.close()

def create_stacked_lego_comparison(data_maps, global_max):
    """Crear figura comparativa con 3 lego plots apilados lado a lado"""
    
    print(f"\nGenerando comparación de 3 lego stacked...")
    
    log_min_global = 0.0
    log_max_global = np.log10(global_max)
    
    fig = plt.figure(figsize=(22, 7))
    fig.suptitle('Comparación: Primarias (rojo, arriba) + Secundarias (azul, abajo)\nSin primeros 2mm | Escala logarítmica común: 1.00e+00 - {:.2e} MeV'.format(global_max), 
                 fontsize=14, fontweight='bold')
    
    case_order = list(data_maps.keys())
    
    for plot_idx, case_label in enumerate(case_order):
        ax = fig.add_subplot(1, 3, plot_idx+1, projection='3d')
        
        primary = data_maps[case_label]['primary']
        secondary = data_maps[case_label]['secondary']
        
        # Submuestrear
        primary_sub = subsample_data(primary, factor=3)
        secondary_sub = subsample_data(secondary, factor=3)
        
        # Crear coordenadas
        ny, nx = primary_sub.shape
        xpos = np.arange(nx)
        ypos = np.arange(ny)
        xposn, yposn = np.meshgrid(xpos, ypos, indexing='ij')
        
        xpos_flat = xposn.flatten()
        ypos_flat = yposn.flatten()
        dx = 0.8 * np.ones_like(xpos_flat)
        dy = 0.8 * np.ones_like(xpos_flat)
        
        # ===== SECUNDARIAS =====
        dz_sec = secondary_sub.flatten()
        dz_sec_log = np.where(dz_sec > 0, np.log10(np.maximum(dz_sec, 1e-10)), log_min_global)
        dz_sec_log = np.maximum(dz_sec_log, log_min_global)
        
        zpos_sec = np.zeros_like(xpos_flat)
        colors_norm_sec = (dz_sec_log - log_min_global) / (log_max_global - log_min_global)
        colors_norm_sec = np.clip(colors_norm_sec, 0, 1)
        
        cmap = cm.get_cmap('Blues')
        colors_sec = cmap(colors_norm_sec * 0.7 + 0.2)
        
        ax.bar3d(xpos_flat, ypos_flat, zpos_sec, dx, dy, dz_sec_log, 
                color=colors_sec, zsort='average', shade=True, alpha=0.7)
        
        # ===== PRIMARIAS =====
        dz_prim = primary_sub.flatten()
        dz_prim_log = np.where(dz_prim > 0, np.log10(np.maximum(dz_prim, 1e-10)), log_min_global)
        dz_prim_log = np.maximum(dz_prim_log, log_min_global)
        
        zpos_prim = dz_sec_log
        
        colors_norm_prim = (dz_prim_log - log_min_global) / (log_max_global - log_min_global)
        colors_norm_prim = np.clip(colors_norm_prim, 0, 1)
        
        cmap_prim = cm.get_cmap('Reds')
        colors_prim = cmap_prim(colors_norm_prim * 0.7 + 0.2)
        
        ax.bar3d(xpos_flat, ypos_flat, zpos_prim, dx, dy, dz_prim_log, 
                color=colors_prim, zsort='average', shade=True, alpha=0.7)
        
        ax.set_xlabel('X (×3)', fontsize=10)
        ax.set_ylabel('Y (×3)', fontsize=10)
        ax.set_zlabel('log₁₀(E) [MeV]', fontsize=10)
        ax.set_title(case_label, fontsize=11, fontweight='bold')
        ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    
    output_file = '/home/fer/fer/newbrachy/lego_stacked_comparison.png'
    plt.savefig(output_file, dpi=120, bbox_inches='tight')
    print(f"  ✓ Guardado: {output_file}")
    print(f"    Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")

if __name__ == "__main__":
    main()

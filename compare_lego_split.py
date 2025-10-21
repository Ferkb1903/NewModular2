#!/usr/bin/env python3
"""
Mapas 3D LEGO: Primarias ARRIBA, Secundarias ABAJO en subgráficas
Tres casos homogéneos, excluyendo los primeros 2mm desde la fuente
Compatible con I-125 (100M) e Ir-192 (200M)
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.gridspec import GridSpec
import os
import sys

# Configuración - FUENTE SELECCIONABLE
SOURCE = sys.argv[1].lower() if len(sys.argv) > 1 else "i125"  # i125 o ir192

if SOURCE == "ir192":
    DATA_DIR = "/home/fer/fer/newbrachy/200M_IR192"
    OUTPUT_PREFIX = "ir192_200m"
    TITLE_SUFFIX = "Ir-192 200M"
else:  # i125
    DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
    OUTPUT_PREFIX = "i125_100m"
    TITLE_SUFFIX = "I-125 100M"

print(f"Usando fuente: {TITLE_SUFFIX}")
print(f"Directorio: {DATA_DIR}\n")

print(f"Usando fuente: {TITLE_SUFFIX}")
print(f"Directorio: {DATA_DIR}\n")

# Casos a comparar: Primarias y secundarias de casos homogéneos
if SOURCE == "ir192":
    CASES = {
        "Pulmón MIRD\n(0.2958 g/cm³)": {
            "primary": None,  # No disponible
            "secondary": None,
        },
        "Hueso\n(1.85 g/cm³)": {
            "primary": "200m_primary_secondary_bone.root",
            "secondary": "200m_primary_secondary_bone.root",
        },
        "Agua\n(1.0 g/cm³)": {
            "primary": "200m_primary_secondary_water.root",
            "secondary": "200m_primary_secondary_water.root",
        },
    }
else:  # i125
    CASES = {
        "Pulmón MIRD\n(0.2958 g/cm³)": {
            "primary": "brachytherapy_eDepPrimary_lunghueco_homo100m.root",
            "secondary": "brachytherapy_eDepSecondary_lunghueco_homo100m.root",
        },
        "Hueso\n(1.85 g/cm³)": {
            "primary": "brachytherapy_eDepPrimary_homo_bone100m.root",
            "secondary": "brachytherapy_eDepSecondary_homo_bone100m.root",
        },
        "Agua\n(1.0 g/cm³)": {
            "primary": "brachytherapy_eDepPrimary_homo_water100m.root",
            "secondary": "brachytherapy_eDepSecondary_homo_water100m.root",
        },
    }

# Parámetros
SOURCE_CENTER_X = 150.0  # bins
SOURCE_CENTER_Y = 150.0  # bins
BIN_SIZE_MM = 1.0
EXCLUDE_RADIUS_MM = 2.0  # Excluir primeros 2mm

# Densidades de materiales (g/cm³)
MATERIAL_DENSITIES = {
    "Pulmón MIRD\n(0.2958 g/cm³)": 0.2958,
    "Hueso\n(1.85 g/cm³)": 1.85,
    "Agua\n(1.0 g/cm³)": 1.0,
}

# Traducción de nombres de materiales al español
MATERIAL_NAMES_ES = {
    "Pulmón MIRD\n(0.2958 g/cm³)": "Pulmón MIRD\n(0.2958 g/cm³)",
    "Hueso\n(1.85 g/cm³)": "Hueso\n(1.85 g/cm³)",
    "Agua\n(1.0 g/cm³)": "Agua\n(1.0 g/cm³)",
}

# Conversión MeV a Gy
# 1 Gy = 1 J/kg = 1 J/(1000 g) = 1e-3 J/g
# 1 MeV = 1.602e-13 J
# Energía en un voxel de 1mm³ = 1e-3 cm³ = 1e-6 cm³
# Para convertir edep (MeV) a dosis (Gy):
# dosis (Gy) = edep (MeV) * 1.602e-13 (J/MeV) / (1e-6 cm³ * densidad g/cm³ * 1e-3 J/g)
# dosis = edep * 1.602e-13 / (1e-6 * densidad * 1e-3)
# dosis = edep * 1.602e-13 / (1e-9 * densidad)
# dosis = edep * 1.602e-4 / densidad

def edep_to_dose_gy(edep_mev, density_g_cm3, volume_cm3=1e-6):
    """
    Convertir energía depositada a dosis en Gy
    edep_mev: energía en MeV
    density_g_cm3: densidad del material en g/cm³
    volume_cm3: volumen de cada voxel en cm³ (default 1mm³ = 1e-6 cm³)
    """
    MeV_to_J = 1.602e-13
    J_per_Gy = 1.0  # 1 Gy = 1 J/kg
    
    # Energía en Joules
    energy_j = edep_mev * MeV_to_J
    
    # Masa en kg del voxel
    mass_g = volume_cm3 * density_g_cm3
    mass_kg = mass_g * 1e-3
    
    # Dosis en Gy
    dose_gy = energy_j / mass_kg if mass_kg > 0 else 0
    return dose_gy

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
    print("MAPAS 3D LEGO: PRIMARIAS (arriba) vs SECUNDARIAS (abajo)")
    print("=" * 80)
    
    # Cargar datos
    data_maps = {}
    for case_label, case_info in CASES.items():
        print(f"\nCargando {case_label.replace(chr(10), '')}...")
        
        # Saltarse si no hay archivos disponibles
        if case_info["primary"] is None or case_info["secondary"] is None:
            print(f"  ⚠ Archivos no disponibles para este material")
            continue
        
        edep_primary = load_histogram(case_info["primary"], "h2_eDepPrimary")
        if edep_primary is None:
            edep_primary = load_histogram(case_info["primary"], "dose_map_primary")
        
        edep_secondary = load_histogram(case_info["secondary"], "h2_eDepSecondary")
        if edep_secondary is None:
            edep_secondary = load_histogram(case_info["secondary"], "dose_map_secondary")
        
        if edep_primary is None or edep_secondary is None:
            print(f"  ❌ No se pudo cargar")
            continue
        
        # Obtener densidad del material
        density = MATERIAL_DENSITIES[case_label]
        
        # Convertir a dosis (Gy)
        dose_primary = np.vectorize(lambda x: edep_to_dose_gy(x, density))(edep_primary)
        dose_secondary = np.vectorize(lambda x: edep_to_dose_gy(x, density))(edep_secondary)
        
        # Aplicar máscara para excluir primeros 2mm
        mask = mask_inner_region(dose_primary, EXCLUDE_RADIUS_MM)
        dose_primary_masked = dose_primary.copy()
        dose_primary_masked[~mask] = 0
        
        mask = mask_inner_region(dose_secondary, EXCLUDE_RADIUS_MM)
        dose_secondary_masked = dose_secondary.copy()
        dose_secondary_masked[~mask] = 0
        
        data_maps[case_label] = {
            'primary': dose_primary_masked,
            'secondary': dose_secondary_masked,
        }
        print(f"  ✓ Cargado exitosamente")
        print(f"    - Primarias: {np.min(dose_primary_masked[dose_primary_masked>0]):.2e} - {np.max(dose_primary_masked):.2e} Gy")
        print(f"    - Secundarias: {np.min(dose_secondary_masked[dose_secondary_masked>0]):.2e} - {np.max(dose_secondary_masked):.2e} Gy")
    
    if len(data_maps) < 2:
        print("\n❌ No se pudieron cargar suficientes casos")
        return
    
    # Encontrar escala SEPARADA para primarias y secundarias
    max_primary = max(np.max(data['primary']) for data in data_maps.values())
    max_secondary = max(np.max(data['secondary']) for data in data_maps.values())
    
    # Convertir a mGy
    max_primary_mgy = max_primary * 1000
    max_secondary_mgy = max_secondary * 1000
    
    print(f"\nValor máximo PRIMARIAS: {max_primary_mgy:.2e} mGy")
    print(f"Valor máximo SECUNDARIAS: {max_secondary_mgy:.2e} mGy")
    
    # Calcular porcentajes de dosis primaria vs secundaria
    print(f"\n{'='*70}")
    print(f"CONTRIBUCIÓN RELATIVA DE DOSIS PRIMARIA vs SECUNDARIA - {TITLE_SUFFIX}")
    print(f"{'='*70}")
    for case_label in data_maps.keys():
        primary_data = data_maps[case_label]['primary']
        secondary_data = data_maps[case_label]['secondary']
        
        total_primary = np.sum(primary_data)
        total_secondary = np.sum(secondary_data)
        total_dose = total_primary + total_secondary
        
        pct_primary = (total_primary / total_dose * 100) if total_dose > 0 else 0
        pct_secondary = (total_secondary / total_dose * 100) if total_dose > 0 else 0
        
        material_name = case_label.replace('\n', ' ')
        print(f"\n{material_name}:")
        print(f"  Dosis primaria:   {pct_primary:6.2f}%  ({total_primary:.2e} Gy·cm³)")
        print(f"  Dosis secundaria: {pct_secondary:6.2f}%  ({total_secondary:.2e} Gy·cm³)")
    print(f"{'='*70}\n")
    
    scales = {
        'primary_max': max_primary,
        'secondary_max': max_secondary,
        'primary_max_mgy': max_primary_mgy,
        'secondary_max_mgy': max_secondary_mgy,
    }
    
    # Crear visualizaciones individuales (2 subplots por material)
    create_split_lego_plots(data_maps, scales)
    
    # Crear comparación en una sola imagen
    create_split_lego_comparison(data_maps, scales)

def create_split_lego_plots(data_maps, scales):
    """Crear figura individual con primarias ARRIBA, secundarias ABAJO"""
    
    case_order = list(data_maps.keys())
    
    # Calcular escalas logarítmicas SEPARADAS para primarias
    log_min = 0.0  # log₁₀(1) = 0
    log_max_primary = np.log10(scales['primary_max'])
    max_secondary = scales['secondary_max']
    
    for idx, case_label in enumerate(case_order):
        print(f"\nGenerando figura split para {case_label.replace(chr(10), '')}...")
        
        fig = plt.figure(figsize=(12, 14))
        material_name_es = MATERIAL_NAMES_ES.get(case_label, case_label)
        fig.suptitle(f'{material_name_es}\n(sin primeros 2mm)', 
                     fontsize=13, fontweight='bold')
        
        # Usar GridSpec para control de espaciado
        gs = GridSpec(2, 1, figure=fig, hspace=0.35)
        
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
        
        # ===== SUBPLOT 1: PRIMARIAS (ARRIBA) =====
        ax1 = fig.add_subplot(gs[0], projection='3d')
        
        dz_prim = primary_sub.flatten()
        dz_prim_log = np.where(dz_prim > 0, np.log10(np.maximum(dz_prim, 1e-10)), log_min)
        dz_prim_log = np.maximum(dz_prim_log, log_min)
        
        zpos_prim = np.zeros_like(xpos_flat)
        
        colors_norm_prim = (dz_prim_log - log_min) / (log_max_primary - log_min)
        colors_norm_prim = np.clip(colors_norm_prim, 0, 1)
        
        cmap_prim = cm.get_cmap('Reds')
        colors_prim = cmap_prim(colors_norm_prim * 0.7 + 0.2)
        
        ax1.bar3d(xpos_flat, ypos_flat, zpos_prim, dx, dy, dz_prim_log, 
                 color=colors_prim, zsort='average', shade=True, alpha=0.8)
        
        # Agregar mapa 2D en la cara superior (en escala log)
        dz_prim_log_2d = np.where(primary_sub > 0, np.log10(np.maximum(primary_sub, 1e-10)), log_min)
        ax1.contourf(xposn, yposn, dz_prim_log_2d, levels=15, cmap='Reds', alpha=0.5, offset=log_max_primary, zdir='z')
        
        ax1.set_xlabel('X (bins × 3)', fontsize=10)
        ax1.set_ylabel('Y (bins × 3)', fontsize=10)
        ax1.set_zlabel('log₁₀(Dosis [Gy])', fontsize=10)
        ax1.set_zlim(log_min, log_max_primary)
        ax1.view_init(elev=25, azim=45)
        
        # Agregar texto "Dosis primaria" en medio entre subplots
        fig.text(0.5, 0.52, 'Dosis primaria', ha='center', fontsize=16, fontweight='bold', color='darkred')
        
        # ===== SUBPLOT 2: SECUNDARIAS (ABAJO) =====
        ax2 = fig.add_subplot(gs[1], projection='3d')
        
        # Escala LOGARÍTMICA para secundarias también
        dz_sec = secondary_sub.flatten()
        dz_sec_log = np.where(dz_sec > 0, np.log10(np.maximum(dz_sec, 1e-10)), log_min)
        dz_sec_log = np.maximum(dz_sec_log, log_min)
        
        zpos_sec = np.zeros_like(xpos_flat)
        
        # Encontrar máximo logarítmico para secundarias
        log_max_secondary = np.max(dz_sec_log)
        colors_norm_sec = (dz_sec_log - log_min) / (log_max_secondary - log_min) if log_max_secondary > log_min else np.zeros_like(dz_sec_log)
        colors_norm_sec = np.clip(colors_norm_sec, 0, 1)
        
        cmap_sec = cm.get_cmap('Blues')
        colors_sec = cmap_sec(colors_norm_sec * 0.7 + 0.2)
        
        ax2.bar3d(xpos_flat, ypos_flat, zpos_sec, dx, dy, dz_sec_log, 
                 color=colors_sec, zsort='average', shade=True, alpha=0.8)
        
        # Agregar mapa 2D en la cara superior (en escala log)
        dz_sec_log_2d = np.where(secondary_sub > 0, np.log10(np.maximum(secondary_sub, 1e-10)), log_min)
        ax2.contourf(xposn, yposn, dz_sec_log_2d, levels=15, cmap='Blues', alpha=0.5, offset=log_max_secondary, zdir='z')
        
        ax2.set_xlabel('X (bins × 3)', fontsize=10)
        ax2.set_ylabel('Y (bins × 3)', fontsize=10)
        ax2.set_zlabel('log₁₀(Dosis [Gy])', fontsize=10)
        ax2.set_zlim(log_min, log_max_secondary)
        ax2.view_init(elev=25, azim=45)
        
        # Agregar texto "Dosis Secundaria" en medio arriba de este subplot
        fig.text(0.5, 0.02, 'Dosis Secundaria', ha='center', fontsize=16, fontweight='bold', color='darkblue')
        
        plt.tight_layout()
        
        output_file = f'/home/fer/fer/newbrachy/lego_split_{OUTPUT_PREFIX}_{idx+1}_{case_label.split(chr(10))[0].replace(" ", "_").lower()}.png'
        plt.savefig(output_file, dpi=120, bbox_inches='tight')
        print(f"  ✓ Guardado: {output_file}")
        print(f"    Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
        plt.close()

def create_split_lego_comparison(data_maps, scales):
    """Crear figura comparativa con primarias ARRIBA, secundarias ABAJO"""
    
    print(f"\nGenerando comparación de materiales con primarias y secundarias...")
    
    log_min = 0.0
    log_max_primary = np.log10(scales['primary_max'])
    
    # Figura con 2 filas (primarias y secundarias) × 3 columnas (materiales)
    fig = plt.figure(figsize=(20, 12))
    
    # Usar GridSpec para control de espaciado vertical entre filas
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    case_order = list(data_maps.keys())
    
    # ===== FILA 1: PRIMARIAS =====
    for col_idx, case_label in enumerate(case_order):
        ax = fig.add_subplot(gs[0, col_idx], projection='3d')
        
        primary = data_maps[case_label]['primary']
        primary_sub = subsample_data(primary, factor=3)
        
        ny, nx = primary_sub.shape
        xpos = np.arange(nx)
        ypos = np.arange(ny)
        xposn, yposn = np.meshgrid(xpos, ypos, indexing='ij')
        
        xpos_flat = xposn.flatten()
        ypos_flat = yposn.flatten()
        dx = 0.8 * np.ones_like(xpos_flat)
        dy = 0.8 * np.ones_like(xpos_flat)
        
        dz_prim = primary_sub.flatten()
        dz_prim_log = np.where(dz_prim > 0, np.log10(np.maximum(dz_prim, 1e-10)), log_min)
        dz_prim_log = np.maximum(dz_prim_log, log_min)
        
        zpos_prim = np.zeros_like(xpos_flat)
        
        colors_norm_prim = (dz_prim_log - log_min) / (log_max_primary - log_min)
        colors_norm_prim = np.clip(colors_norm_prim, 0, 1)
        
        cmap_prim = cm.get_cmap('Reds')
        colors_prim = cmap_prim(colors_norm_prim * 0.7 + 0.2)
        
        ax.bar3d(xpos_flat, ypos_flat, zpos_prim, dx, dy, dz_prim_log, 
                color=colors_prim, zsort='average', shade=True, alpha=0.8)
        
        # Agregar mapa 2D en la cara superior (en escala log)
        dz_prim_log_2d = np.where(primary_sub > 0, np.log10(np.maximum(primary_sub, 1e-10)), log_min)
        ax.contourf(xposn, yposn, dz_prim_log_2d, levels=15, cmap='Reds', alpha=0.5, offset=log_max_primary, zdir='z')
        
        ax.set_xlabel('X (×3)', fontsize=9)
        ax.set_ylabel('Y (×3)', fontsize=9)
        ax.set_zlabel('log₁₀(Dosis)', fontsize=9)
        material_name_es = MATERIAL_NAMES_ES.get(case_label, case_label)
        ax.set_title(material_name_es, fontsize=11, fontweight='bold', color='darkred')
        ax.set_zlim(log_min, log_max_primary)
        ax.view_init(elev=25, azim=45)
    
    # Agregar texto "Dosis primaria" sobre la fila superior
    fig.text(0.5, 0.97, 'Dosis primaria', ha='center', fontsize=18, fontweight='bold', color='darkred', 
             transform=fig.transFigure)
    
    # ===== FILA 2: SECUNDARIAS =====
    for col_idx, case_label in enumerate(case_order):
        ax = fig.add_subplot(gs[1, col_idx], projection='3d')
        
        secondary = data_maps[case_label]['secondary']
        secondary_sub = subsample_data(secondary, factor=3)
        
        ny, nx = secondary_sub.shape
        xpos = np.arange(nx)
        ypos = np.arange(ny)
        xposn, yposn = np.meshgrid(xpos, ypos, indexing='ij')
        
        xpos_flat = xposn.flatten()
        ypos_flat = yposn.flatten()
        dx = 0.8 * np.ones_like(xpos_flat)
        dy = 0.8 * np.ones_like(xpos_flat)
        
        # Escala LOGARÍTMICA para secundarias también
        dz_sec = secondary_sub.flatten()
        dz_sec_log = np.where(dz_sec > 0, np.log10(np.maximum(dz_sec, 1e-10)), log_min)
        dz_sec_log = np.maximum(dz_sec_log, log_min)
        
        zpos_sec = np.zeros_like(xpos_flat)
        
        # Encontrar máximo logarítmico para secundarias
        log_max_secondary = np.max(dz_sec_log)
        colors_norm_sec = (dz_sec_log - log_min) / (log_max_secondary - log_min) if log_max_secondary > log_min else np.zeros_like(dz_sec_log)
        colors_norm_sec = np.clip(colors_norm_sec, 0, 1)
        
        cmap_sec = cm.get_cmap('Blues')
        colors_sec = cmap_sec(colors_norm_sec * 0.7 + 0.2)
        
        ax.bar3d(xpos_flat, ypos_flat, zpos_sec, dx, dy, dz_sec_log, 
                color=colors_sec, zsort='average', shade=True, alpha=0.8)
        
        # Agregar mapa 2D en la cara superior (en escala log)
        dz_sec_log_2d = np.where(secondary_sub > 0, np.log10(np.maximum(secondary_sub, 1e-10)), log_min)
        ax.contourf(xposn, yposn, dz_sec_log_2d, levels=15, cmap='Blues', alpha=0.5, offset=log_max_secondary, zdir='z')
        
        ax.set_xlabel('X (×3)', fontsize=9)
        ax.set_ylabel('Y (×3)', fontsize=9)
        ax.set_zlabel('log₁₀(Dosis [Gy])', fontsize=9)
        material_name_es = MATERIAL_NAMES_ES.get(case_label, case_label)
        ax.set_title(material_name_es, fontsize=11, fontweight='bold', color='darkblue')
        ax.set_zlim(log_min, log_max_secondary)
        ax.view_init(elev=25, azim=45)
    
    # Agregar texto "Dosis Secundaria" sobre la fila inferior
    fig.text(0.5, 0.48, 'Dosis Secundaria', ha='center', fontsize=18, fontweight='bold', color='darkblue', 
             transform=fig.transFigure)
    
    plt.tight_layout()
    
    output_file = f'/home/fer/fer/newbrachy/lego_split_{OUTPUT_PREFIX}_comparison.png'
    plt.savefig(output_file, dpi=120, bbox_inches='tight')
    print(f"  ✓ Guardado: {output_file}")
    print(f"    Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")

if __name__ == "__main__":
    main()

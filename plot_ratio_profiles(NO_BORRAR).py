#!/usr/bin/env python3
"""
Perfiles horizontales de ratios: Casos heterogéneos vs Water Homo
Gráficas de línea mostrando cómo varía el ratio a lo largo del eje X (Y=0)
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
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
    "Lung_ICRP_Hetero": "brachytherapy_hetero_lung100m.root",
    "Lung_Hueco_Hetero": "brachytherapy_hetero_lunghueco100m.root",
    "Bone_Hetero": "brachytherapy_hetero_bone100m.root",
}

# Densidades base (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG_ICRP = 1.05
DENSITY_LUNG_MIRD = 0.2958

# Tamaño de bins
BIN_SIZE_MM = 1.0

def load_histogram(filename):
    """Cargar histograma de archivo ROOT"""
    try:
        with uproot.open(filename) as f:
            for hist_name in ['h20', 'Deph', 'h2_eDepPrimary']:
                if hist_name in f:
                    hist = f[hist_name]
                    edep = hist.values()
                    return edep
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def create_density_map(shape, case_name):
    """Crea un mapa de densidad considerando la región de heterogeneidad"""
    
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

def edep_to_dose(edep_values, density_map):
    """Convierte edep a dosis (Gy) aplicando densidad por región"""
    bin_volume_cm3 = (BIN_SIZE_MM / 10) ** 2 * 0.0125
    density_map_copy = density_map.copy()
    density_map_copy[density_map_copy == 0] = DENSITY_WATER
    dose_gy = edep_values * 1.602e-10 / (bin_volume_cm3 * density_map_copy)
    return dose_gy

def extract_horizontal_profiles(dose_maps):
    """Extrae perfiles horizontales en Y=0 promediando 5 bins"""
    profiles = {}
    center_y = 150
    for case_name, dose_map in dose_maps.items():
        # Promediar 5 bins: Y-2, Y-1, Y0, Y+1, Y+2 para reducir ruido
        profile = (dose_map[:, center_y-2] + dose_map[:, center_y-1] + dose_map[:, center_y] + 
                   dose_map[:, center_y+1] + dose_map[:, center_y+2]) / 5.0
        profiles[case_name] = profile
    return profiles

def get_x_axis_mm(num_bins=300):
    """Retorna el eje X en milímetros"""
    x_min = -150.5
    x_max = 150.5
    x_mm = np.linspace(x_min, x_max, num_bins)
    return x_mm

def filter_data_range(x_axis, profiles, x_min_range=-120, x_max_range=120):
    """Filtra datos al rango [x_min_range, x_max_range] mm"""
    mask = (x_axis >= x_min_range) & (x_axis <= x_max_range)
    x_filtered = x_axis[mask]
    
    profiles_filtered = {}
    for case_name, profile in profiles.items():
        profiles_filtered[case_name] = profile[mask]
    
    return x_filtered, profiles_filtered

def main():
    print("=" * 80)
    print("PERFILES HORIZONTALES DE RATIOS: Heterogéneos vs Water Homo")
    print("=" * 80)
    
    # Cargar Water Homo (referencia)
    print("\nCargando casos...")
    filepath_ref = os.path.join(DATA_DIR, "brachytherapy_homo_water100m.root")
    edep_ref = load_histogram(filepath_ref)
    if edep_ref is None:
        print("❌ No se pudo cargar Water Homo")
        return
    
    density_ref = create_density_map(edep_ref.shape, "Water_Homo")
    dose_ref = edep_to_dose(edep_ref, density_ref)
    print(f"  ✓ Water Homo referencia cargado")
    
    # Cargar casos heterogéneos
    dose_maps = {"Water_Homo": dose_ref}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"  Cargando {case_name}...", end=" ")
        edep = load_histogram(filepath)
        if edep is None:
            print("❌")
            continue
        
        density = create_density_map(edep.shape, case_name)
        dose = edep_to_dose(edep, density)
        dose_maps[case_name] = dose
        print("✓")
    
    # Extraer perfiles horizontales
    print("\nExtrayendo perfiles...", end=" ")
    profiles = extract_horizontal_profiles(dose_maps)
    x_axis = get_x_axis_mm()
    print("✓")
    
    # Filtrar al rango [-15, +120] mm
    print("Filtrando rango [-15, +120] mm...", end=" ")
    x_axis_filtered, profiles_filtered = filter_data_range(x_axis, profiles, x_min_range=-15, x_max_range=120)
    print("✓")
    
    # Calcular ratios (sin filtro agresivo de water > 1e-2)
    ratio_lung_icrp = np.divide(profiles_filtered["Lung_ICRP_Hetero"], 
                                profiles_filtered["Water_Homo"],
                                where=profiles_filtered["Water_Homo"] > 0,
                                out=np.zeros_like(profiles_filtered["Water_Homo"]))
    
    ratio_lung_hueco = np.divide(profiles_filtered["Lung_Hueco_Hetero"], 
                                 profiles_filtered["Water_Homo"],
                                 where=profiles_filtered["Water_Homo"] > 0,
                                 out=np.zeros_like(profiles_filtered["Water_Homo"]))
    
    ratio_bone = np.divide(profiles_filtered["Bone_Hetero"], 
                          profiles_filtered["Water_Homo"],
                          where=profiles_filtered["Water_Homo"] > 0,
                          out=np.zeros_like(profiles_filtered["Water_Homo"]))
    
    # Identificar punto justo antes de entrada a heterogeneidad
    hetero_x_min = HETERO_POS_X - HETERO_SIZE / 2  # 10 mm
    # Buscar el índice más cercano a hetero_x_min (punto de entrada)
    edge_point_x = hetero_x_min  # 10 mm (punto de entrada exacto)
    idx_edge = np.argmin(np.abs(x_axis_filtered - edge_point_x))
    
    # Crear figura con 2x2 paneles
    fig = plt.figure(figsize=(16, 10))
    
    # Panel 1: Perfiles de dosis (escala log)
    ax1 = plt.subplot(2, 2, 1)
    
    for case_name, profile in profiles_filtered.items():
        # Filtrar puntos con valores muy pequeños (< 1e-10)
        mask_valid = profile >= 1e-10
        ax1.plot(x_axis_filtered[mask_valid], profile[mask_valid], linewidth=2.0, marker='o', markersize=3, alpha=0.7, label=case_name)
    
    hetero_x_min = HETERO_POS_X - HETERO_SIZE / 2
    hetero_x_max = HETERO_POS_X + HETERO_SIZE / 2
    ax1.axvspan(hetero_x_min, hetero_x_max, alpha=0.15, color='yellow', label='Heterogeneidad')
    ax1.axvline(hetero_x_min, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axvline(hetero_x_max, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axvline(0, color='red', linestyle=':', linewidth=1.5, alpha=0.6, label='Fuente')
    
    ax1.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Dosis (Gy)', fontsize=11, fontweight='bold')
    ax1.set_title('Perfiles Horizontales de Dosis (Y=0)', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    ax1.set_xlim(-15, 120)
    
    # Panel 2: Ratio Lung ICRP Hetero / Water
    ax2 = plt.subplot(2, 2, 2)
    
    # Plotear líneas solo en la región heterogénea, puntos fuera
    mask_hetero_region = (x_axis_filtered >= hetero_x_min) & (x_axis_filtered <= hetero_x_max)
    mask_outside = ~mask_hetero_region
    
    ax2.plot(x_axis_filtered[mask_hetero_region], ratio_lung_icrp[mask_hetero_region], 
             linewidth=2.0, color='#1f77b4', alpha=0.8)
    ax2.plot(x_axis_filtered[mask_outside], ratio_lung_icrp[mask_outside], 
             linewidth=0, marker='o', markersize=3, color='#1f77b4', alpha=0.8)
    
    # Marcar punto justo antes de la heterogeneidad con un marcador diferente
    ax2.plot(x_axis_filtered[idx_edge], ratio_lung_icrp[idx_edge], 
             marker='s', markersize=5, color='red', markeredgecolor='darkred', 
             markeredgewidth=1, linestyle='none', zorder=5, label='Punto de discontinuidad')
    
    ax2.axvspan(hetero_x_min, hetero_x_max, alpha=0.15, color='yellow')
    ax2.axvline(hetero_x_min, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axvline(hetero_x_max, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axvline(0, color='red', linestyle=':', linewidth=1.5, alpha=0.6, label='Fuente')
    ax2.axhline(1.0, color='black', linestyle='-', linewidth=1.5, label='Referencia (1.0)')
    
    ax2.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Ratio (Hetero/Ref)', fontsize=11, fontweight='bold')
    ax2.set_title('Ratio: Lung ICRP Hetero / Water Homo', fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-15, 120)
    # Ajustar automáticamente al rango de datos
    y_min_2, y_max_2 = np.nanmin(ratio_lung_icrp), np.nanmax(ratio_lung_icrp)
    y_margin_2 = (y_max_2 - y_min_2) * 0.1
    ax2.set_ylim(max(0, y_min_2 - y_margin_2), y_max_2 + y_margin_2)
    
    # Panel 3: Ratio Lung Hueco Hetero / Water
    ax3 = plt.subplot(2, 2, 3)
    
    ax3.plot(x_axis_filtered[mask_hetero_region], ratio_lung_hueco[mask_hetero_region], 
             linewidth=2.0, color='#ff7f0e', alpha=0.8)
    ax3.plot(x_axis_filtered[mask_outside], ratio_lung_hueco[mask_outside], 
             linewidth=0, marker='o', markersize=3, color='#ff7f0e', alpha=0.8)
    
    # Marcar punto justo antes de la heterogeneidad con un marcador diferente
    ax3.plot(x_axis_filtered[idx_edge], ratio_lung_hueco[idx_edge], 
             marker='s', markersize=5, color='red', markeredgecolor='darkred', 
             markeredgewidth=1, linestyle='none', zorder=5)
    
    ax3.axvspan(hetero_x_min, hetero_x_max, alpha=0.15, color='yellow')
    ax3.axvline(hetero_x_min, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax3.axvline(hetero_x_max, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax3.axvline(0, color='red', linestyle=':', linewidth=1.5, alpha=0.6, label='Fuente')
    ax3.axhline(1.0, color='black', linestyle='-', linewidth=1.5, label='Referencia (1.0)')
    
    ax3.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Ratio (Hetero/Ref)', fontsize=11, fontweight='bold')
    ax3.set_title('Ratio: Lung Hueco Hetero / Water Homo', fontsize=12, fontweight='bold')
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(-15, 120)
    # Ajustar automáticamente al rango de datos
    y_min_3, y_max_3 = np.nanmin(ratio_lung_hueco), np.nanmax(ratio_lung_hueco)
    y_margin_3 = (y_max_3 - y_min_3) * 0.1
    ax3.set_ylim(max(0, y_min_3 - y_margin_3), y_max_3 + y_margin_3)
    
    # Panel 4: Ratio Bone Hetero / Water
    ax4 = plt.subplot(2, 2, 4)
    
    ax4.plot(x_axis_filtered[mask_hetero_region], ratio_bone[mask_hetero_region], 
             linewidth=2.0, color='#2ca02c', alpha=0.8)
    ax4.plot(x_axis_filtered[mask_outside], ratio_bone[mask_outside], 
             linewidth=0, marker='o', markersize=3, color='#2ca02c', alpha=0.8)
    
    # Marcar punto justo antes de la heterogeneidad con un marcador diferente
    ax4.plot(x_axis_filtered[idx_edge], ratio_bone[idx_edge], 
             marker='s', markersize=5, color='red', markeredgecolor='darkred', 
             markeredgewidth=1, linestyle='none', zorder=5)
    
    ax4.axvspan(hetero_x_min, hetero_x_max, alpha=0.15, color='yellow')
    ax4.axvline(hetero_x_min, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax4.axvline(hetero_x_max, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax4.axvline(0, color='red', linestyle=':', linewidth=1.5, alpha=0.6, label='Fuente')
    ax4.axhline(1.0, color='black', linestyle='-', linewidth=1.5, label='Referencia (1.0)')
    
    ax4.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Ratio (Hetero/Ref)', fontsize=11, fontweight='bold')
    ax4.set_title('Ratio: Bone Hetero / Water Homo', fontsize=12, fontweight='bold')
    ax4.legend(loc='best', fontsize=9)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(-15, 120)
    # Ajustar automáticamente al rango de datos
    y_min_4, y_max_4 = np.nanmin(ratio_bone), np.nanmax(ratio_bone)
    y_margin_4 = (y_max_4 - y_min_4) * 0.1
    ax4.set_ylim(max(0, y_min_4 - y_margin_4), y_max_4 + y_margin_4)
    
    plt.suptitle('Análisis de Perfiles Horizontales - I125 100M (Y=0, rango -15 a +120 mm)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, 'ratio_profiles_horizontal.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    
    # Estadísticas detalladas
    print("\n" + "="*80)
    print("ESTADÍSTICAS DE RATIOS (rango -120 a +120 mm, Y=0)")
    print("="*80)
    
    mask_hetero = (x_axis_filtered >= hetero_x_min) & (x_axis_filtered <= hetero_x_max)
    mask_water = ~mask_hetero
    
    for ratio_name, ratio_data in [("Lung ICRP Hetero", ratio_lung_icrp), 
                                     ("Lung Hueco Hetero", ratio_lung_hueco),
                                     ("Bone Hetero", ratio_bone)]:
        ratio_valid = ratio_data[ratio_data > 0]
        ratio_hetero_region = ratio_data[mask_hetero]
        ratio_water_region = ratio_data[mask_water]
        
        print(f"\n{ratio_name}:")
        if len(ratio_valid) > 0:
            print(f"  Total (donde hay datos):")
            print(f"    Ratio min: {np.min(ratio_valid):.4f}")
            print(f"    Ratio max: {np.max(ratio_valid):.4f}")
            print(f"    Ratio mean: {np.mean(ratio_valid):.4f}")
        
        hetero_valid = ratio_hetero_region[ratio_hetero_region > 0]
        if len(hetero_valid) > 0:
            print(f"  En heterogeneidad:")
            print(f"    Ratio min: {np.min(hetero_valid):.4f}")
            print(f"    Ratio max: {np.max(hetero_valid):.4f}")
            print(f"    Ratio mean: {np.mean(hetero_valid):.4f}")
        else:
            print(f"  En heterogeneidad: Sin datos (ratio=0)")
        
        water_valid = ratio_water_region[ratio_water_region > 0]
        if len(water_valid) > 0:
            print(f"  En agua (fuera):")
            print(f"    Ratio min: {np.min(water_valid):.4f}")
            print(f"    Ratio max: {np.max(water_valid):.4f}")
            print(f"    Ratio mean: {np.mean(water_valid):.4f}")
        else:
            print(f"  En agua (fuera): Sin datos")
    
    print("\n" + "="*80 + "\n")
    
    plt.show()

if __name__ == "__main__":
    main()

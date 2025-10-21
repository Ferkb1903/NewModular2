#!/usr/bin/env python3
"""
Análisis de Perfiles Horizontales de Dosis Convertida
Braquiterapia I125 (200M)
Genera 3 imágenes separadas: perfiles, ratio bone, ratio lung
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/200M_I125"
HISTOGRAM_NAME = "h20;1"

# Casos de simulación
CASES = {
    "Water_Homo": "brachytherapy_water_homo200m.root",
    "Bone_Hetero": "brachytherapy_Bone_Hetero200m.root",
    "Lung_Hetero": "brachytherapy_Lung_Hetero200m.root"
}

# Densidades base
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 1.05  # 64_LUNG_ICRP

# Tamaño de bins
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

# Parámetros de heterogeneidad
HETERO_SIZE = 60.0
HETERO_POS_X = 40.0
HETERO_POS_Y = 0.0

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
    """Crea un mapa de densidad considerando la región de heterogeneidad"""
    density_map = np.ones(shape, dtype=float) * DENSITY_WATER
    
    if case_name == "Bone_Hetero":
        hetero_density = DENSITY_BONE
    elif case_name == "Lung_Hetero":
        hetero_density = DENSITY_LUNG
    else:
        return density_map
    
    x_min = HETERO_POS_X - HETERO_SIZE / 2
    x_max = HETERO_POS_X + HETERO_SIZE / 2
    y_min = HETERO_POS_Y - HETERO_SIZE / 2
    y_max = HETERO_POS_Y + HETERO_SIZE / 2
    
    scale_factor = 300 / 301.0
    offset = -150.5
    
    x_min_bin = int((x_min - offset) * scale_factor)
    x_max_bin = int((x_max - offset) * scale_factor)
    y_min_bin = int((y_min - offset) * scale_factor)
    y_max_bin = int((y_max - offset) * scale_factor)
    
    x_min_bin = max(0, min(x_min_bin, shape[0]))
    x_max_bin = max(0, min(x_max_bin, shape[0]))
    y_min_bin = max(0, min(y_min_bin, shape[1]))
    y_max_bin = max(0, min(y_max_bin, shape[1]))
    
    density_map[x_min_bin:x_max_bin, y_min_bin:y_max_bin] = hetero_density
    
    return density_map

def edep_to_dose_sectional(edep_values, case_name):
    """Convierte edep a dosis por secciones"""
    density_map = create_density_map(edep_values.shape, case_name)
    density_map[density_map == 0] = DENSITY_WATER
    dose_mgy = edep_values * 1.602e-4 / (BIN_VOLUME * density_map)
    return dose_mgy

def extract_horizontal_profiles(dose_maps, case_names):
    """Extrae perfiles horizontales en Y=0 (línea central)"""
    profiles = {}
    
    # Y=0 corresponde al índice 150 (300/2)
    center_y = 150
    
    for case_name, dose_map in dose_maps.items():
        profile = dose_map[:, center_y]
        profiles[case_name] = profile
    
    return profiles

def get_x_axis_mm(num_bins=300):
    """Retorna el eje X en milímetros"""
    x_min = -150.5
    x_max = 150.5
    x_mm = np.linspace(x_min, x_max, num_bins)
    return x_mm

def filter_data_range(x_axis, profiles, x_max_range=120):
    """Filtra datos al rango [-x_max_range, +x_max_range] mm"""
    mask = (x_axis >= -x_max_range) & (x_axis <= x_max_range)
    x_filtered = x_axis[mask]
    
    profiles_filtered = {}
    for case_name, profile in profiles.items():
        profiles_filtered[case_name] = profile[mask]
    
    return x_filtered, profiles_filtered

def plot_perfiles_dosis():
    """Crea gráfica de perfiles de dosis"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Cargar histogramas
    histograms = {}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Cargando: {case_name}...", end=" ")
        
        hist = load_histogram(filepath, HISTOGRAM_NAME)
        if hist is None:
            print("❌")
            continue
        
        histograms[case_name] = hist.values()
        print("✅")
    
    # Convertir a dosis
    print("Convirtiendo a dosis...", end=" ")
    dose_maps = {}
    for case_name in CASES.keys():
        if case_name in histograms:
            dose_maps[case_name] = edep_to_dose_sectional(histograms[case_name], case_name)
    print("✅")
    
    # Extraer perfiles
    print("Extrayendo perfiles...", end=" ")
    profiles = extract_horizontal_profiles(dose_maps, CASES.keys())
    x_axis = get_x_axis_mm()
    x_axis_filtered, profiles_filtered = filter_data_range(x_axis, profiles, x_max_range=120)
    print("✅")
    
    # Plotear
    for case_name, profile in profiles_filtered.items():
        ax.plot(x_axis_filtered, profile, linewidth=2.5, label=case_name, marker='o', markersize=3, alpha=0.7)
    
    ax.axvline(HETERO_POS_X - HETERO_SIZE / 2, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Bordes heterogeneidad')
    ax.axvline(HETERO_POS_X + HETERO_SIZE / 2, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axhline(0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)
    
    ax.set_xlabel('X (mm)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Dosis (mGy)', fontsize=12, fontweight='bold')
    ax.set_title('Perfiles Horizontales de Dosis Convertida (Y=0)', fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    ax.set_xlim(-120, 120)
    
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '1_perfiles_dosis.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}\n")
    plt.close()

def plot_ratio_bone():
    """Crea gráfica de ratio Bone/Water"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Cargar histogramas
    histograms = {}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Cargando: {case_name}...", end=" ")
        
        hist = load_histogram(filepath, HISTOGRAM_NAME)
        if hist is None:
            print("❌")
            continue
        
        histograms[case_name] = hist.values()
        print("✅")
    
    # Convertir a dosis
    print("Convirtiendo a dosis...", end=" ")
    dose_maps = {}
    for case_name in CASES.keys():
        if case_name in histograms:
            dose_maps[case_name] = edep_to_dose_sectional(histograms[case_name], case_name)
    print("✅")
    
    # Extraer perfiles
    print("Extrayendo perfiles...", end=" ")
    profiles = extract_horizontal_profiles(dose_maps, CASES.keys())
    x_axis = get_x_axis_mm()
    x_axis_filtered, profiles_filtered = filter_data_range(x_axis, profiles, x_max_range=120)
    print("✅")
    
    # Calcular ratio
    ratio_bone = np.divide(profiles_filtered["Bone_Hetero"], profiles_filtered["Water_Homo"],
                           where=profiles_filtered["Water_Homo"] > 0,
                           out=np.ones_like(profiles_filtered["Water_Homo"]))
    
    # Plotear
    ax.plot(x_axis_filtered, ratio_bone, linewidth=2.5, color='brown', label='Bone/Water', marker='o', markersize=3, alpha=0.7)
    ax.axvline(HETERO_POS_X - HETERO_SIZE / 2, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Bordes heterogeneidad')
    ax.axvline(HETERO_POS_X + HETERO_SIZE / 2, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axhline(1.0, color='red', linestyle='-', linewidth=1.5, label='Referencia (1.0)')
    
    ax.set_xlabel('X (mm)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Ratio (Hetero/Water)', fontsize=12, fontweight='bold')
    ax.set_title('Ratio: Bone_Hetero / Water_Homo', fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-120, 120)
    
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '2_ratio_bone_water.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfica guardada: {output_file}\n")
    plt.close()

def plot_ratio_lung():
    """Crea gráfica de ratio Lung/Water"""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Cargar histogramas
    histograms = {}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Cargando: {case_name}...", end=" ")
        
        hist = load_histogram(filepath, HISTOGRAM_NAME)
        if hist is None:
            print("❌")
            continue
        
        histograms[case_name] = hist.values()
        print("✅")
    
    # Convertir a dosis
    print("Convirtiendo a dosis...", end=" ")
    dose_maps = {}
    for case_name in CASES.keys():
        if case_name in histograms:
            dose_maps[case_name] = edep_to_dose_sectional(histograms[case_name], case_name)
    print("✅")
    
    # Extraer perfiles
    print("Extrayendo perfiles...", end=" ")
    profiles = extract_horizontal_profiles(dose_maps, CASES.keys())
    x_axis = get_x_axis_mm()
    x_axis_filtered, profiles_filtered = filter_data_range(x_axis, profiles, x_max_range=120)
    print("✅")
    
    # Calcular ratio
    ratio_lung = np.divide(profiles_filtered["Lung_Hetero"], profiles_filtered["Water_Homo"],
                          where=profiles_filtered["Water_Homo"] > 0,
                          out=np.ones_like(profiles_filtered["Water_Homo"]))
    
    # Plotear
    ax.plot(x_axis_filtered, ratio_lung, linewidth=2.5, color='green', label='Lung/Water', marker='o', markersize=3, alpha=0.7)
    ax.axvline(HETERO_POS_X - HETERO_SIZE / 2, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Bordes heterogeneidad')
    ax.axvline(HETERO_POS_X + HETERO_SIZE / 2, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axhline(1.0, color='red', linestyle='-', linewidth=1.5, label='Referencia (1.0)')
    
    ax.set_xlabel('X (mm)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Ratio (Hetero/Water)', fontsize=12, fontweight='bold')
    ax.set_title('Ratio: Lung_Hetero / Water_Homo', fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-120, 120)
    
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '3_ratio_lung_water.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfica guardada: {output_file}\n")
    plt.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ANÁLISIS DE PERFILES HORIZONTALES - I125 200M")
    print("="*70 + "\n")
    
    print("1. Generando gráfica de perfiles de dosis...")
    plot_perfiles_dosis()
    
    print("2. Generando gráfica de ratio Bone/Water...")
    plot_ratio_bone()
    
    print("3. Generando gráfica de ratio Lung/Water...")
    plot_ratio_lung()
    
    print("="*70)
    print("✅ TODAS LAS GRÁFICAS GENERADAS EXITOSAMENTE")
    print("="*70 + "\n")

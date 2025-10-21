#!/usr/bin/env python3
"""
Análisis de Partículas Primarias y Secundarias
Braquiterapia I125 (100M) - Casos Homogéneos
Comparación de edep por tipo de partícula
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
HIST_TOTAL = "h20;1"
HIST_PRIMARY = "h2_eDepPrimary;1"
HIST_SECONDARY = "h2_eDepSecondary;1"

# Casos de simulación (homogéneos)
CASES = {
    "Water": "brachytherapy_homo_water100m.root",
    "Bone": "brachytherapy_homo_bone100m.root",
    "Lung": "brachytherapy_homo_lung100m.root"
}

# Densidades
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 0.26

# Tamaño de bins
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

def load_histogram(filepath, hist_name):
    """Carga un histograma 2D de un archivo ROOT"""
    try:
        with uproot.open(filepath) as file:
            if hist_name in file:
                hist = file[hist_name]
                return hist.values()
            else:
                return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def edep_to_dose(edep_values, density):
    """Convierte edep a dosis (mGy)"""
    mass_g = BIN_VOLUME * density
    dose_mgy = edep_values * 1.602e-4 / mass_g
    return dose_mgy

def extract_horizontal_profiles(data_2d):
    """Extrae perfil horizontal en Y=0"""
    center_y = 150
    return data_2d[:, center_y]

def get_x_axis_mm(num_bins=300):
    """Retorna el eje X en milímetros"""
    x_min = -150.5
    x_max = 150.5
    x_mm = np.linspace(x_min, x_max, num_bins)
    return x_mm

def filter_data_range(x_axis, profile, x_max_range=120):
    """Filtra datos al rango [-x_max_range, +x_max_range] mm"""
    mask = (x_axis >= -x_max_range) & (x_axis <= x_max_range)
    return x_axis[mask], profile[mask]

def plot_primary_secondary_analysis():
    """Analiza primarias y secundarias para cada caso homogéneo"""
    
    fig = plt.figure(figsize=(18, 5))
    
    x_axis = get_x_axis_mm()
    densities = {
        "Water": DENSITY_WATER,
        "Bone": DENSITY_BONE,
        "Lung": DENSITY_LUNG
    }
    
    for idx, (case_name, filename) in enumerate(CASES.items()):
        print(f"\nProcesando: {case_name}...", end=" ")
        
        filepath_total = os.path.join(DATA_DIR, filename)
        
        # Construir rutas con los nombres correctos (hay espacios en algunos nombres)
        if case_name == "Bone":
            filepath_primary = os.path.join(DATA_DIR, "brachytherapy_eDepPrimary_homo_bone100m.root")
            filepath_secondary = os.path.join(DATA_DIR, "brachytherapy_eDepSecondary_homo_ bone100m.root")
        elif case_name == "Water":
            filepath_primary = os.path.join(DATA_DIR, "brachytherapy_eDepPrimary_homo_water100m.root")
            filepath_secondary = os.path.join(DATA_DIR, "brachytherapy_eDepSecondary_homo_water100m.root")
        elif case_name == "Lung":
            filepath_primary = os.path.join(DATA_DIR, "brachytherapy_eDepPrimary_homo_lung100m.root")
            filepath_secondary = os.path.join(DATA_DIR, "brachytherapy_eDepSecondary_homo_lung100m.root")
        
        # Cargar histogramas
        edep_total = load_histogram(filepath_total, HIST_TOTAL)
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_total is None:
            print("❌ Error cargando total")
            continue
        
        if edep_primary is None:
            print("❌ Error cargando primary")
            continue
        
        if edep_secondary is None:
            print("❌ Error cargando secondary")
            continue
        
        print("✅")
        
        # Convertir a dosis
        density = densities[case_name]
        dose_total = edep_to_dose(edep_total, density)
        dose_primary = edep_to_dose(edep_primary, density)
        dose_secondary = edep_to_dose(edep_secondary, density)
        
        # Extraer perfiles
        profile_total = extract_horizontal_profiles(dose_total)
        profile_primary = extract_horizontal_profiles(dose_primary)
        profile_secondary = extract_horizontal_profiles(dose_secondary)
        
        # Filtrar al rango [-120, +120] mm
        x_filtered, profile_total_f = filter_data_range(x_axis, profile_total, 120)
        _, profile_primary_f = filter_data_range(x_axis, profile_primary, 120)
        _, profile_secondary_f = filter_data_range(x_axis, profile_secondary, 120)
        
        # Plotear
        ax = plt.subplot(1, 3, idx + 1)
        
        ax.plot(x_filtered, profile_total_f, linewidth=2.5, label='Total', marker='o', markersize=2, alpha=0.8)
        ax.plot(x_filtered, profile_primary_f, linewidth=2.5, label='Primary', marker='s', markersize=2, alpha=0.8)
        ax.plot(x_filtered, profile_secondary_f, linewidth=2.5, label='Secondary', marker='^', markersize=2, alpha=0.8)
        
        ax.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Dosis (mGy)', fontsize=11, fontweight='bold')
        ax.set_title(f'{case_name} Homogéneo\n(ρ={density} g/cm³)', fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        ax.set_xlim(-120, 120)
    
    plt.suptitle('Análisis de Primarias y Secundarias - I125 100M (Casos Homogéneos)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '0_primary_secondary_profiles.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}\n")
    plt.close()

def plot_contribution_ratios():
    """Calcula ratios de contribución: Primary/Total, Secondary/Total"""
    
    fig = plt.figure(figsize=(18, 5))
    
    x_axis = get_x_axis_mm()
    densities = {
        "Water": DENSITY_WATER,
        "Bone": DENSITY_BONE,
        "Lung": DENSITY_LUNG
    }
    
    for idx, (case_name, filename) in enumerate(CASES.items()):
        print(f"Calculando contribuciones: {case_name}...", end=" ")
        
        filepath_total = os.path.join(DATA_DIR, filename)
        
        # Construir rutas con los nombres correctos (hay espacios en algunos nombres)
        if case_name == "Bone":
            filepath_primary = os.path.join(DATA_DIR, "brachytherapy_eDepPrimary_homo_bone100m.root")
            filepath_secondary = os.path.join(DATA_DIR, "brachytherapy_eDepSecondary_homo_ bone100m.root")
        elif case_name == "Water":
            filepath_primary = os.path.join(DATA_DIR, "brachytherapy_eDepPrimary_homo_water100m.root")
            filepath_secondary = os.path.join(DATA_DIR, "brachytherapy_eDepSecondary_homo_water100m.root")
        elif case_name == "Lung":
            filepath_primary = os.path.join(DATA_DIR, "brachytherapy_eDepPrimary_homo_lung100m.root")
            filepath_secondary = os.path.join(DATA_DIR, "brachytherapy_eDepSecondary_homo_lung100m.root")
        
        # Cargar histogramas
        edep_total = load_histogram(filepath_total, HIST_TOTAL)
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_total is None or edep_primary is None or edep_secondary is None:
            print("❌")
            continue
        
        print("✅")
        
        # Convertir a dosis
        density = densities[case_name]
        dose_total = edep_to_dose(edep_total, density)
        dose_primary = edep_to_dose(edep_primary, density)
        dose_secondary = edep_to_dose(edep_secondary, density)
        
        # Extraer perfiles
        profile_total = extract_horizontal_profiles(dose_total)
        profile_primary = extract_horizontal_profiles(dose_primary)
        profile_secondary = extract_horizontal_profiles(dose_secondary)
        
        # Filtrar al rango [-120, +120] mm
        x_filtered, profile_total_f = filter_data_range(x_axis, profile_total, 120)
        _, profile_primary_f = filter_data_range(x_axis, profile_primary, 120)
        _, profile_secondary_f = filter_data_range(x_axis, profile_secondary, 120)
        
        # Calcular ratios
        ratio_primary = np.divide(profile_primary_f, profile_total_f,
                                 where=profile_total_f > 0,
                                 out=np.zeros_like(profile_total_f))
        ratio_secondary = np.divide(profile_secondary_f, profile_total_f,
                                   where=profile_total_f > 0,
                                   out=np.zeros_like(profile_total_f))
        
        # Plotear
        ax = plt.subplot(1, 3, idx + 1)
        
        ax.plot(x_filtered, ratio_primary, linewidth=2.5, label='Primary/Total', marker='o', markersize=2, alpha=0.8)
        ax.plot(x_filtered, ratio_secondary, linewidth=2.5, label='Secondary/Total', marker='s', markersize=2, alpha=0.8)
        ax.axhline(0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% ref')
        
        ax.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Razón de Contribución', fontsize=11, fontweight='bold')
        ax.set_title(f'{case_name} - Contribuciones', fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-120, 120)
        ax.set_ylim(0, 1.05)
    
    plt.suptitle('Razones de Contribución (Primary/Total, Secondary/Total) - I125 100M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '1_contribution_ratios.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfica guardada: {output_file}\n")
    plt.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ANÁLISIS DE PRIMARIAS Y SECUNDARIAS - I125 100M (HOMOGÉNEOS)")
    print("="*70 + "\n")
    
    print("1. Generando perfiles de primarias y secundarias...")
    plot_primary_secondary_analysis()
    
    print("2. Generando ratios de contribución...")
    plot_contribution_ratios()
    
    print("="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70 + "\n")

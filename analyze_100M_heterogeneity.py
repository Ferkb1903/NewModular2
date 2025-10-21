#!/usr/bin/env python3
"""
Análisis Completo de Heterogeneidad - I125 100M
Comparación: Homo vs Hetero para Bone y Lung
Incluye: Primarias, Secundarias, Regionales, Ratios, Perfiles
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
HIST_PRIMARY = "h2_eDepPrimary;1"
HIST_SECONDARY = "h2_eDepSecondary;1"
HIST_TOTAL = "h20;1"

# Archivos disponibles
FILES = {
    # Homogéneos
    "Water_Homo_Primary": "brachytherapy_eDepPrimary_homo_water100m.root",
    "Water_Homo_Secondary": "brachytherapy_eDepSecondary_homo_water100m.root",
    "Water_Homo_Total": "brachytherapy_homo_water100m.root",
    
    "Bone_Homo_Primary": "brachytherapy_eDepPrimary_homo_bone100m.root",
    "Bone_Homo_Secondary": "brachytherapy_eDepSecondary_homo_bone100m.root",
    "Bone_Homo_Total": "brachytherapy_homo_bone100m.root",
    
    "Lung_Homo_Primary": "brachytherapy_eDepPrimary_homo_lung100m.root",
    "Lung_Homo_Secondary": "brachytherapy_eDepSecondary_homo_lung100m.root",
    "Lung_Homo_Total": "brachytherapy_homo_lung100m.root",
    
    # Heterogéneos
    "Bone_Hetero_Primary": "brachytherapy_eDepPrimary_hetero_bone100m.root",
    "Bone_Hetero_Secondary": "brachytherapy_eDepSecondary_hetero_bone100m.root",
    "Bone_Hetero_Total": "brachytherapy_hetero_bone100m.root",
    
    "Lung_Hetero_Primary": "brachytherapy_eDepPrimary_hetero_lung100m.root",
    "Lung_Hetero_Secondary": "brachytherapy_eDepSecondary_hetero_lung100m.root",
    "Lung_Hetero_Total": "brachytherapy_hetero_lung100m.root",
}

# Densidades (g/cm³) - ICRP
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 1.05  # ICRP (no 0.26 - ese era incorrecto)

# Parámetros de conversión
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

# Parámetros de heterogeneidad
HETERO_SIZE = 60.0  # mm (6.0 cm)
HETERO_POS_X = 40.0  # mm
HETERO_POS_Y = 0.0   # mm

def get_density_for_material(material_name):
    """Retorna densidad basada en nombre de material"""
    if "Water" in material_name:
        return DENSITY_WATER
    elif "Bone" in material_name:
        return DENSITY_BONE
    elif "Lung" in material_name:
        return DENSITY_LUNG
    return DENSITY_WATER

def load_histogram(filepath, hist_name):
    """Carga un histograma 2D de un archivo ROOT"""
    try:
        with uproot.open(filepath) as file:
            if hist_name in file:
                hist = file[hist_name]
                return hist.values()
            else:
                print(f"❌ Histograma {hist_name} no encontrado")
                return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def edep_to_dose_gy(edep_values, density):
    """Convierte energía depositada (MeV) a dosis (Gy)
    
    Dosis (Gy) = edep (MeV) * 1.602e-10 / (volumen cm³ * densidad g/cm³)
    """
    mass_g = BIN_VOLUME * density
    dose_gy = edep_values * 1.602e-10 / mass_g
    return dose_gy

def create_density_map(shape, case_name):
    """Crea un mapa de densidad considerando la región de heterogeneidad"""
    density_map = np.ones(shape, dtype=float) * DENSITY_WATER
    
    if "Bone_Hetero" in case_name:
        hetero_density = DENSITY_BONE
    elif "Lung_Hetero" in case_name:
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

def analyze_homo_vs_hetero_maps():
    """Análisis visual: Homo vs Hetero (Mapas 2D)"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS 1: MAPAS 2D - HOMO vs HETERO (100M)")
    print("="*70 + "\n")
    
    materials = ["Bone", "Lung"]
    
    fig = plt.figure(figsize=(16, 10))
    
    for mat_idx, material in enumerate(materials):
        # Cargar datos
        homo_key = f"{material}_Homo_Total"
        hetero_key = f"{material}_Hetero_Total"
        
        homo_file = os.path.join(DATA_DIR, FILES[homo_key])
        hetero_file = os.path.join(DATA_DIR, FILES[hetero_key])
        
        print(f"Cargando {material} Homo...", end=" ")
        homo_edep = load_histogram(homo_file, HIST_TOTAL)
        if homo_edep is None:
            print("❌")
            continue
        print("✅")
        
        print(f"Cargando {material} Hetero...", end=" ")
        hetero_edep = load_histogram(hetero_file, HIST_TOTAL)
        if hetero_edep is None:
            print("❌")
            continue
        print("✅")
        
        density = get_density_for_material(homo_key)
        homo_dose = edep_to_dose_gy(homo_edep, density)
        hetero_dose = edep_to_dose_gy(hetero_edep, density)
        
        # Panel Homo
        ax_homo = plt.subplot(2, 2, mat_idx * 2 + 1)
        homo_log = np.copy(homo_dose).astype(float)
        homo_log[homo_log <= 0] = np.min(homo_log[homo_log > 0]) / 10
        
        im_homo = ax_homo.imshow(
            homo_log.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=homo_log.min(), vmax=homo_log.max())
        )
        ax_homo.set_title(f'{material} Homogéneo (100M)', fontsize=12, fontweight='bold')
        ax_homo.set_xlabel('X (bins)')
        ax_homo.set_ylabel('Y (bins)')
        plt.colorbar(im_homo, ax=ax_homo, label='Dosis (Gy)')
        
        # Panel Hetero
        ax_hetero = plt.subplot(2, 2, mat_idx * 2 + 2)
        hetero_log = np.copy(hetero_dose).astype(float)
        hetero_log[hetero_log <= 0] = np.min(hetero_log[hetero_log > 0]) / 10
        
        im_hetero = ax_hetero.imshow(
            hetero_log.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=hetero_log.min(), vmax=hetero_log.max())
        )
        ax_hetero.set_title(f'{material} Heterogéneo (100M)', fontsize=12, fontweight='bold')
        ax_hetero.set_xlabel('X (bins)')
        ax_hetero.set_ylabel('Y (bins)')
        plt.colorbar(im_hetero, ax=ax_hetero, label='Dosis (Gy)')
        draw_heterogeneity(ax_hetero)
    
    plt.suptitle('Comparación: Homogéneo vs Heterogéneo - I125 100M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output = os.path.join(DATA_DIR, '1_homo_vs_hetero_maps.png')
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output}\n")
    plt.close()

def analyze_primary_vs_secondary_hetero():
    """Análisis visual: Primary vs Secondary en casos heterogéneos"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS 2: PRIMARIAS vs SECUNDARIAS - HETERO (100M)")
    print("="*70 + "\n")
    
    materials = ["Bone_Hetero", "Lung_Hetero"]
    
    fig = plt.figure(figsize=(14, 10))
    
    for mat_idx, material in enumerate(materials):
        pri_key = f"{material}_Primary"
        sec_key = f"{material}_Secondary"
        
        pri_file = os.path.join(DATA_DIR, FILES[pri_key])
        sec_file = os.path.join(DATA_DIR, FILES[sec_key])
        
        print(f"Cargando {material} Primary...", end=" ")
        pri_edep = load_histogram(pri_file, HIST_PRIMARY)
        if pri_edep is None:
            print("❌")
            continue
        print("✅")
        
        print(f"Cargando {material} Secondary...", end=" ")
        sec_edep = load_histogram(sec_file, HIST_SECONDARY)
        if sec_edep is None:
            print("❌")
            continue
        print("✅")
        
        density = get_density_for_material(material)
        pri_dose = edep_to_dose_gy(pri_edep, density)
        sec_dose = edep_to_dose_gy(sec_edep, density)
        
        # Panel Primary
        ax_pri = plt.subplot(2, 2, mat_idx * 2 + 1)
        pri_log = np.copy(pri_dose).astype(float)
        pri_log[pri_log <= 0] = np.min(pri_log[pri_log > 0]) / 10
        
        im_pri = ax_pri.imshow(
            pri_log.T,
            aspect='auto',
            origin='lower',
            cmap='viridis',
            norm=colors.LogNorm(vmin=pri_log.min(), vmax=pri_log.max())
        )
        ax_pri.set_title(f'{material.replace("_", " ")} - Primarias', fontsize=12, fontweight='bold')
        ax_pri.set_xlabel('X (bins)')
        ax_pri.set_ylabel('Y (bins)')
        plt.colorbar(im_pri, ax=ax_pri, label='Dosis (Gy)')
        
        # Panel Secondary
        ax_sec = plt.subplot(2, 2, mat_idx * 2 + 2)
        sec_log = np.copy(sec_dose).astype(float)
        sec_log[sec_log <= 0] = np.min(sec_log[sec_log > 0]) / 10
        
        im_sec = ax_sec.imshow(
            sec_log.T,
            aspect='auto',
            origin='lower',
            cmap='plasma',
            norm=colors.LogNorm(vmin=sec_log.min(), vmax=sec_log.max())
        )
        ax_sec.set_title(f'{material.replace("_", " ")} - Secundarias', fontsize=12, fontweight='bold')
        ax_sec.set_xlabel('X (bins)')
        ax_sec.set_ylabel('Y (bins)')
        plt.colorbar(im_sec, ax=ax_sec, label='Dosis (Gy)')
        draw_heterogeneity(ax_sec)
    
    plt.suptitle('Primarias vs Secundarias - Casos Heterogéneos (100M)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output = os.path.join(DATA_DIR, '2_primary_vs_secondary_hetero.png')
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output}\n")
    plt.close()

def analyze_regional_hetero_impact():
    """Análisis regional: impacto de heterogeneidad por zonas"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS 3: IMPACTO REGIONAL DE HETEROGENEIDAD (100M)")
    print("="*70 + "\n")
    
    materials = ["Bone", "Lung"]
    center = 150
    
    regions = {
        '0-5 mm': (0, 5),
        '5-10 mm': (5, 10),
        '10-30 mm': (10, 30),
        '30-50 mm': (30, 50),
        '50-150 mm': (50, 150)
    }
    
    for material in materials:
        print(f"\n{'='*70}")
        print(f"MATERIAL: {material}")
        print(f"{'='*70}")
        
        homo_key = f"{material}_Homo_Total"
        hetero_key = f"{material}_Hetero_Total"
        
        homo_file = os.path.join(DATA_DIR, FILES[homo_key])
        hetero_file = os.path.join(DATA_DIR, FILES[hetero_key])
        
        homo_edep = load_histogram(homo_file, HIST_TOTAL)
        hetero_edep = load_histogram(hetero_file, HIST_TOTAL)
        
        if homo_edep is None or hetero_edep is None:
            continue
        
        density = get_density_for_material(homo_key)
        homo_dose = edep_to_dose_gy(homo_edep, density)
        hetero_dose = edep_to_dose_gy(hetero_edep, density)
        
        print(f"\nDistribución por regiones")
        print(f"{'Región':<12} {'Homo Energy':<18} {'Hetero Energy':<18} {'Ratio E':<12} {'Homo Dose':<18} {'Hetero Dose':<18} {'Ratio D':<12}")
        print("-" * 120)
        
        for region_name, (r_min, r_max) in regions.items():
            # Crear máscara circular
            y_grid, x_grid = np.ogrid[:300, :300]
            dist = np.sqrt((x_grid - center)**2 + (y_grid - center)**2)
            mask = (dist >= r_min) & (dist < r_max)
            
            # Energía
            homo_energy = np.sum(homo_edep[mask])
            hetero_energy = np.sum(hetero_edep[mask])
            
            # Dosis
            homo_dose_sum = np.sum(homo_dose[mask])
            hetero_dose_sum = np.sum(hetero_dose[mask])
            
            # Ratios
            ratio_e = hetero_energy / homo_energy if homo_energy > 0 else 0
            ratio_d = hetero_dose_sum / homo_dose_sum if homo_dose_sum > 0 else 0
            
            print(f"{region_name:<12} {homo_energy:<18.3e} {hetero_energy:<18.3e} {ratio_e:<12.4f} {homo_dose_sum:<18.3e} {hetero_dose_sum:<18.3e} {ratio_d:<12.4f}")

def analyze_secondary_influence_hetero():
    """Análisis de influencia secundaria en casos heterogéneos"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS 4: INFLUENCIA DE SECUNDARIAS - HETERO (100M)")
    print("="*70 + "\n")
    
    materials = ["Bone_Hetero", "Lung_Hetero"]
    
    for material in materials:
        print(f"\n{material}:")
        print("-" * 70)
        
        pri_key = f"{material}_Primary"
        sec_key = f"{material}_Secondary"
        
        pri_file = os.path.join(DATA_DIR, FILES[pri_key])
        sec_file = os.path.join(DATA_DIR, FILES[sec_key])
        
        pri_edep = load_histogram(pri_file, HIST_PRIMARY)
        sec_edep = load_histogram(sec_file, HIST_SECONDARY)
        
        if pri_edep is None or sec_edep is None:
            continue
        
        density = get_density_for_material(material)
        pri_dose = edep_to_dose_gy(pri_edep, density)
        sec_dose = edep_to_dose_gy(sec_edep, density)
        
        # Energías totales
        pri_energy_total = np.sum(pri_edep)
        sec_energy_total = np.sum(sec_edep)
        total_energy = pri_energy_total + sec_energy_total
        
        # Dosis totales
        pri_dose_total = np.sum(pri_dose)
        sec_dose_total = np.sum(sec_dose)
        total_dose = pri_dose_total + sec_dose_total
        
        # Porcentajes
        sec_energy_pct = (sec_energy_total / total_energy) * 100 if total_energy > 0 else 0
        sec_dose_pct = (sec_dose_total / total_dose) * 100 if total_dose > 0 else 0
        
        print(f"  Energía Total: {total_energy:.3e} MeV")
        print(f"    - Primaria: {pri_energy_total:.3e} MeV ({100-sec_energy_pct:.1f}%)")
        print(f"    - Secundaria: {sec_energy_total:.3e} MeV ({sec_energy_pct:.1f}%)")
        print(f"\n  Dosis Total: {total_dose:.3e} Gy")
        print(f"    - Primaria: {pri_dose_total:.3e} Gy ({100-sec_dose_pct:.1f}%)")
        print(f"    - Secundaria: {sec_dose_total:.3e} Gy ({sec_dose_pct:.1f}%)")

def analyze_hetero_impact_percentage():
    """Análisis: Porcentaje de cambio por heterogeneidad"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS 5: IMPACTO PORCENTUAL DE HETEROGENEIDAD (100M)")
    print("="*70 + "\n")
    
    materials = ["Bone", "Lung"]
    
    for material in materials:
        print(f"\n{material}:")
        print("-" * 70)
        
        homo_key = f"{material}_Homo_Total"
        hetero_key = f"{material}_Hetero_Total"
        
        homo_file = os.path.join(DATA_DIR, FILES[homo_key])
        hetero_file = os.path.join(DATA_DIR, FILES[hetero_key])
        
        homo_edep = load_histogram(homo_file, HIST_TOTAL)
        hetero_edep = load_histogram(hetero_file, HIST_TOTAL)
        
        if homo_edep is None or hetero_edep is None:
            continue
        
        density = get_density_for_material(homo_key)
        homo_dose = edep_to_dose_gy(homo_edep, density)
        hetero_dose = edep_to_dose_gy(hetero_edep, density)
        
        # Energía
        homo_energy = np.sum(homo_edep)
        hetero_energy = np.sum(hetero_edep)
        energy_change = ((hetero_energy - homo_energy) / homo_energy) * 100
        
        # Dosis
        homo_dose_sum = np.sum(homo_dose)
        hetero_dose_sum = np.sum(hetero_dose)
        dose_change = ((hetero_dose_sum - homo_dose_sum) / homo_dose_sum) * 100
        
        # Distribución espacial
        homo_nonzero = homo_dose[homo_dose > 0]
        hetero_nonzero = hetero_dose[hetero_dose > 0]
        
        print(f"  Energía total:")
        print(f"    Homo: {homo_energy:.3e} MeV")
        print(f"    Hetero: {hetero_energy:.3e} MeV")
        print(f"    Cambio: {energy_change:+.2f}%")
        
        print(f"\n  Dosis total:")
        print(f"    Homo: {homo_dose_sum:.3e} Gy")
        print(f"    Hetero: {hetero_dose_sum:.3e} Gy")
        print(f"    Cambio: {dose_change:+.2f}%")
        
        print(f"\n  Dosis promedio (píxeles no-cero):")
        print(f"    Homo: {np.mean(homo_nonzero):.3e} Gy")
        print(f"    Hetero: {np.mean(hetero_nonzero):.3e} Gy")
        print(f"    Cambio: {((np.mean(hetero_nonzero) - np.mean(homo_nonzero)) / np.mean(homo_nonzero)) * 100:+.2f}%")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ANÁLISIS COMPLETO: HETEROGENEIDAD - I125 100M")
    print("="*70 + "\n")
    
    # Ejecutar análisis
    analyze_homo_vs_hetero_maps()
    analyze_primary_vs_secondary_hetero()
    analyze_regional_hetero_impact()
    analyze_secondary_influence_hetero()
    analyze_hetero_impact_percentage()
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70 + "\n")

#!/usr/bin/env python3
"""
Análisis Avanzado de Heterogeneidad - I125 100M
Perfiles, diferencias, ratios y análisis regional detallado
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
HIST_TOTAL = "h20;1"

# Archivos
FILES = {
    "Bone_Homo_Total": "brachytherapy_homo_bone100m.root",
    "Bone_Hetero_Total": "brachytherapy_hetero_bone100m.root",
    "Lung_Homo_Total": "brachytherapy_homo_lung100m.root",
    "Lung_Hetero_Total": "brachytherapy_hetero_lung100m.root",
}

# Densidades
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 1.05  # ICRP (no 0.26)

# Parámetros
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

HETERO_SIZE = 60.0
HETERO_POS_X = 40.0
HETERO_POS_Y = 0.0

def get_density_for_material(material_name):
    """Retorna densidad"""
    if "Bone" in material_name:
        return DENSITY_BONE
    elif "Lung" in material_name:
        return DENSITY_LUNG
    return DENSITY_WATER

def load_histogram(filepath):
    """Carga histograma"""
    try:
        with uproot.open(filepath) as file:
            if HIST_TOTAL in file:
                return file[HIST_TOTAL].values()
    except:
        pass
    return None

def edep_to_dose_gy(edep_values, density):
    """Convierte edep a dosis"""
    mass_g = BIN_VOLUME * density
    return edep_values * 1.602e-10 / mass_g

def analyze_difference_maps():
    """Crea mapas de diferencia Hetero - Homo"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS: MAPAS DE DIFERENCIA - HETERO - HOMO (100M)")
    print("="*70 + "\n")
    
    fig = plt.figure(figsize=(14, 10))
    
    for mat_idx, material in enumerate(["Bone", "Lung"]):
        homo_key = f"{material}_Homo_Total"
        hetero_key = f"{material}_Hetero_Total"
        
        homo_file = os.path.join(DATA_DIR, FILES[homo_key])
        hetero_file = os.path.join(DATA_DIR, FILES[hetero_key])
        
        homo_edep = load_histogram(homo_file)
        hetero_edep = load_histogram(hetero_file)
        
        if homo_edep is None or hetero_edep is None:
            continue
        
        density = get_density_for_material(homo_key)
        homo_dose = edep_to_dose_gy(homo_edep, density)
        hetero_dose = edep_to_dose_gy(hetero_edep, density)
        
        diff = hetero_dose - homo_dose
        
        # Panel diferencia
        ax = plt.subplot(2, 2, mat_idx * 2 + 1)
        
        im = ax.imshow(
            diff.T,
            aspect='auto',
            origin='lower',
            cmap='RdBu_r',
            norm=colors.SymLogNorm(linthresh=1e-2, vmin=diff.min(), vmax=diff.max())
        )
        
        ax.set_title(f'{material}: Hetero - Homo (Diferencia)', fontsize=12, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='ΔDosis (Gy)')
        
        # Panel ratio
        ax_ratio = plt.subplot(2, 2, mat_idx * 2 + 2)
        
        ratio = np.divide(hetero_dose, homo_dose, 
                         where=homo_dose > 0,
                         out=np.ones_like(homo_dose))
        
        im_ratio = ax_ratio.imshow(
            ratio.T,
            aspect='auto',
            origin='lower',
            cmap='viridis',
            norm=colors.LogNorm(vmin=np.min(ratio[ratio > 0]), vmax=np.max(ratio))
        )
        
        ax_ratio.set_title(f'{material}: Ratio Hetero/Homo', fontsize=12, fontweight='bold')
        ax_ratio.set_xlabel('X (bins)')
        ax_ratio.set_ylabel('Y (bins)')
        plt.colorbar(im_ratio, ax=ax_ratio, label='Ratio')
    
    plt.suptitle('Mapas de Diferencia y Ratio - I125 100M', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output = os.path.join(DATA_DIR, '3_difference_maps.png')
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfica guardada: {output}\n")
    plt.close()

def analyze_profiles_hetero():
    """Análisis de perfiles horizontales (Y=0)"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS: PERFILES HORIZONTALES - HETERO vs HOMO (100M)")
    print("="*70 + "\n")
    
    fig = plt.figure(figsize=(16, 6))
    
    center_y = 150  # Centro del mapa
    x_axis = np.linspace(-150.5, 150.5, 300)
    
    for mat_idx, material in enumerate(["Bone", "Lung"]):
        homo_key = f"{material}_Homo_Total"
        hetero_key = f"{material}_Hetero_Total"
        
        homo_file = os.path.join(DATA_DIR, FILES[homo_key])
        hetero_file = os.path.join(DATA_DIR, FILES[hetero_key])
        
        homo_edep = load_histogram(homo_file)
        hetero_edep = load_histogram(hetero_file)
        
        if homo_edep is None or hetero_edep is None:
            continue
        
        density = get_density_for_material(homo_key)
        homo_dose = edep_to_dose_gy(homo_edep, density)
        hetero_dose = edep_to_dose_gy(hetero_edep, density)
        
        # Extraer perfiles horizontales
        homo_profile = homo_dose[:, center_y]
        hetero_profile = hetero_dose[:, center_y]
        
        # Panel perfil
        ax = plt.subplot(1, 3, mat_idx + 1)
        
        ax.plot(x_axis, homo_profile, 'b-', linewidth=2.5, label='Homo', alpha=0.8)
        ax.plot(x_axis, hetero_profile, 'r--', linewidth=2.5, label='Hetero', alpha=0.8)
        
        # Marcar región de heterogeneidad
        x_min = HETERO_POS_X - HETERO_SIZE / 2
        x_max = HETERO_POS_X + HETERO_SIZE / 2
        ax.axvline(x_min, color='gray', linestyle=':', alpha=0.5)
        ax.axvline(x_max, color='gray', linestyle=':', alpha=0.5)
        
        ax.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Dosis (Gy)', fontsize=11, fontweight='bold')
        ax.set_title(f'{material} - Perfil Horizontal (Y=0)', fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, which='both')
        ax.legend(loc='best')
        ax.set_xlim(-120, 120)
    
    # Panel ratio
    ax_ratio = plt.subplot(1, 3, 3)
    
    for material, color, linestyle in [("Bone", 'brown', '-'), ("Lung", 'green', '--')]:
        homo_key = f"{material}_Homo_Total"
        hetero_key = f"{material}_Hetero_Total"
        
        homo_file = os.path.join(DATA_DIR, FILES[homo_key])
        hetero_file = os.path.join(DATA_DIR, FILES[hetero_key])
        
        homo_edep = load_histogram(homo_file)
        hetero_edep = load_histogram(hetero_file)
        
        if homo_edep is None or hetero_edep is None:
            continue
        
        density = get_density_for_material(homo_key)
        homo_dose = edep_to_dose_gy(homo_edep, density)
        hetero_dose = edep_to_dose_gy(hetero_edep, density)
        
        homo_profile = homo_dose[:, center_y]
        hetero_profile = hetero_dose[:, center_y]
        
        ratio = np.divide(hetero_profile, homo_profile,
                         where=homo_profile > 0,
                         out=np.ones_like(homo_profile))
        
        ax_ratio.plot(x_axis, ratio, color=color, linestyle=linestyle, 
                     linewidth=2.5, label=material, alpha=0.8)
    
    x_min = HETERO_POS_X - HETERO_SIZE / 2
    x_max = HETERO_POS_X + HETERO_SIZE / 2
    ax_ratio.axvline(x_min, color='gray', linestyle=':', alpha=0.5)
    ax_ratio.axvline(x_max, color='gray', linestyle=':', alpha=0.5)
    ax_ratio.axhline(1.0, color='red', linestyle='-', linewidth=1.5, alpha=0.7)
    
    ax_ratio.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
    ax_ratio.set_ylabel('Ratio Hetero/Homo', fontsize=11, fontweight='bold')
    ax_ratio.set_title('Ratio Horizontal (Y=0)', fontsize=12, fontweight='bold')
    ax_ratio.grid(True, alpha=0.3)
    ax_ratio.legend(loc='best')
    ax_ratio.set_xlim(-120, 120)
    
    plt.suptitle('Perfiles Horizontales - I125 100M', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output = os.path.join(DATA_DIR, '4_horizontal_profiles.png')
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfica guardada: {output}\n")
    plt.close()

def analyze_mm_by_mm_hetero():
    """Análisis detallado: 2 en 2 mm (0-10mm) para heterogéneos"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS: DESGLOSE MM-POR-MM (0-10mm) - HETERO vs HOMO (100M)")
    print("="*70 + "\n")
    
    materials = ["Bone", "Lung"]
    center = 150
    
    for material in materials:
        print(f"\n{'='*70}")
        print(f"MATERIAL: {material}")
        print(f"{'='*70}\n")
        
        homo_key = f"{material}_Homo_Total"
        hetero_key = f"{material}_Hetero_Total"
        
        homo_file = os.path.join(DATA_DIR, FILES[homo_key])
        hetero_file = os.path.join(DATA_DIR, FILES[hetero_key])
        
        homo_edep = load_histogram(homo_file)
        hetero_edep = load_histogram(hetero_file)
        
        if homo_edep is None or hetero_edep is None:
            continue
        
        density = get_density_for_material(homo_key)
        homo_dose = edep_to_dose_gy(homo_edep, density)
        hetero_dose = edep_to_dose_gy(hetero_edep, density)
        
        print(f"{'Rango (mm)':<15} {'Homo Dosis':<18} {'Hetero Dosis':<18} {'Ratio D/H':<15} {'Cambio %':<15}")
        print("-" * 80)
        
        for r_start in range(0, 10, 2):
            r_end = r_start + 2
            
            y_grid, x_grid = np.ogrid[:300, :300]
            dist = np.sqrt((x_grid - center)**2 + (y_grid - center)**2)
            mask = (dist >= r_start) & (dist < r_end)
            
            homo_dose_sum = np.sum(homo_dose[mask])
            hetero_dose_sum = np.sum(hetero_dose[mask])
            
            ratio = hetero_dose_sum / homo_dose_sum if homo_dose_sum > 0 else 0
            pct_change = ((hetero_dose_sum - homo_dose_sum) / homo_dose_sum * 100) if homo_dose_sum > 0 else 0
            
            print(f"{r_start}-{r_end:<13} {homo_dose_sum:<18.3e} {hetero_dose_sum:<18.3e} {ratio:<15.4f} {pct_change:+.2f}%")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ANÁLISIS AVANZADO: HETEROGENEIDAD DETALLADO - I125 100M")
    print("="*70 + "\n")
    
    analyze_difference_maps()
    analyze_profiles_hetero()
    analyze_mm_by_mm_hetero()
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS AVANZADO COMPLETADO")
    print("="*70 + "\n")

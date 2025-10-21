#!/usr/bin/env python3
"""
Análisis de datos 100M - Lung hueco vs normal
Genera matriz 3x2 de gráficas con dosis y ratios respecto a water homo
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LogNorm, Normalize
import warnings
warnings.filterwarnings('ignore')

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
DENSITY_WATER = 1.0  # g/cm³
DENSITY_BONE = 1.85  # g/cm³
DENSITY_LUNG_ICRP = 1.05  # g/cm³ (compact lung)
DENSITY_LUNG_MIRD = 0.2958  # g/cm³ (inflated lung with air)

# Factor de conversión: Gy = MeV / (volumen_cm³ * densidad_g/cm³ * 1.602e-10)
# MeV -> Joules: 1 MeV = 1.602e-13 J
# 1 Gy = 1 J/kg = 1 J / (1000 g)
# Entonces: Gy = (MeV * 1.602e-13 J/MeV) / (volumen_cm³ * densidad_g * 1e-3 kg/g * 1e-6 cm³/m³)
CONVERSION_FACTOR = 1.602e-10  # MeV -> Gy

def load_histogram(filename):
    """Cargar histograma de archivo ROOT"""
    try:
        with uproot.open(filename) as f:
            # Intentar varios nombres posibles
            for hist_name in ['h20', 'Deph', 'h2_eDepPrimary']:
                if hist_name in f:
                    hist = f[hist_name]
                    edep = hist.values()
                    return edep
            # Si no encuentra el histograma, mostrar disponibles
            print(f"  Available keys: {list(f.keys())}")
            return None
    except Exception as e:
        print(f"Error cargando {filename}: {e}")
        return None

def edep_to_dose(edep, volume_per_bin_cm3, density):
    """Convertir energía depositada a dosis (Gy)
    
    Args:
        edep: Energía depositada (MeV)
        volume_per_bin_cm3: Volumen por bin (cm³)
        density: Densidad del material (g/cm³)
    
    Returns:
        Dosis en Gy
    """
    return edep * CONVERSION_FACTOR / (volume_per_bin_cm3 * density)

def main():
    print("=" * 80)
    print("ANÁLISIS 100M - LUNG HUECO vs NORMAL")
    print("=" * 80)
    
    # Dimensiones del histograma (300x300 bins, ~1mm resolución)
    nbins_x, nbins_y = 300, 300
    size_x, size_y = 300.0, 300.0  # mm
    bin_size_mm = size_x / nbins_x
    volume_per_bin_cm3 = (bin_size_mm / 10) ** 2 * 0.0125  # 0.125 mm grosor
    
    # Casos a analizar: (archivo total, archivo primario, nombre, densidad)
    casos = [
        (f"{DATA_DIR}/brachytherapy_homo_water100m.root",
         f"{DATA_DIR}/brachytherapy_eDepPrimary_homo_water100m.root",
         "Water Homo", DENSITY_WATER),
        
        (f"{DATA_DIR}/brachytherapy_homo_lung100m.root",
         f"{DATA_DIR}/brachytherapy_eDepPrimary_homo_lung100m.root",
         "Lung ICRP Homo\n(ρ=1.05 g/cm³)", DENSITY_LUNG_ICRP),
        
        (f"{DATA_DIR}/brachytherapy_hetero_lung100m.root",
         f"{DATA_DIR}/brachytherapy_eDepPrimary_hetero_lung100m.root",
         "Lung ICRP Hetero\n(Water + Lung)", DENSITY_LUNG_ICRP),
        
        (f"{DATA_DIR}/brachytherapy_lunghueco_homo100m.root",
         f"{DATA_DIR}/brachytherapy_eDepPrimary_lunghueco_homo100m.root",
         "Lung Hueco Homo\n(Hollow lung)", DENSITY_LUNG_MIRD),
        
        (f"{DATA_DIR}/brachytherapy_hetero_lunghueco100m.root",
         f"{DATA_DIR}/brachytherapy_eDepPrimary_hetero_lunghueco100m.root",
         "Lung Hueco Hetero\n(Water + Hollow)", DENSITY_LUNG_MIRD),
        
        (f"{DATA_DIR}/brachytherapy_hetero_bone100m.root",
         f"{DATA_DIR}/brachytherapy_eDepPrimary_hetero_bone100m.root",
         "Bone Hetero\n(Water + Bone)", DENSITY_BONE),
    ]
    
    # Cargar todos los histogramas
    datos = []
    for archivo_total, archivo_prim, nombre, densidad in casos:
        print(f"\nCargando: {nombre}")
        edep_total = load_histogram(archivo_total)
        edep_prim = load_histogram(archivo_prim)
        
        if edep_total is None or edep_prim is None:
            print(f"  ⚠️ Error cargando {nombre}")
            continue
        
        # Convertir a dosis
        dose_total = edep_to_dose(edep_total, volume_per_bin_cm3, densidad)
        dose_prim = edep_to_dose(edep_prim, volume_per_bin_cm3, densidad)
        
        datos.append({
            'nombre': nombre,
            'dose_total': dose_total,
            'dose_prim': dose_prim,
            'densidad': densidad
        })
        print(f"  ✓ Cargado exitosamente")
        print(f"    Max dosis total: {np.max(dose_total):.4e} Gy")
        print(f"    Max dosis primaria: {np.max(dose_prim):.4e} Gy")
    
    if len(datos) < 6:
        print(f"\n❌ No se pudieron cargar todos los casos (se cargaron {len(datos)}/6)")
        return
    
    # Referencia: Water homo
    dose_ref = datos[0]['dose_total']
    
    # Crear figura 3x2
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    fig.suptitle('100M Events - Dose Distribution with Reference Ratios\nReferencia: Water Homogeneous', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    axes = axes.flatten()
    
    # Rango de dosis para normalización (usamos el máximo del agua)
    vmax_dose = np.max(dose_ref)
    vmin_dose = np.max(dose_ref) * 1e-3
    
    for idx, (ax, data) in enumerate(zip(axes, datos)):
        dose = data['dose_total']
        nombre = data['nombre']
        
        # Subplot superior: Mapa de dosis
        im = ax.imshow(dose, cmap='jet', norm=LogNorm(vmin=vmin_dose, vmax=vmax_dose),
                       extent=[-150, 150, -150, 150], origin='lower')
        
        # Añadir escala de color
        cbar = plt.colorbar(im, ax=ax, label='Dosis (Gy)', pad=0.02, format='%.1e')
        
        ax.set_xlabel('X (mm)', fontsize=10)
        ax.set_ylabel('Y (mm)', fontsize=10)
        ax.set_title(f'{nombre}\nDose Map (Total Deposited Energy)', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Añadir círculo de fuente
        circle = patches.Circle((0, 0), 2, color='green', fill=False, linewidth=2, label='Source')
        ax.add_patch(circle)
        
        # Crear subplot de ratio (debajo del mapa de dosis)
        # Calcular ratio
        ratio = dose / dose_ref
        ratio = np.nan_to_num(ratio, nan=1.0, posinf=1.0, neginf=1.0)
        
        # Aplicar máscara donde la referencia es muy pequeña
        mask = dose_ref < vmin_dose
        ratio[mask] = 1.0
        
        ax_text = fig.add_axes([ax.get_position().x0, ax.get_position().y0 - 0.08, 
                               ax.get_position().width, 0.07])
        ax_text.axis('off')
        
        # Estadísticas del ratio
        ratio_valid = ratio[~mask]
        if len(ratio_valid) > 0:
            ratio_mean = np.nanmean(ratio_valid)
            ratio_max = np.nanmax(ratio_valid[ratio_valid < 10])  # Excluir outliers
            ratio_min = np.nanmin(ratio_valid[ratio_valid > 0.1])
            
            stats_text = (f"Ratio vs Water Homo | Mean: {ratio_mean:.3f} | "
                         f"Range: [{ratio_min:.3f}, {ratio_max:.3f}]")
        else:
            stats_text = "No valid ratio data"
        
        ax_text.text(0.5, 0.5, stats_text, ha='center', va='center',
                    fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                    transform=ax_text.transAxes)
    
    plt.tight_layout(rect=[0, 0.005, 1, 0.99])
    
    output_file = "/home/fer/fer/newbrachy/100M_I125_pri-sec/dose_maps_3x2_with_ratios.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    
    plt.show()

if __name__ == "__main__":
    import os
    main()

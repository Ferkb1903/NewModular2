#!/usr/bin/env python3
"""
Análisis comparativo: Water Homogéneo vs Bone Homogéneo
Ir-192 200M
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os
from scipy.ndimage import zoom

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/200M_IR192"

# Densidades (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85

# Tamaño de bins
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0

def load_histogram(filename):
    """Cargar histograma de archivo ROOT"""
    try:
        with uproot.open(filename) as f:
            # Buscar en orden
            search_names = ['h20', 'dose_map_primary', 'h2_eDepPrimary']
            
            for name in search_names:
                if name in f:
                    hist = f[name]
                    edep = hist.values()
                    if np.max(edep) > 0:
                        return edep
            
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def edep_to_dose(edep_values, density):
    """Convierte edep a dosis (Gy) aplicando densidad"""
    bin_volume_cm3 = (BIN_SIZE_MM / 10) ** 3
    dose_gy = edep_values * 1.602e-10 / (bin_volume_cm3 * density)
    return dose_gy

def main():
    print("=" * 80)
    print("COMPARACIÓN: Water Homogéneo vs Bone Homogéneo")
    print("Ir-192 200M")
    print("=" * 80)
    
    # Cargar Water Homo
    print("\nCargando casos...")
    filepath_water = os.path.join(DATA_DIR, "200m_water_homogeneous.root")
    edep_water = load_histogram(filepath_water)
    if edep_water is None:
        print("❌ No se pudo cargar Water Homo")
        return
    
    dose_water = edep_to_dose(edep_water, DENSITY_WATER)
    print(f"  ✓ Water Homo cargado, shape: {edep_water.shape}")
    
    # Cargar Bone Homo
    filepath_bone = os.path.join(DATA_DIR, "200m_bone_homogeneous.root")
    edep_bone = load_histogram(filepath_bone)
    if edep_bone is None:
        print("❌ No se pudo cargar Bone Homo")
        return
    
    dose_bone = edep_to_dose(edep_bone, DENSITY_BONE)
    print(f"  ✓ Bone Homo cargado, shape: {edep_bone.shape}")
    
    # Crear figura con 3 columnas: Water, Bone, Diferencia
    fig = plt.figure(figsize=(15, 5))
    fig.suptitle('Comparación: Water Homogéneo vs Bone Homogéneo\n(Ir-192 200M)', 
                 fontsize=13, fontweight='bold', y=0.98)
    
    # Calcular escalas
    dose_max_water = np.nanmax(dose_water)
    dose_max_bone = np.nanmax(dose_bone)
    dose_min_water = np.nanmin(dose_water[dose_water > 0]) if np.sum(dose_water > 0) > 0 else 1e-10
    dose_min_bone = np.nanmin(dose_bone[dose_bone > 0]) if np.sum(dose_bone > 0) > 0 else 1e-10
    
    # Usar escala común
    dose_min_global = min(dose_min_water, dose_min_bone)
    dose_max_global = max(dose_max_water, dose_max_bone)
    
    # COLUMNA 1: Mapa de dosis Water
    ax1 = plt.subplot(1, 3, 1)
    im1 = ax1.imshow(
        dose_water.T,
        aspect='auto',
        origin='lower',
        cmap='jet',
        norm=colors.LogNorm(vmin=dose_min_global, vmax=dose_max_global)
    )
    ax1.set_title('Water Homogéneo (1.0 g/cm³)\nDosis (Gy)', 
                 fontsize=11, fontweight='bold')
    ax1.set_xlabel('X (bins)', fontsize=9)
    ax1.set_ylabel('Y (bins)', fontsize=9)
    cbar1 = plt.colorbar(im1, ax=ax1, label='Dosis (Gy)', format='%.1e')
    
    # COLUMNA 2: Mapa de dosis Bone
    ax2 = plt.subplot(1, 3, 2)
    im2 = ax2.imshow(
        dose_bone.T,
        aspect='auto',
        origin='lower',
        cmap='jet',
        norm=colors.LogNorm(vmin=dose_min_global, vmax=dose_max_global)
    )
    ax2.set_title('Bone Homogéneo (1.85 g/cm³)\nDosis (Gy)', 
                 fontsize=11, fontweight='bold')
    ax2.set_xlabel('X (bins)', fontsize=9)
    ax2.set_ylabel('Y (bins)', fontsize=9)
    cbar2 = plt.colorbar(im2, ax=ax2, label='Dosis (Gy)', format='%.1e')
    
    # COLUMNA 3: Diferencia (Bone - Water)
    # Redimensionar si es necesario para la resta
    if dose_water.shape != dose_bone.shape:
        if dose_water.shape[0] < dose_bone.shape[0]:
            scale_factor = dose_bone.shape[0] / dose_water.shape[0]
            dose_water_resized = zoom(dose_water, scale_factor, order=1)
            diff_absolute = dose_bone - dose_water_resized
            diff_shape = dose_bone.shape
        else:
            scale_factor = dose_water.shape[0] / dose_bone.shape[0]
            dose_bone_resized = zoom(dose_bone, scale_factor, order=1)
            diff_absolute = dose_bone_resized - dose_water
            diff_shape = dose_water.shape
    else:
        diff_absolute = dose_bone - dose_water
        diff_shape = dose_bone.shape
    
    ax3 = plt.subplot(1, 3, 3)
    diff_max = np.nanmax(np.abs(diff_absolute))
    norm_diff = colors.SymLogNorm(linthresh=1e-6, vmin=-diff_max, vmax=diff_max)
    
    im3 = ax3.imshow(
        diff_absolute.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=norm_diff
    )
    ax3.set_title('Diferencia: Bone - Water\n(Gy)', 
                 fontsize=11, fontweight='bold')
    ax3.set_xlabel('X (bins)', fontsize=9)
    ax3.set_ylabel('Y (bins)', fontsize=9)
    cbar3 = plt.colorbar(im3, ax=ax3, label='ΔDosis (Gy)', format='%.1e')
    
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, 'homo_analysis_water_vs_bone.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    
    # Estadísticas
    print(f"\n{'='*80}")
    print("ESTADÍSTICAS")
    print(f"{'='*80}")
    print(f"Water Homogéneo:")
    print(f"  Dosis máxima: {dose_max_water:.6e} Gy")
    print(f"  Dosis mínima: {dose_min_water:.6e} Gy")
    print(f"\nBone Homogéneo:")
    print(f"  Dosis máxima: {dose_max_bone:.6e} Gy")
    print(f"  Dosis mínima: {dose_min_bone:.6e} Gy")
    print(f"\nDiferencia (Bone - Water):")
    print(f"  Diferencia máxima: {diff_max:.6e} Gy")
    print(f"  Diferencia mínima: {np.nanmin(diff_absolute):.6e} Gy")

if __name__ == "__main__":
    main()

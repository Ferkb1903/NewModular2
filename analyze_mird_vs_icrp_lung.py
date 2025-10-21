#!/usr/bin/env python3
"""
Análisis Comparativo: MIRD Lung vs ICRP Lung
Braquiterapia I125 - Simulaciones con diferentes definiciones de pulmón

MIRD Lung: ρ = 0.2958 g/cm³ (pulmón inflado con aire)
ICRP Lung: ρ = 1.05 g/cm³ (tejido pulmonar compacto sin aire)
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches
import os

# Densidades (g/cm³)
DENSITY_WATER = 1.0
DENSITY_LUNG_MIRD = 0.2958  # Pulmón inflado con aire
DENSITY_LUNG_ICRP = 1.05    # Tejido pulmonar compacto

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
HIST_TOTAL = "h20;1"
HIST_PRIMARY = "h2_eDepPrimary;1"
HIST_SECONDARY = "h2_eDepSecondary;1"

# Parámetros de conversión
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

# Heterogeneidad
HETERO_SIZE = 60.0
HETERO_POS_X = 40.0
HETERO_POS_Y = 0.0

# Archivos disponibles
FILES = {
    "Lung_Homo_Primary": "brachytherapy_eDepPrimary_homo_lung100m.root",
    "Lung_Homo_Secondary": "brachytherapy_eDepSecondary_homo_lung100m.root",
    "Lung_Homo_Total": "brachytherapy_homo_lung100m.root",
}

def load_histogram(filepath, hist_name):
    """Carga histograma de archivo ROOT"""
    try:
        with uproot.open(filepath) as file:
            if hist_name in file:
                return file[hist_name].values()
    except:
        pass
    return None

def edep_to_dose_gy(edep_values, density):
    """Convierte edep (MeV) a dosis (Gy)"""
    mass_g = BIN_VOLUME * density
    return edep_values * 1.602e-10 / mass_g

def print_comparison_header():
    """Imprime encabezado de comparación"""
    print("\n" + "="*80)
    print("🔬 ANÁLISIS COMPARATIVO: MIRD LUNG vs ICRP LUNG - I125 100M")
    print("="*80 + "\n")
    
    print("📊 CONFIGURACIÓN DE MATERIALES:")
    print(f"  • MIRD Lung: ρ = {DENSITY_LUNG_MIRD} g/cm³ (16 elementos)")
    print(f"  • ICRP Lung: ρ = {DENSITY_LUNG_ICRP} g/cm³ (12 elementos, comprimido)")
    print(f"  • Ratio ICRP/MIRD: {DENSITY_LUNG_ICRP/DENSITY_LUNG_MIRD:.4f}x\n")

def analyze_lung_comparison():
    """Análisis comparativo MIRD vs ICRP"""
    print_comparison_header()
    
    # Cargar datos
    filepath = os.path.join(DATA_DIR, FILES["Lung_Homo_Total"])
    print("📂 Cargando datos...", end=" ")
    edep_total = load_histogram(filepath, HIST_TOTAL)
    if edep_total is None:
        print("❌ Error")
        return
    print("✅\n")
    
    # Convertir con ambas densidades
    dose_mird = edep_to_dose_gy(edep_total, DENSITY_LUNG_MIRD)
    dose_icrp = edep_to_dose_gy(edep_total, DENSITY_LUNG_ICRP)
    
    # Estadísticas globales
    print("📈 ESTADÍSTICAS GLOBALES:")
    print("-" * 80)
    
    energy_total = np.sum(edep_total)
    dose_mird_total = np.sum(dose_mird)
    dose_icrp_total = np.sum(dose_icrp)
    
    print(f"Energía total depositada: {energy_total:.3e} MeV")
    print(f"\nDosis MIRD (ρ=0.2958): {dose_mird_total:.3e} Gy")
    print(f"Dosis ICRP (ρ=1.05):    {dose_icrp_total:.3e} Gy")
    print(f"\nRatio ICRP/MIRD: {dose_icrp_total/dose_mird_total:.6f}x")
    print(f"Diferencia: {((dose_icrp_total - dose_mird_total)/dose_mird_total)*100:+.2f}%\n")
    
    # Análisis regional
    print("📊 ANÁLISIS REGIONAL (Anillos Circulares desde Centro):")
    print("-" * 80)
    
    center = 150
    regions = {
        '0-5 mm': (0, 5),
        '5-10 mm': (5, 10),
        '10-30 mm': (10, 30),
        '30-50 mm': (30, 50),
        '50-150 mm': (50, 150)
    }
    
    print(f"{'Región':<12} {'MIRD Dosis':<18} {'ICRP Dosis':<18} {'Ratio ICRP/MIRD':<18} {'Energía':<18}")
    print("-" * 80)
    
    for region_name, (r_min, r_max) in regions.items():
        y_grid, x_grid = np.ogrid[:300, :300]
        dist = np.sqrt((x_grid - center)**2 + (y_grid - center)**2)
        mask = (dist >= r_min) & (dist < r_max)
        
        dosis_mird = np.sum(dose_mird[mask])
        dosis_icrp = np.sum(dose_icrp[mask])
        energia = np.sum(edep_total[mask])
        
        ratio = dosis_icrp / dosis_mird if dosis_mird > 0 else 0
        
        print(f"{region_name:<12} {dosis_mird:<18.3e} {dosis_icrp:<18.3e} {ratio:<18.6f} {energia:<18.3e}")
    
    # Análisis de píxeles
    print("\n\n📍 ESTADÍSTICAS DE PÍXELES (no-cero):")
    print("-" * 80)
    
    mird_nonzero = dose_mird[dose_mird > 0]
    icrp_nonzero = dose_icrp[dose_icrp > 0]
    
    print(f"Píxeles con dosis > 0: {len(mird_nonzero)}")
    print(f"\nDosis MIRD:")
    print(f"  Media: {np.mean(mird_nonzero):.3e} Gy")
    print(f"  Mediana: {np.median(mird_nonzero):.3e} Gy")
    print(f"  Máximo: {np.max(mird_nonzero):.3e} Gy")
    print(f"  Std: {np.std(mird_nonzero):.3e} Gy")
    
    print(f"\nDosis ICRP:")
    print(f"  Media: {np.mean(icrp_nonzero):.3e} Gy")
    print(f"  Mediana: {np.median(icrp_nonzero):.3e} Gy")
    print(f"  Máximo: {np.max(icrp_nonzero):.3e} Gy")
    print(f"  Std: {np.std(icrp_nonzero):.3e} Gy")
    
    # Visualización
    fig = plt.figure(figsize=(16, 10))
    
    # Panel MIRD
    ax_mird = plt.subplot(2, 2, 1)
    mird_log = np.copy(dose_mird).astype(float)
    mird_log[mird_log <= 0] = np.min(mird_log[mird_log > 0]) / 10
    
    im_mird = ax_mird.imshow(
        mird_log.T,
        aspect='auto',
        origin='lower',
        cmap='rainbow',
        norm=colors.LogNorm(vmin=mird_log.min(), vmax=mird_log.max())
    )
    ax_mird.set_title('MIRD Lung (ρ=0.2958 g/cm³)', fontsize=12, fontweight='bold')
    ax_mird.set_xlabel('X (bins)')
    ax_mird.set_ylabel('Y (bins)')
    plt.colorbar(im_mird, ax=ax_mird, label='Dosis (Gy)')
    
    # Panel ICRP
    ax_icrp = plt.subplot(2, 2, 2)
    icrp_log = np.copy(dose_icrp).astype(float)
    icrp_log[icrp_log <= 0] = np.min(icrp_log[icrp_log > 0]) / 10
    
    im_icrp = ax_icrp.imshow(
        icrp_log.T,
        aspect='auto',
        origin='lower',
        cmap='rainbow',
        norm=colors.LogNorm(vmin=icrp_log.min(), vmax=icrp_log.max())
    )
    ax_icrp.set_title('ICRP Lung (ρ=1.05 g/cm³)', fontsize=12, fontweight='bold')
    ax_icrp.set_xlabel('X (bins)')
    ax_icrp.set_ylabel('Y (bins)')
    plt.colorbar(im_icrp, ax=ax_icrp, label='Dosis (Gy)')
    
    # Panel Ratio
    ax_ratio = plt.subplot(2, 2, 3)
    ratio_map = np.divide(dose_icrp, dose_mird,
                          where=dose_mird > 0,
                          out=np.ones_like(dose_mird))
    
    im_ratio = ax_ratio.imshow(
        ratio_map.T,
        aspect='auto',
        origin='lower',
        cmap='coolwarm',
        norm=colors.Normalize(vmin=ratio_map[ratio_map > 0].min(), 
                             vmax=ratio_map[ratio_map > 0].max())
    )
    ax_ratio.set_title(f'Ratio ICRP/MIRD (Esperado: {DENSITY_LUNG_ICRP/DENSITY_LUNG_MIRD:.4f})', 
                      fontsize=12, fontweight='bold')
    ax_ratio.set_xlabel('X (bins)')
    ax_ratio.set_ylabel('Y (bins)')
    plt.colorbar(im_ratio, ax=ax_ratio, label='Ratio')
    
    # Panel Diferencia
    ax_diff = plt.subplot(2, 2, 4)
    diff = dose_icrp - dose_mird
    
    im_diff = ax_diff.imshow(
        diff.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=colors.SymLogNorm(linthresh=1e-1, vmin=diff.min(), vmax=diff.max())
    )
    ax_diff.set_title('Diferencia ICRP - MIRD', fontsize=12, fontweight='bold')
    ax_diff.set_xlabel('X (bins)')
    ax_diff.set_ylabel('Y (bins)')
    plt.colorbar(im_diff, ax=ax_diff, label='ΔDosis (Gy)')
    
    plt.suptitle('Comparación: MIRD Lung (0.2958 g/cm³) vs ICRP Lung (1.05 g/cm³) - I125 100M',
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output = os.path.join(DATA_DIR, '5_lung_mird_vs_icrp_comparison.png')
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"\n\n✅ Gráfica guardada: {output}\n")
    plt.close()
    
    print("="*80 + "\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ANÁLISIS COMPARATIVO: MIRD LUNG vs ICRP LUNG - I125 100M")
    print("="*80 + "\n")
    
    print("Materiales a comparar:")
    print(f"  MIRD Lung: ρ = {DENSITY_LUNG_MIRD} g/cm³ (pulmón inflado con aire)")
    print(f"  ICRP Lung: ρ = {DENSITY_LUNG_ICRP} g/cm³ (tejido pulmonar compacto)")
    print(f"  Ratio densidades: {DENSITY_LUNG_ICRP/DENSITY_LUNG_MIRD:.4f}")
    print(f"  Ratio dosis esperado: {DENSITY_LUNG_ICRP/DENSITY_LUNG_MIRD:.4f} (D ∝ 1/ρ)\n")
    
    # Llamar función de análisis cuando existan los datos
    # compare_mird_vs_icrp()
    
    print("\n⚠️  NOTA: Ejecuta primero las simulaciones con MIRD lung")
    print("    Archivos esperados en 100M_I125_pri-sec/:")
    print("      - brachytherapy_MIRD_lung*.root")
    print("\n" + "="*80 + "\n")

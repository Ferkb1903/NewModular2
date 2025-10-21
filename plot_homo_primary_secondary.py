#!/usr/bin/env python3
"""
Análisis de primarias y secundarias en casos homogéneos: Lung Hueco, Water, Bone
Genera matriz 2x4:
- Fila 1: Lung Hueco Homo
- Fila 2: Bone Homo
Columnas:
- Col 1: Primary edep
- Col 2: Secondary edep
- Col 3: Primary/Total ratio
- Col 4: Secondary/Total ratio
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"

# Parámetros de heterogeneidad (del macro)
HETERO_SIZE = 60.0  # mm (6.0 cm)
HETERO_POS_X = 40.0  # mm (posición en X)
HETERO_POS_Y = 0.0   # mm (posición en Y)

# Casos homogéneos a analizar
HOMO_CASES = {
    "Lung_Hueco_Homo": {
        "total": "brachytherapy_lunghueco_homo100m.root",
        "primary": "brachytherapy_eDepPrimary_lunghueco_homo100m.root",
        "secondary": "brachytherapy_eDepSecondary_lunghueco_homo100m.root",
    },
    "Bone_Homo": {
        "total": "brachytherapy_homo_bone100m.root",
        "primary": "brachytherapy_eDepPrimary_homo_bone100m.root",
        "secondary": "brachytherapy_eDepSecondary_homo_ bone100m.root",  # Nota: hay espacio antes de 'bone'
    },
}

# Histogramas de primarias y secundarias
HISTOGRAMS = {
    "h2_eDepPrimary": "Primarias",
    "h2_eDepSecondary": "Secundarias",
}

# Densidades base (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG_MIRD = 0.2958  # Lung inflado con aire (MIRD)

# Tamaño de bins
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

def load_histogram(filename, hist_name):
    """Cargar histograma específico de archivo ROOT"""
    try:
        filepath = os.path.join(DATA_DIR, filename) if filename else None
        if not filepath or not os.path.exists(filepath):
            return None
        
        with uproot.open(filepath) as f:
            if hist_name in f:
                hist = f[hist_name]
                edep = hist.values()
                return edep
            return None
    except Exception as e:
        print(f"  Error loading {hist_name}: {e}")
        return None

def create_density_map(shape, case_name):
    """Crea un mapa de densidad para casos homogéneos"""
    
    if "Lung_Hueco" in case_name:
        return np.ones(shape, dtype=float) * DENSITY_LUNG_MIRD
    elif "Bone" in case_name:
        return np.ones(shape, dtype=float) * DENSITY_BONE
    else:
        return np.ones(shape, dtype=float) * DENSITY_WATER

def edep_to_dose(edep_values, density_map):
    """Convierte edep a dosis (Gy) aplicando densidad por región"""
    bin_volume_cm3 = (BIN_SIZE_MM / 10) ** 2 * 0.0125
    density_map_copy = density_map.copy()
    density_map_copy[density_map_copy == 0] = DENSITY_WATER
    dose_gy = edep_values * 1.602e-10 / (bin_volume_cm3 * density_map_copy)
    return dose_gy

def main():
    print("=" * 80)
    print("ANÁLISIS DE PRIMARIAS Y SECUNDARIAS: Casos Homogéneos")
    print("=" * 80)
    
    case_order = ["Lung_Hueco_Homo", "Bone_Homo"]
    
    # Crear figura 2x3 (2 casos x 3 columnas: Primary edep, Secondary edep, Horizontal profiles)
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle('Análisis de Primarias vs Secundarias - Casos Homogéneos (I125 100M)', 
                 fontsize=14, fontweight='bold', y=0.995)
    
    # Mapas de información
    info_text = {
        "Lung_Hueco_Homo": "Lung MIRD (0.2958 g/cm³)",
        "Bone_Homo": "Hueso (1.85 g/cm³)",
    }
    
    # Calcular escalas globales
    edep_primary_min = np.inf
    edep_primary_max = 0
    edep_secondary_min = np.inf
    edep_secondary_max = 0
    
    all_data = {}
    for case_name in case_order:
        if case_name not in HOMO_CASES:
            continue
            
        files = HOMO_CASES[case_name]
        print(f"\nCargando {case_name}...")
        
        # Cargar primarias y secundarias desde archivos separados
        edep_primary = load_histogram(files["primary"], "h2_eDepPrimary")
        edep_secondary = load_histogram(files["secondary"], "h2_eDepSecondary")
        edep_total = load_histogram(files["total"], "h20")
        
        if edep_primary is None or edep_secondary is None or edep_total is None:
            print(f"  ❌ No se pudo cargar histogramas")
            continue
        
        density = create_density_map(edep_primary.shape, case_name)
        
        all_data[case_name] = {
            'edep_primary': edep_primary,
            'edep_secondary': edep_secondary,
            'edep_total': edep_total,
            'density': density
        }
        
        print(f"  ✓ Primarias: {np.nanmax(edep_primary):.2e} MeV")
        print(f"  ✓ Secundarias: {np.nanmax(edep_secondary):.2e} MeV")
        print(f"  ✓ Total: {np.nanmax(edep_total):.2e} MeV")
        
        # Calcular mínimos/máximos para escalas globales
        edep_primary_min = min(edep_primary_min, np.nanmin(edep_primary[edep_primary > 0]))
        edep_primary_max = max(edep_primary_max, np.nanmax(edep_primary))
        edep_secondary_min = min(edep_secondary_min, np.nanmin(edep_secondary[edep_secondary > 0]))
        edep_secondary_max = max(edep_secondary_max, np.nanmax(edep_secondary))
    
    # Plotear casos
    for row_idx, case_name in enumerate(case_order, 1):
        if case_name not in all_data:
            continue
        
        edep_primary = all_data[case_name]['edep_primary']
        edep_secondary = all_data[case_name]['edep_secondary']
        edep_total = all_data[case_name]['edep_total']
        
        # COLUMNA 1: Mapa de Primarias edep
        ax1 = plt.subplot(2, 3, 3*row_idx - 2)
        
        im1 = ax1.imshow(
            edep_primary.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=edep_primary_min, vmax=edep_primary_max)
        )
        
        ax1.set_title(f'{info_text[case_name]}\nPrimarias edep (MeV)', 
                     fontsize=11, fontweight='bold')
        ax1.set_xlabel('X (bins)', fontsize=9)
        ax1.set_ylabel('Y (bins)', fontsize=9)
        cbar1 = plt.colorbar(im1, ax=ax1, label='edep (MeV)', format='%.1e')
        
        # COLUMNA 2: Mapa de Secundarias edep
        ax2 = plt.subplot(2, 3, 3*row_idx - 1)
        
        im2 = ax2.imshow(
            edep_secondary.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=edep_secondary_min, vmax=edep_secondary_max)
        )
        
        ax2.set_title(f'{info_text[case_name]}\nSecundarias edep (MeV)', 
                     fontsize=11, fontweight='bold')
        ax2.set_xlabel('X (bins)', fontsize=9)
        ax2.set_ylabel('Y (bins)', fontsize=9)
        cbar2 = plt.colorbar(im2, ax=ax2, label='edep (MeV)', format='%.1e')
        
        # COLUMNA 3: Perfiles horizontales de dosis (primarias vs secundarias)
        ax3 = plt.subplot(2, 3, 3*row_idx)
        
        # Extraer perfil horizontal en Y=150 (centro de geometría)
    y_center = 150
    y_range = np.arange(max(0, y_center-1), min(edep_primary.shape[1], y_center+2))
    # Promediar 3 bins en Y
    primary_profile = np.mean(edep_primary[:, y_range], axis=1)
    secondary_profile = np.mean(edep_secondary[:, y_range], axis=1)
        
    x_bins = np.arange(len(primary_profile))

    ax3.plot(x_bins, primary_profile, 'o-', label='Primarias', linewidth=2, markersize=4, color='#1f77b4')
    ax3.plot(x_bins, secondary_profile, 's-', label='Secundarias', linewidth=2, markersize=4, color='#ff7f0e')

    ax3.set_title(f'{info_text[case_name]}\nPerfil Horizontal (Y=150)', fontsize=11, fontweight='bold')
    ax3.set_xlabel('X (bins)', fontsize=9)
    ax3.set_ylabel('Dosis (MeV)', fontsize=9)
    ax3.set_yscale('log')
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)
        
    # Estadísticas
    print(f"\n{case_name}:")
    print(f"  Primarias:")
    print(f"    Total: {np.nansum(edep_primary):.6e} MeV")
    print(f"    Media: {np.nanmean(edep_primary[edep_primary > 0]):.6e} MeV")
    print(f"  Secundarias:")
    print(f"    Total: {np.nansum(edep_secondary):.6e} MeV")
    print(f"    Media: {np.nanmean(edep_secondary[edep_secondary > 0]):.6e} MeV")
    print(f"  Ratio Primarias/Total: {np.nansum(edep_primary) / (np.nansum(edep_total) + 1e-15):.4f}")
    print(f"  Ratio Secundarias/Total: {np.nansum(edep_secondary) / (np.nansum(edep_total) + 1e-15):.4f}")
    
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, 'homo_primary_secondary_2x3.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    
    plt.show()

    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    
    plt.show()
    
    # Plotear casos
    for row_idx, case_name in enumerate(case_order, 1):
        if case_name not in all_data:
            continue
        
        edep_primary = all_data[case_name]['edep_primary']
        edep_secondary = all_data[case_name]['edep_secondary']
        edep_total = all_data[case_name]['edep_total']
        
        # COLUMNA 1: Mapa de Primarias edep
        ax1 = plt.subplot(2, 4, 4*row_idx - 3)
        
        im1 = ax1.imshow(
            edep_primary.T,
            aspect='auto',
            origin='lower',
            cmap='hot',
            norm=colors.LogNorm(vmin=edep_primary_min, vmax=edep_primary_max)
        )
        
        ax1.set_title(f'{info_text[case_name]}\nPrimarias edep (MeV)', 
                     fontsize=11, fontweight='bold')
        ax1.set_xlabel('X (bins)', fontsize=9)
        ax1.set_ylabel('Y (bins)', fontsize=9)
        cbar1 = plt.colorbar(im1, ax=ax1, label='edep (MeV)', format='%.1e')
        
        # COLUMNA 2: Mapa de Secundarias edep
        ax2 = plt.subplot(2, 4, 4*row_idx - 2)
        
        im2 = ax2.imshow(
            edep_secondary.T,
            aspect='auto',
            origin='lower',
            cmap='hot',
            norm=colors.LogNorm(vmin=edep_secondary_min, vmax=edep_secondary_max)
        )
        
        ax2.set_title(f'{info_text[case_name]}\nSecundarias edep (MeV)', 
                     fontsize=11, fontweight='bold')
        ax2.set_xlabel('X (bins)', fontsize=9)
        ax2.set_ylabel('Y (bins)', fontsize=9)
        cbar2 = plt.colorbar(im2, ax=ax2, label='edep (MeV)', format='%.1e')
        
        # COLUMNA 3: Ratio Primarias / Total
        ax3 = plt.subplot(2, 4, 4*row_idx - 1)
        
        ratio_primary = edep_primary / (edep_total + 1e-15)
        ratio_primary = np.nan_to_num(ratio_primary, nan=0.5, posinf=1.0, neginf=0.0)
        
        im3 = ax3.imshow(
            ratio_primary.T,
            aspect='auto',
            origin='lower',
            cmap='viridis',
            norm=colors.Normalize(vmin=0, vmax=1)
        )
        
        ax3.set_title(f'{info_text[case_name]}\nRatio Primarias/Total', 
                     fontsize=11, fontweight='bold')
        ax3.set_xlabel('X (bins)', fontsize=9)
        ax3.set_ylabel('Y (bins)', fontsize=9)
        cbar3 = plt.colorbar(im3, ax=ax3, label='Ratio', format='%.2f')
        
        # COLUMNA 4: Ratio Secundarias / Total
        ax4 = plt.subplot(2, 4, 4*row_idx)
        
        ratio_secondary = edep_secondary / (edep_total + 1e-15)
        ratio_secondary = np.nan_to_num(ratio_secondary, nan=0.5, posinf=1.0, neginf=0.0)
        
        im4 = ax4.imshow(
            ratio_secondary.T,
            aspect='auto',
            origin='lower',
            cmap='plasma',
            norm=colors.Normalize(vmin=0, vmax=1)
        )
        
        ax4.set_title(f'{info_text[case_name]}\nRatio Secundarias/Total', 
                     fontsize=11, fontweight='bold')
        ax4.set_xlabel('X (bins)', fontsize=9)
        ax4.set_ylabel('Y (bins)', fontsize=9)
        cbar4 = plt.colorbar(im4, ax=ax4, label='Ratio', format='%.2f')
        
        # Estadísticas
        print(f"\n{case_name}:")
        print(f"  Primarias:")
        print(f"    Total: {np.nansum(edep_primary):.6e} MeV")
        print(f"    Media: {np.nanmean(edep_primary[edep_primary > 0]):.6e} MeV")
        print(f"  Secundarias:")
        print(f"    Total: {np.nansum(edep_secondary):.6e} MeV")
        print(f"    Media: {np.nanmean(edep_secondary[edep_secondary > 0]):.6e} MeV")
        print(f"  Ratio Primarias/Total: {np.nansum(edep_primary) / (np.nansum(edep_total) + 1e-15):.4f}")
        print(f"  Ratio Secundarias/Total: {np.nansum(edep_secondary) / (np.nansum(edep_total) + 1e-15):.4f}")
    
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, 'homo_primary_secondary_2x4.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    
    plt.show()

if __name__ == "__main__":
    main()

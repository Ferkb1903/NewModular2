#!/usr/bin/env python3
"""
Análisis de casos homogéneos: Ir-192 200M
Compara: Water Homogeneous vs Bone Homogeneous
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/200M_IR192"

# Casos para Ir-192: Water Homo y Bone Homo
HOMO_CASES = {
    "Water_Homo": "200m_water_homogeneous.root",
    "Bone_Homo": "200m_bone_homogeneous.root",
}

# Densidades base (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG_MIRD = 0.2958  # Lung inflado con aire (MIRD)

# Tamaño de bins
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

def load_histogram(filename, hist_name="dose_map_primary"):
    """Cargar histograma de archivo ROOT (busca en múltiples nombres)"""
    try:
        with uproot.open(filename) as f:
            # Intenta en este orden
            search_names = ['h20', 'dose_map_primary', 'h2_eDepPrimary', 'h2_eDepSecondary', 'Deph']
            
            for name in search_names:
                if name in f:
                    hist = f[name]
                    edep = hist.values()
                    if np.max(edep) > 0:  # Verifica que tenga datos
                        return edep
            
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def create_density_map(shape, case_name):
    """Crea un mapa de densidad uniforme - en Ir-192 todo es Hueso"""
    # Todos los casos en Ir-192 son Hueso (1.85 g/cm³)
    return np.ones(shape, dtype=float) * DENSITY_BONE

def edep_to_dose(edep_values, density_map):
    """Convierte edep a dosis (Gy) aplicando densidad"""
    bin_volume_cm3 = (BIN_SIZE_MM / 10) ** 2 * 0.0125
    density_map_copy = density_map.copy()
    density_map_copy[density_map_copy == 0] = DENSITY_WATER
    dose_gy = edep_values * 1.602e-10 / (bin_volume_cm3 * density_map_copy)
    return dose_gy

def get_x_axis_mm():
    """Obtiene el eje X en mm (300 bins)"""
    return np.linspace(-150, 150, 300)

def filter_data_range(x_axis, dose_map, x_min_range=-150, x_max_range=150):
    """Filtra datos al rango especificado"""
    mask = (x_axis >= x_min_range) & (x_axis <= x_max_range)
    x_filtered = x_axis[mask]
    dose_filtered = dose_map[np.where(mask)[0], :, :]
    return x_filtered, dose_filtered

def main():
    print("=" * 80)
    print("ANÁLISIS DE CASOS HOMOGÉNEOS: Ir-192 200M - HUESO")
    print("=" * 80)
    
    # Cargar Bone Homo (referencia)
    print("\nCargando casos...")
    filepath_ref = os.path.join(DATA_DIR, HOMO_CASES["Bone_Homo"])
    edep_ref = load_histogram(filepath_ref, "dose_map_primary")
    if edep_ref is None:
        print("❌ No se pudo cargar Bone Homo")
        return
    
    density_ref = create_density_map(edep_ref.shape, "Bone_Homo")
    dose_ref = edep_to_dose(edep_ref, density_ref)
    print(f"  ✓ Bone Homo (referencia) cargado, shape: {edep_ref.shape}")
    
    # Cargar caso heterogéneo
    datos_homo = {}
    for case_name, filename in HOMO_CASES.items():
        if case_name == "Bone_Homo":
            datos_homo[case_name] = {'dose': dose_ref, 'edep': edep_ref}
            continue
            
        filepath = os.path.join(DATA_DIR, filename)
        print(f"  Cargando {case_name}...", end=" ")
        edep = load_histogram(filepath, "dose_map_primary")
        if edep is None:
            print("❌")
            continue
        
        density = create_density_map(edep.shape, case_name)
        dose = edep_to_dose(edep, density)
        datos_homo[case_name] = {'dose': dose, 'edep': edep}
        print(f"✓ (shape: {edep.shape})")
    
    # Crear figura 1x3 (1 fila x 3 columnas: dosis, diferencia, ratio)
    fig = plt.figure(figsize=(15, 5))
    fig.suptitle('Análisis Hueso Homogéneo vs Heterogéneo\n(Ir-192 200M)', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Mapas de información
    info_text = {
        "Bone_Homo": "Hueso Homogéneo (1.85 g/cm³)",
        "Bone_Hetero": "Hueso Heterogéneo (1.85 g/cm³)",
    }
    
    case_order = ["Bone_Hetero"]  # Solo heterogéneo vs homo
    
    # Para cada caso, mostrar sus propias escalas (sin comparación directa)
    for case_name in case_order:
        if case_name not in datos_homo:
            continue
            
        edep_caso = datos_homo[case_name]['edep']
        dose_caso = datos_homo[case_name]['dose']
        
        # Crear figura 1x2 (dosis hetero y diferencia)
        fig_case = plt.figure(figsize=(12, 5))
        fig_case.suptitle(f'{info_text[case_name]} vs Homo\n(Ir-192 200M)', 
                         fontsize=12, fontweight='bold')
        
        # Calcular escalas para este caso
        dose_max_hetero = np.nanmax(dose_caso)
        dose_max_homo = np.nanmax(dose_ref)
        dose_min_hetero = np.nanmin(dose_caso[dose_caso > 0]) if np.sum(dose_caso > 0) > 0 else 1e-10
        dose_min_homo = np.nanmin(dose_ref[dose_ref > 0]) if np.sum(dose_ref > 0) > 0 else 1e-10
        
        # COLUMNA 1: Mapa de dosis hetero
        ax1 = plt.subplot(1, 2, 1)
        im1 = ax1.imshow(
            dose_caso.T,
            aspect='auto',
            origin='lower',
            cmap='jet',
            norm=colors.LogNorm(vmin=dose_min_hetero, vmax=dose_max_hetero)
        )
        ax1.set_title(f'{info_text[case_name]}\nDosis (Gy)', 
                     fontsize=11, fontweight='bold')
        ax1.set_xlabel('X (bins)', fontsize=9)
        ax1.set_ylabel('Y (bins)', fontsize=9)
        draw_heterogeneity(ax1)
        cbar1 = plt.colorbar(im1, ax=ax1, label='Dosis (Gy)', format='%.1e')
        
        # COLUMNA 2: Diferencia de dosis (hetero - homo)
        # Redimensionar la referencia a la forma del heterogéneo para la resta
        from scipy.ndimage import zoom
        if dose_ref.shape != dose_caso.shape:
            scale_factor = dose_caso.shape[0] / dose_ref.shape[0]
            dose_ref_resized = zoom(dose_ref, scale_factor, order=1)
        else:
            dose_ref_resized = dose_ref
        
        ax2 = plt.subplot(1, 2, 2)
        diff_absolute = dose_caso - dose_ref_resized
        
        diff_max = np.nanmax(np.abs(diff_absolute))
        norm_diff = colors.SymLogNorm(linthresh=1e-6, vmin=-diff_max, vmax=diff_max)
        
        im2 = ax2.imshow(
            diff_absolute.T,
            aspect='auto',
            origin='lower',
            cmap='RdBu_r',
            norm=norm_diff
        )
        ax2.set_title(f'Diferencia: Hetero - Homo\n(Gy)', 
                     fontsize=11, fontweight='bold')
        ax2.set_xlabel('X (bins)', fontsize=9)
        ax2.set_ylabel('Y (bins)', fontsize=9)
        draw_heterogeneity(ax2)
        cbar2 = plt.colorbar(im2, ax=ax2, label='ΔDosis (Gy)', format='%.1e')
        
        plt.tight_layout()
        
        output_file_case = os.path.join(DATA_DIR, f'homo_analysis_ir192_{case_name.lower()}.png')
        plt.savefig(output_file_case, dpi=150, bbox_inches='tight')
        print(f"\n✅ Gráfica guardada: {output_file_case}")
        print(f"   Tamaño: {np.round(os.path.getsize(output_file_case) / 1e6, 2)} MB")
        
        plt.close(fig_case)
        
        # Estadísticas
        print(f"\n{case_name} - Análisis:")
        print(f"  Dosis máxima hetero: {dose_max_hetero:.6e} Gy")
        print(f"  Dosis máxima homo: {dose_max_homo:.6e} Gy")
        print(f"  Diferencia máxima: {diff_max:.6e} Gy")
    
    print("\n" + "=" * 80)
    print("ANÁLISIS COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()

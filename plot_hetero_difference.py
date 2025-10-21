#!/usr/bin/env python3
"""
Análisis de diferencia de dosis: Casos heterogéneos - Water Homo
Ir-192 200M
Genera matriz 3x2 de gráficas mostrando solo el efecto de la heterogeneidad
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/200M_IR192"
HISTOGRAM_NAME = "h20"

# Parámetros de heterogeneidad (del macro)
HETERO_SIZE = 60.0  # mm (6.0 cm)
HETERO_POS_X = 40.0  # mm (posición en X)
HETERO_POS_Y = 0.0   # mm (posición en Y)

# Casos de simulación - heterogéneos Ir-192
CASES = {
    "Bone_Hetero": "200m_heterogeneous_bone.root",
}

# Caso homogéneo para comparación
HOMO_REF = "200m_water_homogeneous.root"

# Densidades base (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85

# Tamaño de bins
BIN_SIZE_MM = 1.0
BIN_SIZE_CM = BIN_SIZE_MM / 10.0
BIN_VOLUME = BIN_SIZE_CM ** 3

# Exclusión de región central (2mm de radio)
SOURCE_CENTER_X = 150.0  # bins
SOURCE_CENTER_Y = 150.0  # bins
EXCLUDE_RADIUS_MM = 2.0  # mm

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
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def edep_to_dose(edep_values, density_value=DENSITY_WATER):
    """Convierte edep a dosis (Gy)
    Nota: Los archivos ROOT ya tienen edep calculado correctamente.
    Solo necesitamos convertir a Gy usando la densidad del material.
    """
    # Conversión: Dose(Gy) = edep(MeV) * 1.602e-4 / (density * bin_volume)
    # bin_volume = 1 mm³ = 1e-6 cm³
    # Entonces: Dose(Gy) = edep(MeV) * 1.602e-4 / (density * 1e-6)
    bin_volume_cm3 = 1e-6  # 1 mm³ en cm³
    dose_gy = edep_values * 1.602e-4 / (density_value * bin_volume_cm3)
    return dose_gy

def mask_inner_region(dose_map, exclude_radius_mm=EXCLUDE_RADIUS_MM):
    """Máscara para excluir la región central (2mm de radio)"""
    shape = dose_map.shape
    x_indices = np.arange(shape[0])
    y_indices = np.arange(shape[1])
    
    x_coords = x_indices - SOURCE_CENTER_X
    y_coords = y_indices - SOURCE_CENTER_Y
    
    # Crear matriz de distancias radiales
    X, Y = np.meshgrid(x_coords, y_coords, indexing='ij')
    radial_distance = np.sqrt(X**2 + Y**2)
    
    # Máscara: mantener solo lo que está fuera de los 2mm
    mask = radial_distance > exclude_radius_mm
    
    masked_dose = dose_map.copy()
    masked_dose[~mask] = np.nan
    
    return masked_dose

def main():
    print("=" * 80)
    print("DIFERENCIA DE DOSIS: Heterogéneos - Water Homo")
    print("Ir-192 200M")
    print("=" * 80)
    
    # Cargar Water Homo (referencia)
    print("\nCargando casos...")
    filepath_ref = os.path.join(DATA_DIR, HOMO_REF)
    edep_ref = load_histogram(filepath_ref)
    if edep_ref is None:
        print("❌ No se pudo cargar Water Homo")
        return
    
    density_ref = np.ones(edep_ref.shape, dtype=float) * DENSITY_WATER
    dose_ref = edep_to_dose(edep_ref, density_ref)
    print(f"  ✓ Water Homo referencia cargado, shape: {edep_ref.shape}")
    
    # Cargar casos heterogéneos
    datos_hetero = {}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"  Cargando {case_name}...", end=" ")
        edep = load_histogram(filepath)
        if edep is None:
            print("❌")
            continue
        
        density = create_density_map(edep.shape, case_name)
        dose = edep_to_dose(edep, density)
        datos_hetero[case_name] = {
            'dose': dose,
            'density': density
        }
        print(f"✓ (shape: {edep.shape})")
    
    # Crear figura 2 filas (diferencia arriba, dosis abajo)
    fig = plt.figure(figsize=(12, 10))
    fig.suptitle('Análisis de Heterogeneidad: Bone vs Water Homogéneo\n(Ir-192 200M)', 
                 fontsize=14, fontweight='bold', y=0.995)
    
    # Mapas de información
    info_text = {
        "Bone_Hetero": "Hueso Heterogéneo (1.85 g/cm³)",
    }
    
    for case_name, data in datos_hetero.items():
        dose_hetero = data['dose']
        
        # Redimensionar la referencia si es necesario
        from scipy.ndimage import zoom
        if dose_ref.shape != dose_hetero.shape:
            scale_factor = dose_hetero.shape[0] / dose_ref.shape[0]
            dose_ref_resized = zoom(dose_ref, scale_factor, order=1)
        else:
            dose_ref_resized = dose_ref
        
        # Aplicar máscara de exclusión de 2mm al centro
        dose_hetero_masked = mask_inner_region(dose_hetero)
        dose_ref_masked = mask_inner_region(dose_ref_resized)
        
        # FILA 1 (ARRIBA): Diferencia (Hetero - Water Homo)
        ax_diff = plt.subplot(2, 1, 1)
        
        diff_absolute = dose_hetero - dose_ref_resized
        
        # Usar escala logarítmica de diferencia (valores positivos y negativos)
        norm_diff = colors.SymLogNorm(linthresh=1e-5, vmin=-np.nanmax(np.abs(diff_absolute)), 
                                      vmax=np.nanmax(np.abs(diff_absolute)))
        
        im_diff = ax_diff.imshow(
            diff_absolute.T,
            aspect='auto',
            origin='lower',
            cmap='RdBu_r',
            norm=norm_diff
        )
        
        ax_diff.set_title(f'DIFERENCIA: {info_text[case_name]} - Water Homo (Gy)\n(Rojo: Mayor dosis en Hetero, Azul: Mayor dosis en Water)', 
                         fontsize=12, fontweight='bold')
        ax_diff.set_xlabel('X (bins)', fontsize=9)
        ax_diff.set_ylabel('Y (bins)', fontsize=9)
        cbar_diff = plt.colorbar(im_diff, ax=ax_diff, label='ΔDosis (Gy)', format='%.1e')
        
        # FILA 2 (ABAJO): Mapa de dosis heterogéneo
        ax_hetero = plt.subplot(2, 1, 2)
        
        im_hetero = ax_hetero.imshow(
            dose_hetero.T,
            aspect='auto',
            origin='lower',
            cmap='jet',
            norm=colors.LogNorm(vmin=np.nanmin(dose_hetero[dose_hetero > 0]), 
                                vmax=np.nanmax(dose_hetero))
        )
        
        ax_hetero.set_title(f'DOSIS: {info_text[case_name]} (Gy)', 
                           fontsize=12, fontweight='bold')
        ax_hetero.set_xlabel('X (bins)', fontsize=9)
        ax_hetero.set_ylabel('Y (bins)', fontsize=9)
        cbar_hetero = plt.colorbar(im_hetero, ax=ax_hetero, label='Dosis (Gy)', format='%.1e')
        
        # Estadísticas (usando datos mascados sin 2mm centrales)
        mask_valid = ~np.isnan(dose_ref_masked)
        if np.sum(mask_valid) > 0:
            diff_masked = dose_hetero_masked - dose_ref_masked
            diff_mean = np.nanmean(diff_masked[mask_valid])
            diff_max = np.nanmax(np.abs(diff_masked[mask_valid]))
            
            print(f"\n{case_name} (excluyendo 2mm centrales):")
            print(f"  Diferencia promedio: {diff_mean:.6e} Gy")
            print(f"  Diferencia máxima: {diff_max:.6e} Gy")
    
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, 'hetero_difference_from_water_ir192.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")

if __name__ == "__main__":
    main()

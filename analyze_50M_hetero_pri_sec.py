#!/usr/bin/env python3
"""
Análisis de Primarias vs Secundarias - 50M I125
Comparación: Water Homo vs Bone Hetero vs Lung Hetero
Con análisis regional mm-a-mm
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/50M_I125"
HIST_PRIMARY = "h2_eDepPrimary;1"
HIST_SECONDARY = "h2_eDepSecondary;1"

# Archivos para 50M
FILES = {
    "Water_Homo": "brachytherapy_water_homo_50m.root",
    "Bone_Hetero": "brachytherapy_bone_hetero50m.root",
    "Lung_Hetero": "brachytherapy_lung_hetero50m.root"
}

# Densidades (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 0.26

# Parámetros de conversión
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

def edep_to_dose_gy(edep_values, density):
    """Convierte energía depositada (MeV) a dosis (Gy)"""
    mass_g = BIN_VOLUME * density
    dose_gy = edep_values * 1.602e-10 / mass_g
    return dose_gy

def analyze_regional_detail():
    """Análisis detallado de 2 en 2 mm hasta 10 mm para datos 50M"""
    
    print("\n" + "="*70)
    print("📊 ANÁLISIS REGIONAL 50M: DESGLOSE DE 2 EN 2 MM (0-10 mm)")
    print("="*70 + "\n")
    
    materials = {
        "Water_Homo": DENSITY_WATER,
        "Bone_Hetero": DENSITY_BONE,
        "Lung_Hetero": DENSITY_LUNG
    }
    
    center = 150
    
    for material_name, density in materials.items():
        filepath = os.path.join(DATA_DIR, FILES[material_name])
        
        # Verificar si el archivo existe
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            continue
        
        print(f"\n{'='*95}")
        print(f"📍 MATERIAL: {material_name} (ρ={density} g/cm³)")
        print(f"{'='*95}\n")
        
        # Cargar archivo (suponiendo que solo tiene un histograma total, no separado)
        edep_data = load_histogram(filepath, "h20;1")
        
        if edep_data is None:
            print(f"❌ No se pudo cargar el histograma de {material_name}")
            continue
        
        # Crear malla de distancias
        y, x = np.ogrid[:300, :300]
        distance_grid = np.sqrt((x - center)**2 + (y - center)**2)
        
        # Convertir a dosis
        dose_data = edep_to_dose_gy(edep_data, density)
        
        # Totales globales
        dose_total = np.sum(dose_data)
        energy_total = np.sum(edep_data)
        
        print(f"Energía total:    {energy_total:.3e} MeV")
        print(f"Dosis total:      {dose_total:.3e} Gy\n")
        
        print(f"{'Anillo (mm)':<15} {'Energía (MeV)':<18} {'% Energía':<12} {'Dosis (Gy)':<18} {'% Dosis':<12} {'Pixeles':<10}")
        print("-" * 105)
        
        for mm_start in range(0, 10, 2):
            mm_end = mm_start + 2
            
            if mm_start == 0:
                mask = distance_grid < mm_end
                label = f"0-{mm_end} mm"
            else:
                mask = (distance_grid >= mm_start) & (distance_grid < mm_end)
                label = f"{mm_start}-{mm_end} mm"
            
            energy_in_ring = np.sum(edep_data[mask])
            dose_in_ring = np.sum(dose_data[mask])
            
            energy_pct = (energy_in_ring / energy_total * 100) if energy_total > 0 else 0
            dose_pct = (dose_in_ring / dose_total * 100) if dose_total > 0 else 0
            
            num_pixels = np.sum(mask)
            
            print(f"{label:<15} {energy_in_ring:<18.3e} {energy_pct:<12.2f} {dose_in_ring:<18.3e} {dose_pct:<12.2f} {num_pixels:<10}")
        
        # Anillo 8-10 mm específicamente
        mask_8_10 = (distance_grid >= 8) & (distance_grid < 10)
        energy_8_10 = np.sum(edep_data[mask_8_10])
        dose_8_10 = np.sum(dose_data[mask_8_10])
        
        energy_pct_8_10 = (energy_8_10 / energy_total * 100) if energy_total > 0 else 0
        dose_pct_8_10 = (dose_8_10 / dose_total * 100) if dose_total > 0 else 0
        
        num_pixels_8_10 = np.sum(mask_8_10)
        
        print("-" * 105)
        print(f"{'8-10 mm':<15} {energy_8_10:<18.3e} {energy_pct_8_10:<12.2f} {dose_8_10:<18.3e} {dose_pct_8_10:<12.2f} {num_pixels_8_10:<10}")
        
        # Total 0-10 mm
        mask_0_10 = distance_grid < 10
        energy_0_10 = np.sum(edep_data[mask_0_10])
        dose_0_10 = np.sum(dose_data[mask_0_10])
        
        energy_0_10_pct = (energy_0_10 / energy_total * 100) if energy_total > 0 else 0
        dose_0_10_pct = (dose_0_10 / dose_total * 100) if dose_total > 0 else 0
        
        num_pixels_0_10 = np.sum(mask_0_10)
        
        print("=" * 105)
        print(f"{'TOTAL 0-10mm':<15} {energy_0_10:<18.3e} {energy_0_10_pct:<12.2f} {dose_0_10:<18.3e} {dose_0_10_pct:<12.2f} {num_pixels_0_10:<10}")
        
        # Tabla de energía por pixel
        print(f"\n{'Anillo (mm)':<15} {'Pixeles':<12} {'Energía/px (MeV)':<20} {'Dosis/px (Gy)':<20}")
        print("-" * 70)
        
        for mm_start in range(0, 10, 2):
            mm_end = mm_start + 2
            
            if mm_start == 0:
                mask = distance_grid < mm_end
                label = f"0-{mm_end} mm"
            else:
                mask = (distance_grid >= mm_start) & (distance_grid < mm_end)
                label = f"{mm_start}-{mm_end} mm"
            
            num_pixels = np.sum(mask)
            energy_in_ring = np.sum(edep_data[mask])
            dose_in_ring = np.sum(dose_data[mask])
            
            if num_pixels > 0:
                energy_per_px = energy_in_ring / num_pixels
                dose_per_px = dose_in_ring / num_pixels
            else:
                energy_per_px = 0
                dose_per_px = 0
            
            print(f"{label:<15} {num_pixels:<12} {energy_per_px:<20.3e} {dose_per_px:<20.3e}")
        
        # 8-10 mm específicamente
        mask_8_10 = (distance_grid >= 8) & (distance_grid < 10)
        num_pixels = np.sum(mask_8_10)
        energy_in_ring = np.sum(edep_data[mask_8_10])
        dose_in_ring = np.sum(dose_data[mask_8_10])
        
        if num_pixels > 0:
            energy_per_px = energy_in_ring / num_pixels
            dose_per_px = dose_in_ring / num_pixels
        else:
            energy_per_px = 0
            dose_per_px = 0
        
        print("-" * 70)
        print(f"{'8-10 mm':<15} {num_pixels:<12} {energy_per_px:<20.3e} {dose_per_px:<20.3e}")
    
    print("\n" + "="*70)
    print("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ANÁLISIS DE DOSIS - 50M I125")
    print("Water Homo vs Bone Hetero vs Lung Hetero")
    print("="*70 + "\n")
    
    analyze_regional_detail()
    
    print("="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70 + "\n")

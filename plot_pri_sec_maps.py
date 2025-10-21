#!/usr/bin/env python3
"""
Visualización de Energías Primarias y Secundarias
Braquiterapia I125 (100M) - Casos Homogéneos
6 paneles: Primary y Secondary para Water, Bone, Lung
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"
HIST_PRIMARY = "h2_eDepPrimary;1"
HIST_SECONDARY = "h2_eDepSecondary;1"

# Archivos
FILES = {
    "Water_Primary": "brachytherapy_eDepPrimary_homo_water100m.root",
    "Water_Secondary": "brachytherapy_eDepSecondary_homo_water100m.root",
    "Bone_Primary": "brachytherapy_eDepPrimary_homo_bone100m.root",
    "Bone_Secondary": "brachytherapy_eDepSecondary_homo_ bone100m.root",
    "Lung_Primary": "brachytherapy_eDepPrimary_homo_lung100m.root",
    "Lung_Secondary": "brachytherapy_eDepSecondary_homo_lung100m.root"
}

# Densidades (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 1.05  # 64_LUNG_ICRP

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
    """Convierte energía depositada (MeV) a dosis (Gy)
    
    Dosis (Gy) = edep (MeV) * (1.602e-13 J/MeV) / (masa en kg)
    Dosis (Gy) = edep (MeV) * 1.602e-13 / (volumen cm³ * densidad g/cm³ * 1e-3)
    Dosis (Gy) = edep (MeV) * 1.602e-10 / (volumen cm³ * densidad g/cm³)
    """
    mass_g = BIN_VOLUME * density
    dose_gy = edep_values * 1.602e-10 / mass_g
    return dose_gy

def plot_secondary_comparison():
    """Crea visualización de secundarias con colormap rainbow"""
    
    materials = ["Water", "Bone", "Lung"]
    densities = {
        "Water": DENSITY_WATER,
        "Bone": DENSITY_BONE,
        "Lung": DENSITY_LUNG
    }
    
    # Primero cargamos todas las secundarias
    print("\n🔍 Cargando datos de secundarias...\n")
    all_dose_secondary = []
    
    for material in materials:
        density = densities[material]
        filepath_secondary = os.path.join(DATA_DIR, FILES[f"{material}_Secondary"])
        print(f"Cargando {material} Secondary...", end=" ")
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_secondary is None:
            print("❌")
            continue
        print("✅")
        
        # Convertir a dosis (Gy)
        dose_secondary_gy = edep_to_dose_gy(edep_secondary, density)
        all_dose_secondary.append(dose_secondary_gy)
    
    # Encontrar límites comunes
    all_values_stacked = np.hstack([d.flatten() for d in all_dose_secondary])
    all_values_nonzero = all_values_stacked[all_values_stacked > 0]
    
    vmin_abs = np.min(all_values_nonzero)
    vmax_abs = np.max(all_values_nonzero)
    
    print(f"\n📊 Rango absoluto: {vmin_abs:.2e} - {vmax_abs:.2e} Gy\n")
    
    # Visualización con rainbow
    fig = plt.figure(figsize=(15, 5))
    
    for mat_idx, material in enumerate(materials):
        ax = plt.subplot(1, 3, mat_idx + 1)
        
        values_log = np.copy(all_dose_secondary[mat_idx]).astype(float)
        values_log[values_log <= 0] = vmin_abs / 10
        
        im = ax.imshow(values_log.T, aspect='auto', origin='lower', cmap='rainbow',
                      norm=colors.LogNorm(vmin=vmin_abs, vmax=vmax_abs))
        
        density = densities[material]
        ax.set_title(f'{material} (ρ={density} g/cm³)', fontsize=12, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
    
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Dosis (Gy)', fontsize=11)
    
    plt.suptitle('Secundarias - Escala Logarítmica (Rainbow)', 
                 fontsize=14, fontweight='bold')
    plt.subplots_adjust(right=0.9)
    
    output = os.path.join(DATA_DIR, '1_secondary_comparison.png')
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfica guardada: {output}\n")
    plt.close()

def plot_primary_secondary_maps():
    """Crea 6 paneles con mapas de dosis primaria y secundaria"""
    
    fig = plt.figure(figsize=(14, 10))
    
    # Layout: 3 filas (materials) x 2 columnas (Primary, Secondary)
    materials = ["Water", "Bone", "Lung"]
    densities = {
        "Water": DENSITY_WATER,
        "Bone": DENSITY_BONE,
        "Lung": DENSITY_LUNG
    }
    
    for mat_idx, material in enumerate(materials):
        density = densities[material]
        
        # Panel Primary
        ax_primary = plt.subplot(3, 2, mat_idx * 2 + 1)
        
        filepath_primary = os.path.join(DATA_DIR, FILES[f"{material}_Primary"])
        print(f"Cargando {material} Primary...", end=" ")
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        
        if edep_primary is None:
            print("❌")
            ax_primary.text(0.5, 0.5, f"Error cargando {material} Primary", 
                          ha='center', va='center', transform=ax_primary.transAxes)
            continue
        print("✅")
        
        # Convertir a dosis (Gy)
        dose_primary_gy = edep_to_dose_gy(edep_primary, density)
        
        # Escala log
        values_log = np.copy(dose_primary_gy).astype(float)
        values_log[values_log <= 0] = np.min(values_log[values_log > 0]) / 10
        
        im_primary = ax_primary.imshow(
            values_log.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=values_log.min(), vmax=values_log.max())
        )
        
        ax_primary.set_title(f'{material} - Primaria (ρ={density} g/cm³)', fontsize=11, fontweight='bold')
        ax_primary.set_xlabel('X (bins)')
        ax_primary.set_ylabel('Y (bins)')
        plt.colorbar(im_primary, ax=ax_primary, label='Dosis (Gy)')
        
        # Panel Secondary
        ax_secondary = plt.subplot(3, 2, mat_idx * 2 + 2)
        
        filepath_secondary = os.path.join(DATA_DIR, FILES[f"{material}_Secondary"])
        print(f"Cargando {material} Secondary...", end=" ")
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_secondary is None:
            print("❌")
            ax_secondary.text(0.5, 0.5, f"Error cargando {material} Secondary", 
                            ha='center', va='center', transform=ax_secondary.transAxes)
            continue
        print("✅")
        
        # Convertir a dosis (Gy)
        dose_secondary_gy = edep_to_dose_gy(edep_secondary, density)
        
        # Escala log
        values_log = np.copy(dose_secondary_gy).astype(float)
        values_log[values_log <= 0] = np.min(values_log[values_log > 0]) / 10
        
        im_secondary = ax_secondary.imshow(
            values_log.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=values_log.min(), vmax=values_log.max())
        )
        
        ax_secondary.set_title(f'{material} - Secundaria (ρ={density} g/cm³)', fontsize=11, fontweight='bold')
        ax_secondary.set_xlabel('X (bins)')
        ax_secondary.set_ylabel('Y (bins)')
        plt.colorbar(im_secondary, ax=ax_secondary, label='Dosis (Gy)')
    
    plt.suptitle('Mapas de Energía Depositada - Primarias vs Secundarias\nI125 100M (Casos Homogéneos)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '0_primary_secondary_maps.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}\n")
    plt.close()

def analyze_secondary_influence():
    """Analiza qué material tiene mayor influencia de dosis secundaria"""
    
    print("\n" + "="*70)
    print("📊 ANÁLISIS DE INFLUENCIA DE DOSIS SECUNDARIA")
    print("="*70 + "\n")
    
    materials = ["Water", "Bone", "Lung"]
    densities = {
        "Water": DENSITY_WATER,
        "Bone": DENSITY_BONE,
        "Lung": DENSITY_LUNG
    }
    
    stats = {}
    
    for material in materials:
        density = densities[material]
        
        # Cargar primaria
        filepath_primary = os.path.join(DATA_DIR, FILES[f"{material}_Primary"])
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        
        # Cargar secundaria
        filepath_secondary = os.path.join(DATA_DIR, FILES[f"{material}_Secondary"])
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_primary is None or edep_secondary is None:
            continue
        
        # Convertir a dosis
        dose_primary = edep_to_dose_gy(edep_primary, density)
        dose_secondary = edep_to_dose_gy(edep_secondary, density)
        dose_total = dose_primary + dose_secondary
        
        # Valores no-cero para cálculos significativos
        primary_nonzero = dose_primary[dose_primary > 0]
        secondary_nonzero = dose_secondary[dose_secondary > 0]
        total_nonzero = dose_total[dose_total > 0]
        
        # Calcular estadísticas
        if len(primary_nonzero) > 0 and len(secondary_nonzero) > 0:
            stats[material] = {
                'primary_mean': np.mean(primary_nonzero),
                'primary_max': np.max(primary_nonzero),
                'primary_sum': np.sum(dose_primary),
                'secondary_mean': np.mean(secondary_nonzero),
                'secondary_max': np.max(secondary_nonzero),
                'secondary_sum': np.sum(dose_secondary),
                'total_sum': np.sum(dose_total),
                'sec_fraction_mean': np.mean(secondary_nonzero) / (np.mean(primary_nonzero) + np.mean(secondary_nonzero)),
                'sec_fraction_sum': np.sum(dose_secondary) / (np.sum(dose_primary) + np.sum(dose_secondary)),
            }
    
    # Imprimir resultados
    print(f"{'Material':<10} {'Primary Mean':<15} {'Secondary Mean':<15} {'Sec/Total %':<12}")
    print("-" * 60)
    
    max_sec_fraction = 0
    influential_material = None
    
    for material in materials:
        if material in stats:
            s = stats[material]
            sec_fraction_pct = s['sec_fraction_mean'] * 100
            print(f"{material:<10} {s['primary_mean']:.3e} Gy {s['secondary_mean']:.3e} Gy {sec_fraction_pct:.1f}%")
            
            if sec_fraction_pct > max_sec_fraction:
                max_sec_fraction = sec_fraction_pct
                influential_material = material
    
    print("\n" + "-" * 60)
    print(f"\n{'Material':<10} {'Primary Sum':<15} {'Secondary Sum':<15} {'Sec/Total %':<12}")
    print("-" * 60)
    
    for material in materials:
        if material in stats:
            s = stats[material]
            sec_fraction_sum_pct = s['sec_fraction_sum'] * 100
            print(f"{material:<10} {s['primary_sum']:.3e} Gy {s['secondary_sum']:.3e} Gy {sec_fraction_sum_pct:.1f}%")
    
    print("\n" + "="*70)
    print(f"🎯 MATERIAL CON MAYOR INFLUENCIA SECUNDARIA: {influential_material}")
    print(f"   Contribución secundaria: {max_sec_fraction:.1f}% de la dosis total")
    print("="*70 + "\n")

def analyze_secondary_by_region():
    """Analiza influencia secundaria dividiendo el mapa en regiones radiales"""
    
    print("\n" + "="*70)
    print("📊 ANÁLISIS REGIONAL DE DOSIS SECUNDARIA")
    print("="*70 + "\n")
    
    materials = ["Water", "Bone", "Lung"]
    densities = {
        "Water": DENSITY_WATER,
        "Bone": DENSITY_BONE,
        "Lung": DENSITY_LUNG
    }
    
    # Definir regiones por distancia desde el centro (en bins)
    # Histograma es 300x300, centro en (150, 150)
    center = 150
    regions = {
        '0-5 mm': (0, 5),
        '5-10 mm': (5, 10),
        '10-30 mm': (10, 30),
        '30-50 mm': (30, 50),
        '50-150 mm': (50, 150)
    }
    
    print(f"Centro del mapa: ({center}, {center})")
    print(f"Rango total: ±150.5 mm (~1 mm/bin)\n")
    
    for material in materials:
        print(f"\n{'='*70}")
        print(f"📍 MATERIAL: {material}")
        print(f"{'='*70}")
        
        density = densities[material]
        
        # Cargar archivos
        filepath_primary = os.path.join(DATA_DIR, FILES[f"{material}_Primary"])
        filepath_secondary = os.path.join(DATA_DIR, FILES[f"{material}_Secondary"])
        
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_primary is None or edep_secondary is None:
            print(f"❌ Error cargando datos para {material}")
            continue
        
        # Convertir a dosis
        dose_primary = edep_to_dose_gy(edep_primary, density)
        dose_secondary = edep_to_dose_gy(edep_secondary, density)
        
        print(f"\n{'Región':<20} {'Primary (Gy)':<15} {'Secondary (Gy)':<15} {'Sec %':<10} {'Sec % del Total':<15}")
        print("-" * 85)
        
        secondary_total = np.sum(dose_secondary)
        
        for region_name, (dist_min, dist_max) in regions.items():
            # Crear máscara para pixeles dentro de la región
            y, x = np.ogrid[:300, :300]
            distance = np.sqrt((x - center)**2 + (y - center)**2)
            mask = (distance >= dist_min) & (distance < dist_max)
            
            # Sumar dosis en la región
            primary_region = np.sum(dose_primary[mask])
            secondary_region = np.sum(dose_secondary[mask])
            total_region = primary_region + secondary_region
            
            if total_region > 0:
                sec_pct = (secondary_region / total_region) * 100
            else:
                sec_pct = 0
            
            if secondary_total > 0:
                sec_pct_total = (secondary_region / secondary_total) * 100
            else:
                sec_pct_total = 0
            
            print(f"{region_name:<20} {primary_region:<15.3e} {secondary_region:<15.3e} {sec_pct:<10.1f}% {sec_pct_total:<15.1f}%")
        
        # Estadística total
        print("-" * 85)
        primary_total = np.sum(dose_primary)
        total_all = primary_total + secondary_total
        sec_pct_total_all = (secondary_total / total_all * 100) if total_all > 0 else 0
        print(f"{'TOTAL':<20} {primary_total:<15.3e} {secondary_total:<15.3e} {sec_pct_total_all:<10.1f}% {'100.0':<15}%")
    
    print("\n" + "="*70)
    print("="*70 + "\n")

def analyze_secondary_by_region_energy():
    """Analiza influencia secundaria por energía (MeV) dividiendo el mapa en regiones radiales"""
    
    print("\n" + "="*70)
    print("📊 ANÁLISIS REGIONAL DE ENERGÍA SECUNDARIA (MeV)")
    print("="*70 + "\n")
    
    materials = ["Water", "Bone", "Lung"]
    
    # Definir regiones por distancia desde el centro (en bins)
    center = 150
    regions = {
        '0-5 mm': (0, 5),
        '5-10 mm': (5, 10),
        '10-30 mm': (10, 30),
        '30-50 mm': (30, 50),
        '50-150 mm': (50, 150)
    }
    
    print(f"Centro del mapa: ({center}, {center})")
    print(f"Rango total: ±150.5 mm (~1 mm/bin)\n")
    
    for material in materials:
        print(f"\n{'='*70}")
        print(f"📍 MATERIAL: {material}")
        print(f"{'='*70}")
        
        # Cargar archivos (energía en MeV directamente)
        filepath_primary = os.path.join(DATA_DIR, FILES[f"{material}_Primary"])
        filepath_secondary = os.path.join(DATA_DIR, FILES[f"{material}_Secondary"])
        
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_primary is None or edep_secondary is None:
            print(f"❌ Error cargando datos para {material}")
            continue
        
        # Usar energía directamente (MeV)
        energy_primary = edep_primary  # en MeV
        energy_secondary = edep_secondary  # en MeV
        
        print(f"\n{'Región':<20} {'Primary (MeV)':<15} {'Secondary (MeV)':<15} {'Sec %':<10} {'Sec % del Total':<15}")
        print("-" * 85)
        
        secondary_total = np.sum(energy_secondary)
        
        for region_name, (dist_min, dist_max) in regions.items():
            # Crear máscara para pixeles dentro de la región
            y, x = np.ogrid[:300, :300]
            distance = np.sqrt((x - center)**2 + (y - center)**2)
            mask = (distance >= dist_min) & (distance < dist_max)
            
            # Sumar energía en la región
            primary_region = np.sum(energy_primary[mask])
            secondary_region = np.sum(energy_secondary[mask])
            total_region = primary_region + secondary_region
            
            if total_region > 0:
                sec_pct = (secondary_region / total_region) * 100
            else:
                sec_pct = 0
            
            if secondary_total > 0:
                sec_pct_total = (secondary_region / secondary_total) * 100
            else:
                sec_pct_total = 0
            
            print(f"{region_name:<20} {primary_region:<15.3e} {secondary_region:<15.3e} {sec_pct:<10.1f}% {sec_pct_total:<15.1f}%")
        
        # Estadística total
        print("-" * 85)
        primary_total = np.sum(energy_primary)
        total_all = primary_total + secondary_total
        sec_pct_total_all = (secondary_total / total_all * 100) if total_all > 0 else 0
        print(f"{'TOTAL':<20} {primary_total:<15.3e} {secondary_total:<15.3e} {sec_pct_total_all:<10.1f}% {'100.0':<15}%")
    
    print("\n" + "="*70)
    print("="*70 + "\n")

def diagnostic_energy_analysis():
    """Análisis diagnóstico detallado de energías para verificar inconsistencias"""
    
    print("\n" + "="*70)
    print("🔍 DIAGNÓSTICO DE ENERGÍA - VERIFICACIÓN DE INCONSISTENCIAS")
    print("="*70 + "\n")
    
    materials = ["Water", "Bone", "Lung"]
    
    for material in materials:
        print(f"\n{'='*70}")
        print(f"📍 MATERIAL: {material}")
        print(f"{'='*70}\n")
        
        # Cargar archivos
        filepath_primary = os.path.join(DATA_DIR, FILES[f"{material}_Primary"])
        filepath_secondary = os.path.join(DATA_DIR, FILES[f"{material}_Secondary"])
        
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_primary is None or edep_secondary is None:
            print(f"❌ Error cargando datos para {material}")
            continue
        
        # Estadísticas básicas
        primary_total = np.sum(edep_primary)
        secondary_total = np.sum(edep_secondary)
        total_energy = primary_total + secondary_total
        
        # Propiedades del array
        print(f"Dimensiones: {edep_primary.shape}")
        print(f"Tipo de dato: {edep_primary.dtype}\n")
        
        # Estadísticas por tipo
        print(f"{'ENERGÍA PRIMARIA':<30}")
        print("-" * 60)
        print(f"Suma total:        {primary_total:.3e} MeV")
        print(f"Media (todos):     {np.mean(edep_primary):.3e} MeV")
        print(f"Mediana (todos):   {np.median(edep_primary):.3e} MeV")
        print(f"Max:               {np.max(edep_primary):.3e} MeV")
        print(f"Min:               {np.min(edep_primary):.3e} MeV")
        print(f"Pixeles con >0:    {np.sum(edep_primary > 0)} / {edep_primary.size}")
        print(f"% con energía:     {(np.sum(edep_primary > 0) / edep_primary.size * 100):.2f}%")
        print(f"Mean (no-zero):    {np.mean(edep_primary[edep_primary > 0]):.3e} MeV\n")
        
        print(f"{'ENERGÍA SECUNDARIA':<30}")
        print("-" * 60)
        print(f"Suma total:        {secondary_total:.3e} MeV")
        print(f"Media (todos):     {np.mean(edep_secondary):.3e} MeV")
        print(f"Mediana (todos):   {np.median(edep_secondary):.3e} MeV")
        print(f"Max:               {np.max(edep_secondary):.3e} MeV")
        print(f"Min:               {np.min(edep_secondary):.3e} MeV")
        print(f"Pixeles con >0:    {np.sum(edep_secondary > 0)} / {edep_secondary.size}")
        print(f"% con energía:     {(np.sum(edep_secondary > 0) / edep_secondary.size * 100):.2f}%")
        print(f"Mean (no-zero):    {np.mean(edep_secondary[edep_secondary > 0]):.3e} MeV\n")
        
        print(f"{'RESUMEN TOTAL':<30}")
        print("-" * 60)
        print(f"Energía primaria:     {primary_total:.3e} MeV")
        print(f"Energía secundaria:   {secondary_total:.3e} MeV")
        print(f"Energía total:        {total_energy:.3e} MeV")
        print(f"Ratio Sec/Prim:       {(secondary_total/primary_total*100):.1f}%")
        print(f"Ratio Sec/Total:      {(secondary_total/total_energy*100):.1f}%\n")
        
        # Análisis espacial
        center = 150
        
        print(f"{'DISTRIBUCIÓN ESPACIAL':<30}")
        print("-" * 60)
        
        # Distancia máxima con energía
        y, x = np.ogrid[:300, :300]
        distance_grid = np.sqrt((x - center)**2 + (y - center)**2)
        
        max_dist_primary = np.max(distance_grid[edep_primary > 0])
        max_dist_secondary = np.max(distance_grid[edep_secondary > 0])
        
        print(f"Distancia máxima (primaria):   {max_dist_primary:.1f} mm")
        print(f"Distancia máxima (secundaria): {max_dist_secondary:.1f} mm\n")
        
        # Energía en diferentes radios
        print(f"{'Radio':<15} {'Primary (MeV)':<20} {'Secondary (MeV)':<20} {'% Prim':<10} {'% Sec':<10}")
        print("-" * 75)
        
        for radius in [5, 10, 20, 30, 50, 100, 150]:
            mask = distance_grid < radius
            prim_in_radius = np.sum(edep_primary[mask])
            sec_in_radius = np.sum(edep_secondary[mask])
            prim_pct = (prim_in_radius / primary_total * 100) if primary_total > 0 else 0
            sec_pct = (sec_in_radius / secondary_total * 100) if secondary_total > 0 else 0
            print(f"< {radius} mm{'':<10} {prim_in_radius:<20.3e} {sec_in_radius:<20.3e} {prim_pct:<10.1f} {sec_pct:<10.1f}")
    
    print("\n" + "="*70)
    print("="*70 + "\n")

def detailed_0_5mm_analysis():
    """Análisis detallado de 2 en 2 mm hasta 10mm"""
    
    print("\n" + "="*70)
    print("📊 ANÁLISIS DETALLADO: DESGLOSE DE 2 EN 2 MM (0-10 mm)")
    print("="*70 + "\n")
    
    materials = ["Water", "Bone", "Lung"]
    center = 150
    
    for material in materials:
        print(f"\n{'='*95}")
        print(f"📍 MATERIAL: {material}")
        print(f"{'='*95}\n")
        
        # Cargar archivos
        filepath_primary = os.path.join(DATA_DIR, FILES[f"{material}_Primary"])
        filepath_secondary = os.path.join(DATA_DIR, FILES[f"{material}_Secondary"])
        
        edep_primary = load_histogram(filepath_primary, HIST_PRIMARY)
        edep_secondary = load_histogram(filepath_secondary, HIST_SECONDARY)
        
        if edep_primary is None or edep_secondary is None:
            print(f"❌ Error cargando datos para {material}")
            continue
        
        # Crear malla de distancias
        y, x = np.ogrid[:300, :300]
        distance_grid = np.sqrt((x - center)**2 + (y - center)**2)
        
        # Totales globales
        primary_total = np.sum(edep_primary)
        secondary_total = np.sum(edep_secondary)
        
        print(f"{'Anillo (mm)':<15} {'Primary (MeV)':<18} {'% Prim':<10} {'Secondary (MeV)':<18} {'% Sec':<10} {'Sec/Total %':<12} {'Pixeles':<10}")
        print("-" * 110)
        
        # Análisis de 2 en 2 mm hasta 10 mm
        cumulative_primary = 0
        cumulative_secondary = 0
        
        for mm_start in range(0, 10, 2):
            mm_end = mm_start + 2
            
            if mm_start == 0:
                mask = distance_grid < mm_end
                label = f"0-{mm_end} mm"
            else:
                mask = (distance_grid >= mm_start) & (distance_grid < mm_end)
                label = f"{mm_start}-{mm_end} mm"
            
            prim_in_ring = np.sum(edep_primary[mask])
            sec_in_ring = np.sum(edep_secondary[mask])
            total_in_ring = prim_in_ring + sec_in_ring
            
            prim_pct = (prim_in_ring / primary_total * 100) if primary_total > 0 else 0
            sec_pct = (sec_in_ring / secondary_total * 100) if secondary_total > 0 else 0
            
            if total_in_ring > 0:
                sec_fraction = (sec_in_ring / total_in_ring * 100)
            else:
                sec_fraction = 0
            
            num_pixels = np.sum(mask)
            
            cumulative_primary += prim_in_ring if mm_start > 0 else 0
            cumulative_secondary += sec_in_ring if mm_start > 0 else 0
            
            print(f"{label:<15} {prim_in_ring:<18.3e} {prim_pct:<10.2f} {sec_in_ring:<18.3e} {sec_pct:<10.2f} {sec_fraction:<12.1f} {num_pixels:<10}")
        
        # Anillo 8-10 mm específicamente
        mask_8_10 = (distance_grid >= 8) & (distance_grid < 10)
        prim_8_10 = np.sum(edep_primary[mask_8_10])
        sec_8_10 = np.sum(edep_secondary[mask_8_10])
        total_8_10 = prim_8_10 + sec_8_10
        
        prim_pct_8_10 = (prim_8_10 / primary_total * 100) if primary_total > 0 else 0
        sec_pct_8_10 = (sec_8_10 / secondary_total * 100) if secondary_total > 0 else 0
        
        if total_8_10 > 0:
            sec_fraction_8_10 = (sec_8_10 / total_8_10 * 100)
        else:
            sec_fraction_8_10 = 0
        
        num_pixels_8_10 = np.sum(mask_8_10)
        
        print("-" * 110)
        print(f"{'8-10 mm':<15} {prim_8_10:<18.3e} {prim_pct_8_10:<10.2f} {sec_8_10:<18.3e} {sec_pct_8_10:<10.2f} {sec_fraction_8_10:<12.1f} {num_pixels_8_10:<10}")
        
        # Total 0-10 mm
        mask_0_10 = distance_grid < 10
        prim_0_10 = np.sum(edep_primary[mask_0_10])
        sec_0_10 = np.sum(edep_secondary[mask_0_10])
        total_0_10 = prim_0_10 + sec_0_10
        
        prim_0_10_pct = (prim_0_10 / primary_total * 100) if primary_total > 0 else 0
        sec_0_10_pct = (sec_0_10 / secondary_total * 100) if secondary_total > 0 else 0
        
        if total_0_10 > 0:
            sec_0_10_fraction = (sec_0_10 / total_0_10 * 100)
        else:
            sec_0_10_fraction = 0
        
        num_pixels_0_10 = np.sum(mask_0_10)
        
        print("=" * 110)
        print(f"{'TOTAL 0-10mm':<15} {prim_0_10:<18.3e} {prim_0_10_pct:<10.2f} {sec_0_10:<18.3e} {sec_0_10_pct:<10.2f} {sec_0_10_fraction:<12.1f} {num_pixels_0_10:<10}")
        
        # Tabla de energía por pixel
        print(f"\n{'Anillo (mm)':<15} {'Pixeles':<12} {'Primary/px':<18} {'Secondary/px':<18} {'Total/px':<18}")
        print("-" * 85)
        
        for mm_start in range(0, 10, 2):
            mm_end = mm_start + 2
            
            if mm_start == 0:
                mask = distance_grid < mm_end
                label = f"0-{mm_end} mm"
            else:
                mask = (distance_grid >= mm_start) & (distance_grid < mm_end)
                label = f"{mm_start}-{mm_end} mm"
            
            num_pixels = np.sum(mask)
            prim_in_ring = np.sum(edep_primary[mask])
            sec_in_ring = np.sum(edep_secondary[mask])
            
            if num_pixels > 0:
                prim_per_px = prim_in_ring / num_pixels
                sec_per_px = sec_in_ring / num_pixels
                total_per_px = (prim_in_ring + sec_in_ring) / num_pixels
            else:
                prim_per_px = 0
                sec_per_px = 0
                total_per_px = 0
            
            print(f"{label:<15} {num_pixels:<12} {prim_per_px:<18.3e} {sec_per_px:<18.3e} {total_per_px:<18.3e}")
        
        # 8-10 mm específicamente
        mask_8_10 = (distance_grid >= 8) & (distance_grid < 10)
        num_pixels = np.sum(mask_8_10)
        prim_in_ring = np.sum(edep_primary[mask_8_10])
        sec_in_ring = np.sum(edep_secondary[mask_8_10])
        
        if num_pixels > 0:
            prim_per_px = prim_in_ring / num_pixels
            sec_per_px = sec_in_ring / num_pixels
            total_per_px = (prim_in_ring + sec_in_ring) / num_pixels
        else:
            prim_per_px = 0
            sec_per_px = 0
            total_per_px = 0
        
        print("-" * 85)
        print(f"{'8-10 mm':<15} {num_pixels:<12} {prim_per_px:<18.3e} {sec_per_px:<18.3e} {total_per_px:<18.3e}")
    
    print("\n" + "="*70)
    print("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("VISUALIZACIÓN DE MAPAS: PRIMARIAS vs SECUNDARIAS - I125 100M")
    print("="*70 + "\n")
    
    print("📊 GENERANDO VISUALIZACIÓN 1: Primarias vs Secundarias (escala individual)")
    print("-"*70)
    plot_primary_secondary_maps()
    
    print("\n📊 GENERANDO VISUALIZACIÓN 2: Secundarias (Rainbow)")
    print("-"*70)
    plot_secondary_comparison()
    
    print("\n📊 GENERANDO ANÁLISIS 3: Análisis de influencia secundaria")
    print("-"*70)
    analyze_secondary_influence()
    
    print("\n📊 GENERANDO ANÁLISIS 4: Análisis regional de secundaria")
    print("-"*70)
    analyze_secondary_by_region()
    
    print("\n📊 GENERANDO ANÁLISIS 5: Análisis regional de secundaria (ENERGÍA en MeV)")
    print("-"*70)
    analyze_secondary_by_region_energy()
    
    print("\n📊 GENERANDO ANÁLISIS 6: Diagnóstico de Energía (Verificación)")
    print("-"*70)
    diagnostic_energy_analysis()
    
    print("\n📊 GENERANDO ANÁLISIS 7: Desglose mm-a-mm de los primeros 5mm")
    print("-"*70)
    detailed_0_5mm_analysis()
    
    print("="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70 + "\n")

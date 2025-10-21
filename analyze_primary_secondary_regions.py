#!/usr/bin/env python3
"""
Análisis de primarias vs secundarias por regiones de distancia radial
Calcula porcentaje de primarias y secundarias en cada región:
- 0-1 mm
- 1-5 mm
- 5-10 mm
- 10-20 mm
- 20-30 mm
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os
import pandas as pd

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/100M_I125_pri-sec"

# Casos homogéneos a analizar
HOMO_CASES = {
    "Lung_Hueco_Homo": {
        "total": "brachytherapy_lunghueco_homo100m.root",
        "primary": "brachytherapy_eDepPrimary_lunghueco_homo100m.root",
        "secondary": "brachytherapy_eDepSecondary_lunghueco_homo100m.root",
        "density": 0.2958,  # MIRD Lung
    },
    "Bone_Homo": {
        "total": "brachytherapy_homo_bone100m.root",
        "primary": "brachytherapy_eDepPrimary_homo_bone100m.root",
        "secondary": "brachytherapy_eDepSecondary_homo_ bone100m.root",  # Nota: hay espacio
        "density": 1.85,  # Bone
    },
    "Water_Homo": {
        "total": "brachytherapy_homo_water100m.root",
        "primary": "brachytherapy_eDepPrimary_homo_water100m.root",
        "secondary": "brachytherapy_eDepSecondary_homo_water100m.root",
        "density": 1.0,  # Water
    },
}

# Densidades base (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG_MIRD = 0.2958

# Tamaño de bins en mm
BIN_SIZE_MM = 1.0

# Centro de la geometría (fuente de I125)
SOURCE_CENTER_X = 150.0  # bins
SOURCE_CENTER_Y = 150.0  # bins

# Regiones de análisis en mm
REGIONS = {
    "3-4 mm": (3.0, 4.0),
    "4-5 mm": (4.0, 5.0),
    "5-6 mm": (5.0, 6.0),
    "6-7 mm": (6.0, 7.0),
    "7-8 mm": (7.0, 8.0),
    "8-9 mm": (8.0, 9.0),
    "9-10 mm": (9.0, 10.0),
    "10-11 mm": (10.0, 11.0),
    "11-12 mm": (11.0, 12.0),
    "12-13 mm": (12.0, 13.0),
    "13-14 mm": (13.0, 14.0),
    "14-15 mm": (14.0, 15.0),
    "15-16 mm": (15.0, 16.0),
    "16-17 mm": (16.0, 17.0),
    "17-18 mm": (17.0, 18.0),
    "18-19 mm": (18.0, 19.0),
    "19-20 mm": (19.0, 20.0),
    "20-25 mm": (20.0, 25.0),
    "25-30 mm": (25.0, 30.0),
    "30-40 mm": (30.0, 40.0),
    "40-50 mm": (40.0, 50.0),
    "50-60 mm": (50.0, 60.0),
    "60-70 mm": (60.0, 70.0),
}

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

def calculate_radial_distance(x, y, source_x, source_y):
    """Calcula distancia radial en mm desde la fuente"""
    # Convertir bins a mm
    dx_mm = (x - source_x) * BIN_SIZE_MM
    dy_mm = (y - source_y) * BIN_SIZE_MM
    distance_mm = np.sqrt(dx_mm**2 + dy_mm**2)
    return distance_mm

def analyze_regions(edep_primary, edep_secondary, edep_total):
    """Analiza composición de primarias/secundarias en cada región"""
    
    # Crear matrices de distancia radial
    nx, ny = edep_primary.shape
    x_coords, y_coords = np.meshgrid(np.arange(nx), np.arange(ny), indexing='ij')
    
    # Calcular distancias radiales para cada bin
    radial_distances = calculate_radial_distance(x_coords, y_coords, SOURCE_CENTER_X, SOURCE_CENTER_Y)
    
    results = {}
    
    for region_name, (r_min, r_max) in REGIONS.items():
        # Máscara para la región
        mask = (radial_distances >= r_min) & (radial_distances < r_max)
        
        # Extraer energía depositada en la región
        primary_in_region = edep_primary[mask]
        secondary_in_region = edep_secondary[mask]
        total_in_region = edep_total[mask]
        
        # Calcular totales
        total_primary = np.nansum(primary_in_region)
        total_secondary = np.nansum(secondary_in_region)
        total_energy = np.nansum(total_in_region)
        
        # Calcular porcentajes
        if total_energy > 0:
            pct_primary = 100.0 * total_primary / total_energy
            pct_secondary = 100.0 * total_secondary / total_energy
        else:
            pct_primary = 0.0
            pct_secondary = 0.0
        
        # Número de bins con energía
        bins_with_energy = np.sum(total_in_region > 0)
        
        results[region_name] = {
            'total_primary': total_primary,
            'total_secondary': total_secondary,
            'total_energy': total_energy,
            'pct_primary': pct_primary,
            'pct_secondary': pct_secondary,
            'bins_with_energy': bins_with_energy,
            'avg_primary': np.nanmean(primary_in_region[primary_in_region > 0]) if np.any(primary_in_region > 0) else 0,
            'avg_secondary': np.nanmean(secondary_in_region[secondary_in_region > 0]) if np.any(secondary_in_region > 0) else 0,
        }
    
    return results

def main():
    print("=" * 90)
    print("ANÁLISIS DE PRIMARIAS vs SECUNDARIAS POR REGIONES")
    print("=" * 90)
    
    case_order = ["Lung_Hueco_Homo", "Bone_Homo", "Water_Homo"]
    all_results = {}
    
    # Cargar datos
    for case_name in case_order:
        if case_name not in HOMO_CASES:
            continue
        
        files = HOMO_CASES[case_name]
        print(f"\nCargando {case_name}...")
        
        edep_primary = load_histogram(files["primary"], "h2_eDepPrimary")
        edep_secondary = load_histogram(files["secondary"], "h2_eDepSecondary")
        edep_total = load_histogram(files["total"], "h20")
        
        if edep_primary is None or edep_secondary is None or edep_total is None:
            print(f"  ❌ No se pudo cargar histogramas")
            continue
        
        print(f"  ✓ Histogramas cargados")
        
        # Analizar regiones
        results = analyze_regions(edep_primary, edep_secondary, edep_total)
        all_results[case_name] = results
        
        # Imprimir tabla
        print(f"\n{case_name}:")
        print("-" * 90)
        print(f"{'Región':<15} {'Primarias':<15} {'Secundarias':<15} {'Primarias %':<15} {'Secundarias %':<15}")
        print("-" * 90)
        
        for region_name in REGIONS.keys():
            r = results[region_name]
            print(f"{region_name:<15} {r['total_primary']:>13.2e} MeV {r['total_secondary']:>13.2e} MeV "
                  f"{r['pct_primary']:>13.2f}% {r['pct_secondary']:>13.2f}%")
        
        print("-" * 90)
        total_primary = sum(r['total_primary'] for r in results.values())
        total_secondary = sum(r['total_secondary'] for r in results.values())
        print(f"{'TOTAL':<15} {total_primary:>13.2e} MeV {total_secondary:>13.2e} MeV "
              f"{100*total_primary/(total_primary+total_secondary):>13.2f}% {100*total_secondary/(total_primary+total_secondary):>13.2f}%")
    
    # Crear visualización
    create_visualization(all_results)

def create_visualization(all_results):
    """Crear gráfico de líneas con los 3 casos"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24, 10))
    fig.suptitle('Análisis de Primarias vs Secundarias por Región (3-70 mm)', fontsize=14, fontweight='bold')
    
    region_names = list(REGIONS.keys())
    x_pos = np.arange(len(region_names))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Azul, naranja, verde
    case_labels_dict = {
        "Lung_Hueco_Homo": "Lung MIRD (0.2958 g/cm³)",
        "Bone_Homo": "Hueso (1.85 g/cm³)",
        "Water_Homo": "Agua (1.0 g/cm³)"
    }
    
    # ========== GRÁFICO 1: PORCENTAJE DE PRIMARIAS ==========
    for idx, (case_name, color) in enumerate(zip(["Lung_Hueco_Homo", "Bone_Homo", "Water_Homo"], colors)):
        if case_name not in all_results:
            continue
        
        results = all_results[case_name]
        primary_pcts = [results[r]['pct_primary'] for r in region_names]
        
        ax1.plot(x_pos, primary_pcts, 'o-', label=case_labels_dict[case_name], 
                linewidth=2.5, markersize=8, color=color)
        
        # Añadir valores en los puntos
        for i, pct in enumerate(primary_pcts):
            ax1.text(i, pct + 0.5, f'{pct:.1f}%', ha='center', fontsize=9, fontweight='bold')
    
    ax1.set_ylabel('Porcentaje de Primarias (%)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Región de Distancia', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(region_names, rotation=45, ha='right')
    ax1.set_ylim(98, 100.5)
    ax1.legend(loc='best', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Composición de Primarias por Región', fontsize=12, fontweight='bold')
    
    # ========== GRÁFICO 2: PORCENTAJE DE SECUNDARIAS ==========
    for idx, (case_name, color) in enumerate(zip(["Lung_Hueco_Homo", "Bone_Homo", "Water_Homo"], colors)):
        if case_name not in all_results:
            continue
        
        results = all_results[case_name]
        secondary_pcts = [results[r]['pct_secondary'] for r in region_names]
        
        ax2.plot(x_pos, secondary_pcts, 's-', label=case_labels_dict[case_name], 
                linewidth=2.5, markersize=8, color=color)
        
        # Añadir valores en los puntos
        for i, pct in enumerate(secondary_pcts):
            ax2.text(i, pct + 0.02, f'{pct:.2f}%', ha='center', fontsize=9, fontweight='bold')
    
    ax2.set_ylabel('Porcentaje de Secundarias (%)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Región de Distancia', fontsize=12, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(region_names, rotation=45, ha='right')
    ax2.set_ylim(0, 1.5)
    ax2.legend(loc='best', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Composición de Secundarias por Región', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    output_file = os.path.join(DATA_DIR, 'regional_analysis_primary_secondary.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    print(f"   Tamaño: {np.round(os.path.getsize(output_file) / 1e6, 2)} MB")
    create_csv_report(all_results)
    plt.show()

def create_csv_report(all_results):
    """Crear reporte CSV con todos los datos"""
    
    data = []
    for case_name in ["Lung_Hueco_Homo", "Bone_Homo", "Water_Homo"]:
        if case_name not in all_results:
            continue
        
        results = all_results[case_name]
        material = "Lung MIRD" if "Lung" in case_name else "Bone"
        
        for region_name in REGIONS.keys():
            r = results[region_name]
            data.append({
                'Material': material,
                'Región': region_name,
                'Primarias (MeV)': f'{r["total_primary"]:.2e}',
                'Secundarias (MeV)': f'{r["total_secondary"]:.2e}',
                'Total (MeV)': f'{r["total_energy"]:.2e}',
                'Primarias %': f'{r["pct_primary"]:.2f}',
                'Secundarias %': f'{r["pct_secondary"]:.2f}',
                'Media Primarias': f'{r["avg_primary"]:.2e}',
                'Media Secundarias': f'{r["avg_secondary"]:.2e}',
            })
    
    df = pd.DataFrame(data)
    output_csv = os.path.join(DATA_DIR, 'regional_analysis_primary_secondary.csv')
    df.to_csv(output_csv, index=False)
    print(f"✅ Reporte CSV guardado: {output_csv}")

if __name__ == "__main__":
    main()

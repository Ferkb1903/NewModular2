#!/usr/bin/env python3
"""
Análisis comparativo de simulaciones de braquiterapia I125 - 200M
Compara tres casos: agua homogéneo, hueso heterogéneo y pulmón heterogéneo
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
from pathlib import Path

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/200M_I125"
HISTOGRAM_NAME = "h20;1"

# Casos de simulación
CASES = {
    "Water_Homo": "brachytherapy_water_homo200m.root",
    "Bone_Hetero": "brachytherapy_Bone_Hetero200m.root",
    "Lung_Hetero": "brachytherapy_Lung_Hetero200m.root"
}

def load_histogram(filepath, hist_name):
    """Carga un histograma 2D de un archivo ROOT"""
    try:
        with uproot.open(filepath) as file:
            if hist_name in file:
                hist = file[hist_name]
                return hist
            else:
                print(f"⚠️  Histograma {hist_name} no encontrado en {filepath}")
                print(f"   Histogramas disponibles: {list(file.keys())}")
                return None
    except Exception as e:
        print(f"❌ Error abriendo {filepath}: {e}")
        return None

def extract_histogram_data(hist):
    """Extrae datos de un histograma 2D de uproot"""
    try:
        # Obtener contenido, bordes de ejes
        if hasattr(hist, 'values'):
            data = hist.values()
            # Para histogramas 2D
            if len(data.shape) == 2:
                return {
                    'values': data,
                    'x_edges': hist.axes[0].edges(),
                    'y_edges': hist.axes[1].edges(),
                    'title': hist.title if hasattr(hist, 'title') else 'Histogram',
                    'x_label': 'X',
                    'y_label': 'Y'
                }
        return None
    except Exception as e:
        print(f"❌ Error extrayendo datos del histograma: {e}")
        return None

def analyze_histogram(hist_data, case_name):
    """Analiza estadísticas de un histograma"""
    if hist_data is None:
        return None
    
    values = hist_data['values']
    
    stats = {
        'case': case_name,
        'total_entries': np.sum(values),
        'max_value': np.max(values),
        'min_value': np.min(values),
        'mean': np.mean(values),
        'std': np.std(values),
        'median': np.median(values),
        'x_bins': values.shape[0],
        'y_bins': values.shape[1]
    }
    
    return stats

def print_statistics(all_stats):
    """Imprime estadísticas comparativas"""
    print("\n" + "="*80)
    print("ANÁLISIS ESTADÍSTICO - BRAQUITERAPIA I125 (200M)")
    print("="*80)
    
    for stats in all_stats:
        if stats is None:
            continue
        print(f"\n📊 Caso: {stats['case']}")
        print(f"   Entradas totales:  {stats['total_entries']:.2e}")
        print(f"   Valor máximo:      {stats['max_value']:.4e}")
        print(f"   Valor mínimo:      {stats['min_value']:.4e}")
        print(f"   Media:             {stats['mean']:.4e}")
        print(f"   Desv. estándar:    {stats['std']:.4e}")
        print(f"   Mediana:           {stats['median']:.4e}")
        print(f"   Bins X × Y:        {stats['x_bins']} × {stats['y_bins']}")

def plot_comparison(histograms_data):
    """Crea visualización comparativa de los 3 casos"""
    cases_names = list(histograms_data.keys())
    
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    for idx, case_name in enumerate(cases_names):
        hist_data = histograms_data[case_name]
        if hist_data is None:
            continue
        
        values = hist_data['values']
        
        # Imagen del mapa de dosis
        ax_image = fig.add_subplot(gs[idx, 0])
        im = ax_image.imshow(values.T, aspect='auto', origin='lower', cmap='viridis')
        ax_image.set_title(f'{case_name}\nMapa de Dosis 2D', fontsize=11, fontweight='bold')
        ax_image.set_xlabel('X bins')
        ax_image.set_ylabel('Y bins')
        plt.colorbar(im, ax=ax_image, label='Dosis')
        
        # Proyección en X
        ax_x = fig.add_subplot(gs[idx, 1])
        x_projection = np.sum(values, axis=1)
        x_bins = np.arange(len(x_projection))
        ax_x.plot(x_bins, x_projection, 'b-', linewidth=1.5)
        ax_x.fill_between(x_bins, x_projection, alpha=0.3)
        ax_x.set_title(f'{case_name}\nProyección X', fontsize=11, fontweight='bold')
        ax_x.set_xlabel('X bin')
        ax_x.set_ylabel('Dosis integrada')
        ax_x.grid(True, alpha=0.3)
        
        # Proyección en Y
        ax_y = fig.add_subplot(gs[idx, 2])
        y_projection = np.sum(values, axis=0)
        y_bins = np.arange(len(y_projection))
        ax_y.plot(y_bins, y_projection, 'r-', linewidth=1.5)
        ax_y.fill_between(y_bins, y_projection, alpha=0.3, color='red')
        ax_y.set_title(f'{case_name}\nProyección Y', fontsize=11, fontweight='bold')
        ax_y.set_xlabel('Y bin')
        ax_y.set_ylabel('Dosis integrada')
        ax_y.grid(True, alpha=0.3)
    
    plt.suptitle('Comparación de Simulaciones I125 - 200M', fontsize=14, fontweight='bold', y=0.995)
    output_file = os.path.join(DATA_DIR, 'comparison_200M_I125.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    plt.show()

def compare_dose_distributions(histograms_data):
    """Compara distribuciones de dosis normalizadas"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    for idx, (case_name, hist_data) in enumerate(histograms_data.items()):
        if hist_data is None:
            continue
        
        values = hist_data['values'].flatten()
        values = values[values > 0]  # Solo valores positivos
        
        axes[idx].hist(values, bins=100, edgecolor='black', alpha=0.7, color='steelblue')
        axes[idx].set_yscale('log')
        axes[idx].set_xscale('log')
        axes[idx].set_title(f'{case_name}', fontweight='bold')
        axes[idx].set_xlabel('Dosis (escala log)')
        axes[idx].set_ylabel('Frecuencia (escala log)')
        axes[idx].grid(True, alpha=0.3)
    
    plt.suptitle('Distribución de Dosis - Comparación (escala log-log)', fontsize=13, fontweight='bold')
    plt.tight_layout()
    output_file = os.path.join(DATA_DIR, 'dose_distribution_200M_I125.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfica de distribuciones guardada: {output_file}")
    plt.show()

def create_ratio_maps(histograms_data):
    """Crea mapas de razón: Hetero/Homo"""
    if histograms_data['Water_Homo'] is None:
        print("   ⚠️  No se puede crear mapa de razón: Water_Homo no disponible")
        return
    
    water_homo = histograms_data['Water_Homo']['values']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    hetero_cases = ['Bone_Hetero', 'Lung_Hetero']
    hetero_labels = ['Bone/Water', 'Lung/Water']
    
    for idx, (case, label) in enumerate(zip(hetero_cases, hetero_labels)):
        if histograms_data[case] is None:
            print(f"   ⚠️  {case} no disponible")
            continue
            
        hetero = histograms_data[case]['values']
        
        # Evitar división por cero
        ratio = np.divide(hetero, water_homo, 
                         where=water_homo > 0, 
                         out=np.ones_like(hetero, dtype=float))
        
        im = axes[idx].imshow(ratio.T, aspect='auto', origin='lower', cmap='RdYlBu_r')
        axes[idx].set_title(f'Razón de Dosis: {label}', fontweight='bold')
        axes[idx].set_xlabel('X bins')
        axes[idx].set_ylabel('Y bins')
        cbar = plt.colorbar(im, ax=axes[idx], label='Razón')
        
        # Estadísticas
        ratio_valid = ratio[ratio > 0]
        print(f"\n   {label}:")
        print(f"      Razón mín: {np.min(ratio_valid):.4f}")
        print(f"      Razón máx: {np.max(ratio_valid):.4f}")
        print(f"      Razón media: {np.mean(ratio_valid):.4f}")
    
    plt.suptitle('Mapas de Razón: Heterogéneo / Homogéneo', fontsize=13, fontweight='bold')
    plt.tight_layout()
    output_file = os.path.join(DATA_DIR, 'ratio_maps_200M_I125.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Mapas de razón guardados: {output_file}")
    plt.show()

def main():
    """Función principal"""
    print("\n" + "="*80)
    print("ANALIZADOR DE BRAQUITERAPIA I125 - 200M (3 CASOS)")
    print("="*80)
    
    histograms_data = {}
    all_stats = []
    
    # Cargar histogramas
    print("\n📂 Cargando histogramas...")
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"\n   Caso: {case_name}")
        print(f"   Archivo: {filename}")
        
        hist = load_histogram(filepath, HISTOGRAM_NAME)
        if hist is not None:
            hist_data = extract_histogram_data(hist)
            histograms_data[case_name] = hist_data
            
            stats = analyze_histogram(hist_data, case_name)
            all_stats.append(stats)
            print(f"   ✅ Cargado exitosamente")
        else:
            print(f"   ❌ Error al cargar")
    
    # Mostrar estadísticas
    print_statistics(all_stats)
    
    # Crear visualizaciones
    print("\n📈 Generando visualizaciones...")
    plot_comparison(histograms_data)
    compare_dose_distributions(histograms_data)
    
    print("\n📊 Calculando mapas de razón (Heterogéneo/Homogéneo)...")
    if all(case in histograms_data for case in ['Water_Homo', 'Bone_Hetero', 'Lung_Hetero']):
        create_ratio_maps(histograms_data)
    else:
        print("   ⚠️  No se pudieron crear mapas de razón (falta algún caso)")
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

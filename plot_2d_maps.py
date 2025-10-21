#!/usr/bin/env python3
"""
Visualización de mapas 2D de dosis - Braquiterapia I125 (200M)
Escala logarítmica con colormap rainbow
Incluye marcas de heterogeneidad
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as patches
import os

# Configuración
DATA_DIR = "/home/fer/fer/newbrachy/200M_I125"
HISTOGRAM_NAME = "h20;1"

# Parámetros de heterogeneidad (del macro)
# size: 6.0 x 6.0 x 6.0 cm -> 60 mm x 60 mm x 60 mm
# position: 40.0 0.0 0.0 mm (X, Y, Z)
HETERO_SIZE = 60.0  # mm (6.0 cm)
HETERO_POS_X = 40.0  # mm (posición en X)
HETERO_POS_Y = 0.0   # mm (posición en Y)

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
                print(f"❌ Histograma {hist_name} no encontrado en {filepath}")
                return None
    except Exception as e:
        print(f"❌ Error abriendo {filepath}: {e}")
        return None

def draw_heterogeneity(ax):
    """Dibuja un rectángulo que marca la región de heterogeneidad"""
    # Calcular bordes del cubo de heterogeneidad
    x_min = HETERO_POS_X - HETERO_SIZE / 2
    x_max = HETERO_POS_X + HETERO_SIZE / 2
    y_min = HETERO_POS_Y - HETERO_SIZE / 2
    y_max = HETERO_POS_Y + HETERO_SIZE / 2
    
    # Convertir de mm a índices de bins (aproximadamente)
    # Rango: -150.5 a 150.5 mm en 300 bins
    # Factor de escala: 300 / 301 ≈ 0.997
    scale_factor = 300 / 301.0
    
    x_min_bin = (x_min - (-150.5)) * scale_factor
    x_max_bin = (x_max - (-150.5)) * scale_factor
    y_min_bin = (y_min - (-150.5)) * scale_factor
    y_max_bin = (y_max - (-150.5)) * scale_factor
    
    # Dibujar rectángulo
    rect = patches.Rectangle(
        (x_min_bin, y_min_bin),
        x_max_bin - x_min_bin,
        y_max_bin - y_min_bin,
        linewidth=1.5,
        edgecolor='white',
        facecolor='none',
        linestyle='--'
    )
    ax.add_patch(rect)

def plot_2d_maps():
    """Crea visualización de mapas 2D con escala log y colormap rainbow"""
    
    fig = plt.figure(figsize=(18, 10))
    
    # Cargar todos los histogramas primero
    histograms = {}
    for case_name, filename in CASES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Procesando: {case_name}...", end=" ")
        
        hist = load_histogram(filepath, HISTOGRAM_NAME)
        if hist is None:
            print("❌ Error")
            continue
        
        histograms[case_name] = hist.values()
        print("✅")
    
    # Fila 1: Mapas originales (escala log)
    for idx, case_name in enumerate(CASES.keys()):
        ax = plt.subplot(2, 3, idx + 1)
        
        if case_name not in histograms:
            continue
        
        values = histograms[case_name]
        
        # Reemplazar ceros con un valor muy pequeño para la escala log
        values_log = np.copy(values).astype(float)
        values_log[values_log <= 0] = np.min(values_log[values_log > 0]) / 10
        
        # Crear imagen con escala logarítmica
        im = ax.imshow(
            values_log.T,
            aspect='auto',
            origin='lower',
            cmap='rainbow',
            norm=colors.LogNorm(vmin=values_log.min(), vmax=values_log.max())
        )
        
        ax.set_title(f'{case_name}', fontsize=12, fontweight='bold')
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        plt.colorbar(im, ax=ax, label='Dosis (log)')
        
        # Dibujar heterogeneidad
        draw_heterogeneity(ax)
    
    # Fila 2: Restas (Hetero - Homo) en escala logarítmica con signo
    # Resta 1: Bone_Hetero - Water_Homo
    ax_bone = plt.subplot(2, 3, 4)
    diff_bone = histograms['Bone_Hetero'] - histograms['Water_Homo']
    
    # Para escala log con valores negativos, usar SymLogNorm
    im_bone = ax_bone.imshow(
        diff_bone.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=colors.SymLogNorm(linthresh=1e2, vmin=diff_bone.min(), vmax=diff_bone.max())
    )
    
    ax_bone.set_title('Bone_Hetero - Water_Homo (SymLog)', fontsize=12, fontweight='bold')
    ax_bone.set_xlabel('X (bins)')
    ax_bone.set_ylabel('Y (bins)')
    plt.colorbar(im_bone, ax=ax_bone, label='Diferencia (SymLog)')
    draw_heterogeneity(ax_bone)
    
    # Resta 2: Lung_Hetero - Water_Homo
    ax_lung = plt.subplot(2, 3, 5)
    diff_lung = histograms['Lung_Hetero'] - histograms['Water_Homo']
    
    # Para escala log con valores negativos, usar SymLogNorm
    im_lung = ax_lung.imshow(
        diff_lung.T,
        aspect='auto',
        origin='lower',
        cmap='RdBu_r',
        norm=colors.SymLogNorm(linthresh=1e2, vmin=diff_lung.min(), vmax=diff_lung.max())
    )
    
    ax_lung.set_title('Lung_Hetero - Water_Homo (SymLog)', fontsize=12, fontweight='bold')
    ax_lung.set_xlabel('X (bins)')
    ax_lung.set_ylabel('Y (bins)')
    plt.colorbar(im_lung, ax=ax_lung, label='Diferencia (SymLog)')
    draw_heterogeneity(ax_lung)
    
    # Panel vacío para simetría
    ax_empty = plt.subplot(2, 3, 6)
    ax_empty.axis('off')
    
    plt.suptitle('Mapas 2D de Dosis - I125 200M - Análisis Comparativo', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_file = os.path.join(DATA_DIR, '2D_dose_maps_log_rainbow.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada: {output_file}")
    plt.show()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("VISUALIZACIÓN 2D DE MAPAS DE DOSIS")
    print("="*60 + "\n")
    plot_2d_maps()
    print("\n" + "="*60 + "\n")

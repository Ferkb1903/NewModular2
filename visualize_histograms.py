#!/usr/bin/env python3
"""
Visualización simple de histogramas ROOT con región de heterogeneidad marcada
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import SymLogNorm, LogNorm
import os

# ===== CONSTANTES FÍSICAS =====
# Densidades GEANT4 (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.92  # G4_BONE_COMPACT_ICRU
DENSITY_LUNG = 0.26  # G4_LUNG_ICRP

# Conversión energía → dosis
# 1 keV = 1.602e-13 J
# Voxel: 1mm × 1mm × 1mm = 0.1 cm³
VOXEL_VOLUME_CM3 = 0.1  # cm³

# ===== HETEROGENEIDAD =====
# Centrada en (40mm, 0mm) con tamaño 60x60mm
# En voxeles: X[160,220], Y[120,180]
HETERO_X_MIN, HETERO_X_MAX = 160, 220
HETERO_Y_MIN, HETERO_Y_MAX = 120, 180

def edep_to_dose_gy(edep_kev, density_g_cm3):
    """
    Convierte EDEP (keV) a Dosis (Gy)
    Dose = Energy / mass
    mass = density × volume
    """
    if edep_kev == 0:
        return 0
    
    energy_joules = edep_kev * 1.602e-13  # J
    mass_kg = density_g_cm3 * VOXEL_VOLUME_CM3 / 1000  # kg
    dose_gy = energy_joules / mass_kg
    return dose_gy

FILES = {
    'water_homo': ('200M_I125/brachytherapy_water_homo200m.root', 'Water (Homo)'),
    'bone_hetero': ('200M_I125/brachytherapy_Bone_Hetero200m.root', 'Bone (Hetero)'),
    'lung_hetero': ('200M_I125/brachytherapy_Lung_Hetero200m.root', 'Lung (Hetero)'),
}

def read_dose_map(filepath):
    """Lee el mapa de dosis 2D (h20)"""
    if not os.path.exists(filepath):
        return None
    
    try:
        with uproot.open(filepath) as f:
            if 'h20;1' in f:
                hist = f['h20;1']
                return hist.values()
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
    
    return None

def convert_to_dose(edep_map, material_name):
    """
    Convierte mapa EDEP a Dosis considerando heterogeneidad
    
    material_name: 'water_homo', 'bone_hetero', o 'lung_hetero'
    """
    dose_map = np.zeros_like(edep_map, dtype=float)
    
    if material_name == 'water_homo':
        # Todo es agua
        for i in range(edep_map.shape[0]):
            for j in range(edep_map.shape[1]):
                dose_map[i, j] = edep_to_dose_gy(edep_map[i, j], DENSITY_WATER)
    
    elif material_name == 'bone_hetero':
        # Dentro de heterogeneidad: Bone, fuera: Water
        for i in range(edep_map.shape[0]):
            for j in range(edep_map.shape[1]):
                if HETERO_X_MIN <= i < HETERO_X_MAX and HETERO_Y_MIN <= j < HETERO_Y_MAX:
                    density = DENSITY_BONE
                else:
                    density = DENSITY_WATER
                dose_map[i, j] = edep_to_dose_gy(edep_map[i, j], density)
    
    elif material_name == 'lung_hetero':
        # Dentro de heterogeneidad: Lung, fuera: Water
        for i in range(edep_map.shape[0]):
            for j in range(edep_map.shape[1]):
                if HETERO_X_MIN <= i < HETERO_X_MAX and HETERO_Y_MIN <= j < HETERO_Y_MAX:
                    density = DENSITY_LUNG
                else:
                    density = DENSITY_WATER
                dose_map[i, j] = edep_to_dose_gy(edep_map[i, j], density)
    
    return dose_map

# Leer todos los mapas
dose_maps = {}
print("\n" + "="*80)
print("CARGANDO DATOS 200M_I125 - 3 CASOS")
print("="*80)
for name, (filepath, title) in FILES.items():
    edep_map = read_dose_map(filepath)
    if edep_map is not None:
        # Convertir a dosis considerando heterogeneidad
        dose_map = convert_to_dose(edep_map, name)
        dose_maps[name] = dose_map
        print(f"  ✓ {name:<15} - Shape: {dose_map.shape}")
        print(f"    Min: {np.min(dose_map[dose_map > 0]):.6e} Gy, Max: {np.max(dose_map):.6e} Gy")
    else:
        print(f"  ✗ {name:<15} NO ENCONTRADO")

# ===== HETEROGENEIDAD =====
# Centrada en (40mm, 0mm) con tamaño 60x60mm
# En mapa centrado en (0,0): X[10,70]mm, Y[-30,30]mm
# En voxeles (asumiendo 0.5mm/voxel, 300x300 de [-150,150]mm):
# X: 10mm → voxel (10+150)/0.5 = 320... No, revisar escala
# Si 300 voxeles para 300mm: 1 voxel = 1mm
# Entonces: X[10,70]mm → voxeles [10,70]... pero eso no encaja con el análisis anterior
# Mejor: X centrado en 150 voxeles (0mm), entonces:
# X: 40mm = voxel 190, rango [10,70]mm = voxeles [160,220]
# Y: 0mm = voxel 150, rango [-30,30]mm = voxeles [120,180]

HETERO_X_MIN, HETERO_X_MAX = 160, 220
HETERO_Y_MIN, HETERO_Y_MAX = 120, 180

# ===== CREAR FIGURA =====
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, (name, (filepath, title)) in enumerate(FILES.items()):
    ax = axes[idx]
    
    # Mostrar mapa
    data = dose_maps[name]
    vmin = np.min(data[data > 0])  # mínimo excluyendo ceros
    vmax = np.max(data)
    im = ax.imshow(data.T, cmap='rainbow', aspect='auto', origin='lower', 
                   norm=LogNorm(vmin=vmin, vmax=vmax))
    
    # Marcar región de heterogeneidad con rectángulo
    rect = patches.Rectangle(
        (HETERO_X_MIN, HETERO_Y_MIN),
        HETERO_X_MAX - HETERO_X_MIN,
        HETERO_Y_MAX - HETERO_Y_MIN,
        linewidth=2,
        edgecolor='cyan',
        facecolor='none',
        linestyle='--',
        label='Heterogeneity'
    )
    ax.add_patch(rect)
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('X (voxels)', fontsize=10)
    ax.set_ylabel('Y (voxels)', fontsize=10)
    ax.legend(loc='upper right', fontsize=9)
    plt.colorbar(im, ax=ax, label='Dose (Gy)')

plt.suptitle('200M I125 - Histogramas ROOT con Heterogeneidad Marcada', 
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()

# Guardar figura
output_file = '200M_I125_histograms_with_heterogeneity.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✓ Gráfico guardado: {output_file}")

print("\n" + "="*80)
print("INFORMACIÓN DE HETEROGENEIDAD")
print("="*80)
print(f"Región marcada (voxeles):")
print(f"  X: [{HETERO_X_MIN}, {HETERO_X_MAX}]")
print(f"  Y: [{HETERO_Y_MIN}, {HETERO_Y_MAX}]")
print(f"  Tamaño: {HETERO_X_MAX - HETERO_X_MIN} × {HETERO_Y_MAX - HETERO_Y_MIN} voxeles")
print(f"\nCentro en voxeles: ({(HETERO_X_MIN + HETERO_X_MAX)//2}, {(HETERO_Y_MIN + HETERO_Y_MAX)//2})")
print("="*80)

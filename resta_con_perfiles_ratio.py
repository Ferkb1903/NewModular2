#!/usr/bin/env python3
"""
Resta de dosis + Perfiles de ratio (hetero/homo)
Muestra mapas de diferencia + perfiles horizontales de cociente
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import CenteredNorm
import os

# ===== CONSTANTES FÍSICAS =====
DENSITY_WATER = 1.0
DENSITY_BONE = 1.92  # G4_BONE_COMPACT_ICRU
DENSITY_LUNG = 0.26  # G4_LUNG_ICRP

VOXEL_VOLUME_CM3 = 0.1  # cm³

# ===== HETEROGENEIDAD =====
HETERO_X_MIN, HETERO_X_MAX = 160, 220
HETERO_Y_MIN, HETERO_Y_MAX = 120, 180

def voxel_to_mm(voxel_idx):
    """Convierte índice de voxel a mm"""
    return (voxel_idx - 150)

def edep_to_dose_gy(edep_kev, density_g_cm3):
    """Convierte EDEP (keV) a Dosis (Gy)"""
    if edep_kev == 0:
        return 0
    
    energy_joules = edep_kev * 1.602e-13  # J
    mass_kg = density_g_cm3 * VOXEL_VOLUME_CM3 / 1000  # kg
    dose_gy = energy_joules / mass_kg
    return dose_gy

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
    """Convierte mapa EDEP a Dosis considerando heterogeneidad"""
    dose_map = np.zeros_like(edep_map, dtype=float)
    
    if material_name == 'water_homo':
        for i in range(edep_map.shape[0]):
            for j in range(edep_map.shape[1]):
                dose_map[i, j] = edep_to_dose_gy(edep_map[i, j], DENSITY_WATER)
    
    elif material_name == 'bone_hetero':
        for i in range(edep_map.shape[0]):
            for j in range(edep_map.shape[1]):
                if HETERO_X_MIN <= i < HETERO_X_MAX and HETERO_Y_MIN <= j < HETERO_Y_MAX:
                    density = DENSITY_BONE
                else:
                    density = DENSITY_WATER
                dose_map[i, j] = edep_to_dose_gy(edep_map[i, j], density)
    
    elif material_name == 'lung_hetero':
        for i in range(edep_map.shape[0]):
            for j in range(edep_map.shape[1]):
                if HETERO_X_MIN <= i < HETERO_X_MAX and HETERO_Y_MIN <= j < HETERO_Y_MAX:
                    density = DENSITY_LUNG
                else:
                    density = DENSITY_WATER
                dose_map[i, j] = edep_to_dose_gy(edep_map[i, j], density)
    
    return dose_map

# ===== CARGAR MAPAS =====
print("\n" + "="*80)
print("CARGANDO Y CONVIRTIENDO A DOSIS")
print("="*80)

water_homo_edep = read_dose_map('200M_I125/brachytherapy_water_homo200m.root')
water_homo_dose = convert_to_dose(water_homo_edep, 'water_homo')
print(f"✓ Water Homo")

bone_hetero_edep = read_dose_map('200M_I125/brachytherapy_Bone_Hetero200m.root')
bone_hetero_dose = convert_to_dose(bone_hetero_edep, 'bone_hetero')
print(f"✓ Bone Hetero")

lung_hetero_edep = read_dose_map('200M_I125/brachytherapy_Lung_Hetero200m.root')
lung_hetero_dose = convert_to_dose(lung_hetero_edep, 'lung_hetero')
print(f"✓ Lung Hetero")

# ===== CALCULAR RESTAS Y RATIOS =====
print("\n" + "="*80)
print("CALCULANDO RESTAS Y RATIOS")
print("="*80)

diff_bone = bone_hetero_dose - water_homo_dose
diff_lung = lung_hetero_dose - water_homo_dose

# Ratios (hetero / homo), evitar división por cero
ratio_bone = np.divide(bone_hetero_dose, water_homo_dose, 
                       where=water_homo_dose != 0, 
                       out=np.ones_like(bone_hetero_dose))
ratio_lung = np.divide(lung_hetero_dose, water_homo_dose, 
                       where=water_homo_dose != 0, 
                       out=np.ones_like(lung_hetero_dose))

# Extraer perfiles verticales en X=150 (X=0mm, línea vertical a través del centro)
x_center = 150
profile_ratio_bone = ratio_bone[:, x_center]
profile_ratio_lung = ratio_lung[:, x_center]

y_mm = np.array([voxel_to_mm(i) for i in range(300)])

print(f"\nBone ratio profile - Min: {np.min(profile_ratio_bone):.4f}, Max: {np.max(profile_ratio_bone):.4f}")
print(f"Lung ratio profile - Min: {np.min(profile_ratio_lung):.4f}, Max: {np.max(profile_ratio_lung):.4f}")

# ===== GRAFICAR =====
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# FILA 1: Mapas de resta
# Bone difference
ax_diff_bone = fig.add_subplot(gs[0, 0])
vmax_bone = np.max(np.abs(diff_bone))
im_bone = ax_diff_bone.imshow(diff_bone.T, cmap='RdBu_r', aspect='auto', origin='lower',
                              norm=CenteredNorm(vcenter=0, halfrange=vmax_bone))
rect_bone = patches.Rectangle(
    (HETERO_X_MIN, HETERO_Y_MIN),
    HETERO_X_MAX - HETERO_X_MIN,
    HETERO_Y_MAX - HETERO_Y_MIN,
    linewidth=2, edgecolor='cyan', facecolor='none', linestyle='--', label='Heterogeneity'
)
ax_diff_bone.add_patch(rect_bone)
ax_diff_bone.set_title('Bone Hetero - Water Homo', fontsize=11, fontweight='bold')
ax_diff_bone.set_xlabel('X (voxels)', fontsize=10)
ax_diff_bone.set_ylabel('Y (voxels)', fontsize=10)
ax_diff_bone.legend(loc='upper right', fontsize=9)
plt.colorbar(im_bone, ax=ax_diff_bone, label='ΔDose (Gy)')

# Lung difference
ax_diff_lung = fig.add_subplot(gs[0, 1])
vmax_lung = np.max(np.abs(diff_lung))
im_lung = ax_diff_lung.imshow(diff_lung.T, cmap='RdBu_r', aspect='auto', origin='lower',
                              norm=CenteredNorm(vcenter=0, halfrange=vmax_lung))
rect_lung = patches.Rectangle(
    (HETERO_X_MIN, HETERO_Y_MIN),
    HETERO_X_MAX - HETERO_X_MIN,
    HETERO_Y_MAX - HETERO_Y_MIN,
    linewidth=2, edgecolor='cyan', facecolor='none', linestyle='--', label='Heterogeneity'
)
ax_diff_lung.add_patch(rect_lung)
ax_diff_lung.set_title('Lung Hetero - Water Homo', fontsize=11, fontweight='bold')
ax_diff_lung.set_xlabel('X (voxels)', fontsize=10)
ax_diff_lung.set_ylabel('Y (voxels)', fontsize=10)
ax_diff_lung.legend(loc='upper right', fontsize=9)
plt.colorbar(im_lung, ax=ax_diff_lung, label='ΔDose (Gy)')

# FILA 2: Perfiles de ratio
# Bone ratio profile
ax_ratio_bone = fig.add_subplot(gs[1, 0])
ax_ratio_bone.plot(y_mm, profile_ratio_bone, 'r-', linewidth=2.5, label='Bone Hetero / Water Homo')
ax_ratio_bone.axhline(y=1.0, color='black', linestyle=':', alpha=0.5, label='Ratio = 1')
ax_ratio_bone.axvline(x=voxel_to_mm(HETERO_Y_MIN), color='gray', linestyle='--', alpha=0.5)
ax_ratio_bone.axvline(x=voxel_to_mm(HETERO_Y_MAX), color='gray', linestyle='--', alpha=0.5)
ax_ratio_bone.fill_between(y_mm, 0, 2, 
                           where=(y_mm >= voxel_to_mm(HETERO_Y_MIN)) & (y_mm < voxel_to_mm(HETERO_Y_MAX)), 
                           alpha=0.1, color='gray', transform=ax_ratio_bone.get_xaxis_transform())
ax_ratio_bone.set_xlabel('Y (mm)', fontsize=10)
ax_ratio_bone.set_ylabel('Dose Ratio', fontsize=10)
ax_ratio_bone.set_title('Bone: Ratio Profile (X=0mm)', fontsize=11, fontweight='bold')
ax_ratio_bone.grid(True, alpha=0.3)
ax_ratio_bone.legend(fontsize=9, loc='best')
ax_ratio_bone.set_ylim([0.9, 1.1])

# Lung ratio profile
ax_ratio_lung = fig.add_subplot(gs[1, 1])
ax_ratio_lung.plot(y_mm, profile_ratio_lung, 'g-', linewidth=2.5, label='Lung Hetero / Water Homo')
ax_ratio_lung.axhline(y=1.0, color='black', linestyle=':', alpha=0.5, label='Ratio = 1')
ax_ratio_lung.axvline(x=voxel_to_mm(HETERO_Y_MIN), color='gray', linestyle='--', alpha=0.5)
ax_ratio_lung.axvline(x=voxel_to_mm(HETERO_Y_MAX), color='gray', linestyle='--', alpha=0.5)
ax_ratio_lung.fill_between(y_mm, 0, 2, 
                           where=(y_mm >= voxel_to_mm(HETERO_Y_MIN)) & (y_mm < voxel_to_mm(HETERO_Y_MAX)), 
                           alpha=0.1, color='gray', transform=ax_ratio_lung.get_xaxis_transform())
ax_ratio_lung.set_xlabel('Y (mm)', fontsize=10)
ax_ratio_lung.set_ylabel('Dose Ratio', fontsize=10)
ax_ratio_lung.set_title('Lung: Ratio Profile (X=0mm)', fontsize=11, fontweight='bold')
ax_ratio_lung.grid(True, alpha=0.3)
ax_ratio_lung.legend(fontsize=9, loc='best')
ax_ratio_lung.set_ylim([0.5, 2.5])

# FILA 3: Perfiles superpuestos
# Comparación de ratios
ax_both_ratio = fig.add_subplot(gs[2, :])
ax_both_ratio.plot(y_mm, profile_ratio_bone, 'r-', linewidth=2.5, label='Bone Hetero / Water Homo', alpha=0.8)
ax_both_ratio.plot(y_mm, profile_ratio_lung, 'g-', linewidth=2.5, label='Lung Hetero / Water Homo', alpha=0.8)
ax_both_ratio.axhline(y=1.0, color='black', linestyle=':', alpha=0.5, linewidth=1.5)
ax_both_ratio.axvline(x=voxel_to_mm(HETERO_Y_MIN), color='gray', linestyle='--', alpha=0.5)
ax_both_ratio.axvline(x=voxel_to_mm(HETERO_Y_MAX), color='gray', linestyle='--', alpha=0.5)
ax_both_ratio.fill_between(y_mm, 0, 3, 
                           where=(y_mm >= voxel_to_mm(HETERO_Y_MIN)) & (y_mm < voxel_to_mm(HETERO_Y_MAX)), 
                           alpha=0.1, color='gray', transform=ax_both_ratio.get_xaxis_transform())
ax_both_ratio.set_xlabel('Y (mm)', fontsize=10)
ax_both_ratio.set_ylabel('Dose Ratio', fontsize=10)
ax_both_ratio.set_title('Comparación: Ratios de Dosis (X=0mm)', fontsize=11, fontweight='bold')
ax_both_ratio.grid(True, alpha=0.3)
ax_both_ratio.legend(fontsize=10, loc='best')

plt.suptitle('200M I125 - Resta de Dosis + Perfiles de Ratio', 
             fontsize=14, fontweight='bold', y=0.995)

# Guardar figura
output_file = '200M_I125_resta_y_perfiles_ratio.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"\n✓ Gráfico guardado: {output_file}")

print("\n" + "="*80)

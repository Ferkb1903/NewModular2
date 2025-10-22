#!/usr/bin/env python3
"""
Visualización 3D de la malla de scoring (300x300x300 mm) y la heterogeneidad
Genera un cubo transparente con bordes que muestra el volumen de scoring
y la región de heterogeneidad Lung MIRD centrada en (40, 0, 0) mm
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# Parámetros
MESH_SIZE = 300.0  # mm (±150 mm en cada dirección)
HETERO_SIZE = 60.0  # mm (6.0 cm)
HETERO_POS = np.array([40.0, 0.0, 0.0])  # mm

def create_cube_vertices(center, half_size):
    """Crea los 8 vértices de un cubo"""
    h = half_size
    vertices = [
        center + np.array([-h, -h, -h]),
        center + np.array([h, -h, -h]),
        center + np.array([h, h, -h]),
        center + np.array([-h, h, -h]),
        center + np.array([-h, -h, h]),
        center + np.array([h, -h, h]),
        center + np.array([h, h, h]),
        center + np.array([-h, h, h]),
    ]
    return np.array(vertices)

def create_cube_faces(vertices):
    """Define las 6 caras del cubo a partir de 8 vértices"""
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # bottom
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # top
        [vertices[0], vertices[3], vertices[7], vertices[4]],  # left
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # right
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # front
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # back
    ]
    return faces

# Crear figura
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# --- Malla de scoring (300x300x300 mm) ---
mesh_vertices = create_cube_vertices(np.array([0, 0, 0]), MESH_SIZE / 2.0)
mesh_faces = create_cube_faces(mesh_vertices)

mesh_poly = Poly3DCollection(
    mesh_faces,
    alpha=0.1,
    facecolor='cyan',
    edgecolor='blue',
    linewidth=2.5
)
ax.add_collection3d(mesh_poly)

# --- Heterogeneidad (60x60x60 mm) ---
hetero_vertices = create_cube_vertices(HETERO_POS, HETERO_SIZE / 2.0)
hetero_faces = create_cube_faces(hetero_vertices)

hetero_poly = Poly3DCollection(
    hetero_faces,
    alpha=0.4,
    facecolor='orange',
    edgecolor='red',
    linewidth=2.0
)
ax.add_collection3d(hetero_poly)

# --- Fuente puntual (en el origen) ---
ax.scatter([0], [0], [0], color='green', s=200, marker='*', label='Fuente I-125', zorder=5)

# --- Etiquetas y títulos ---
ax.set_xlabel('X (mm)', fontsize=11, fontweight='bold')
ax.set_ylabel('Y (mm)', fontsize=11, fontweight='bold')
ax.set_zlabel('Z (mm)', fontsize=11, fontweight='bold')
ax.set_title(
    'Geometría de Scoring: Malla 300×300×300 mm con Heterogeneidad Lung MIRD\n'
    'Cubo azul: región de scoring (±150 mm) | Cubo naranja: heterogeneidad (60 mm centrada en x=40 mm)',
    fontsize=13,
    fontweight='bold',
    pad=20
)

# Ajustar limites
ax.set_xlim([-160, 160])
ax.set_ylim([-160, 160])
ax.set_zlim([-160, 160])

# Añadir grid sutil
ax.grid(True, alpha=0.3)

# Leyenda
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='cyan', edgecolor='blue', alpha=0.3, label='Malla de scoring (300×300×300 mm)'),
    Patch(facecolor='orange', edgecolor='red', alpha=0.4, label='Heterogeneidad Lung MIRD (60×60×60 mm @ x=40mm)'),
    plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='green', markersize=15, label='Fuente I-125'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

# Ajustar perspectiva
ax.view_init(elev=25, azim=45)

plt.tight_layout()
output_path = '/home/fer/fer/newbrachy/200M_IR192/mesh_visualization_3d.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Imagen guardada: {output_path}")
print(f"   Resolución: 300 DPI | Tamaño: ~{np.round(plt.gcf().get_size_inches()[0]*300/25.4, 1)} × {np.round(plt.gcf().get_size_inches()[1]*300/25.4, 1)} píxeles")

plt.show()

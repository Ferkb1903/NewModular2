#!/usr/bin/env python3
"""
Visualización de la estructura de la fuente TG186 Iridium
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# ============================================================================
# Vista lateral (Z-axis)
# ============================================================================
ax1 = axes[0]

# Escala en mm
scale = 5  # 5 pixels per mm para visualización

# Cápsula principal (Stainless Steel Tube)
capsule_radius = 0.5  # mm
capsule_half_length = 2.25 / 2  # mm
capsule_z = -0.4  # mm

rect_capsule = patches.Rectangle(
    (-capsule_radius * scale, (capsule_z - capsule_half_length) * scale),
    capsule_radius * 2 * scale,
    capsule_half_length * 2 * scale,
    linewidth=2, edgecolor='red', facecolor='red', alpha=0.3
)
ax1.add_patch(rect_capsule)
ax1.text(0, (capsule_z - capsule_half_length - 1) * scale, 'Cápsula SS\n(r=0.5mm, L=2.25mm)', 
         ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Núcleo de Iridio (activo)
ir_radius = 0.30  # mm
ir_half_length = 1.75 / 2  # mm
ir_z = 0.4  # mm

rect_ir = patches.Rectangle(
    (-ir_radius * scale, (ir_z - ir_half_length) * scale),
    ir_radius * 2 * scale,
    ir_half_length * 2 * scale,
    linewidth=2, edgecolor='magenta', facecolor='magenta', alpha=0.6
)
ax1.add_patch(rect_ir)
ax1.text(ir_radius * scale + 1.5, ir_z * scale, 'Iridio\n(r=0.3mm\nL=1.75mm)', 
         ha='left', fontsize=9, fontweight='bold', color='magenta',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

# Cable
cable_radius = 0.5  # mm
cable_half_length = 1.0  # mm
cable_z = -3.65  # mm

rect_cable = patches.Rectangle(
    (-cable_radius * scale, (cable_z - cable_half_length) * scale),
    cable_radius * 2 * scale,
    cable_half_length * 2 * scale,
    linewidth=1, edgecolor='orange', facecolor='orange', alpha=0.2
)
ax1.add_patch(rect_cable)
ax1.text(0, (cable_z - cable_half_length - 1.5) * scale, 'Cable', 
         ha='center', fontsize=8)

# Esfera de la punta de la cápsula
tip_sphere_radius = 0.5  # mm
tip_z = 1.85  # mm

circle_tip = patches.Circle(
    (0, tip_z * scale),
    tip_sphere_radius * scale,
    linewidth=1, edgecolor='red', facecolor='red', alpha=0.3
)
ax1.add_patch(circle_tip)
ax1.text(0, (tip_z + 1.2) * scale, 'Punta esférica', ha='center', fontsize=8)

# Configurar ejes
ax1.set_xlim(-4 * scale, 4 * scale)
ax1.set_ylim(-7 * scale, 3 * scale)
ax1.set_aspect('equal')
ax1.set_xlabel('Radio (mm)', fontsize=10)
ax1.set_ylabel('Altura Z (mm)', fontsize=10)
ax1.set_title('VISTA LATERAL - Estructura de Fuente TG186 Iridium', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Añadir líneas de referencia
ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=0.5)
ax1.axvline(x=0, color='k', linestyle='--', alpha=0.3, linewidth=0.5)

# ============================================================================
# Vista frontal (X-Y)
# ============================================================================
ax2 = axes[1]

# Cápsula y núcleo (cono concéntrico)
circle_capsule = patches.Circle(
    (0, 0),
    capsule_radius * scale,
    linewidth=2, edgecolor='red', facecolor='red', alpha=0.3
)
ax2.add_patch(circle_capsule)

circle_ir = patches.Circle(
    (0, 0),
    ir_radius * scale,
    linewidth=2, edgecolor='magenta', facecolor='magenta', alpha=0.6
)
ax2.add_patch(circle_ir)

# Anotaciones
ax2.text(0, 0, 'Ir\n0.3mm', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
ax2.text(capsule_radius * scale + 0.5, 0, 'SS\n0.5mm', ha='left', va='center', fontsize=9, color='red')

ax2.set_xlim(-2.5 * scale, 3 * scale)
ax2.set_ylim(-2.5 * scale, 2.5 * scale)
ax2.set_aspect('equal')
ax2.set_xlabel('X (mm)', fontsize=10)
ax2.set_ylabel('Y (mm)', fontsize=10)
ax2.set_title('VISTA FRONTAL - Sección Transversal', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=0.5)
ax2.axvline(x=0, color='k', linestyle='--', alpha=0.3, linewidth=0.5)

plt.suptitle('Estructura Geométrica de la Fuente TG186 Iridium (Brachytherapy)', 
             fontsize=14, fontweight='bold', y=1.00)

plt.tight_layout()
plt.savefig('/home/fer/fer/newbrachy/100M_I125_pri-sec/source_geometry_TG186.png', dpi=150, bbox_inches='tight')
print("✅ Visualización guardada: source_geometry_TG186.png")

# ============================================================================
# Tabla comparativa
# ============================================================================
fig2, ax = plt.subplots(figsize=(12, 6))
ax.axis('tight')
ax.axis('off')

data = [
    ['Componente', 'Tipo Geométrico', 'Radio (mm)', 'Longitud (mm)', 'Posición Z (mm)', 'Material'],
    ['Núcleo Iridio', 'Cilindro', '0.30', '1.75', '+0.4', 'Ir (activo)'],
    ['Cápsula', 'Cilindro', '0.50', '2.25', '-0.4', 'Acero Inox.'],
    ['Punta', 'Esfera', '0.50', '—', '+1.85', 'Acero Inox.'],
    ['Cable', 'Cilindro', '0.50', '1.0', '-3.65', 'Acero Inox.'],
    ['', '', '', '', '', ''],
    ['CONCLUSIÓN', 'La fuente tiene dimensiones muy pequeñas (~0.3mm)', '', '', '', ''],
    ['', 'En mallas de 1mm/bin, aparece como "puntual"', '', '', '', ''],
]

table = ax.table(cellText=data, cellLoc='center', loc='center', 
                colWidths=[0.12, 0.15, 0.12, 0.12, 0.12, 0.15])

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)

# Colorear encabezados
for i in range(6):
    table[(0, i)].set_facecolor('#40466e')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Colorear fila de conclusión
for i in range(6):
    table[(6, i)].set_facecolor('#ffffcc')
    table[(7, i)].set_facecolor('#ffffcc')

plt.savefig('/home/fer/fer/newbrachy/100M_I125_pri-sec/source_specs_table.png', dpi=150, bbox_inches='tight')
print("✅ Tabla de especificaciones guardada: source_specs_table.png")

print("\n" + "="*80)
print("EXPLICACIÓN: POR QUÉ LAS SECUNDARIAS SON IGUALES EN TODOS LOS MATERIALES")
print("="*80)
print("""
1. UBICACIÓN FÍSICA:
   - El núcleo de iridio (donde se produce la radiación) tiene radio de 0.30 mm
   - Es esencialmente "puntual" comparado con la malla de 1 mm

2. PRODUCCIÓN DE SECUNDARIAS:
   - Las partículas secundarias (electrones, fotones secundarios) se producen 
     principalmente en la región del iridio
   - Esta región es idéntica en todos los casos (Lung, Bone, Water)
   - Por eso el espectro de secundarias es el MISMO

3. DISPERSIÓN DE PRIMARIAS:
   - Las partículas primarias (I-125 y sus fotones gamma) se producen en el iridio
   - Pero luego se dispersan diferente según el material:
     • En Lung (baja densidad): viajan más lejos
     • En Bone (alta densidad): se atenúan más rápido
     • En Water (media densidad): caso intermedio
   - Por eso las primarias varían según el material

4. EN LA MALLA DE HISTOGRAMAS (1mm bins):
   - 0-1 mm: Principalmente el núcleo de iridio
   - 1-2 mm: Extensión del campo de radiación desde el iridio
   - 2+ mm: Principalmente material circundante (sin fuente)
""")
print("="*80)

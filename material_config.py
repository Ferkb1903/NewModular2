#!/usr/bin/env python3
"""
Configuración de Materiales para Análisis de Braquiterapia I125
Define diferentes definiciones de materiales según composición MIRD/ICRP
"""

# ============================================================================
# DEFINICIONES DE DENSIDAD Y COMPOSICIÓN
# ============================================================================

# Densidades base (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE_STANDARD = 1.85

# LUNG: Dos definiciones diferentes
DENSITY_LUNG_MIRD = 0.2958          # MIRD lung material (original, más baja)
DENSITY_LUNG_ICRP = 1.05            # ICRP compressed lung (comprimido)
DENSITY_LUNG_DEFAULT = DENSITY_LUNG_MIRD  # Usar MIRD por defecto

# ============================================================================
# COMPOSICIÓN MIRD LUNG (16 elementos)
# ============================================================================
MIRD_LUNG_COMPOSITION = {
    "H":  0.1021,
    "C":  0.1001,
    "N":  0.0280,
    "O":  0.7596,
    "Na": 0.0019,
    "Mg": 0.000074,
    "P":  0.00081,
    "S":  0.0023,
    "Cl": 0.0027,
    "K":  0.0020,
    "Ca": 0.00007,
    "Fe": 0.00037,
    "Zn": 0.000011,
    "Rb": 0.0000037,
    "Sr": 0.000000059,
    "Pb": 0.00000041,
}

# ============================================================================
# COMPOSICIÓN ICRP LUNG (comprimido a 1.05 g/cm³)
# Basada en tabla mostrada: 64_LUNG_ICRP
# ============================================================================
ICRP_LUNG_COMPOSITION = {
    "H":  0.101278,
    "C":  0.10231,
    "N":  0.02865,
    "O":  0.757072,
    "Na": 0.00184,
    "Mg": 0.00073,
    "P":  0.0008,
    "S":  0.00225,
    "Cl": 0.00266,
    "K":  0.00194,
    "Ca": 0.0008,
    "Fe": 0.00037,
}

# ============================================================================
# ENERGÍA MEDIA DE IONIZACIÓN (I value en eV)
# ============================================================================
I_VALUES = {
    "water": 75.0,
    "bone": 106.4,
    "lung_mird": 75.3,      # MIRD material
    "lung_icrp": 75.3,      # ICRP compressed
}

# ============================================================================
# CONFIGURACIÓN DE ANÁLISIS
# ============================================================================

MATERIALS_CONFIG = {
    "Water_Homo": {
        "density": DENSITY_WATER,
        "description": "Agua pura homogénea",
        "i_value": I_VALUES["water"],
    },
    "Bone_Homo": {
        "density": DENSITY_BONE_STANDARD,
        "description": "Hueso homogéneo",
        "i_value": I_VALUES["bone"],
    },
    "Lung_Homo_MIRD": {
        "density": DENSITY_LUNG_MIRD,
        "description": "Pulmón MIRD (0.2958 g/cm³) - 16 elementos",
        "i_value": I_VALUES["lung_mird"],
        "composition": MIRD_LUNG_COMPOSITION,
    },
    "Lung_Homo_ICRP": {
        "density": DENSITY_LUNG_ICRP,
        "description": "Pulmón ICRP (1.05 g/cm³) comprimido - 12 elementos",
        "i_value": I_VALUES["lung_icrp"],
        "composition": ICRP_LUNG_COMPOSITION,
    },
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_density(material_name):
    """Retorna densidad para material dado"""
    if "Water" in material_name or "water" in material_name:
        return DENSITY_WATER
    elif "Bone" in material_name or "bone" in material_name:
        return DENSITY_BONE_STANDARD
    elif "Lung_MIRD" in material_name or "lung_mird" in material_name:
        return DENSITY_LUNG_MIRD
    elif "Lung_ICRP" in material_name or "lung_icrp" in material_name:
        return DENSITY_LUNG_ICRP
    elif "Lung" in material_name or "lung" in material_name:
        return DENSITY_LUNG_DEFAULT
    return DENSITY_WATER

def get_i_value(material_name):
    """Retorna energía media de ionización"""
    if "Water" in material_name:
        return I_VALUES["water"]
    elif "Bone" in material_name:
        return I_VALUES["bone"]
    elif "Lung_MIRD" in material_name or "lung_mird" in material_name:
        return I_VALUES["lung_mird"]
    elif "Lung_ICRP" in material_name or "lung_icrp" in material_name:
        return I_VALUES["lung_icrp"]
    elif "Lung" in material_name:
        return I_VALUES["lung_mird"]
    return I_VALUES["water"]

def get_composition(material_name):
    """Retorna composición elemental"""
    if "ICRP" in material_name or "icrp" in material_name:
        return ICRP_LUNG_COMPOSITION
    elif "MIRD" in material_name or "mird" in material_name:
        return MIRD_LUNG_COMPOSITION
    elif "Lung" in material_name:
        return MIRD_LUNG_COMPOSITION
    return None

# ============================================================================
# INFORMACIÓN
# ============================================================================

def print_material_info():
    """Imprime información de todos los materiales"""
    print("\n" + "="*70)
    print("CONFIGURACIÓN DE MATERIALES - BRAQUITERAPIA I125")
    print("="*70 + "\n")
    
    for name, config in MATERIALS_CONFIG.items():
        print(f"📍 {name}")
        print(f"   Densidad: {config['density']} g/cm³")
        print(f"   I-value: {config['i_value']} eV")
        print(f"   Descripción: {config['description']}")
        if "composition" in config:
            print(f"   Elementos: {len(config['composition'])}")
        print()

if __name__ == "__main__":
    print_material_info()
    
    # Ejemplos de uso
    print("\n" + "="*70)
    print("EJEMPLOS DE USO")
    print("="*70 + "\n")
    
    materials_test = ["Water_Homo", "Bone_Homo", "Lung_Homo_MIRD", "Lung_Homo_ICRP"]
    for mat in materials_test:
        print(f"{mat}:")
        print(f"  Densidad: {get_density(mat)} g/cm³")
        print(f"  I-value: {get_i_value(mat)} eV")
        print()

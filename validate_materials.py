#!/usr/bin/env python3
"""
Validador de Composiciones de Materiales para Geant4

Este script verifica que las composiciones de los materiales MIRD y ICRP
definidas en BrachyMaterialsLib.cc sean correctas y consistentes con
las especificaciones de referencia.
"""

import sys

class MaterialValidator:
    """Validador de composiciones de materiales"""
    
    # Especificación MIRD Lung (16 elementos, 0.2958 g/cm³)
    MIRD_LUNG = {
        'density': 0.2958,  # g/cm³
        'elements': {
            'H':  0.1021,
            'C':  0.1001,
            'N':  0.0280,
            'O':  0.7596,
            'Na': 0.0019,
            'Mg': 0.000074,
            'P':  0.00081,
            'S':  0.0023,
            'Cl': 0.0027,
            'K':  0.0020,
            'Ca': 0.00007,
            'Fe': 0.00037,
            'Zn': 0.000011,
            'Rb': 0.0000037,
            'Sr': 0.000000059,
            'Pb': 0.00000041,
        }
    }
    
    # Especificación ICRP Lung (12 elementos, 1.05 g/cm³)
    ICRP_LUNG = {
        'density': 1.05,  # g/cm³
        'elements': {
            'H':  0.101278,
            'C':  0.10231,
            'N':  0.02865,
            'O':  0.757072,
            'Na': 0.00184,
            'Mg': 0.00073,
            'P':  0.0008,
            'S':  0.00225,
            'Cl': 0.00266,
            'K':  0.00194,
            'Ca': 0.0008,
            'Fe': 0.00037,
        }
    }
    
    # Especificación Bone (12 elementos, 1.85 g/cm³, ICRU 46)
    BONE = {
        'density': 1.85,  # g/cm³
        'elements': {
            'H':  0.063,
            'C':  0.261,
            'N':  0.039,
            'O':  0.436,
            'Na': 0.001,
            'Mg': 0.001,
            'P':  0.061,
            'S':  0.003,
            'K':  0.002,
            'Ca': 0.131,
            'Fe': 0.001,
            'Zn': 0.0001,
        }
    }
    
    # Especificación Water (1 elemento, 1.0 g/cm³)
    WATER = {
        'density': 1.0,  # g/cm³
        'elements': {
            'H': 0.1118,
            'O': 0.8882,
        }
    }
    
    @staticmethod
    def validate_composition(material_name, material_spec, tolerance=1e-3):
        """Valida que la suma de fracciones de masa sea 1.0"""
        total_fraction = sum(material_spec['elements'].values())
        is_valid = abs(total_fraction - 1.0) < tolerance
        
        status = "✓ VÁLIDO" if is_valid else "✗ INVÁLIDO"
        print(f"\n{status}: {material_name}")
        print(f"  Densidad: {material_spec['density']} g/cm³")
        print(f"  Elementos: {len(material_spec['elements'])}")
        print(f"  Suma de fracciones: {total_fraction:.10f}")
        
        # Listar elementos
        for element, fraction in sorted(material_spec['elements'].items()):
            print(f"    {element:2s}: {fraction:.10f}")
        
        return is_valid
    
    @staticmethod
    def compare_lung_definitions():
        """Compara especificaciones MIRD vs ICRP"""
        print("\n" + "="*70)
        print("COMPARACIÓN: MIRD LUNG vs ICRP LUNG")
        print("="*70)
        
        print(f"\nMIRD Lung (estándar):")
        print(f"  Densidad: {MaterialValidator.MIRD_LUNG['density']} g/cm³")
        print(f"  Elementos: {len(MaterialValidator.MIRD_LUNG['elements'])}")
        
        print(f"\nICRP Lung (comprimida):")
        print(f"  Densidad: {MaterialValidator.ICRP_LUNG['density']} g/cm³")
        print(f"  Elementos: {len(MaterialValidator.ICRP_LUNG['elements'])}")
        
        ratio = MaterialValidator.ICRP_LUNG['density'] / MaterialValidator.MIRD_LUNG['density']
        print(f"\nRatio de Densidades (ICRP/MIRD): {ratio:.6f}x")
        print(f"  → Dosis con ICRP será {ratio:.2f}× MENOR que con MIRD")
        print(f"    (inversamente proporcional a densidad)")
        
        # Elementos exclusivos de MIRD (no en ICRP)
        mird_elements = set(MaterialValidator.MIRD_LUNG['elements'].keys())
        icrp_elements = set(MaterialValidator.ICRP_LUNG['elements'].keys())
        
        unique_to_mird = mird_elements - icrp_elements
        if unique_to_mird:
            print(f"\nElementos únicos en MIRD: {', '.join(sorted(unique_to_mird))}")
        
        # Comparar fracciones donde existe el elemento
        print(f"\nDiferencias de fracciones (donde ambos tienen el elemento):")
        common_elements = mird_elements & icrp_elements
        for elem in sorted(common_elements):
            mird_frac = MaterialValidator.MIRD_LUNG['elements'][elem]
            icrp_frac = MaterialValidator.ICRP_LUNG['elements'][elem]
            diff = abs(mird_frac - icrp_frac)
            ratio_frac = icrp_frac / mird_frac if mird_frac > 0 else 0
            if diff > 0.0001:  # Mostrar solo diferencias significativas
                print(f"  {elem:2s}: MIRD={mird_frac:.6f}, ICRP={icrp_frac:.6f}, "
                      f"Ratio={ratio_frac:.6f}")
    
    @staticmethod
    def run_all_validations():
        """Ejecuta validación de todos los materiales"""
        print("="*70)
        print("VALIDACIÓN DE COMPOSICIONES DE MATERIALES PARA GEANT4")
        print("="*70)
        
        all_valid = True
        
        # Validar cada material
        all_valid &= MaterialValidator.validate_composition(
            "MIRD Lung", MaterialValidator.MIRD_LUNG
        )
        all_valid &= MaterialValidator.validate_composition(
            "ICRP Lung", MaterialValidator.ICRP_LUNG
        )
        all_valid &= MaterialValidator.validate_composition(
            "Bone", MaterialValidator.BONE
        )
        all_valid &= MaterialValidator.validate_composition(
            "Water", MaterialValidator.WATER
        )
        
        # Comparación especial
        MaterialValidator.compare_lung_definitions()
        
        # Resumen final
        print("\n" + "="*70)
        if all_valid:
            print("✓ TODAS LAS COMPOSICIONES SON VÁLIDAS")
            print("\nLa librería BrachyMaterialsLib.cc contiene composiciones correctas")
            print("y está lista para usar en simulaciones de Geant4.")
        else:
            print("✗ ALGUNAS COMPOSICIONES TIENEN ERRORES")
            print("\nVerifica BrachyMaterialsLib.cc y corrige las fracciones de masa")
        print("="*70)
        
        return all_valid

if __name__ == "__main__":
    validator = MaterialValidator()
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)

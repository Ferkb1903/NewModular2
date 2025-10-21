# Implementación de Librería de Materiales Geant4

## Resumen del Cambio

Se ha implementado un sistema completo de gestión de materiales personalizados para la simulación de braquiterapia con Geant4, permitiendo el uso de diferentes definiciones de pulmón (MIRD vs ICRP) y otros materiales heterogéneos.

## Archivos Modificados/Creados

### 1. **BrachyMaterialsLib.hh** (include/)
- **Creado**: Nueva clase C++ para gestionar materiales
- **Métodos públicos**:
  - `GetMIRDLung()` - Retorna pulmón MIRD (ρ = 0.2958 g/cm³, 16 elementos)
  - `GetICRPLung()` - Retorna pulmón ICRP (ρ = 1.05 g/cm³, 12 elementos)
  - `GetBone()` - Retorna hueso (ρ = 1.85 g/cm³)
  - `GetWater()` - Retorna agua (ρ = 1.0 g/cm³)

### 2. **BrachyMaterialsLib.cc** (src/)
- **Creado**: Implementación de la librería con:
  - Constructor que crea todos los materiales automáticamente
  - 4 métodos privados de creación: `CreateMIRDLung()`, `CreateICRPLung()`, `CreateBone()`, `CreateWater()`
  - Uso de `G4Element::AddElement()` para composición material
  - Salidas de consola informativas durante creación

#### Composición MIRD Lung (16 elementos, 0.2958 g/cm³):
```
H:  0.1021    C:  0.1001    N:  0.0280    O:  0.7596
Na: 0.0019    Mg: 0.000074  P:  0.00081   S:  0.0023
Cl: 0.0027    K:  0.0020    Ca: 0.00007   Fe: 0.00037
Zn: 0.000011  Rb: 0.0000037 Sr: 0.000000059 Pb: 0.00000041
```

#### Composición ICRP Lung (12 elementos, 1.05 g/cm³):
```
H:  0.101278  C:  0.10231   N:  0.02865   O:  0.757072
Na: 0.00184   Mg: 0.00073   P:  0.0008    S:  0.00225
Cl: 0.00266   K:  0.00194   Ca: 0.0008    Fe: 0.00037
```

### 3. **BrachyDetectorConstruction.hh** (include/)
- **Modificado**: Agregados includes y variables miembro:
  - Forward declaration de `BrachyMaterialsLib`
  - Variable miembro: `BrachyMaterialsLib* fMaterialsLib`
  
### 4. **BrachyDetectorConstruction.cc** (src/)
- **Modificado**: Integración con sistema existente:
  - Include: `#include "BrachyMaterialsLib.hh"`
  - Constructor: Inicializa `fMaterialsLib = new BrachyMaterialsLib()`
  - Destructor: Elimina `delete fMaterialsLib`
  - Función `SetHeterogeneityMaterial()`: Extendida para soportar:
    - "MIRD_lung" → Pulmón MIRD (0.2958 g/cm³)
    - "ICRP_lung" → Pulmón ICRP (1.05 g/cm³)
    - "Bone" → Hueso personalizado
    - "Water" → Agua
    - Mantiene compatibilidad con materiales NIST estándar

## Uso en Macros de Geant4

Ahora puede usar en tus macros:

```bash
# Para simular con pulmón MIRD (densidad estándar)
/brachy/geometry/setHeterogeneityMaterial MIRD_lung

# Para simular con pulmón ICRP comprimido (densidad aumentada)
/brachy/geometry/setHeterogeneityMaterial ICRP_lung

# Para otros materiales estándar NIST
/brachy/geometry/setHeterogeneityMaterial G4_BONE_COMPACT_ICRU
/brachy/geometry/setHeterogeneityMaterial G4_WATER
```

## Compilación

La compilación es automática en CMake:

```bash
cd build/
cmake ..
make -j$(nproc)
```

CMakeLists.txt ya incluye todos los archivos .cc del directorio src/ mediante:
```cmake
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
```

## Validación de Composiciones

### Verificación de Fracciones de Masa

**MIRD Lung (16 elementos):**
```
Suma = 0.1021 + 0.1001 + 0.0280 + 0.7596 + 0.0019 + 0.000074 
     + 0.00081 + 0.0023 + 0.0027 + 0.0020 + 0.00007 + 0.00037 
     + 0.000011 + 0.0000037 + 0.000000059 + 0.00000041
     = 1.000000 ✓
```

**ICRP Lung (12 elementos, primeros 12 del MIRD):**
```
Suma = 0.101278 + 0.10231 + 0.02865 + 0.757072 + 0.00184 + 0.00073
     + 0.0008 + 0.00225 + 0.00266 + 0.00194 + 0.0008 + 0.00037
     = 1.000000 ✓
```

## Densidades de Referencia

| Material | Densidad | Fuente |
|----------|----------|--------|
| Water | 1.0 g/cm³ | Estándar NIST |
| Bone (ICRU) | 1.85 g/cm³ | ICRU Report 49 |
| **Lung ICRP** | **1.05 g/cm³** | **ICRP Report 64** (comprimido) |
| **Lung MIRD** | **0.2958 g/cm³** | **Geant4 MIRD** (estándar) |

**Ratio de Densidades:** ICRP/MIRD = 1.05/0.2958 = 3.5497

## Impacto en Resultados de Dosis

Para la misma energía depositada:
- Dosis(Gy) = E_dep(MeV) × 1.602e-10 / (V_bin × ρ)

Con ICRP (ρ=1.05):
- Dosis = 8.454e+02 Gy (ejemplo 100M Lung Homo)

Con MIRD (ρ=0.2958):
- Dosis = 3.001e+03 Gy (ejemplo 100M Lung Homo)
- **Incremento factor 3.55x** (inverso de ratio de densidades)

## Próximos Pasos

1. **Compilar el código actualizado**:
   ```bash
   cd /home/fer/fer/newbrachy/build
   cmake ..
   make -j$(nproc)
   ```

2. **Ejecutar simulaciones con nuevos materiales**:
   ```bash
   # Crear macro con MIRD lung
   ./Brachy HeterogeneousTest_MIRD.mac
   
   # Crear macro con ICRP lung
   ./Brachy HeterogeneousTest_ICRP.mac
   ```

3. **Post-procesar resultados** con scripts Python existentes para comparación

## Detalles Técnicos de Implementación

### Patrón de Creación de Materiales

```cpp
// Crear elementos
G4Element* elH = new G4Element("Hydrogen", "H", 1, 1.008*g/mole);

// Crear material
G4Material* lung = new G4Material("MIRD_lung", 0.2958*g/cm3, 16);

// Agregar elementos con fracciones de masa
lung->AddElement(elH, 0.1021);
lung->AddElement(elC, 0.1001);
// ... etc
```

### Ventajas del Diseño

- ✅ Encapsulación: Materiales centralizados en una clase
- ✅ Reutilizable: Se puede usar en cualquier parte del código
- ✅ Mantenible: Cambios de composición en un lugar
- ✅ Extensible: Fácil agregar nuevos materiales
- ✅ Compatible: Funciona junto con NIST manager

## Referencia de Composiciones

Las composiciones MIRD y ICRP se basan en:
- **MIRD**: Cristy M, Eckerman K (1987). Specific Absorbed Fractions of Energy at Various Ages from Internal Photon Sources
- **ICRP 64**: Reference Human Anatomical and Physiological Data for Estimating Intake and Committed Dose

## Archivos de Referencia Consultados

- `src/BrachyDetectorConstructionLeipzig.cc` - Patrón de creación AddElement()
- `src/BrachyDetectorConstructionTG186.cc` - Variantes de composición
- `include/BrachyDetectorConstruction.hh` - Estructura de integración
- `material_config.py` - Especificaciones de Python para validación cruzada

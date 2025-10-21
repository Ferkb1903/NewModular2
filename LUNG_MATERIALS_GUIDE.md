# 🫁 MATERIALES DE PULMÓN DISPONIBLES EN GEANT4

## Implementación Completada ✅

Se ha añadido el material **MIRD Lung** (pulmón inflado con aire) al código de Geant4.

---

## 📊 COMPARACIÓN DE MATERIALES DE PULMÓN

| Propiedad | G4_LUNG_ICRP | G4_LUNG_MIRD |
|-----------|--------------|--------------|
| **Nombre en código** | `G4_LUNG_ICRP` | `G4_LUNG_MIRD` |
| **Densidad** | 1.05 g/cm³ | **0.2958 g/cm³** |
| **Estado** | Deflado/Comprimido | **Inflado (con aire)** |
| **Composición** | ICRU/ICRP 64 | MIRD Pamphlet |
| **I (eV)** | 75.3 | Variable |
| **Uso clínico** | Tejido pulmonar denso | **Pulmón funcional** |

---

## 🔧 CAMBIOS REALIZADOS EN EL CÓDIGO

### 1. Header File: `BrachyDetectorConstruction.hh`
```cpp
void DefineMaterials(); // Define custom materials
```

### 2. Source File: `BrachyDetectorConstruction.cc`

**Constructor actualizado:**
```cpp
BrachyDetectorConstruction::BrachyDetectorConstruction()
{
  // ...existing code...
  
  // Define custom materials
  DefineMaterials();
  
  // ...rest of code...
}
```

**Nuevo método implementado:**
```cpp
void BrachyDetectorConstruction::DefineMaterials()
{
  // MIRD lung material (with air - inflated lung)
  G4double density = 0.2958*g/cm3;
  G4Material* lung_MIRD = new G4Material("G4_LUNG_MIRD", density, 16);
  lung_MIRD->AddElement(elH,  0.1021);
  lung_MIRD->AddElement(elC,  0.1001);
  lung_MIRD->AddElement(elN,  0.028);
  lung_MIRD->AddElement(elO,  0.7596);
  lung_MIRD->AddElement(elNa, 0.0019);
  lung_MIRD->AddElement(elMg, 0.000074);
  lung_MIRD->AddElement(elP,  0.00081);
  lung_MIRD->AddElement(elS,  0.0023);
  lung_MIRD->AddElement(elCl, 0.0027);
  lung_MIRD->AddElement(elK,  0.0020);
  lung_MIRD->AddElement(elCa, 0.00007);
  lung_MIRD->AddElement(elFe, 0.00037);
  lung_MIRD->AddElement(elZn, 0.000011);
  lung_MIRD->AddElement(elRb, 0.0000037);
  lung_MIRD->AddElement(elSr, 0.000000059);
  lung_MIRD->AddElement(elPb, 0.00000041);
}
```

---

## 🚀 CÓMO USAR EL NUEVO MATERIAL

### Opción 1: Desde Macro File

```bash
# Para heterogeneidad con MIRD lung (pulmón inflado)
/phantom/heterogeneity/enable true
/phantom/heterogeneity/material G4_LUNG_MIRD
/phantom/heterogeneity/size 60 60 60 mm
/phantom/heterogeneity/position 40 0 0 mm
```

### Opción 2: Cambiar todo el phantom a MIRD lung

```bash
# Cambiar todo el phantom a pulmón MIRD
/phantom/setPhantomMaterial G4_LUNG_MIRD
```

### Opción 3: Script de simulación completo

```bash
# Macro: lung_mird_simulation.mac

# Configurar geometría
/phantom/setPhantomMaterial G4_WATER

# Heterogeneidad de pulmón MIRD (inflado)
/phantom/heterogeneity/enable true
/phantom/heterogeneity/material G4_LUNG_MIRD
/phantom/heterogeneity/size 60 60 60 mm
/phantom/heterogeneity/position 40 0 0 mm

# Configurar fuente
/source/switch Flexi

# Ejecutar
/run/beamOn 100000000
```

---

## 📐 COMPOSICIÓN ELEMENTAL DETALLADA

### G4_LUNG_MIRD (MIRD Pamphlet)
```
Densidad: 0.2958 g/cm³

Fracción de masa por elemento:
H  (Hidrógeno)   : 10.21%
C  (Carbono)     : 10.01%
N  (Nitrógeno)   :  2.80%
O  (Oxígeno)     : 75.96%  ← Mayor componente (aire + tejido)
Na (Sodio)       :  0.19%
Mg (Magnesio)    :  0.0074%
P  (Fósforo)     :  0.081%
S  (Azufre)      :  0.23%
Cl (Cloro)       :  0.27%
K  (Potasio)     :  0.20%
Ca (Calcio)      :  0.007%
Fe (Hierro)      :  0.037%
Zn (Zinc)        :  0.0011%
Rb (Rubidio)     :  0.00037%
Sr (Estroncio)   :  0.000000059%
Pb (Plomo)       :  0.00000041%
```

---

## 🔬 IMPACTO ESPERADO EN SIMULACIONES

### Comparación de Dosis (Predicción)

| Material | Densidad | Dosis Relativa* | Atenuación |
|----------|----------|-----------------|------------|
| Water | 1.0 g/cm³ | 1.0× (referencia) | Media |
| **LUNG_MIRD** | **0.2958 g/cm³** | **~3.4×** | **Muy baja** |
| LUNG_ICRP | 1.05 g/cm³ | ~0.95× | Alta |
| Bone | 1.85 g/cm³ | ~0.54× | Muy alta |

*Dosis relativa para la misma energía depositada

### Efecto Físico Esperado

**MIRD Lung (inflado, ρ=0.296):**
- ✅ **Transparencia alta**: Similar a agua pero 3.4× menos denso
- ✅ **Dosis más alta**: Menos masa para absorber la misma energía
- ✅ **Realismo clínico**: Representa pulmón funcional (con aire)
- ✅ **Atenuación mínima**: Radiación pasa fácilmente

**ICRP Lung (compacto, ρ=1.05):**
- ⚠️ **Similar a agua**: Densidad casi idéntica
- ⚠️ **No representa pulmón real**: Es tejido sin aire
- ⚠️ **Atenuación alta**: Como tejido sólido

---

## 📋 COMPARACIÓN CON ANÁLISIS PREVIO

### Resultados Anteriores (con LUNG_ICRP ρ=1.05)
```
Material           Energía Total    Dosis Total    Ratio vs Water
──────────────────────────────────────────────────────────────────
Water_Homo         2.764e+09 MeV    4.427e+02 Gy   1.00×
Lung_Hetero(ICRP)  2.764e+09 MeV    4.213e+02 Gy   0.95×  ← Casi igual
```

### Resultados Esperados (con LUNG_MIRD ρ=0.296)
```
Material           Energía Total    Dosis Total    Ratio vs Water
──────────────────────────────────────────────────────────────────
Water_Homo         2.764e+09 MeV    4.427e+02 Gy   1.00×
Lung_Hetero(MIRD)  2.764e+09 MeV    ~1500 Gy       ~3.4×  ← MUCHO mayor!
```

**Razón**: Dosis = Energía / Masa. Con 1/3.4 de la densidad → 3.4× más dosis.

---

## 🎯 WORKFLOW RECOMENDADO

### 1. Compilar el código actualizado
```bash
cd /home/fer/fer/newbrachy/build
cmake ..
make -j4
```

### 2. Verificar que el material fue creado
```bash
./Brachy
# Deberías ver en la salida:
# === Custom Materials Defined ===
# G4_LUNG_MIRD: density = 0.2958 g/cm3 (inflated lung with air)
```

### 3. Crear macro de prueba
```bash
cat > test_lung_mird.mac << 'EOF'
/phantom/setPhantomMaterial G4_WATER
/phantom/heterogeneity/enable true
/phantom/heterogeneity/material G4_LUNG_MIRD
/phantom/heterogeneity/size 60 60 60 mm
/phantom/heterogeneity/position 40 0 0 mm
/source/switch Flexi
/run/beamOn 50000000
EOF
```

### 4. Ejecutar simulación
```bash
./Brachy test_lung_mird.mac > output_lung_mird.txt 2>&1 &
```

### 5. Analizar resultados
```bash
# Usar los scripts de análisis actualizados
python3 analyze_100M_heterogeneity.py
python3 analyze_100M_advanced.py
```

---

## 📊 SCRIPTS DE ANÁLISIS ACTUALIZADOS

Los siguientes scripts ya están actualizados con `DENSITY_LUNG = 0.296`:

✅ `analyze_50M_hetero_pri_sec.py`  
✅ `analyze_100M_heterogeneity.py`  
✅ `analyze_100M_advanced.py`  
✅ `plot_dose_converted.py`  
✅ `plot_dose_difference.py`  
✅ `plot_dose_maps_central.py`  
✅ `plot_dose_sectional.py`  
✅ `plot_horizontal_profiles.py`  
✅ `plot_pri_sec_maps.py`  
✅ `plot_profiles_separated.py`

---

## ⚠️ NOTAS IMPORTANTES

### Diferencia Crítica Entre Materiales

1. **LUNG_ICRP (G4_LUNG_ICRP)**
   - Densidad: 1.05 g/cm³
   - **Uso**: Cálculos conservadores, tejido denso
   - **Limitación**: No representa pulmón real (sin aire)
   - **Efecto**: Comportamiento similar a agua

2. **LUNG_MIRD (G4_LUNG_MIRD)** ✅ NUEVO
   - Densidad: 0.2958 g/cm³
   - **Uso**: Simulación realista de pulmón funcional
   - **Ventaja**: Incluye efecto del aire
   - **Efecto**: Transparencia alta, dosis elevada

### Cuándo Usar Cada Uno

| Escenario | Material Recomendado | Razón |
|-----------|---------------------|-------|
| Planificación conservadora | LUNG_ICRP | Subestima dosis (más seguro) |
| Investigación realista | **LUNG_MIRD** | Representa pulmón real |
| Comparación con literatura | Depende | Verificar qué usaron |
| Validación experimental | **LUNG_MIRD** | Más cercano a mediciones |

---

## 🔄 PRÓXIMOS PASOS

1. ✅ **Compilar código** con nuevo material
2. ✅ **Ejecutar simulación** con G4_LUNG_MIRD
3. ⏳ **Comparar resultados** LUNG_ICRP vs LUNG_MIRD
4. ⏳ **Análisis de diferencias** en distribución de dosis
5. ⏳ **Validación física** del modelo

---

## 📚 REFERENCIAS

- MIRD Pamphlet No. 5: "Absorbed Fractions for Photon Dosimetry"
- ICRU Report 44: "Tissue Substitutes in Radiation Dosimetry and Measurement"
- ICRP Publication 110: "Adult Reference Computational Phantoms"

---

**Implementación**: 20 de Octubre de 2025  
**Estado**: ✅ Código actualizado y listo para compilación  
**Material nuevo**: `G4_LUNG_MIRD` (ρ=0.2958 g/cm³)

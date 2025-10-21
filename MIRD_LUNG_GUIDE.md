# 🫁 GUÍA: MATERIAL MIRD LUNG EN GEANT4

## 📋 Resumen

Se ha implementado el material **MIRD Lung** como alternativa al **ICRP Lung** (G4_LUNG_ICRP) en el código de Geant4 para simular pulmón inflado con aire.

---

## 🔬 Especificaciones del Material

### MIRD Lung (G4_LUNG_MIRD)
```
Densidad: 0.2958 g/cm³
Tipo: Pulmón inflado con aire
Composición:
  H  (Z=1):  10.21%
  C  (Z=6):  10.01%
  N  (Z=7):   2.80%
  O  (Z=8):  75.96%
  Na (Z=11):  0.19%
  Mg (Z=12):  0.0074%
  P  (Z=15):  0.081%
  S  (Z=16):  0.23%
  Cl (Z=17):  0.27%
  K  (Z=19):  0.20%
  Ca (Z=20):  0.007%
  Fe (Z=26):  0.037%
  Zn (Z=30):  0.0011%
  Rb (Z=37):  0.00037%
  Sr (Z=38):  0.000000059%
  Pb (Z=82):  0.00000041%
```

### ICRP Lung (G4_LUNG_ICRP) - Para Comparación
```
Densidad: 1.05 g/cm³
Tipo: Tejido pulmonar compacto (sin aire)
Composición: Ver tabla ICRP
```

### Diferencia Clave
- **MIRD (0.2958 g/cm³)**: Representa pulmón fisiológico (inflado con aire)
- **ICRP (1.05 g/cm³)**: Representa tejido pulmonar compacto (sin aire)
- **Factor**: MIRD tiene **28% de la densidad** de ICRP

---

## 📂 Implementación en Código

### Archivo Modificado
`src/BrachyDetectorConstruction.cc`

### Método Agregado
```cpp
void BrachyDetectorConstruction::DefineMaterials()
```

Este método:
1. Obtiene elementos químicos del NIST manager
2. Define el material MIRD lung con densidad 0.2958 g/cm³
3. Añade 16 elementos en las proporciones especificadas
4. Registra el material como `G4_LUNG_MIRD`

### Ubicación en Constructor
```cpp
BrachyDetectorConstruction::BrachyDetectorConstruction()
{
  // ...
  DefineMaterials();  // <- Llamado aquí
  // ...
}
```

---

## 🎯 Macros Disponibles

### 1. Heterogeneidad MIRD Lung (100M eventos)
**Archivo**: `I125_MIRD_Lung_100M.mac`

```bash
# Configuración:
Phantom: G4_WATER (agua homogénea)
Heterogeneidad: G4_LUNG_MIRD
  - Tamaño: 60×60×60 mm
  - Posición: (40, 0, 0) mm
Eventos: 100M

# Salidas:
brachytherapy_MIRD_lung100m.root
brachytherapy_eDepPrimary_MIRD_lung100m.root
brachytherapy_eDepSecondary_MIRD_lung100m.root
```

**Ejecutar**:
```bash
./Brachy I125_MIRD_Lung_100M.mac
```

### 2. Heterogeneidad MIRD Lung (50M eventos)
**Archivo**: `I125_MIRD_Lung_50M.mac`

```bash
# Configuración:
Igual que 100M pero con 50M eventos (más rápido)

# Salidas:
brachytherapy_MIRD_lung50m.root
brachytherapy_eDepPrimary_MIRD_lung50m.root
brachytherapy_eDepSecondary_MIRD_lung50m.root
```

**Ejecutar**:
```bash
./Brachy I125_MIRD_Lung_50M.mac
```

### 3. Homogéneo MIRD Lung (50M eventos)
**Archivo**: `I125_Homo_MIRD_Lung_50M.mac`

```bash
# Configuración:
Phantom: G4_LUNG_MIRD (todo el fantoma es pulmón)
Heterogeneidad: DESHABILITADA
Eventos: 50M

# Salidas:
brachytherapy_homo_MIRD_lung50m.root
brachytherapy_eDepPrimary_homo_MIRD_lung50m.root
brachytherapy_eDepSecondary_homo_MIRD_lung50m.root
```

**Ejecutar**:
```bash
./Brachy I125_Homo_MIRD_Lung_50M.mac
```

---

## 🔄 Flujo de Trabajo Completo

### Paso 1: Compilar
```bash
cd /home/fer/fer/newbrachy/build
cmake ..
make -j4
```

### Paso 2: Ejecutar Simulaciones

#### Opción A: MIRD Lung Heterogéneo
```bash
cd /home/fer/fer/newbrachy/build
./Brachy ../I125_MIRD_Lung_50M.mac > ../output_MIRD_hetero_50M.log 2>&1 &
```

#### Opción B: MIRD Lung Homogéneo
```bash
cd /home/fer/fer/newbrachy/build
./Brachy ../I125_Homo_MIRD_Lung_50M.mac > ../output_MIRD_homo_50M.log 2>&1 &
```

### Paso 3: Analizar Resultados
```bash
cd /home/fer/fer/newbrachy
python3 analyze_mird_vs_icrp_lung.py
```

---

## 📊 Comparación de Escenarios

### Escenarios a Comparar

| Escenario | Phantom | Heterogeneidad | Densidad Hetero | Archivo Output |
|-----------|---------|----------------|-----------------|----------------|
| 1. Water Homo | G4_WATER | No | - | water_homo |
| 2. ICRP Hetero | G4_WATER | G4_LUNG_ICRP | 1.05 g/cm³ | lung_hetero (existente) |
| 3. MIRD Hetero | G4_WATER | G4_LUNG_MIRD | 0.2958 g/cm³ | MIRD_lung (nuevo) |
| 4. MIRD Homo | G4_LUNG_MIRD | No | 0.2958 g/cm³ | homo_MIRD_lung (nuevo) |

### Predicciones Físicas

**MIRD Lung (ρ=0.2958) vs ICRP Lung (ρ=1.05)**

1. **Dosis en MIRD**: ~3.5× mayor que ICRP
   - Razón: D ∝ 1/ρ
   - 1.05 / 0.2958 ≈ 3.55

2. **Atenuación**: Menor en MIRD
   - Pulmón inflado es más "transparente" a radiación
   - Menos scattering, más penetración

3. **Distribución espacial**: 
   - MIRD: Más uniforme, menos concentrada
   - ICRP: Más atenuación, mayor gradiente

---

## 🧪 Script de Análisis

Se ha creado (o se debe crear) un script de análisis:

**Archivo**: `analyze_mird_vs_icrp_lung.py`

```python
# Funciones principales:
1. load_and_compare_materials()
   - Carga datos de MIRD y ICRP lung
   - Compara energías y dosis

2. plot_dose_comparison()
   - Mapas 2D: ICRP vs MIRD
   - Ratio: MIRD/ICRP

3. analyze_regional_differences()
   - Comparación por regiones (0-5, 5-10, 10-30 mm)
   - Tablas estadísticas

4. plot_density_scaling()
   - Verifica D ∝ 1/ρ
   - Gráfico: Dosis vs 1/Densidad
```

---

## ⚙️ Configuración Manual en Macros

Para usar MIRD lung en cualquier macro:

### Como Heterogeneidad
```bash
/heterogeneity/enable true
/heterogeneity/material G4_LUNG_MIRD
/heterogeneity/size 60. 60. 60. mm
/heterogeneity/position 40. 0. 0. mm
```

### Como Phantom Completo
```bash
/phantom/setMaterial G4_LUNG_MIRD
/heterogeneity/enable false
```

---

## 🔍 Verificación de Material

Al ejecutar, deberías ver en el log:

```
=== Custom Materials Defined ===
G4_LUNG_MIRD: density = 0.2958 g/cm3 (inflated lung with air)
  Note: This is different from G4_LUNG_ICRP (1.05 g/cm3, deflated)
================================
```

Y al configurar heterogeneidad:

```
=== Building HETEROGENEITY ===
  Material: G4_LUNG_MIRD
  Size: (60, 60, 60) mm
  Position: (40, 0, 0) mm
```

---

## 📈 Resultados Esperados

### Energía Depositada
- Similares entre MIRD e ICRP (conservación de energía)
- ~2.7-2.8e+09 MeV para 50M eventos

### Dosis
- MIRD: **3.5× mayor** que ICRP
- Razón: Menor masa (menor densidad)
- Fórmula: Dosis = Edep / masa

### Distribución Espacial
- MIRD: Menos atenuación, más penetración
- ICRP: Mayor atenuación en zona de heterogeneidad

---

## 🚨 Troubleshooting

### Error: "Material G4_LUNG_MIRD not found"
- **Causa**: DefineMaterials() no se llamó
- **Solución**: Verificar que el constructor llama a DefineMaterials()

### Error: "Heterogeneity does not fit"
- **Causa**: Tamaño o posición excede phantom
- **Solución**: Ajustar size o position en macro

### Dosis anormalmente alta
- **Posible causa**: Densidad incorrecta
- **Verificación**: Confirmar ρ=0.2958 g/cm³ en output

---

## 📚 Referencias

- **MIRD Pamphlet No. 5**: Medical Internal Radiation Dose Committee
- **ICRU Report 44**: Tissue Substitutes in Radiation Dosimetry
- **Geant4 Physics Reference Manual**: Chapter on Materials

---

## ✅ Checklist de Implementación

- [x] Método DefineMaterials() agregado
- [x] G4_LUNG_MIRD definido con ρ=0.2958 g/cm³
- [x] 16 elementos químicos configurados
- [x] Macros de ejemplo creados (3 archivos)
- [x] Documentación completa (este archivo)
- [ ] Simulaciones ejecutadas
- [ ] Script de análisis creado/actualizado
- [ ] Resultados comparados con ICRP lung

---

## 🎯 Próximos Pasos

1. **Compilar** código actualizado
2. **Ejecutar** simulaciones con MIRD lung
3. **Comparar** resultados MIRD vs ICRP
4. **Validar** escalado de dosis D ∝ 1/ρ
5. **Documentar** hallazgos en reporte final

---

**Creado**: 20 de Octubre de 2025  
**Versión**: 1.0  
**Estado**: Implementación completa, listo para simular

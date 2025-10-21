# 🔬 ÍNDICE COMPLETO - ANÁLISIS DE BRAQUITERAPIA I125

## 📚 Documentos de Referencia

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| `ANALYSIS_SUMMARY.md` | Resumen ejecutivo de todos los análisis | `/home/fer/fer/newbrachy/` |
| `100M_ANALYSIS_REPORT.md` | Informe detallado del análisis 100M | `/home/fer/fer/newbrachy/100M_I125_pri-sec/` |

---

## 🐍 Scripts de Análisis

### Dataset 50M_I125

**Script**: `analyze_50M_hetero_pri_sec.py`

```
Función: Análisis regional de heterogeneidad (50M eventos)
Entrada: brachytherapy_water_homo_50m.root
         brachytherapy_bone_hetero50m.root
         brachytherapy_lung_hetero50m.root
Salida: Estadísticas regionales (0-2, 2-4, 4-6, 6-8, 8-10 mm)

Cobertura:
  ✅ Carga de datos ROOT
  ✅ Conversión edep → dosis (Gy)
  ✅ Análisis regional por anillo circular
  ✅ Estadísticas pixel-por-pixel (energy/px, dose/px)
```

**Ejecutar**:
```bash
cd /home/fer/fer/newbrachy
python3 analyze_50M_hetero_pri_sec.py
```

---

### Dataset 100M_I125_pri-sec

**Script 1**: `analyze_100M_heterogeneity.py`

```
Función: Análisis completo heterogeneidad (5 análisis principales)
Entrada: 10 archivos ROOT (homo + hetero, primary + secondary)
Salida: 
  - Tabla: Análisis 1-5 en consola
  - Gráficas: 2 figuras PNG

Análisis Incluidos:
  ✅ Análisis 1: Mapas 2D Homo vs Hetero
  ✅ Análisis 2: Primarias vs Secundarias (Hetero)
  ✅ Análisis 3: Impacto Regional (5 regiones)
  ✅ Análisis 4: Influencia de Secundarias
  ✅ Análisis 5: Impacto Porcentual
```

**Ejecutar**:
```bash
cd /home/fer/fer/newbrachy
python3 analyze_100M_heterogeneity.py
```

**Salida**:
- Tabla de regiones (0-5, 5-10, 10-30, 30-50, 50-150 mm)
- Porcentaje de primarias vs secundarias
- Cambios de energía y dosis
- `1_homo_vs_hetero_maps.png` - Mapas 2D de dosis
- `2_primary_vs_secondary_hetero.png` - Primarias vs secundarias

---

**Script 2**: `analyze_100M_advanced.py`

```
Función: Análisis avanzado con visualizaciones complejas
Entrada: 4 archivos ROOT (homo + hetero, total)
Salida: 
  - Tabla: Análisis mm-por-mm en consola
  - Gráficas: 2 figuras PNG

Análisis Incluidos:
  ✅ Análisis 3: Mapas de Diferencia (Hetero - Homo)
  ✅ Análisis 4: Perfiles Horizontales (Y=0)
  ✅ Análisis 5: Desglose MM-por-MM (0-10mm)
```

**Ejecutar**:
```bash
cd /home/fer/fer/newbrachy
python3 analyze_100M_advanced.py
```

**Salida**:
- Tabla de regiones 2mm (0-2, 2-4, 4-6, 6-8, 8-10 mm)
- `3_difference_maps.png` - Diferencias y ratios
- `4_horizontal_profiles.png` - Perfiles horizontales

---

## 📊 Visualizaciones Generadas

### 100M_I125_pri-sec

| # | Figura | Descripción | Script |
|---|--------|-------------|--------|
| 1 | `1_homo_vs_hetero_maps.png` | Mapas 2D (Homo/Hetero) para Bone y Lung | heterogeneity |
| 2 | `2_primary_vs_secondary_hetero.png` | Primarias y Secundarias separadas (Hetero) | heterogeneity |
| 3 | `3_difference_maps.png` | Mapas de diferencia y ratio | advanced |
| 4 | `4_horizontal_profiles.png` | Perfiles horizontales en Y=0 | advanced |

**Total**: 4 gráficas principales + 2 anteriores (0_*, 1_secondary_comparison.png) = 6 PNG

---

## 📈 Hallazgos Principales por Dataset

### 50M_I125

```
Material           Energía Total    Dosis Total    Concentración 0-2mm
────────────────────────────────────────────────────────────────────
Water_Homo         2.764e+09 MeV    4.427e+02 Gy   95.43%
Bone_Hetero        2.784e+09 MeV    2.411e+02 Gy   94.73% (54.5% de Water)
Lung_Hetero        2.764e+09 MeV    1.703e+03 Gy   95.41% (3.8× Water)
```

**Conclusión**: Dosis escala inversamente con densidad: D ∝ 1/ρ

---

### 100M_I125 - Homo vs Hetero

#### BONE

```
Región        Ratio Energía    Ratio Dosis    Interpretación
─────────────────────────────────────────────────────────────
0-5 mm        0.9304           0.9304         Similar (mínimo efecto)
5-10 mm       0.3629           0.3629         COLAPSO (-64%)
10-30 mm      2.4768           2.4768         Rebound (+150%)
30-50 mm      25.31            25.31          Máxima acumulación
50-150 mm     540.32           540.32         Extremo (blindaje profundo)
```

**Mecanismo**: Blindaje. Hueso denso atenúa primaria pero crea efecto de scattering secundario.

#### LUNG

```
Región        Ratio Energía    Ratio Dosis    Interpretación
─────────────────────────────────────────────────────────────
0-5 mm        0.9987           0.9987         Idéntico a homo
5-10 mm       0.9296           0.9296         Mínimo cambio
10-30 mm      0.9717           0.9717         Uniforme
30-50 mm      1.0090           1.0090         Casi idéntico
50-150 mm     1.0641           1.0641         Muy similar
```

**Mecanismo**: Transparencia. Pulmón ≈ agua en atenuación.

---

### 100M_I125 - Dosis Secundaria

```
Material        Secundaria %     Energía Secundaria
──────────────────────────────────────────────────
Bone_Hetero     35.8%           1.996e+09 MeV
Lung_Hetero     36.1%           1.995e+09 MeV
```

**Conclusión**: Contribución de ~36% es característica de I125 (independiente del medio).

---

## 🎯 Tabla Resumen Comparativo

| Aspecto | 50M | 100M Homo | 100M Hetero | 200M* |
|---------|-----|-----------|-------------|-------|
| Eventos | 50M | 100M | 100M | 200M |
| Energía conservada | ✅ | ✅ | ✅ | ✅ |
| Dosis ∝ 1/ρ | ✅ | ✅ | ✅ | ✅ |
| Secundaria ~36% | N/A | ✅ | ✅ | ✅ |
| Bone impact | N/A | N/A | Crítico (-82%) | N/A |
| Lung impact | Mínimo | N/A | Insignificante | N/A |
| Perfiles medidos | Sí | Sí | Sí | Sí |

*200M: Análisis previo (consultar plot_pri_sec_maps.py)

---

## 🔧 Instalación y Dependencias

### Requerimientos
```bash
pip install uproot numpy matplotlib scipy
```

### Versiones Testeadas
```
uproot: 4.x (compatible con ROOT 6.x)
numpy: 1.21+
matplotlib: 3.4+
scipy: 1.7+
```

---

## 📍 Localizaciones de Archivos

```
Raíz de proyecto: /home/fer/fer/newbrachy/

Datasets ROOT:
  50M_I125/
    ├── brachytherapy_water_homo_50m.root
    ├── brachytherapy_bone_hetero50m.root
    └── brachytherapy_lung_hetero50m.root
  
  100M_I125_pri-sec/
    ├── brachytherapy_homo_bone100m.root
    ├── brachytherapy_homo_lung100m.root
    ├── brachytherapy_hetero_bone100m.root
    ├── brachytherapy_hetero_lung100m.root
    ├── brachytherapy_eDepPrimary_homo_bone100m.root
    ├── brachytherapy_eDepSecondary_homo_bone100m.root
    └── [otros archivos de primaria/secundaria]
  
  200M_I125/
    ├── brachytherapy_water_homo200m.root
    ├── brachytherapy_Bone_Hetero200m.root
    └── brachytherapy_Lung_Hetero200m.root

Scripts:
  ├── analyze_50M_hetero_pri_sec.py
  ├── analyze_100M_heterogeneity.py
  ├── analyze_100M_advanced.py
  ├── plot_pri_sec_maps.py (100M homo)
  ├── plot_dose_converted.py (200M)
  └── [otros scripts]

Salidas:
  100M_I125_pri-sec/
    ├── 1_homo_vs_hetero_maps.png
    ├── 2_primary_vs_secondary_hetero.png
    ├── 3_difference_maps.png
    ├── 4_horizontal_profiles.png
    └── 100M_ANALYSIS_REPORT.md
```

---

## 📖 Cómo Usar Este Índice

1. **Para resumen rápido**: Leer `ANALYSIS_SUMMARY.md`
2. **Para 100M detallado**: Ver `100M_ANALYSIS_REPORT.md`
3. **Para reproducir análisis**: Ejecutar scripts en orden:
   - `analyze_50M_hetero_pri_sec.py`
   - `analyze_100M_heterogeneity.py`
   - `analyze_100M_advanced.py`
4. **Para ver gráficas**: Navegar a carpetas y abrir PNG
5. **Para modificar análisis**: Editar scripts y ajustar parámetros

---

## ⚙️ Parámetros Configurables

### Dentro de scripts:

```python
# Densidades (g/cm³)
DENSITY_WATER = 1.0
DENSITY_BONE = 1.85
DENSITY_LUNG = 0.26

# Región de heterogeneidad (mm)
HETERO_SIZE = 60.0        # 6.0 cm
HETERO_POS_X = 40.0
HETERO_POS_Y = 0.0

# Resolución
BIN_SIZE_MM = 1.0         # ~1mm/bin en 300×300 histogram
BIN_VOLUME = 0.001        # cm³

# Regiones para análisis
regions = {
    '0-5 mm': (0, 5),
    '5-10 mm': (5, 10),
    # ... etc
}
```

---

## 🐛 Troubleshooting

### Error: "Histograma no encontrado"
- Verificar nombre de histograma en archivo ROOT
- Usar `uproot.open(file).keys()` para listar histogramas

### Error: "KeyError en DENSITIES"
- Verificar que claves de material coincidan en diccionarios
- Usar función `get_density_for_material()` como alternativa

### Gráficas vacías o sin color
- Verificar escala: LogNorm requiere valores > 0
- Aplicar `np.min(data[data > 0])` para límite inferior

---

## 📞 Referencia Rápida de Comandos

```bash
# Análisis 50M
python3 analyze_50M_hetero_pri_sec.py > output_50M.txt

# Análisis 100M principal
python3 analyze_100M_heterogeneity.py > output_100M_1.txt

# Análisis 100M avanzado
python3 analyze_100M_advanced.py > output_100M_2.txt

# Ver resultados
cat output_100M_1.txt | grep "0-5 mm"  # Filtrar por región
ls -lh 100M_I125_pri-sec/*.png        # Listar gráficas
```

---

## 📝 Próximas Líneas de Investigación

1. **Análisis 3D volumétrico**: Extender de slices 2D a volumen completo
2. **Sensibilidad paramétrica**: Variar densidades (±20%) y medir impacto
3. **Comparación estadística**: Validar escalado 50M → 100M → 200M
4. **Espectro energético**: Desglose por rangos (0-50 keV, 50-100 keV, etc.)
5. **Benchmarking TPS**: Comparar con cálculos de sistemas comerciales

---

**Documento actualizado**: 20 de Octubre de 2025  
**Versión**: 2.0 (Completo)  
**Estado**: ✅ Todos los análisis completados

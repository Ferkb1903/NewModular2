# 📊 ANÁLISIS COMPLETO: HETEROGENEIDAD EN BRAQUITERAPIA I125 (100M)

## Resumen Ejecutivo

Análisis comprehensivo del impacto de heterogeneidades (Bone y Lung) en distribuciones de dosis comparadas con casos homogéneos en simulación de I125 con 100M eventos.

---

## 1️⃣ DESCUBRIMIENTOS PRINCIPALES

### Bone Heterogeneidad
- **Impacto en energía**: -6.50% (5.955e+09 MeV → 5.568e+09 MeV)
- **Impacto en dosis total**: -6.50% (5.157e+02 Gy → 4.822e+02 Gy)
- **Distribución regional**: Altamente concentrada en zona de heterogeneidad
  - 0-5 mm: 93% de dosis (energía sin cambio significativo: 0.93)
  - 5-10 mm: Caída dramática a 3.63% de energía de homo
  - >10 mm: Prácticamente nula la energía

### Lung Heterogeneidad
- **Impacto en energía**: -0.23% (5.541e+09 MeV → 5.528e+09 MeV)
- **Impacto en dosis total**: -0.23% (3.414e+03 Gy → 3.406e+03 Gy)
- **Distribución regional**: Muy similar a homo, cambio mínimo
  - 0-5 mm: Ratio 0.999 (casi idéntico)
  - Toda la región mantiene ~93-99% del valor homo

---

## 2️⃣ ANÁLISIS POR REGIONES (Anillo Circular desde Centro)

### BONE
```
Región      Homo Energy    Hetero Energy   Ratio E    Homo Dose       Hetero Dose     Ratio D
0-5 mm      5.727e+09      5.328e+09       0.9304     4.959e+02       4.614e+02       0.9304
5-10 mm     1.673e+08      6.071e+07       0.3629     1.449e+01       5.258e+00       0.3629
10-30 mm    6.000e+07      1.486e+08       2.4768     5.196e+00       1.287e+01       2.4768
30-50 mm    7.641e+05      1.934e+07       25.3079    6.617e-02       1.675e+00       25.3079
50-150 mm   2.053e+04      1.109e+07       540.3204   1.777e-03       9.603e-01       540.3204
```

**Interpretación Bone:**
- Heterogeneidad acumula energía/dosis en zona 10-30mm (2.5x más)
- Reducción aguda en 5-10mm (solo 36% de homo)
- Efecto de BLINDAJE: hueso más denso reduce transmisión

### LUNG  
```
Región      Homo Energy    Hetero Energy   Ratio E    Homo Dose       Hetero Dose     Ratio D
0-5 mm      5.335e+09      5.328e+09       0.9987     3.287e+03       3.283e+03       0.9987
5-10 mm     6.574e+07      6.112e+07       0.9296     4.051e+01       3.766e+01       0.9296
10-30 mm    9.658e+07      9.385e+07       0.9717     5.951e+01       5.782e+01       0.9717
30-50 mm    2.736e+07      2.761e+07       1.0090     1.686e+01       1.701e+01       1.0090
50-150 mm   1.632e+07      1.736e+07       1.0641     1.005e+01       1.070e+01       1.0641
```

**Interpretación Lung:**
- Prácticamente SIN cambio (ratios ~0.99-1.06)
- Pulmón (ρ=0.26) es muy similar a agua (ρ=1.0)
- Menor impacto de heterogeneidad

---

## 3️⃣ ANÁLISIS MM-POR-MM (0-10mm, Incrementos de 2mm)

### BONE - Zona de Máximo Cambio
```
Rango (mm)   Homo Dosis    Hetero Dosis   Ratio D/H   Cambio %
0-2          4.711e+02     4.567e+02      0.9695      -3.05%
2-4          1.933e+01     3.384e+00      0.1750      -82.50% ⚠️ CAÍDA BRUSCA
4-6          1.080e+01     2.748e+00      0.2545      -74.55%
6-8          5.696e+00     2.047e+00      0.3593      -64.07%
8-10         3.440e+00     1.723e+00      0.5009      -49.91%
```

**Patrón**: 
- Primera zona (0-2mm): -3% (casi sin cambio)
- Zona 2-4mm: COLAPSO a 17.5% del valor homo
- Gradual recuperación: 25% → 36% → 50%

### LUNG - Zona Estable
```
Rango (mm)   Homo Dosis    Hetero Dosis   Ratio D/H   Cambio %
0-2          3.251e+03     3.250e+03      0.9996      -0.04%
2-4          2.618e+01     2.411e+01      0.9208      -7.92%
4-6          2.122e+01     1.961e+01      0.9243      -7.57%
6-8          1.575e+01     1.465e+01      0.9300      -7.00%
8-10         1.326e+01     1.239e+01      0.9340      -6.60%
```

**Patrón**: 
- Cambio consistente -0.04% a -7.92%
- Efecto SUAVE y gradual
- Diferencia fundamental respecto a Bone

---

## 4️⃣ INFLUENCIA DE DOSIS SECUNDARIA (HETERO)

### Bone_Hetero
- **Energía Total**: 5.568e+09 MeV
  - Primaria: 3.572e+09 MeV (64.2%)
  - Secundaria: 1.996e+09 MeV (35.8%)
- **Dosis Total**: 4.822e+02 Gy
  - Primaria: 3.093e+02 Gy (64.2%)
  - Secundaria: 1.728e+02 Gy (35.8%)

### Lung_Hetero
- **Energía Total**: 5.528e+09 MeV
  - Primaria: 3.533e+09 MeV (63.9%)
  - Secundaria: 1.995e+09 MeV (36.1%)
- **Dosis Total**: 3.406e+03 Gy
  - Primaria: 2.177e+03 Gy (63.9%)
  - Secundaria: 1.229e+03 Gy (36.1%)

**Conclusión**: Secundarias contribuyen ~35-36% de la dosis en ambos casos heterogéneos.

---

## 5️⃣ COMPARACIÓN VISUAL

### Mapas 2D
- **Homo vs Hetero**: Diferencia visual clara solo en Bone
- **Bone Hetero**: Mayor concentración central, caída más rápida
- **Lung Hetero**: Prácticamente idéntico a Homo

### Diferencias (Hetero - Homo)
- **Bone**: Diferencias positivas solo en región 10-30mm (blindaje)
- **Lung**: Diferencias mínimas, casi imperceptibles

### Ratios (Hetero / Homo)
- **Bone**: Rango 0.17 a 540 (cambio extremo según región)
- **Lung**: Rango 0.93 a 1.06 (variación mínima, <10%)

---

## 6️⃣ INTERPRETACIÓN FÍSICA

### Efecto Bone (Densidad 1.85 g/cm³)
1. **Zona 0-2mm**: Mínimo impacto (-3%) - es la región primaria
2. **Zona 2-4mm**: COLAPSO (-82%) - efecto de blindaje del hueso
3. **Zona 4-10mm**: Recuperación gradual - múltiples scattering

**Mecanismo**: El hueso denso actúa como blindaje para radiación primaria, reduciendo transmisión.

### Efecto Lung (Densidad 0.26 g/cm³)
1. **Uniformemente bajo**: -0.04% a -7.92%
2. **Muy similar a agua**: Pulmón ≈ Agua en términos de atenuación
3. **Sin efecto de blindaje**: Baja densidad permite transmisión normal

**Mecanismo**: La baja densidad del pulmón hace que sea transparente a la radiación primaria.

---

## 7️⃣ CONCLUSIONES CLAVE

1. **Heterogeneidad de Bone**: CRÍTICA en clínica
   - Reduce dosis efectiva en zona proximal
   - Genera "sombra" de radiación
   - Importante para TPS (Treatment Planning Systems)

2. **Heterogeneidad de Lung**: MÍNIMA IMPORTANCIA
   - Cambios <8% en toda región 0-10mm
   - Tratamiento puede aproximarse con agua homogénea

3. **Energía vs Densidad**:
   - Bone: Similar energía pero dosis baja (blindaje)
   - Lung: Similar energía y dosis (transparencia)

4. **Dosis Secundaria**:
   - Consistentemente ~35-36% en ambos materiales
   - Indica dependencia del espectro de I125 (no del medio)

---

## 📁 ARCHIVOS GENERADOS

### Análisis 1 - Mapas Homo vs Hetero
- `1_homo_vs_hetero_maps.png`

### Análisis 2 - Primarias vs Secundarias (Hetero)
- `2_primary_vs_secondary_hetero.png`

### Análisis 3 - Mapas de Diferencia
- `3_difference_maps.png`

### Análisis 4 - Perfiles Horizontales
- `4_horizontal_profiles.png`

---

## 🔬 RECOMENDACIONES PARA INVESTIGACIÓN

1. **Validación clínica**: Comparar con datos de pacientes reales
2. **Espectro energético**: Analizar energía promedio por región
3. **Correlación 3D**: Extender a análisis volumétrico completo
4. **TPS comparación**: Usar estos datos para validar sistemas comerciales
5. **Ajustes de densidad**: Probar diferentes valores de ρ para optimizar modelos

---

*Análisis completado: 2025-10-20*
*Dataset: I125 100M (Homo + Hetero)*
*Scripts: analyze_100M_heterogeneity.py, analyze_100M_advanced.py*

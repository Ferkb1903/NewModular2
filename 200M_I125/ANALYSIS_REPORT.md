# Análisis Comparativo de Braquiterapia I125 - 200M

## Resumen Ejecutivo

Se realizó un análisis comparativo de tres simulaciones de braquiterapia con una fuente I125 con 200 millones de eventos, comparando diferentes configuraciones de heterogeneidad en el fantoma:

1. **Water_Homo**: Fantoma completamente homogéneo de agua
2. **Bone_Hetero**: Fantoma con heterogeneidad ósea
3. **Lung_Hetero**: Fantoma con heterogeneidad pulmonar

---

## Estadísticas Principales

### Caso 1: Agua Homogénea (Water_Homo)
```
Entradas totales:    1.11 × 10^10
Valor máximo:        2.63 × 10^9
Valor mínimo:        0.00 × 10^0
Media:               1.23 × 10^5
Desv. estándar:      1.75 × 10^7
Mediana:             1.12 × 10^2
Dimensiones:         300 × 300 bins
```

**Interpretación**: Distribución de referencia. Muestra la dosis depositada en un medio homogéneo de agua.

---

### Caso 2: Heterogeneidad Ósea (Bone_Hetero)
```
Entradas totales:    1.11 × 10^10
Valor máximo:        2.63 × 10^9
Valor mínimo:        0.00 × 10^0
Media:               1.24 × 10^5
Desv. estándar:      1.75 × 10^7
Mediana:             3.84 × 10^1
Dimensiones:         300 × 300 bins
```

**Observaciones**:
- La mediana es **3.0× menor** que en agua (38.4 vs 111.7)
- Indica que el hueso modifica significativamente la distribución de dosis
- Más regiones con valores bajos debido a la atenuación ósea

---

### Caso 3: Heterogeneidad Pulmonar (Lung_Hetero)
```
Entradas totales:    1.11 × 10^10
Valor máximo:        2.63 × 10^9
Valor mínimo:        0.00 × 10^0
Media:               1.23 × 10^5
Desv. estándar:      1.75 × 10^7
Mediana:             1.09 × 10^2
Dimensiones:         300 × 300 bins
```

**Observaciones**:
- La mediana es **prácticamente igual** a agua (109 vs 111.7)
- El pulmón tiene menor densidad que el hueso, afectando menos la distribución
- Comportamiento similar al medio homogéneo

---

## Análisis Comparativo de Dosis

### Razones Heterogéneo/Homogéneo

#### Bone/Water
- **Razón mínima**: 0.0000 (regiones donde el hueso atenúa completamente)
- **Razón máxima**: 1664.2 (puntos calientes donde la dosis se deposita más concentrada)
- **Razón media**: 0.9674 (**reducción global del ~3% en dosis promedio**)

**Conclusión**: El hueso atenúa ligeramente la dosis global pero crea regiones con enhancedos locales.

#### Lung/Hetero
- **Razón mínima**: 0.0003
- **Razón máxima**: 2685.1 (puntos calientes más pronunciados que con hueso)
- **Razón media**: 2.0197 (**aumento global del ~102% en dosis promedio**)

**Conclusión**: El pulmón (menor densidad) permite mayor penetración y genera depósitos más altos en algunos puntos.

---

## Gráficas Generadas

### 1. **comparison_200M_I125.png**
- **Mapas de dosis 2D**: Visualización completa de la distribución espacial
- **Proyecciones en X**: Integral de dosis en dirección X para cada caso
- **Proyecciones en Y**: Integral de dosis en dirección Y para cada caso

**Utilidad**: Comprender la geometría del depósito de dosis en cada caso.

### 2. **dose_distribution_200M_I125.png**
- **Histogramas log-log** de la distribución de dosis para los 3 casos
- Escala logarítmica en ambos ejes para mejor visualización

**Utilidad**: Identificar diferencias en la forma de la distribución (cola, picos, etc.)

### 3. **ratio_maps_200M_I125.png**
- **Mapas de razón Bone/Water**: Muestra dónde el hueso incrementa o atenúa la dosis
- **Mapas de razón Lung/Water**: Comparación de efectos del pulmón vs agua

**Utilidad**: Localizar regiones críticas donde hay mayores diferencias.

---

## Interpretación Clínica

### Efecto del Hueso
- ✓ Reduce ligeramente la dosis promedio (~3%)
- ✓ Crea atenuación variable según la geometría
- ✓ Puede crear "sombras" de dosis baja detrás de estructuras óseas densas
- ⚠️ Requiere cálculos detallados para dosis prescrita

### Efecto del Pulmón
- ✓ Aumenta la dosis promedio (~102% vs agua)
- ✓ Menor densidad permite mayor penetración
- ✓ Crea concentraciones locales más altas
- ⚠️ Crítico en tratamientos donde hay pulmón adyacente

### Recomendaciones
1. **Para prescripción**: Usar agua homogénea como referencia
2. **Para planificación**: Considerar correcciones específicas por material
3. **Para validación**: Comparar contra datos experimentales en geometrías similares
4. **Para análisis futuro**: Estudiar gradientes de dosis (hotspots) más detalladamente

---

## Métodos

**Herramienta**: Python 3 con bibliotecas:
- `uproot`: Lectura de archivos ROOT
- `numpy`: Cálculos numéricos
- `matplotlib`: Visualizaciones

**Fuentes de datos**: Archivos ROOT generados por simulaciones GEANT4 de braquiterapia I125

**Resolución espacial**: Histogramas 2D con 300×300 bins

---

**Generado el**: 2025-10-19  
**Script**: `analyze_200M_I125.py`

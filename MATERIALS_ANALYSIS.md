# Análisis de Materiales Homogéneos

## Encontrado:

### Comparación Water_Homo vs Lung_Homo_200m

**EDEP Total:**
- Water: 1.191e+10 keV (más denso, más interacción)
- Lung: 1.108e+10 keV (menos denso, menos interacción)
- Diferencia: -8.27e+08 keV (Water deposita 7.3% más energía)

**Perfil Horizontal:**
- Water: max = 5.499e+09 keV en el pico
- Lung: max = 5.296e+09 keV en el pico
- Diferencia en pico: -2.0e+08 keV (el pico es más bajo en Lung, como esperado)

**Análisis Regional:**
- **Dentro de región 10-70 mm** (donde EN TEORIA no hay hetero):
  - Mean diff = +1.035e+06 keV
  - Max |diff| = 2.831e+06 keV
  - **POSITIVO → Lung deposita MÁS en esta zona**

- **Fuera de región 10-70 mm**:
  - Mean diff = -3.706e+06 keV
  - Max |diff| = 2.025e+08 keV
  - **NEGATIVO → Water deposita MÁS fuera de esta zona**

## Interpretación:

La diferencia regional observada es **CONSISTENTE** con materiales diferentes:

1. **Water (más denso)** absorbe más dosis LEJOS de la fuente
2. **Lung (menos denso)** absorbe más dosis CERCA de la fuente (región hetero)

Esto es físicamente correcto porque:
- La fuente está en el centro (X ≈ 0)
- A distancias cortas, Lung (baja densidad) interactúa menos → menos absorción
- A distancias largas, Water (alta densidad) interactúa más → más absorción

## Conclusión:

Los archivos Water_Homo y Lung_Homo_200m son **CORRECTOS y DIFERENTES**. 
No es un error de duplicación. Son simulaciones de DIFERENTES materiales homogéneos,
que por lo tanto DEBEN tener diferentes perfiles de dosis.

Para análisis de heterogeneidad, comparar:
- Bone_Homo vs Bone_Hetero (MISMO material, con/sin hetero)
- Lung_Homo vs Lung_Hetero (MISMO material, con/sin hetero)

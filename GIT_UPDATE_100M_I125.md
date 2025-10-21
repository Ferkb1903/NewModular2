# Actualización Git - Campaña I-125 (100M eventos)

## Contexto y objetivos
- Se incorporó la nueva campaña `100M_I125_pri-sec/` con simulaciones separadas en agua, pulmón (ICRP/MIRD) y hueso, incluyendo los ROOTs de energía depositada para totales, primarios y secundarios.
- El objetivo principal fue validar la separación primaria/secundaria en un conjunto de 100M eventos y generar visualizaciones comparativas entre materiales homogéneos y heterogéneos.
- Todos los scripts nuevos leen directamente desde la carpeta `100M_I125_pri-sec/` y producen salidas en la misma ruta para mantener la trazabilidad.

## Scripts añadidos
- `analyze_100M_hollow_lung.py`: matriz 3×2 con mapas de dosis (log) y ratios respecto a agua homogénea para pulmones ICRP/MIRD y hueso.
- `analyze_primary_secondary_regions.py`: cálculo zonal (fuente, heterogeneidad, periferia) diferenciando primarios y secundarios; exporta CSV y gráfico.
- `analyze_secondary_distribution.py`: histogramas y estadísticas de la contribución secundaria, con control de escala log.
- `compare_lego_split.py` y `compare_lego_split_ir192.py`: gráficas tipo lego para comparar primario/ secundario (I-125 e Ir-192) con opción de escala log en secundarios.
- `compare_primary_secondary_lego.py` y `compare_secondary_lego.py`: comparativas concentradas en la separación primaria/secundaria y entre casos heterogéneos.
- `compare_secondary_maps.py`: diferencia y cociente de mapas secundarios (log) para detectar excesos o déficits por material.
- `plot_hetero_difference.py`: diferencias heterogeneidad vs agua con máscara de 2 mm centrada y heterogeneidad anclada en (40 mm, 0 mm).
- `plot_homo_analysis.py`, `plot_homo_analysis_water_vs_bone.py`, `plot_homo_primary_secondary.py`: paneles homogéneos 3×3/2×3/2×4 para comparar dosis total vs primaria y material.
- `plot_ratio_profiles(NO_BORRAR).py`: perfiles horizontales con ratios (agua como referencia) preservando todos los bins originales.
- `visualize_source_geometry.py`: auxiliar para recordar dimensiones TG-186 y superponer geometría de la fuente en los mapas.

## Archivos de datos y salidas
- Nuevos ROOTs por caso (`brachytherapy_*.root`, `brachytherapy_eDepPrimary_*`, `brachytherapy_eDepSecondary_*`).
- PNGs generados automáticamente (`dose_maps_sectional_3x2.png`, `homo_analysis_3x3.png`, `hetero_difference_from_water.png`, etc.).
- `regional_analysis_primary_secondary.csv` con las métricas tabulares usadas en los reportes.

## Modificación relevante
- `plot_dose_sectional.py` ahora apunta a la campaña de 100M, crea un panel 3×2, diferencia pulmones ICRP/MIRD homogéneos y heterogéneos, y actualiza la conversión a Gy usando el espesor de 0.125 mm. La visualización trabaja en escala log y guarda `dose_maps_sectional_3x2.png` dentro de la carpeta de campaña.

## Validaciones realizadas
- Verificación manual de que todos los histogramas (`h20`) existen; se añaden fallbacks y mensajes claros en caso de falta.
- Revisiones de máximos de dosis (primaria y total) para cada caso; se imprime en consola en los scripts principales.
- Confirmación visual de que la heterogeneidad permanece centrada en (40 mm, 0 mm) y que la máscara de 2 mm elimina el voxel central en los mapas de diferencia.

## Próximos pasos sugeridos
1. Correr `analyze_primary_secondary_regions.py` para obtener promedios ponderados de dosis y validar el CSV con literatura TG-186.
2. Repetir la misma estructura para campañas de 200M eventos y comparar la estabilidad estadística.
3. Actualizar `GIT_UPDATE_SUMMARY.md` cuando se cierre la fase Ir-192, integrando hallazgos clave con capturas representativas.

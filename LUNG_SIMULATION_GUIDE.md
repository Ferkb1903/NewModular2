# 🚀 GUÍA DE EJECUCIÓN: SIMULACIONES CON PULMÓN MIRD

## 📋 Resumen

Esta guía explica cómo ejecutar simulaciones con el nuevo material **G4_LUNG_MIRD** (pulmón inflado, ρ=0.2958 g/cm³).

---

## 🔧 PASO 1: Compilar el Código Actualizado

```bash
cd /home/fer/fer/newbrachy/build

# Limpiar compilación anterior (opcional pero recomendado)
make clean

# Recompilar con CMake
cmake ..
make -j4

# Verificar que compiló sin errores
echo $?  # Debe retornar 0
```

### Verificación de Compilación

Si todo está bien, deberías ver al final:
```
[100%] Built target Brachy
```

---

## ✅ PASO 2: Verificar Material Definido

```bash
cd /home/fer/fer/newbrachy/build

# Ejecutar Brachy en modo interactivo
./Brachy

# Deberías ver en la salida:
# === Custom Materials Defined ===
# G4_LUNG_MIRD: density = 0.2958 g/cm3 (inflated lung with air)
#   Note: This is different from G4_LUNG_ICRP (1.05 g/cm3, deflated)
# ================================

# Salir
exit
```

---

## 🎯 PASO 3: Ejecutar Simulaciones

### Opción A: Simulación 50M (Test Rápido)

```bash
cd /home/fer/fer/newbrachy/build

# Ejecutar en background
nohup ./Brachy ../I125_Lung_MIRD_50M.mac > lung_mird_50M.log 2>&1 &

# Ver progreso
tail -f lung_mird_50M.log

# Verificar que está corriendo
ps aux | grep Brachy
```

**Tiempo estimado**: 30-60 minutos (dependiendo del hardware)

### Opción B: Simulación 100M (Producción)

```bash
cd /home/fer/fer/newbrachy/build

# Ejecutar en background
nohup ./Brachy ../I125_Lung_MIRD_100M.mac > lung_mird_100M.log 2>&1 &

# Ver progreso
tail -f lung_mird_100M.log

# Verificar que está corriendo
ps aux | grep Brachy
```

**Tiempo estimado**: 1-2 horas

---

## 📊 PASO 4: Monitorear Simulación

### Verificar Progreso

```bash
# Ver últimas líneas del log
tail -n 50 lung_mird_50M.log

# Buscar errores
grep -i "error\|warning" lung_mird_50M.log

# Verificar archivo ROOT generado
ls -lh brachytherapy*.root
```

### Señales de Simulación Exitosa

✅ Log muestra: `Run terminated.`  
✅ Archivo `.root` generado con tamaño > 100 MB  
✅ Sin mensajes de error críticos  

---

## 🔬 PASO 5: Analizar Resultados

### Preparar Datos

```bash
cd /home/fer/fer/newbrachy

# Crear carpeta para resultados MIRD
mkdir -p 50M_LUNG_MIRD
mkdir -p 100M_LUNG_MIRD

# Mover archivos ROOT a carpeta correspondiente
mv build/brachytherapy*.root 50M_LUNG_MIRD/
# o
mv build/brachytherapy*.root 100M_LUNG_MIRD/
```

### Ejecutar Análisis (Ejemplo para 50M)

```bash
# Crear script de análisis adaptado
cat > analyze_50M_lung_mird.py << 'EOF'
#!/usr/bin/env python3
import uproot
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = "/home/fer/fer/newbrachy/50M_LUNG_MIRD"
DENSITY_WATER = 1.0
DENSITY_LUNG_MIRD = 0.2958  # ← DENSIDAD CORRECTA

# ... [resto del código similar a analyze_50M_hetero_pri_sec.py]
EOF

python3 analyze_50M_lung_mird.py
```

---

## 📈 PASO 6: Comparar con Resultados Anteriores

### Comparación Esperada

| Dataset | Material | Densidad | Energía Total | Dosis Total | Ratio |
|---------|----------|----------|---------------|-------------|-------|
| Anterior | LUNG_ICRP | 1.05 g/cm³ | 2.764e+09 MeV | ~421 Gy | 0.95× |
| **Nuevo** | **LUNG_MIRD** | **0.2958 g/cm³** | **2.764e+09 MeV** | **~1500 Gy** | **~3.4×** |

**Explicación física**: Misma energía depositada, pero menor masa → mayor dosis.

---

## 🎨 PASO 7: Generar Visualizaciones

### Script de Visualización Completo

```bash
# Actualizar scripts con densidad MIRD
sed -i 's/DENSITY_LUNG = 1.05/DENSITY_LUNG = 0.2958/' analyze_*.py
sed -i 's/DENSITY_LUNG = 0.26/DENSITY_LUNG = 0.2958/' plot_*.py

# Ejecutar análisis completo
python3 analyze_100M_heterogeneity.py
python3 analyze_100M_advanced.py
```

### Gráficas Esperadas

1. **1_homo_vs_hetero_maps.png**: Comparación Water vs LUNG_MIRD
2. **2_primary_vs_secondary_hetero.png**: Primarias/Secundarias en LUNG_MIRD
3. **3_difference_maps.png**: Diferencias LUNG_MIRD - Water
4. **4_horizontal_profiles.png**: Perfiles de dosis

---

## 🔍 PASO 8: Validación de Resultados

### Checklist de Validación

| Verificación | Esperado | Método |
|--------------|----------|--------|
| ✅ Energía total | ~2.76e+09 MeV | Suma de todos los bins |
| ✅ Dosis total | ~1400-1600 Gy | Conversión con ρ=0.2958 |
| ✅ Concentración 0-2mm | >95% | Análisis regional |
| ✅ Ratio vs Water | ~3.4× | Comparación directa |
| ✅ Distribución suave | Sin picos anómalos | Inspección visual |

### Comandos de Verificación

```bash
# Verificar energía total
python3 -c "
import uproot
import numpy as np
file = uproot.open('50M_LUNG_MIRD/brachytherapy_hetero_lung_mird.root')
hist = file['h20;1']
energy_total = np.sum(hist.values())
print(f'Energía total: {energy_total:.3e} MeV')
"

# Verificar dosis total
python3 -c "
import uproot
import numpy as np
file = uproot.open('50M_LUNG_MIRD/brachytherapy_hetero_lung_mird.root')
hist = file['h20;1']
edep = hist.values()
dose = edep * 1.602e-10 / (0.001 * 0.2958)  # ρ=0.2958
print(f'Dosis total: {np.sum(dose):.3e} Gy')
"
```

---

## 🚨 TROUBLESHOOTING

### Error: "Material G4_LUNG_MIRD not found"

**Causa**: Código no compilado o material no definido.

**Solución**:
```bash
cd /home/fer/fer/newbrachy/build
make clean
cmake ..
make -j4
```

### Error: Compilación falla con "DefineMaterials undefined"

**Causa**: Header no actualizado.

**Solución**:
```bash
# Verificar que BrachyDetectorConstruction.hh tiene:
grep "DefineMaterials" /home/fer/fer/newbrachy/include/BrachyDetectorConstruction.hh

# Si no está, añadir manualmente o re-aplicar cambios
```

### Simulación muy lenta

**Causa**: Hardware limitado o demasiados eventos.

**Solución**:
```bash
# Reducir número de eventos temporalmente
sed -i 's/beamOn 100000000/beamOn 10000000/' I125_Lung_MIRD_50M.mac

# O ejecutar en cluster si está disponible
```

### Dosis inesperadamente baja

**Causa**: Scripts de análisis usando densidad incorrecta.

**Solución**:
```bash
# Verificar densidad en scripts
grep "DENSITY_LUNG" analyze_*.py

# Debe ser 0.2958, no 1.05 ni 0.26
```

---

## 📊 COMPARACIÓN DE SIMULACIONES

### Plan de Comparación Completo

```bash
# 1. Lung ICRP (denso, ρ=1.05) - YA HECHO
#    Resultados en: 50M_I125/ o 100M_I125_pri-sec/

# 2. Lung MIRD (inflado, ρ=0.2958) - NUEVO
#    Ejecutar: I125_Lung_MIRD_50M.mac

# 3. Comparación lado a lado
python3 compare_lung_materials.py
```

### Script de Comparación

```python
#!/usr/bin/env python3
"""
Comparación: LUNG_ICRP vs LUNG_MIRD
"""
import uproot
import numpy as np
import matplotlib.pyplot as plt

# Cargar datos
file_icrp = uproot.open('50M_I125/brachytherapy_lung_hetero50m.root')
file_mird = uproot.open('50M_LUNG_MIRD/brachytherapy_lung_mird.root')

edep_icrp = file_icrp['h20;1'].values()
edep_mird = file_mird['h20;1'].values()

# Conversión a dosis
dose_icrp = edep_icrp * 1.602e-10 / (0.001 * 1.05)
dose_mird = edep_mird * 1.602e-10 / (0.001 * 0.2958)

# Comparar
print(f"LUNG_ICRP: {np.sum(dose_icrp):.2e} Gy")
print(f"LUNG_MIRD: {np.sum(dose_mird):.2e} Gy")
print(f"Ratio: {np.sum(dose_mird)/np.sum(dose_icrp):.2f}×")
```

---

## 🎯 PRÓXIMOS PASOS

1. ✅ **Compilar** código actualizado
2. ⏳ **Ejecutar** simulación 50M (test)
3. ⏳ **Verificar** resultados preliminares
4. ⏳ **Ejecutar** simulación 100M (producción)
5. ⏳ **Analizar** y comparar con ICRP
6. ⏳ **Documentar** hallazgos

---

## 📚 ARCHIVOS CLAVE

```
/home/fer/fer/newbrachy/
├── LUNG_MATERIALS_GUIDE.md          ← Guía de materiales
├── LUNG_SIMULATION_GUIDE.md         ← Esta guía
├── I125_Lung_MIRD_50M.mac           ← Macro 50M eventos
├── I125_Lung_MIRD_100M.mac          ← Macro 100M eventos
├── src/BrachyDetectorConstruction.cc ← Definición de materiales
├── include/BrachyDetectorConstruction.hh ← Header
└── build/
    ├── Brachy                        ← Ejecutable
    └── *.root                        ← Resultados

50M_LUNG_MIRD/                       ← Carpeta resultados 50M
100M_LUNG_MIRD/                      ← Carpeta resultados 100M
```

---

## 💡 CONSEJOS FINALES

1. **Backup datos**: Hacer copia antes de análisis
2. **Verificar densidad**: Siempre comprobar ρ=0.2958 en scripts
3. **Comparar con literatura**: Verificar si resultados son físicamente razonables
4. **Documentar diferencias**: Anotar cambios vs LUNG_ICRP
5. **Validar estadísticas**: >50M eventos para buena estadística

---

**Guía creada**: 20 de Octubre de 2025  
**Estado**: ✅ Lista para ejecutar  
**Material**: G4_LUNG_MIRD (ρ=0.2958 g/cm³)

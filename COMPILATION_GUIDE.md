# Instrucciones de Compilación e Ejecución

## Paso 1: Compilar el Código Actualizado

```bash
cd /home/fer/fer/newbrachy/build
cmake ..
make -j$(nproc)
```

**Salida esperada:**
```
Scanning dependencies of target Brachy
[ 95%] Building CXX object CMakeFiles/Brachy.dir/src/BrachyMaterialsLib.cc.o
[ 96%] Building CXX object CMakeFiles/Brachy.dir/src/BrachyDetectorConstruction.cc.o
[100%] Linking CXX executable Brachy
[100%] Built target Brachy
```

Si hay errores de compilación, verifica:
- Geant4 está correctamente instalado: `which geant4-config`
- Las rutas de include están correctas: `echo $GEANT4_INCLUDE_PATH`
- CMake versión ≥ 3.16: `cmake --version`

## Paso 2: Verificar Instalación

```bash
cd /home/fer/fer/newbrachy/build
./Brachy -h
```

Debe mostrar opciones de ejecución de Brachy.

## Paso 3: Ejecutar Simulaciones

### Opción A: Con interfaz interactiva

```bash
cd /home/fer/fer/newbrachy/build
./Brachy
```

Luego en el prompt interactivo:

```
Idle> /brachy/geometry/enableHeterogeneity true
Idle> /brachy/geometry/setHeterogeneityMaterial MIRD_lung
Idle> /brachy/geometry/setHeterogeneitySize 6 6 6 cm
Idle> /brachy/geometry/setHeterogeneityPosition 4 0 0 cm
Idle> /brachy/source/selectSource I125
Idle> /run/initialize
Idle> /run/beamOn 1000000
Idle> exit
```

### Opción B: Con macros proporcionados

Para simular con **MIRD lung (0.2958 g/cm³)**:
```bash
cd /home/fer/fer/newbrachy/build
./Brachy I125_MIRD_Lung.mac
```

Para simular con **ICRP lung (1.05 g/cm³)**:
```bash
cd /home/fer/fer/newbrachy/build
./Brachy I125_ICRP_Lung.mac
```

## Paso 4: Monitoreo Durante la Simulación

La simulación mostrará en consola:

```
✓ MIRD Lung material created (ρ = 0.2958 g/cm³, 16 elementos)
✓ ICRP Lung material created (ρ = 1.05 g/cm³, 12 elementos)
✓ Bone material created (ρ = 1.85 g/cm³)
✓ Water material created (ρ = 1.0 g/cm³)

...

✓ Using MIRD lung (ρ = 0.2958 g/cm³, 16 elementos)
Initializing geometry...
Simulating 1000000 events...
Saving results to: 100M_I125_MIRD_Lung.root
```

## Paso 5: Archivos de Salida

Los archivos ROOT generados:
- `100M_I125_MIRD_Lung.root` - Simulación con MIRD lung
- `100M_I125_ICRP_Lung.root` - Simulación con ICRP lung

## Análisis Post-Simulación

Usar los scripts Python existentes:

```bash
cd /home/fer/fer/newbrachy

# Comparar resultados MIRD vs ICRP
python3 analyze_mird_vs_icrp_lung.py

# Analizar impacto de heterogeneidad
python3 analyze_100M_heterogeneity.py

# Análisis avanzado
python3 analyze_100M_advanced.py
```

## Troubleshooting

### Error: "cannot find -lGeant4"
```bash
# Agregar librería Geant4 al PATH
source /path/to/geant4.11.0/bin/geant4.sh
```

### Error: "G4SystemOfUnits.hh: No such file"
```bash
# Verificar CMakeLists.txt incluye Geant4
# Regenerar build
rm -rf build/*
mkdir -p build
cd build
cmake ..
make
```

### Error: "No materials available"
- Asegurar que BrachyMaterialsLib.cc se compiló correctamente
- Verificar output de make contiene: "Building CXX object CMakeFiles/Brachy.dir/src/BrachyMaterialsLib.cc.o"

### Simulación muy lenta
- Reducir número de eventos (pruebas: 10000, producción: 1000000)
- Aumentar threads: `make -j8`

## Materiales Disponibles

Los siguientes materiales están disponibles para `setHeterogeneityMaterial`:

| Nombre | Densidad | Fuente | Elementos |
|--------|----------|--------|-----------|
| `MIRD_lung` | 0.2958 g/cm³ | Librería personalizada | 16 |
| `ICRP_lung` | 1.05 g/cm³ | Librería personalizada | 12 |
| `Bone` | 1.85 g/cm³ | Librería personalizada | 4 |
| `Water` | 1.0 g/cm³ | NIST | - |
| `G4_BONE_COMPACT_ICRU` | Estándar ICRU | NIST | - |
| Otros materiales NIST | Estándar | NIST | - |

## Documentación de Referencia

Ver también:
- `MATERIALS_IMPLEMENTATION_NOTES.md` - Detalles técnicos de implementación
- `material_config.py` - Configuraciones de Python para análisis
- `analyze_mird_vs_icrp_lung.py` - Script de comparación MIRD vs ICRP

# Quick Start - Cluster Deployment

**Para ejecutar en el cluster, sigue estos pasos:**

## 1. Clone del GitHub

```bash
# En tu máquina local
git clone https://github.com/Ferkb1903/NewModular2.git
cd NewModular2

# O descarga como ZIP desde: https://github.com/Ferkb1903/NewModular2/archive/refs/heads/main.zip
```

## 2. Transfer al Cluster

```bash
# Opción A: SCP
scp -r NewModular2/ user@cluster.edu:/scratch/user/

# Opción B: SFTP
sftp user@cluster.edu
put -r NewModular2 /scratch/user/

# Opción C: Direct git clone en el cluster
ssh user@cluster.edu
cd /scratch/user
git clone https://github.com/Ferkb1903/NewModular2.git
```

## 3. En el Cluster

```bash
# SSH al cluster
ssh user@cluster.edu
cd /scratch/user/NewModular2

# Cargar módulos
module load gcc/11.4.0
module load cmake/3.24.1
module load geant4/11.2.0

# Compilar
mkdir build && cd build
cmake ..
make -j 8

# Verificar
./Brachy --help
```

## 4. Ejecutar Simulación

### Opción A: Ejecución Directa (prueba rápida)

```bash
cd /scratch/user/NewModular2
./build/Brachy HomogeneousTest.mac
```

### Opción B: Job Submission (SLURM)

Crear archivo `run_brachy.slurm`:

```bash
#!/bin/bash
#SBATCH --job-name=brachy
#SBATCH --output=brachy_%j.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00

module load gcc/11.4.0
module load geant4/11.2.0
cd /scratch/$USER/NewModular2
export OMP_NUM_THREADS=8
./build/Brachy TG186SourceMacro.mac
```

Submitir:
```bash
sbatch run_brachy.slurm
```

## 5. Recuperar Resultados

```bash
# Listar resultados
ls -lh brachytherapy_*.root

# Copiar a máquina local (en tu PC)
scp user@cluster.edu:/scratch/user/NewModular2/brachytherapy_*.root ./results/

# O directamente desde local
rsync -avz user@cluster.edu:/scratch/user/NewModular2/brachytherapy_*.root ~/results/
```

## 6. Analizar Resultados (Local)

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Ejecutar análisis
python3 verify_primary_secondary.py
python3 analyze_hetero_50m.py
python3 horizontal_profile.py
```

## Parámetros de Simulación

### Variar número de eventos en macro

```bash
# Editar macro (ej: TG186SourceMacro.mac)
/run/beamOn 100000    # Cambiar número de eventos
```

### Variar materiales (heterogeneidad)

```bash
# En la macro
/brachy/det/setHeterogeneity 1    # Activar (default)
/brachy/det/setHeterogeneity 0    # Desactivar
```

### Cambiar región de heterogeneidad

Ver: `CLUSTER_GUIDE.md` sección "Geometry Configuration"

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| geant4-config no encontrado | `module load geant4/11.2.0` |
| CMake error con Geant4 | `export Geant4_DIR=/opt/geant4/11.2.0/lib/cmake/Geant4` |
| Out of memory | Aumentar `--mem` en SLURM o reducir events |
| Timeout | Aumentar `--time` en SLURM |
| Python uproot error | `pip install uproot numpy matplotlib` |

## Performance Típico

- **100K eventos**: 5-10 min (8 cores)
- **1M eventos**: 50-100 min (8 cores)
- **10M eventos**: 8-16 horas (8 cores)

Usa `--ntasks=1 --cpus-per-task=16` para más cores si disponible.

## Más Información

- **Instalación detallada**: Ver `INSTALL.md`
- **Guía completa cluster**: Ver `CLUSTER_GUIDE.md`
- **Documentación completa**: Ver `DOCUMENTATION.md`
- **GitHub**: https://github.com/Ferkb1903/NewModular2

---

**¡Listo para ejecutar!** 🚀

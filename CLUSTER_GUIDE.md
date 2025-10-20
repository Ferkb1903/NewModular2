# Cluster Execution Guide

Instructions for running Brachy simulations on HPC clusters.

## Supported Cluster Systems

This guide covers typical HPC clusters using:
- **Job Scheduler**: SLURM (most common), PBS, or SGE
- **Module System**: Environment Modules or Lmod
- **Compiler**: GCC with CMake

## Pre-Cluster Setup (Local Machine)

```bash
# 1. Prepare your code
git clone https://github.com/Ferkb1903/NewModular2.git
cd NewModular2

# 2. Test locally
./build/Brachy HomogeneousTest.mac

# 3. Prepare for transfer
tar czf brachy.tar.gz src/ include/ CMakeLists.txt *.mac requirements.txt .gitignore
```

## Cluster Setup

### Step 1: Transfer Files

```bash
# Using scp
scp brachy.tar.gz user@cluster.edu:/scratch/user/

# Or using rsync
rsync -avz --exclude='build' --exclude='*.root' --exclude='*.o' \
  . user@cluster.edu:/scratch/user/brachy/
```

### Step 2: SSH to Cluster

```bash
ssh user@cluster.edu
cd /scratch/user/brachy
tar xzf brachy.tar.gz
```

### Step 3: Check Available Modules

```bash
# List available modules
module avail

# Look for Geant4
module avail geant4

# Look for compilers
module avail compiler

# Look for CMake
module avail cmake

# Example output:
# geant4/11.2.0 (D)
# gcc/11.4.0
# cmake/3.24.1
```

### Step 4: Load Required Modules

```bash
# Typical setup for SLURM-based cluster
module load gcc/11.4.0
module load cmake/3.24.1
module load geant4/11.2.0

# Verify
which g++
which cmake
geant4-config --version
```

### Step 5: Compile on Cluster

```bash
# Create build directory
mkdir -p build
cd build

# Configure (using module-provided Geant4)
cmake ..

# Compile
make -j 8

# Verify
ls -la Brachy
./Brachy --help
```

## Job Submission

### SLURM Job Script Template

Create `submit_brachy.slurm`:

```bash
#!/bin/bash
#SBATCH --job-name=brachy_sim
#SBATCH --output=brachy_%j.log
#SBATCH --error=brachy_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --partition=cpu

# Load modules
module load gcc/11.4.0
module load geant4/11.2.0

# Set up environment
cd /scratch/$USER/brachy
export OMP_NUM_THREADS=8
export G4DATADIR=/opt/geant4/data

# Run simulation
echo "Starting simulation..."
date
./build/Brachy TG186SourceMacro.mac
echo "Simulation completed!"
date

# Copy results back
rsync -avz brachytherapy_*.root /home/$USER/results/
```

Submit with:
```bash
sbatch submit_brachy.slurm

# Monitor job
squeue -u $USER

# Check output
tail -f brachy_*.log
```

### PBS Job Script Template

Create `submit_brachy.pbs`:

```bash
#!/bin/bash
#PBS -N brachy_sim
#PBS -o brachy.log
#PBS -e brachy.err
#PBS -l nodes=1:ppn=8
#PBS -l mem=16gb
#PBS -l walltime=02:00:00

# Load modules
module load gcc/11.4.0
module load geant4/11.2.0

# Set up environment
cd $PBS_O_WORKDIR
export OMP_NUM_THREADS=8

# Run simulation
echo "Starting simulation..."
./build/Brachy TG186SourceMacro.mac
echo "Simulation completed!"

# Copy results
cp brachytherapy_*.root $HOME/results/
```

Submit with:
```bash
qsub submit_brachy.pbs
```

## Running Multiple Simulations

### Batch Script (Multiple Jobs)

Create `batch_submit.sh`:

```bash
#!/bin/bash

# Array of macros to run
MACROS=(
    "TG186SourceMacro.mac"
    "IodineSourceMacro.mac"
    "HomogeneousTest.mac"
    "HeterogeneousTest.mac"
)

# Submit each macro as separate job
for macro in "${MACROS[@]}"; do
    echo "Submitting $macro..."
    
    # Create temporary job script
    cat > temp_job.slurm << EOF
#!/bin/bash
#SBATCH --job-name=brachy_$macro
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G

module load gcc/11.4.0
module load geant4/11.2.0

cd /scratch/\$USER/brachy
./build/Brachy $macro
EOF
    
    sbatch temp_job.slurm
    sleep 2
done

rm temp_job.slurm
```

Run with:
```bash
chmod +x batch_submit.sh
./batch_submit.sh
```

### Parameter Sweep

For varying simulation parameters:

```bash
# Create macro variants
for events in 10000 50000 100000; do
    cat > sim_${events}events.mac << EOF
/run/numberOfThreads 8
/run/beamOn $events
EOF
    
    sbatch --job-name=brachy_$events submit_job.slurm sim_${events}events.mac
done
```

## Data Management

### Directory Structure

```
/scratch/$USER/brachy/
├── src/
├── include/
├── build/
├── Brachy (executable)
├── *.mac (macros)
└── results/
    ├── analysis/
    └── root_files/
```

### Efficient File Transfer

```bash
# Transfer only necessary files
rsync -avz --include='*.root' --exclude='*' \
  /scratch/$USER/brachy/brachytherapy_*.root \
  /home/$USER/results/

# Compress before transfer
tar czf brachy_results_$(date +%Y%m%d).tar.gz *.root
scp brachy_results_*.tar.gz user@local:/home/results/
```

## Performance Optimization

### Multi-threading

```bash
# In Geant4 macro
/run/numberOfThreads 8

# In job script
export OMP_NUM_THREADS=8
export G4DEBUG_TRACK_CHECK=0  # Disable debug checks for performance
```

### Memory Management

```bash
# For large simulations
#SBATCH --mem=32G  # Increase memory

# Check memory usage during run
srun ps aux | grep Brachy
```

### Time Limits

Estimate simulation time:
```bash
# Quick test to estimate
time ./build/Brachy HomogeneousTest.mac

# Scale for full simulation
# If 1000 events take 30 sec, 1M events take ~500 sec (8.3 min)
```

## Monitoring and Debugging

### Check Job Status

```bash
# SLURM
squeue -u $USER
sinfo
sacct -u $USER

# PBS
qstat
qstat -a

# Check specific job
scontrol show job <jobid>  # SLURM
qstat -f <jobid>          # PBS
```

### View Output

```bash
# Live monitoring
tail -f brachy_*.log

# Check for errors
grep -i error brachy_*.err

# Full output
less brachy_*.log
```

### Debug Compilation Issues

```bash
# Clean and rebuild with verbose output
cd build
rm -rf *
cmake .. -DCMAKE_VERBOSE_MAKEFILE=ON
make 2>&1 | tee build.log

# Check for warnings
grep -i warning build.log
```

## Retrieve Results

### Download from Cluster

```bash
# After simulation completes
exit  # Exit cluster SSH

# On local machine
rsync -avz user@cluster.edu:/scratch/user/brachy/brachytherapy_*.root ./results/

# Or use scp
scp user@cluster.edu:/scratch/user/brachy/results/*.root ./
```

### Analyze on Local Machine

```bash
# Transfer analysis scripts
scp cluster_scripts/*.py .

# Run locally
python3 analyze_hetero_50m.py

# Or continue on cluster (recommended for large datasets)
ssh cluster_edu
python3 /scratch/$USER/brachy/verify_primary_secondary.py
```

## Common Issues

### Module Dependencies

```bash
# Error: "geant4-config: command not found"
# Solution:
module load geant4/11.2.0

# Or manually set paths
export PATH=/opt/geant4/11.2.0/bin:$PATH
export LD_LIBRARY_PATH=/opt/geant4/11.2.0/lib:$LD_LIBRARY_PATH
```

### Compilation with Different Geant4 Version

```bash
# If default Geant4 is old, specify version
cmake .. -DGEANT4_DIR=/opt/geant4/11.2.0/lib/cmake/Geant4

# Or use environment variable
export Geant4_DIR=/opt/geant4/11.2.0/lib/cmake/Geant4
cmake ..
```

### Timeout Issues

```bash
# For longer simulations, increase walltime
#SBATCH --time=10:00:00  # 10 hours

# Estimate needed time
# 1M events typically takes 10-30 minutes depending on hardware
```

### Out of Memory

```bash
# Increase memory allocation
#SBATCH --mem=64G

# Or reduce scoring resolution in simulation
# Modify CMakeLists.txt or macro files
```

## Example: Complete Workflow

```bash
# On local machine
scp -r brachy/ user@cluster.edu:/scratch/user/

# On cluster
ssh user@cluster.edu
cd /scratch/user/brachy

# Compile
mkdir build && cd build && cmake .. && make -j8

# Create job script (see example above)
sbatch submit_brachy.slurm

# Monitor
squeue -u $USER

# Wait for completion...

# Check results
ls brachytherapy_*.root

# Retrieve to local
exit
rsync -avz user@cluster.edu:/scratch/user/brachy/brachytherapy_*.root ~/results/

# Analyze locally
python3 analyze_hetero_50m.py
```

## Performance Benchmarks

Typical simulation times (single core):
- **1,000 events**: ~1 minute
- **10,000 events**: ~10 minutes
- **100,000 events**: ~100 minutes (1.7 hours)
- **1,000,000 events**: ~16+ hours

With multi-threading (8 cores): roughly 4-6× speedup

## Tips for Efficiency

1. **Use multi-threading**: Set `/run/numberOfThreads 8` in macro
2. **Batch jobs**: Run multiple simulations simultaneously
3. **Optimize memory**: Use larger events per job to reduce overhead
4. **Monitor disk space**: `/scratch` often has quotas
5. **Archive results**: Compress old results to free space
6. **Parallelize post-processing**: Use cluster for analysis scripts too

---

**Last Updated**: October 19, 2025  
**Tested Clusters**: SLURM-based systems (AlmaLinux 8, CentOS 7)

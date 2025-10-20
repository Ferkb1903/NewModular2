# Installation Guide

Complete step-by-step installation instructions for the Brachy project.

## Prerequisites Check

```bash
# Check CMake
cmake --version  # Required: >= 3.16

# Check Compiler
g++ --version    # Required: GCC 5.0+

# Check Python
python3 --version  # Required: >= 3.8

# Check ROOT (optional but recommended)
root-config --version  # Optional, for analysis
```

## Step 1: Install Geant4

### Option A: Using Package Manager (Recommended for Most Systems)

#### CentOS/AlmaLinux/RHEL
```bash
# Install development tools
sudo yum groupinstall "Development Tools"
sudo yum install cmake3 qt-devel expat-devel

# Install Geant4
sudo yum install geant4 geant4-devel geant4-examples
```

#### Ubuntu/Debian
```bash
# Install development tools
sudo apt-get install build-essential cmake

# Install Geant4
sudo apt-get install geant4 libgeant4-dev geant4-examples
```

### Option B: From Source (If Needed)

```bash
# Download Geant4 (v11.2.0 recommended)
cd /tmp
wget https://gitlab.cern.ch/geant4/geant4/-/archive/v11.2.0/geant4-v11.2.0.tar.gz
tar xzf geant4-v11.2.0.tar.gz
cd geant4-v11.2.0

# Create build directory
mkdir build && cd build

# Configure with CMake
cmake .. \
  -DCMAKE_INSTALL_PREFIX=/opt/geant4/11.2.0 \
  -DCMAKE_BUILD_TYPE=Release \
  -DGEANT4_INSTALL_DATA=ON \
  -DGEANT4_USE_SYSTEM_EXPAT=ON

# Compile and install
make -j$(nproc)
sudo make install

# Setup environment (add to ~/.bashrc)
source /opt/geant4/11.2.0/bin/geant4.sh
```

### Verify Geant4 Installation

```bash
geant4-config --version
geant4-config --prefix
```

## Step 2: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/Ferkb1903/NewModular2.git
cd NewModular2

# Or, if using existing directory
cd /home/fer/fer/newbrachy
git status
```

## Step 3: Install Python Dependencies

```bash
# Option A: Install globally
pip install -r requirements.txt

# Option B: Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Verify Python Setup

```bash
python3 -c "import uproot; import numpy; import matplotlib; print('✓ All packages installed')"
```

## Step 4: Build the Project

```bash
# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake ..

# Build (parallel compilation for speed)
make -j8

# Verify build
ls -la Brachy
./Brachy --help
```

### Build Options

If you need specific configurations:

```bash
# Clean build
rm -rf build && mkdir build && cd build

# Configure with custom Geant4 path
cmake .. -DGEANT4_DIR=/opt/geant4/11.2.0

# Debug build (with symbols)
cmake .. -DCMAKE_BUILD_TYPE=Debug

# Release build (optimized)
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE="-O3"
```

## Step 5: Verify Installation

```bash
# Navigate to project root
cd /home/fer/fer/newbrachy

# Run a quick test
./build/Brachy HomogeneousTest.mac

# Check output
ls -la brachytherapy_*.root
```

Expected output:
```
3 ROOT files generated:
  brachytherapy_<timestamp>.root
  brachytherapy_eDepPrimary_<timestamp>.root
  brachytherapy_eDepSecondary_<timestamp>.root
```

## Step 6: Optional - Install ROOT (For Advanced Analysis)

```bash
# Install ROOT (CentOS/AlmaLinux)
sudo yum install root root-devel

# Or build from source
cd /tmp
git clone --depth 1 https://github.com/root-project/root.git
cd root
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/opt/root
make -j8
sudo make install
```

## Environment Setup

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Geant4
source /usr/lib64/cmake/Geant4/Geant4Config.cmake 2>/dev/null || \
source /opt/geant4/11.2.0/bin/geant4.sh 2>/dev/null

# Python virtual environment (if using venv)
# source /path/to/newbrachy/venv/bin/activate

# ROOT (if installed)
source /opt/root/bin/thisroot.sh 2>/dev/null || \
source $(root-config --prefix)/bin/thisroot.sh 2>/dev/null
```

Then reload:
```bash
source ~/.bashrc
```

## Troubleshooting Installation

### CMake can't find Geant4

```bash
# Option 1: Set Geant4_DIR explicitly
export Geant4_DIR=/opt/geant4/11.2.0/lib64/cmake/Geant4
cmake ..

# Option 2: Add geant4-config to PATH
export PATH=/opt/geant4/11.2.0/bin:$PATH
cmake ..

# Option 3: Use geant4.sh
source /opt/geant4/11.2.0/bin/geant4.sh
cmake ..
```

### Compilation Errors

```bash
# Check compiler version
g++ --version  # Need C++14 support (GCC 5.0+)

# Try explicit C++ standard
cmake .. -DCMAKE_CXX_STANDARD=14

# Check for missing libraries
ldd build/Brachy | grep "not found"
```

### Python Modules Not Found

```bash
# Verify Python installation
python3 -m pip list | grep -E "uproot|numpy|matplotlib"

# Reinstall requirements
pip install --upgrade -r requirements.txt

# For specific versions:
pip install uproot==5.19.1 numpy==1.23.0 matplotlib==3.7.0
```

### Missing Data Files

```bash
# Geant4 data files
export G4DATADIR=/opt/geant4/11.2.0/share/Geant4-11.2.0/data

# Or point to system installation
export G4DATADIR=/usr/share/Geant4

# Verify
ls $G4DATADIR/G4PII1.3
```

## Post-Installation

### Run Initial Test

```bash
cd /home/fer/fer/newbrachy

# Test 1: Quick homogeneous simulation
./build/Brachy HomogeneousTest.mac
echo "✓ Test 1 passed"

# Test 2: Primary/Secondary validation
./build/Brachy TestPrimarySecondary.mac
echo "✓ Test 2 passed"

# Test 3: Analysis script
python3 verify_primary_secondary.py
echo "✓ All tests passed!"
```

### Performance Tuning

For faster compilation on cluster:

```bash
# Multi-core compilation
export MAKEFLAGS="-j 16"  # or number of available cores
cd build && cmake .. && make

# Pre-compiled headers
cmake .. -DCMAKE_PCH_PROLOGUE="$(pwd)/include/precompiled.hh"
```

## Installation for Cluster

See [CLUSTER_GUIDE.md](CLUSTER_GUIDE.md) for cluster-specific setup.

Key differences:
- Module system (e.g., `module load geant4`)
- Different CMake paths
- MPI support for parallel jobs
- Job submission scripts

---

**Last Updated**: October 19, 2025  
**Tested On**: CentOS 7, AlmaLinux 8, Ubuntu 20.04  
**Geant4 Version**: 11.2.0

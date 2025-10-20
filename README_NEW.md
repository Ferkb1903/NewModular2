# Brachy: Primary/Secondary Dose Separation in Brachytherapy

**A Geant4-based simulation framework for calculating primary and secondary dose contributions in brachytherapy.**

## Overview

This project implements a modified version of the Geant4 brachytherapy example with the capability to separate primary and secondary dose contributions. It features:

- **Primary/Secondary Dose Separation**: Distinct tracking and scoring of direct and indirect radiation contributions
- **Multi-source Support**: TG186 (Ir-192), I-125, Flexi source, and Leipzig source configurations
- **Heterogeneity Support**: Material inhomogeneities (lung, bone) in the scoring region
- **Comprehensive Analysis**: 17+ Python analysis scripts for dose evaluation
- **ROOT-based Output**: Full ROOT file support with histograms and scoring meshes

## 🎯 Key Features

### Physics
- Livermore electromagnetic physics (emlivermore)
- Accurate secondary particle tracking
- Cascading lineage tracking for primary classification
- Energy deposition scoring at ~1×1×10 mm voxel resolution

### Dose Classification
- **Primary Dose**: Direct contributions from gamma rays and charged cascades
- **Secondary Dose**: Photons (bremsstrahlung, fluorescence), Compton electrons, and non-primary particles

### Geometry
- 150×150×5 mm scoring box with 300×300×1 voxel resolution
- Configurable heterogeneous regions (lung/bone)
- Support for multiple source types

## 📋 Requirements

### System Requirements
- **OS**: Linux (tested on CentOS/AlmaLinux)
- **Compiler**: GCC/Clang with C++14 support
- **CMake**: ≥ 3.16

### Dependencies
- **Geant4**: ≥ v11.0 (tested with v11.2.0)
- **ROOT**: ≥ 6.20 (optional, for ROOT file analysis)
- **Python**: ≥ 3.8 (for analysis scripts)

### Python Packages
```bash
uproot>=5.0.0
numpy>=1.20.0
matplotlib>=3.5.0
scipy>=1.7.0
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Ferkb1903/NewModular2.git
cd NewModular2
```

### 2. Install Geant4

If not already installed:

```bash
# Option A: Using package manager (CentOS/AlmaLinux)
sudo yum install geant4 geant4-devel

# Option B: From source
cd /path/to/geant4/sources
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/opt/geant4
make -j8 && sudo make install
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Build the Project

```bash
mkdir build
cd build
cmake ..
make -j8
```

The executable `Brachy` will be created in the `build/` directory.

### 5. Verify Installation

```bash
./build/Brachy --help
# Or test with a macro:
./build/Brachy TestPrimarySecondary.mac
```

## 📖 Usage

### Basic Execution

```bash
cd /home/fer/fer/newbrachy
./build/Brachy macro_filename.mac
```

### Available Macros

| Macro | Purpose |
|-------|---------|
| `TG186SourceMacro.mac` | TG186 Ir-192 source (homogeneous) |
| `IodineSourceMacro.mac` | I-125 decay source |
| `HomogeneousTest.mac` | Quick test in water |
| `HeterogeneousTest.mac` | Test with bone heterogeneity |
| `TestPrimarySecondary.mac` | Validate primary/secondary separation |
| `I125_Decay_HomoVsHetero.mac` | Compare homo vs hetero |

### Output Files

Each simulation generates:
- `brachytherapy_<timestamp>.root` - Total dose (histogram h20)
- `brachytherapy_eDepPrimary_<timestamp>.root` - Primary dose (h2_eDepPrimary)
- `brachytherapy_eDepSecondary_<timestamp>.root` - Secondary dose (h2_eDepSecondary)

## 🔬 Analysis Scripts

### Quick Start
```bash
# Analyze primary/secondary separation
python3 verify_primary_secondary.py

# Compare homogeneous vs heterogeneous
python3 analyze_hetero_50m.py

# Extract dose profiles
python3 horizontal_profile.py

# Study symmetry
python3 analyze_symmetry.py
```

### Available Scripts

| Script | Purpose |
|--------|---------|
| `analyze_hetero_50m.py` | 6-panel heterogeneity analysis |
| `verify_primary_secondary.py` | Validate dose separation |
| `horizontal_profile.py` | Extract 1D dose profiles |
| `analyze_symmetry.py` | Detect and measure symmetry |
| `compare_dose_Gy.py` | Convert to Gy and compare |
| `dose_conversion_regional.py` | Regional dose analysis |
| `dose_ratio_profile.py` | Profile ratio analysis |

## 📊 Example Workflow

```bash
# 1. Run simulation
./build/Brachy TG186SourceMacro.mac

# 2. Analyze results
python3 analyze_hetero_50m.py

# 3. Extract dose profiles
python3 horizontal_profile.py

# 4. Visualize
ls -la *.png  # View generated plots
```

## 🏗️ Project Structure

```
.
├── src/                          # C++ source files
│   ├── Brachy.cc                # Main program
│   ├── BrachyTrackingAction.cc   # PRIMARY/SECONDARY classification
│   ├── BrachyDetectorConstruction.cc
│   └── ...
├── include/                      # C++ header files
├── macros/                       # Geant4 command macros
├── scripts/                      # Analysis scripts
├── comparison/                   # Reference data
├── CMakeLists.txt               # Build configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔑 Key Implementation Details

### Primary/Secondary Classification

The classification occurs in `src/BrachyTrackingAction.cc`:

**PRIMARY**: Charged particles from any gamma ray OR descendants of primary carriers
**SECONDARY**: Photons, uncoupled Compton electrons, or non-primary particles

```cpp
// Simplified logic
if (charge != 0.0 && parentIsGamma) {
    info->SetPrimaryDoseCarrier(true);  // Mark as primary
}
else if (parentInfo->IsPrimaryDoseCarrier()) {
    info->SetPrimaryDoseCarrier(true);  // Cascade inheritance
}
```

### Geometry Configuration

- **Scoring Region**: 150×150×5 mm box
- **Voxel Size**: ~1×1×10 mm (300×300×1 bins)
- **Heterogeneity Region**: X=[10-70]mm, Y=[-30-30]mm
- **Materials**: Water (ρ=1.0), Lung (ρ=0.2), Bone (ρ=1.85)

## 📈 Validation Results

### Primary/Secondary Separation
- **Test**: 100 events, TG186 Ir-192 source
- **Result**: 48.4% primary, 51.6% secondary
- **Status**: ✅ Physically correct and energy-conserving

### File Consistency (1m measurement)
- Total EDEP: 6.042605e+07 keV
- Primary: 4.016088e+07 keV (66.5%)
- Secondary: 2.026518e+07 keV (33.5%)
- Coverage: 100.0% (excellent)

## 🖥️ Cluster Execution

See [CLUSTER_GUIDE.md](CLUSTER_GUIDE.md) for detailed instructions on running simulations on HPC clusters.

Quick start:
```bash
# Load Geant4
module load geant4/11.2.0

# Compile
mkdir build && cd build && cmake .. && make -j8

# Submit job
qsub job.sh  # See CLUSTER_GUIDE.md for job script template
```

## 🐛 Troubleshooting

### Compilation Errors
- **CMake can't find Geant4**: Ensure `geant4-config` is in PATH
- **Missing dependencies**: Check all requirements are installed

### Runtime Issues
- **Empty ROOT files**: Check macro syntax and particle generation
- **Memory errors**: Reduce simulation events or voxel count

### Analysis Script Errors
- **Module not found**: Run `pip install -r requirements.txt`
- **ROOT file errors**: Verify ROOT files exist and are not corrupted

## 📚 Documentation

- [INSTALL.md](INSTALL.md) - Detailed installation guide
- [CLUSTER_GUIDE.md](CLUSTER_GUIDE.md) - HPC cluster execution
- [DOCUMENTATION.md](DOCUMENTATION.md) - Complete documentation index
- [FIX_PRIMARY_SECONDARY.md](FIX_PRIMARY_SECONDARY.md) - Technical details of primary/secondary fix

## 📄 License

This project is based on the Geant4 brachytherapy example and includes modifications for primary/secondary dose separation.

## 👥 Authors

- Fernando (Ferkb1903) - Primary/Secondary separation implementation
- Original Geant4 example authors

## 🤝 Contributing

For bug reports and feature requests, please open an issue on GitHub.

## 📞 Contact

For questions about the implementation, please refer to the documentation files or open a GitHub issue.

---

**Last Updated**: October 19, 2025  
**Status**: ✅ Production-Ready  
**Geant4 Version**: 11.2.0

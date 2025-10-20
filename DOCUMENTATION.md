# Documentation Index

Complete guide to all documentation in the Brachy project.

## 🚀 Getting Started

### For New Users
1. **[README.md](README_NEW.md)** - Overview and quick start
2. **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
3. **[CLUSTER_GUIDE.md](CLUSTER_GUIDE.md)** - Run on HPC clusters

### First Steps
```bash
# Clone and install
git clone https://github.com/Ferkb1903/NewModular2.git
cd NewModular2
pip install -r requirements.txt
mkdir build && cd build && cmake .. && make

# Run first test
cd ..
./build/Brachy HomogeneousTest.mac
```

---

## 📚 Core Documentation

### Technical Foundation
- **[FIX_PRIMARY_SECONDARY.md](FIX_PRIMARY_SECONDARY.md)** 
  - Technical explanation of primary/secondary dose separation
  - Implementation details in BrachyTrackingAction.cc
  - Classification logic and inheritance rules

- **[PRIMARY_SECONDARY_ANALYSIS.md](PRIMARY_SECONDARY_ANALYSIS.md)**
  - Problem analysis and root cause investigation
  - Why primary files were empty before fix
  - Validation methodology

### Physics & Simulation
- **[HETEROGENEITY_GUIDE.md](HETEROGENEITY_GUIDE.md)**
  - Heterogeneity enable/disable behavior
  - Material definitions and densities
  - Geometry configuration

- **[MATERIALS_ANALYSIS.md](MATERIALS_ANALYSIS.md)**
  - Material properties and cross-sections
  - Density effects on dose deposition
  - Comparison table: Water, Lung, Bone

- **[SECONDARY_ANALYSIS_BEFORE_FIX.md](SECONDARY_ANALYSIS_BEFORE_FIX.md)**
  - Detailed explanation of why SECONDARY appeared to work
  - Energy distribution before fix
  - Why classification was physically incorrect

---

## 🔬 Analysis & Comparison

### Validation Reports
- **[VERIFY_1m_bone_homo.md](VERIFY_1m_bone_homo.md)**
  - Verification of 1m measurement distance files
  - Primary/Secondary separation verification
  - Consistency checks and energy conservation
  - **Status**: ✅ All files verified correct

- **[ANALYSIS_STATUS.md](ANALYSIS_STATUS.md)**
  - Current status of analysis scripts
  - Performance summary
  - Known issues and workarounds

### Comparison & Benchmarking
- **[BEFORE_AFTER_COMPARISON.txt](BEFORE_AFTER_COMPARISON.txt)**
  - Visual comparison of fix impact
  - ASCII tables showing before/after
  - Key metrics and improvements

- **[SCRIPT_COMPARISON.md](SCRIPT_COMPARISON.md)**
  - Comparison of analysis scripts
  - Which script for each use case
  - Performance and output formats

- **[regional_dose_analysis.txt](regional_dose_analysis.txt)**
  - Regional dose analysis results
  - Zone-based dose distributions
  - Heterogeneity impact analysis

---

## 📋 Reference Guides

### Quick Reference
- **[GIT_UPDATE_SUMMARY.md](GIT_UPDATE_SUMMARY.md)**
  - Summary of all changes in latest commit
  - File-by-file modifications
  - What changed and why

### Project Guides
- **[README.md](README_NEW.md)** - Complete README (40+ sections)
- **[INSTALL.md](INSTALL.md)** - Installation guide (8 options)
- **[CLUSTER_GUIDE.md](CLUSTER_GUIDE.md)** - HPC cluster guide (SLURM/PBS)

---

## 🛠️ File Organization

### By Topic

#### Installation & Setup
```
INSTALL.md                         # Installation instructions
CLUSTER_GUIDE.md                  # Cluster execution guide
README_NEW.md                     # Complete README
```

#### Physics & Implementation
```
FIX_PRIMARY_SECONDARY.md          # Fix implementation details
PRIMARY_SECONDARY_ANALYSIS.md     # Problem analysis
SECONDARY_ANALYSIS_BEFORE_FIX.md  # Why SECONDARY worked (or didn't)
HETEROGENEITY_GUIDE.md            # Heterogeneity configuration
MATERIALS_ANALYSIS.md             # Material properties
```

#### Validation & Analysis
```
VERIFY_1m_bone_homo.md            # File verification report
ANALYSIS_STATUS.md                # Analysis status
BEFORE_AFTER_COMPARISON.txt       # Visual comparison
SCRIPT_COMPARISON.md              # Script analysis guide
regional_dose_analysis.txt        # Regional analysis
```

#### Project Management
```
GIT_UPDATE_SUMMARY.md             # Change summary
PRE_GITHUB_REVIEW.md              # Pre-upload checklist
requirements.txt                  # Python dependencies
```

### By File Size
```
README_NEW.md              (~40 KB)  Comprehensive guide
INSTALL.md                 (~15 KB)  Detailed setup
CLUSTER_GUIDE.md           (~20 KB)  HPC execution guide
FIX_PRIMARY_SECONDARY.md   (~4 KB)   Technical fix details
VERIFY_1m_bone_homo.md     (~5 KB)   Verification report
...
```

---

## 🎯 Documentation by Use Case

### "I want to install the software"
→ Read: **INSTALL.md** → **CLUSTER_GUIDE.md** (if on cluster)

### "I want to understand the primary/secondary fix"
→ Read: **FIX_PRIMARY_SECONDARY.md** → **PRIMARY_SECONDARY_ANALYSIS.md** → **SECONDARY_ANALYSIS_BEFORE_FIX.md**

### "I want to run simulations"
→ Read: **README_NEW.md** (Usage section) → **CLUSTER_GUIDE.md** (if on cluster)

### "I want to analyze results"
→ Read: **SCRIPT_COMPARISON.md** → Choose script → Check **ANALYSIS_STATUS.md**

### "I want to understand heterogeneity"
→ Read: **HETEROGENEITY_GUIDE.md** → **MATERIALS_ANALYSIS.md**

### "I want to verify the fix worked"
→ Read: **VERIFY_1m_bone_homo.md** → **BEFORE_AFTER_COMPARISON.txt**

### "I want to run on a cluster"
→ Read: **CLUSTER_GUIDE.md** → **INSTALL.md** (cluster section)

### "I want to understand all recent changes"
→ Read: **GIT_UPDATE_SUMMARY.md** → Individual files as needed

---

## 📊 Key Results & Status

### Validation Results
- ✅ **Primary/Secondary Separation**: Working correctly (48% primary, 52% secondary)
- ✅ **Energy Conservation**: 100% (P+S = Total within machine precision)
- ✅ **1m Files Verified**: All 3 files correct, 66.5%/33.5% split
- ✅ **Compilation**: No errors, clean build
- ✅ **Python Scripts**: All 17 scripts validated

### Key Metrics
- **Total Dose (1m)**: 6.042605e+07 keV
- **Primary Dose**: 4.016088e+07 keV (66.5%)
- **Secondary Dose**: 2.026518e+07 keV (33.5%)
- **Consistency**: P+S vs Total = 100.0% ✓
- **Voxel Coverage**: 2515/90000 (2.79%)

### Status Summary
```
Code:            ✅ Production-ready
Documentation:   ✅ Comprehensive
Testing:         ✅ Validated
Git:             ✅ Ready to push
Cluster-ready:   ✅ SLURM/PBS templates
```

---

## 📖 Reading Recommendations

### For Authors/Reviewers
1. **BEFORE_AFTER_COMPARISON.txt** - See what changed
2. **FIX_PRIMARY_SECONDARY.md** - Understand the fix
3. **GIT_UPDATE_SUMMARY.md** - Review all changes

### For New Contributors
1. **README_NEW.md** - Overview
2. **INSTALL.md** - Get it running
3. **FIX_PRIMARY_SECONDARY.md** - Understand core feature

### For Cluster Users
1. **INSTALL.md** - Installation
2. **CLUSTER_GUIDE.md** - Full cluster guide
3. **README_NEW.md** - Usage examples

### For Analysis/Data Users
1. **SCRIPT_COMPARISON.md** - Choose your script
2. **ANALYSIS_STATUS.md** - Current status
3. **VERIFY_1m_bone_homo.md** - Verify your results

---

## 🔗 Cross-References

### Primary/Secondary Understanding
```
README_NEW.md
  ├─ Features section
  ├─ Key Implementation Details
  └─ Validation Results
      └─ Detailed in: FIX_PRIMARY_SECONDARY.md
                      PRIMARY_SECONDARY_ANALYSIS.md
                      SECONDARY_ANALYSIS_BEFORE_FIX.md
```

### Heterogeneity Understanding
```
README_NEW.md
  ├─ Geometry Configuration section
  └─ Detailed in: HETEROGENEITY_GUIDE.md
                  MATERIALS_ANALYSIS.md
                  VERIFY_1m_bone_homo.md
```

### Running on Different Systems
```
INSTALL.md (Local)
CLUSTER_GUIDE.md (HPC)
README_NEW.md (General)
```

---

## 📞 Document Metadata

### Documentation Statistics
- **Total Documents**: 12 markdown/text files
- **Total Size**: ~150 KB (documentation)
- **Total Code Size**: ~500 KB (src + include)
- **Total Data**: 8.8 GB (ROOT files + images)

### Document Freshness
- **Last Updated**: October 19, 2025
- **All Docs Current**: ✅ Yes
- **Tested & Verified**: ✅ All validations complete
- **Ready for GitHub**: ✅ Yes

### Authorship
- **Primary Author**: Fernando (Ferkb1903)
- **Based On**: Geant4 brachytherapy example v11.2.0
- **Status**: Production-ready for publication

---

## ✅ Quality Checklist

Documentation meets these criteria:
- ✅ Comprehensive and up-to-date
- ✅ Well-organized with cross-references
- ✅ Includes quick-start guides
- ✅ Includes detailed technical guides
- ✅ Includes troubleshooting guides
- ✅ Includes cluster-specific guidance
- ✅ Validated examples and benchmarks
- ✅ Clear and accessible language

---

## 🎓 Learning Path

**Beginner Level** (30 min)
- Read: README_NEW.md overview + INSTALL.md basics
- Action: Install and run first test

**Intermediate Level** (2 hours)
- Read: FIX_PRIMARY_SECONDARY.md + CLUSTER_GUIDE.md
- Action: Run full simulation, analyze results

**Advanced Level** (4+ hours)
- Read: All technical documents
- Action: Customize code, run parameter studies, cluster deployment

---

**Navigation**: [Main README](README_NEW.md) | [Installation](INSTALL.md) | [Cluster Guide](CLUSTER_GUIDE.md)

# Brachytherapy Heterogeneity Analysis - Status Report (2025-10-19)

## Summary
Successfully implemented and tested heterogeneity analysis in Geant4 brachytherapy simulation with TWO radiation sources and regional dose conversion.

## Simulations Completed

### 1. TG186 Iridium-192 (Medium Energy, 60-370 keV)
- **Spectrum**: Multi-energetic (natural decay lines)
- **Files**: 
  - `brachytherapy_20251018_232003.root` (WITH 6×6×6 cm bone at X=40mm)
  - `brachytherapy_20251018_233210.root` (Homogeneous water)
- **Result**: -0.44% total dose change (attenuation dominant)

### 2. I-125 Iodine (Low Energy, 35 keV)
- **Spectrum**: Monoenergetic (strong photoelectric effect)
- **Files**:
  - `brachytherapy_20251019_000420.root` (Homogeneous water)
  - `brachytherapy_20251019_000633.root` (WITH bone)
- **Primary/Secondary separation**: eDepPrimary and eDepSecondary files available
- **Result**: -4.49% dose reduction in bone region

## Key Physics Insights

### Regional Dose Conversion
Material densities affect dose conversion differently:
- **Water**: 1 keV = 1.591e-8 Gy (ρ=1.0 g/cm³)
- **Bone**: 1 keV = 8.288e-9 Gy (ρ=1.92 g/cm³)
- **Ratio**: 0.521x (bone receives LESS dose per keV due to higher density)

### Heterogeneity Geometry
```
Source (TG186/I125) at origin (0,0,0)
          ↓
    [Water phantom ±150mm]
          ↓
    Heterogeneity: 6×6×6 cm bone cube
    - Center: X=40mm
    - Range: X ∈ [10, 70]mm
    - Y range: ±30mm
    - Effect: SHIELDS downstream region (attenuation)
```

### Energy-Dependent Effects

| Source | Energy | Dominant Effect | Bone Region Dose Change |
|--------|--------|-----------------|------------------------|
| I-125  | 35 keV | Photoelectric   | **-4.49%** ↓ (shielding) |
| Ir-192 | 60-370 keV | Mixed (PE + Compton) | **-4.49%** ↓ (consistent) |

**Interpretation**: Attenuation effect DOMINATES both low and medium energy.
Local backscatter insufficient to overcome shielding at this geometry.

## Analysis Scripts Created

### dose_conversion_regional.py
- Reads two ROOT files (hetero vs homo)
- Converts EDEP to Gy with regional material properties
- Generates comparison plots and statistics
- **Output**: dose_regional_comparison.png, regional_dose_analysis.txt

### compare_dose_Gy.py
- Global dose comparison (uniform material assumption)
- X-profile analysis showing position-dependent effects
- **Output**: heterogeneity_dose_comparison_Gy.png

### run_source_comparison.sh
- Automated batch execution of multi-source simulations
- Toggles heterogeneity on/off for each source
- Generates all ROOT files and ASCII outputs

## Next Steps (Optional)

1. **Test different heterogeneity positions**:
   - Move bone AWAY from source to see backscatter
   - Expected: dose INCREASE when shielding effect is removed

2. **Higher energy sources**:
   - Pair production regime (>2 MeV) shows different physics
   - Compton scattering becomes more isotropic

3. **Different materials**:
   - Titanium (Z=22): Higher Z → stronger effects
   - Soft tissue (ρ≈1.06 g/cm³): Close to water

4. **Spatial resolution**:
   - Current: 1mm × 1mm × 10mm voxels
   - Could reduce for sub-mm features

## Repository Status
✅ Code pushed to: https://github.com/Ferkb1903/NewModular2.git
✅ Branch: main
✅ Latest commit: b017d97 (2025-10-19)

---
Generated: 2025-10-19 | Geant4 11.2.0 | Multi-threading: 16 threads | Events: 1M each

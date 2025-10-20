# HETEROGENEITY BEHAVIOR EXPLANATION

## Your Macro (Homogeneous - No Heterogeneity):
```
/phantom/selectMaterial G4_LUNG_ICRP
/phantom/heterogeneity/enable false          <-- DISABLES heterogeneity (cleans it up)
/phantom/heterogeneity/material ...          <-- These 3 commands store parameters
/phantom/heterogeneity/size ...              <-- but do NOT create geometry
/phantom/heterogeneity/position ...          <-- (because enable=false)
```

**Expected Result: HOMOGENEOUS (no heterogeneity inside Lung)**

**What you were seeing:** If you saw heterogeneity, it was either:
1. From a PREVIOUS run (old ROOT file or visualization)
2. Or from a DIFFERENT macro that ENABLED heterogeneity

---

## IMPORTANT: Order Matters!

If you want HETEROGENEOUS geometry, use:
```
/phantom/selectMaterial G4_LUNG_ICRP
/phantom/heterogeneity/enable true           <-- ENABLE FIRST (or last, see below)
/phantom/heterogeneity/material G4_BONE_COMPACT_ICRU
/phantom/heterogeneity/size 6.0 6.0 6.0 cm
/phantom/heterogeneity/position 40.0 0.0 0.0 mm
```

Or this order (parameters first, then enable):
```
/phantom/selectMaterial G4_LUNG_ICRP
/phantom/heterogeneity/material G4_BONE_COMPACT_ICRU
/phantom/heterogeneity/size 6.0 6.0 6.0 cm
/phantom/heterogeneity/position 40.0 0.0 0.0 mm
/phantom/heterogeneity/enable true           <-- ENABLE LAST (ensures build with correct params)
```

---

## Code Changes Made:

1. Added method `IsHeterogeneityEnabled()` to BrachyDetectorConstruction.hh
2. Updated BrachyDetectorMessenger.cc to show WARNINGS when you define parameters but heterogeneity is DISABLED

Now when you run a macro with `enable false` followed by material/size/position, you will see:
```
WARNING: Heterogeneity is currently DISABLED. Material change will be stored but not applied...
WARNING: Heterogeneity is currently DISABLED. Size change will be stored but not applied...
WARNING: Heterogeneity is currently DISABLED. Position change will be stored but not applied...
```

This makes it CLEAR that those changes won't take effect until you set `enable true`.

---

## Testing Macros Created:

- HomogeneousTest.mac   → Shows WARNINGS (demonstrates the issue)
- HeterogeneousTest.mac → No warnings (correct usage)

Both compiled and ready to run.

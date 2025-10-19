#!/bin/bash
# Script to run heterogeneity comparison with DIFFERENT SOURCES

cd /home/fer/fer/newbrachy
mkdir -p simulation_results

echo "========================================================================"
echo "HETEROGENEITY STUDY WITH DIFFERENT SOURCES"
echo "========================================================================"

# Function to run simulation
run_sim() {
    local source_name=$1
    local hetero_status=$2
    local output_label=$3
    
    cat > temp_hetero_study.mac << EOF
/control/verbose 0
/run/verbose 0
/control/execute TG186_Analysis.mac
/run/initialize
/phantom/heterogeneity/enable $hetero_status
/phantom/heterogeneity/material G4_BONE_COMPACT_ICRU
/phantom/heterogeneity/size 6.0 6.0 6.0 cm
/phantom/heterogeneity/position 40.0 0.0 0.0 mm
/source/switch $source_name
/run/beamOn 1000000
EOF

    echo ""
    echo "Running: $output_label"
    echo "  Source: $source_name"
    echo "  Heterogeneity: $hetero_status"
    
    ./build/Brachy temp_hetero_study.mac
    
    # Rename output file
    if [ -f brachytherapy_*.root ]; then
        mv brachytherapy_*.root "simulation_results/${output_label}.root"
        echo "  Output: simulation_results/${output_label}.root"
    fi
}

# ====================================================================
# I-125 IODINE SOURCE (35 keV - low energy, high photoelectric effect)
# ====================================================================
echo ""
echo "Starting I-125 IODINE source simulations (35 keV)..."

run_sim "Iodine" "false" "I125_Homogeneous"
run_sim "Iodine" "true"  "I125_WithBone"

# ====================================================================
# Ir-192 IRIDIUM SOURCE (60-370 keV - medium energy, mixed interactions)
# ====================================================================
echo ""
echo "Starting Ir-192 IRIDIUM source simulations (poly-energetic)..."

run_sim "TG186" "false" "Ir192_Homogeneous"
run_sim "Ir192" "true"  "Ir192_WithBone"

# ====================================================================
# Leipzig IRIDIUM SOURCE (if available)
# ====================================================================
echo ""
echo "Starting Leipzig IRIDIUM source simulations..."

run_sim "Leipzig" "false" "Leipzig_Homogeneous"
run_sim "Leipzig" "true"  "Leipzig_WithBone"

# Clean up
rm -f temp_hetero_study.mac

echo ""
echo "========================================================================"
echo "SIMULATIONS COMPLETE"
echo "========================================================================"
ls -lh simulation_results/

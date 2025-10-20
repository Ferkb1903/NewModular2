#!/bin/bash
# Simple script: Compare I-125 vs Ir-192 with/without bone heterogeneity

cd /home/fer/fer/newbrachy
mkdir -p simulation_results

echo "========================================================================"
echo "COMPARING I-125 vs Ir-192 WITH/WITHOUT BONE HETEROGENEITY"
echo "========================================================================"

# Function to run simulation
run_sim() {
    local macro=$1
    local enable_hetero=$2
    local output_label=$3
    
    echo ""
    echo ">>> Running: $output_label"
    
    # Modify macro temporarily to enable/disable heterogeneity
    sed "s|/phantom/heterogeneity/enable false|/phantom/heterogeneity/enable $enable_hetero|" $macro > temp_analysis.mac
    
    ./build/Brachy temp_analysis.mac > /dev/null 2>&1
    
    # Find and rename output
    for f in brachytherapy_*.root; do
        if [ -f "$f" ]; then
            mv "$f" "simulation_results/${output_label}.root"
            echo "    Output: simulation_results/${output_label}.root"
            break
        fi
    done
}

# ====================================================================
# Ir-192 SIMULATIONS
# ====================================================================
echo ""
echo "==== Ir-192 (Multi-energetic: 61-370 keV) ===="

run_sim "TG186_Analysis.mac" "false" "Ir192_Homogeneous"
echo "    (No heterogeneity)"

run_sim "TG186_Analysis.mac" "true"  "Ir192_WithBone"
echo "    (With bone heterogeneity at X=40mm)"

# ====================================================================
# I-125 SIMULATIONS
# ====================================================================
echo ""
echo "==== I-125 (Monochromatic: 35 keV) ===="

run_sim "I125_Analysis.mac" "false" "I125_Homogeneous"
echo "    (No heterogeneity)"

run_sim "I125_Analysis.mac" "true"  "I125_WithBone"
echo "    (With bone heterogeneity at X=40mm)"

# Clean up
rm -f temp_analysis.mac

echo ""
echo "========================================================================"
echo "SIMULATIONS COMPLETE"
echo "========================================================================"
ls -lh simulation_results/

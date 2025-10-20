#!/usr/bin/env python3
"""
Verify which ROOT file contains which material by analyzing dose distribution
"""

import subprocess
import sys

files = {
    "Bone_Homo": "brachytherapy_Bone_Homo.root",
    "Bone_Hetero": "brachytherapy_Bone_Hetero.root",
    "Lung_Homo": "brachytherapy_Lung_Homo.root",
    "Lung_Hetero": "brachytherapy_Lung_Hetero.root",
    "Water_Homo": "brachytherapy_Water_Homo.root"
}

print("=" * 80)
print("ROOT FILE VERIFICATION - Using ROOT command line tools")
print("=" * 80)

for label, fname in files.items():
    # Use ROOT command line to get histogram info
    cmd = f'root -b -q -e "auto f = TFile::Open(\\"{fname}\\"); auto h = f->Get(\\\"h20\\\"); if(h) std::cout << h->GetEntries() << \\\" \\\" << h->Integral() << std::endl;"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()
        if output:
            parts = output.split()
            if len(parts) >= 2:
                entries = parts[-2]
                integral = parts[-1]
                print(f"\n{label:15}")
                print(f"  File: {fname}")
                print(f"  Entries: {entries}, Integral: {integral}")
            else:
                print(f"\n{label:15} | Partial output: {output}")
        else:
            print(f"\n{label:15} | No output from ROOT")
    except Exception as e:
        print(f"\n{label:15} | Error: {e}")

print("\n" + "=" * 80)
print("EXPECTED TOTAL EDEP BY MATERIAL:")
print("=" * 80)
print("Bone (ρ=1.92 g/cm³):  Lower EDEP (density increases stopping power)")
print("Water (ρ=1.0 g/cm³):  Medium EDEP")
print("Lung (ρ≈0.26 g/cm³):  Higher EDEP (low density, less stopping power)")
print("=" * 80)

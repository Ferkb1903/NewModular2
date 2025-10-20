// Analyze heterogeneity region specifically
// Check if bone cube at Y=40mm±30mm is affecting dose

void analyze_heterogeneity_region(const char* fileHetero = "brachytherapy_20251018_223244.root",
                                   const char* fileWater = "brachytherapy_20251018_223441.root") {
    
    TFile *fHetero = TFile::Open(fileHetero);
    TFile *fWater = TFile::Open(fileWater);
    
    if (!fHetero || !fWater) {
        cout << "ERROR: Cannot open files" << endl;
        return;
    }
    
    TH2D *hHetero = (TH2D*)fHetero->Get("h20");
    TH2D *hWater = (TH2D*)fWater->Get("h20");
    
    if (!hHetero || !hWater) {
        cout << "ERROR: Cannot find histograms" << endl;
        return;
    }
    
    cout << "\n=== HETEROGENEITY REGION ANALYSIS ===" << endl;
    cout << "Heterogeneity: 6x6x6 cm³ bone cube at (X=0, Y=40mm, Z=0)" << endl;
    cout << "Expected region: X=±30mm, Y=10-70mm" << endl << endl;
    
    // Analyze several Y slices in heterogeneity region
    double yPositions[] = {10, 20, 30, 40, 50, 60, 70};
    
    cout << "Y [mm]\tHetero\tWater\tDiff\t\tRatio\t% Change" << endl;
    cout << "================================================================" << endl;
    
    for (int i = 0; i < 7; i++) {
        double yPos = yPositions[i];
        int ybin = hHetero->GetYaxis()->FindBin(yPos);
        
        // Sum over X within ±30mm (heterogeneity width)
        double sumHetero = 0, sumWater = 0;
        int xbinMin = hHetero->GetXaxis()->FindBin(-30.0);
        int xbinMax = hHetero->GetXaxis()->FindBin(30.0);
        
        for (int xbin = xbinMin; xbin <= xbinMax; xbin++) {
            sumHetero += hHetero->GetBinContent(xbin, ybin);
            sumWater += hWater->GetBinContent(xbin, ybin);
        }
        
        double diff = sumHetero - sumWater;
        double ratio = (sumWater > 0) ? sumHetero / sumWater : 0;
        double percentChange = (sumWater > 0) ? 100.0 * (sumHetero - sumWater) / sumWater : 0;
        
        cout << yPos << "\t" 
             << sumHetero << "\t"
             << sumWater << "\t"
             << diff << "\t"
             << ratio << "\t"
             << percentChange << "%" << endl;
    }
    
    // Total in heterogeneity region
    cout << "\n=== INTEGRATED ANALYSIS ===" << endl;
    
    int ybinMin = hHetero->GetYaxis()->FindBin(10.0);
    int ybinMax = hHetero->GetYaxis()->FindBin(70.0);
    int xbinMin = hHetero->GetXaxis()->FindBin(-30.0);
    int xbinMax = hHetero->GetXaxis()->FindBin(30.0);
    
    double totalHetero = 0, totalWater = 0;
    for (int xbin = xbinMin; xbin <= xbinMax; xbin++) {
        for (int ybin = ybinMin; ybin <= ybinMax; ybin++) {
            totalHetero += hHetero->GetBinContent(xbin, ybin);
            totalWater += hWater->GetBinContent(xbin, ybin);
        }
    }
    
    cout << "Total in heterogeneity region (X±30mm, Y=10-70mm):" << endl;
    cout << "  With bone: " << totalHetero << endl;
    cout << "  Water only: " << totalWater << endl;
    cout << "  Difference: " << (totalHetero - totalWater) << endl;
    cout << "  Ratio: " << (totalWater > 0 ? totalHetero/totalWater : 0) << endl;
    cout << "  % Change: " << (totalWater > 0 ? 100.0*(totalHetero-totalWater)/totalWater : 0) << "%" << endl;
    
    // Create comparison plot focused on heterogeneity region
    TCanvas *c = new TCanvas("c", "Heterogeneity Region", 1200, 800);
    c->Divide(2, 2);
    
    // Projection Y (shows dose vs distance from source)
    c->cd(1);
    TH1D *pyHetero = hHetero->ProjectionY("pyHetero");
    TH1D *pyWater = hWater->ProjectionY("pyWater");
    pyHetero->SetLineColor(kRed);
    pyHetero->SetLineWidth(2);
    pyWater->SetLineColor(kBlue);
    pyWater->SetLineWidth(2);
    pyHetero->GetXaxis()->SetRangeUser(-10, 80);
    pyHetero->SetStats(0);
    pyHetero->SetTitle("Dose vs Y position");
    pyHetero->GetXaxis()->SetTitle("Y [mm]");
    pyHetero->GetYaxis()->SetTitle("Energy Deposition [MeV]");
    pyHetero->Draw();
    pyWater->Draw("SAME");
    
    TLegend *leg1 = new TLegend(0.6, 0.7, 0.9, 0.9);
    leg1->AddEntry(pyHetero, "With bone", "l");
    leg1->AddEntry(pyWater, "Water only", "l");
    leg1->Draw();
    
    // Add lines showing heterogeneity region
    TLine *line1 = new TLine(10, 0, 10, pyHetero->GetMaximum());
    TLine *line2 = new TLine(70, 0, 70, pyHetero->GetMaximum());
    line1->SetLineStyle(2);
    line2->SetLineStyle(2);
    line1->Draw();
    line2->Draw();
    
    // Difference projection Y
    c->cd(2);
    TH1D *pyDiff = (TH1D*)pyHetero->Clone("pyDiff");
    pyDiff->Add(pyWater, -1.0);
    pyDiff->SetLineColor(kBlack);
    pyDiff->SetLineWidth(2);
    pyDiff->SetTitle("Dose Difference (Bone - Water)");
    pyDiff->GetXaxis()->SetRangeUser(-10, 80);
    pyDiff->GetXaxis()->SetTitle("Y [mm]");
    pyDiff->GetYaxis()->SetTitle("Difference [MeV]");
    pyDiff->SetStats(0);
    pyDiff->Draw();
    TLine *line0 = new TLine(-10, 0, 80, 0);
    line0->SetLineStyle(2);
    line0->Draw();
    line1->Draw();
    line2->Draw();
    
    // 2D view of difference
    c->cd(3);
    TH2D *hDiff = (TH2D*)hHetero->Clone("hDiff");
    hDiff->Add(hWater, -1.0);
    hDiff->SetTitle("2D Difference (Bone - Water)");
    hDiff->GetXaxis()->SetRangeUser(-50, 50);
    hDiff->GetYaxis()->SetRangeUser(-10, 80);
    hDiff->SetStats(0);
    hDiff->Draw("COLZ");
    
    // Ratio
    c->cd(4);
    TH1D *pyRatio = (TH1D*)pyHetero->Clone("pyRatio");
    pyRatio->Divide(pyWater);
    pyRatio->SetLineColor(kGreen+2);
    pyRatio->SetLineWidth(2);
    pyRatio->SetTitle("Dose Ratio (Bone / Water)");
    pyRatio->GetXaxis()->SetRangeUser(-10, 80);
    pyRatio->GetYaxis()->SetRangeUser(0.8, 1.2);
    pyRatio->GetXaxis()->SetTitle("Y [mm]");
    pyRatio->GetYaxis()->SetTitle("Ratio");
    pyRatio->SetStats(0);
    pyRatio->Draw();
    TLine *line1_0 = new TLine(-10, 1.0, 80, 1.0);
    line1_0->SetLineStyle(2);
    line1_0->Draw();
    line1->Draw();
    line2->Draw();
    
    c->SaveAs("heterogeneity_detailed_analysis.png");
    cout << "\n==> Detailed plot saved as: heterogeneity_detailed_analysis.png" << endl;
}

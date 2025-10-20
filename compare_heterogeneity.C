// Compare two brachytherapy ROOT files to verify heterogeneity effect
// Usage: root -l -q 'compare_heterogeneity.C("file1.root", "file2.root")'

void compare_heterogeneity(const char* file1 = "brachytherapy_20251018_222005.root", 
                           const char* file2 = "brachytherapy_20251018_222005.root") {
    
    // Open ROOT files
    TFile *f1 = TFile::Open(file1);
    TFile *f2 = TFile::Open(file2);
    
    if (!f1 || f1->IsZombie()) {
        cout << "ERROR: Cannot open file: " << file1 << endl;
        return;
    }
    if (!f2 || f2->IsZombie()) {
        cout << "ERROR: Cannot open file: " << file2 << endl;
        return;
    }
    
    cout << "\n=== Comparing ROOT files ===" << endl;
    cout << "File 1: " << file1 << endl;
    cout << "File 2: " << file2 << endl;
    
    // Get the histograms
    TH2D *h1 = (TH2D*)f1->Get("h20");
    TH2D *h2 = (TH2D*)f2->Get("h20");
    
    if (!h1) {
        cout << "ERROR: Cannot find histogram h20 in file 1" << endl;
        f1->ls();
        return;
    }
    if (!h2) {
        cout << "ERROR: Cannot find histogram h20 in file 2" << endl;
        f2->ls();
        return;
    }
    
    cout << "\nHistogram 1: " << h1->GetName() << endl;
    cout << "  Entries: " << h1->GetEntries() << endl;
    cout << "  Mean: " << h1->GetMean() << endl;
    cout << "  Integral: " << h1->Integral() << endl;
    
    cout << "\nHistogram 2: " << h2->GetName() << endl;
    cout << "  Entries: " << h2->GetEntries() << endl;
    cout << "  Mean: " << h2->GetMean() << endl;
    cout << "  Integral: " << h2->Integral() << endl;
    
    // Clone histograms for manipulation
    TH2D *diff = (TH2D*)h1->Clone("diff");
    diff->SetTitle("Difference: File1 - File2");
    diff->Add(h2, -1.0);  // Subtract h2 from h1
    
    TH2D *ratio = (TH2D*)h1->Clone("ratio");
    ratio->SetTitle("Ratio: File1 / File2");
    ratio->Divide(h2);
    
    cout << "\nDifference histogram:" << endl;
    cout << "  Mean: " << diff->GetMean() << endl;
    cout << "  RMS: " << diff->GetRMS() << endl;
    cout << "  Max difference: " << diff->GetMaximum() << endl;
    cout << "  Min difference: " << diff->GetMinimum() << endl;
    
    // Create canvas for visualization
    TCanvas *c1 = new TCanvas("c1", "Comparison", 1600, 1200);
    c1->Divide(2, 3);
    
    // Plot File 1
    c1->cd(1);
    gPad->SetLogz();
    h1->SetStats(0);
    h1->Draw("COLZ");
    h1->GetXaxis()->SetTitle("X [mm]");
    h1->GetYaxis()->SetTitle("Y [mm]");
    
    // Plot File 2
    c1->cd(2);
    gPad->SetLogz();
    h2->SetStats(0);
    h2->Draw("COLZ");
    h2->GetXaxis()->SetTitle("X [mm]");
    h2->GetYaxis()->SetTitle("Y [mm]");
    
    // Plot Difference
    c1->cd(3);
    diff->SetStats(0);
    diff->Draw("COLZ");
    diff->GetXaxis()->SetTitle("X [mm]");
    diff->GetYaxis()->SetTitle("Y [mm]");
    
    // Plot Ratio
    c1->cd(4);
    ratio->SetStats(0);
    ratio->GetZaxis()->SetRangeUser(0.5, 1.5);
    ratio->Draw("COLZ");
    ratio->GetXaxis()->SetTitle("X [mm]");
    ratio->GetYaxis()->SetTitle("Y [mm]");
    
    // Projection X for both files
    c1->cd(5);
    TH1D *px1 = h1->ProjectionX("px1");
    TH1D *px2 = h2->ProjectionX("px2");
    px1->SetLineColor(kBlue);
    px2->SetLineColor(kRed);
    px1->SetStats(0);
    px1->Draw();
    px2->Draw("SAME");
    px1->GetXaxis()->SetTitle("X [mm]");
    px1->GetYaxis()->SetTitle("Energy Deposition");
    TLegend *leg1 = new TLegend(0.7, 0.7, 0.9, 0.9);
    leg1->AddEntry(px1, "File 1", "l");
    leg1->AddEntry(px2, "File 2", "l");
    leg1->Draw();
    
    // Projection Y for both files
    c1->cd(6);
    TH1D *py1 = h1->ProjectionY("py1");
    TH1D *py2 = h2->ProjectionY("py2");
    py1->SetLineColor(kBlue);
    py2->SetLineColor(kRed);
    py1->SetStats(0);
    py1->Draw();
    py2->Draw("SAME");
    py1->GetXaxis()->SetTitle("Y [mm]");
    py1->GetYaxis()->SetTitle("Energy Deposition");
    TLegend *leg2 = new TLegend(0.7, 0.7, 0.9, 0.9);
    leg2->AddEntry(py1, "File 1", "l");
    leg2->AddEntry(py2, "File 2", "l");
    leg2->Draw();
    
    c1->SaveAs("heterogeneity_comparison.png");
    cout << "\nPlot saved as: heterogeneity_comparison.png" << endl;
    
    // Statistical test
    cout << "\n=== Statistical Comparison ===" << endl;
    Double_t chi2 = h1->Chi2Test(h2, "WW P");
    cout << "Chi2 test p-value: " << chi2 << endl;
    if (chi2 < 0.05) {
        cout << "Files are SIGNIFICANTLY DIFFERENT (heterogeneity detected!)" << endl;
    } else {
        cout << "Files are statistically similar (no significant heterogeneity effect)" << endl;
    }
    
    // Check specific region where heterogeneity should be (Y=40mm)
    cout << "\n=== Region Analysis (Y = 40 mm) ===" << endl;
    int ybin = h1->GetYaxis()->FindBin(40.0);
    cout << "Y bin at 40mm: " << ybin << endl;
    
    Double_t sum1 = 0, sum2 = 0;
    for (int i = 1; i <= h1->GetNbinsX(); i++) {
        sum1 += h1->GetBinContent(i, ybin);
        sum2 += h2->GetBinContent(i, ybin);
    }
    cout << "Sum at Y=40mm - File 1: " << sum1 << endl;
    cout << "Sum at Y=40mm - File 2: " << sum2 << endl;
    cout << "Difference: " << (sum1 - sum2) << " (" << 100*(sum1-sum2)/sum2 << "%)" << endl;
}

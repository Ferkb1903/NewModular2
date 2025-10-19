//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
//
// --------------------------------------------------------------
//                 GEANT 4 - Brachytherapy example
// --------------------------------------------------------------
//
// Code developed by:
//  S.Guatelli and D. Cutajar
//
//
//    *******************************
//    *                             *
//    *    BrachyRunAction.cc       *
//    *                             *
//    *******************************
//
//

#include "BrachyRunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4ios.hh"
#include "G4SystemOfUnits.hh"
#include "G4ScoringManager.hh"
#include "G4VScoringMesh.hh"
#include "G4MultiFunctionalDetector.hh"
#include "G4VPrimitiveScorer.hh"
#include "globals.hh"

#include "BrachyParentFilter.hh"

#include <ctime>
#include <iomanip>
#include <sstream>

namespace {
  // Helper function to generate timestamp string
  G4String GetTimestampString() {
    auto t = std::time(nullptr);
    auto tm = *std::localtime(&t);
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y%m%d_%H%M%S");
    return oss.str();
  }
}

void BrachyRunAction::BeginOfRunAction(const G4Run* aRun)
{ 
G4cout << "### Run " << aRun -> GetRunID() << " start." << G4endl;

auto analysisManager = G4AnalysisManager::Instance();

// Generate filename with timestamp
G4String timestamp = GetTimestampString();
G4String fileName = "primary_" + timestamp + ".root";

G4bool fileOpen = analysisManager -> OpenFile(fileName);

if (! fileOpen) {
    G4cerr << "\n---> The ROOT output file has not been opened "
           << analysisManager->GetFileName() << G4endl;
  }
  
G4cout << "Using " << analysisManager->GetType() << G4endl;
analysisManager -> SetVerboseLevel(1);

// Create histogram with the energy spectrum of the photons emitted by the
// radionucldie
analysisManager -> CreateH1("h10","energy spectrum", 800, 0., 800.);

ConfigureDoseFilters();
}

void BrachyRunAction::EndOfRunAction(const G4Run* aRun)
{ 
G4cout << "number of events = " << aRun->GetNumberOfEvent() << G4endl;
 
// save histograms in primary.root
auto analysisManager = G4AnalysisManager::Instance();
analysisManager -> Write();
analysisManager -> CloseFile();
}

void BrachyRunAction::ConfigureDoseFilters() const
{
  auto scoringManager = G4ScoringManager::GetScoringManagerIfExist();
  if (!scoringManager) {
    return;
  }

  const size_t meshCount = scoringManager->GetNumberOfMesh();
  for (size_t iMesh = 0; iMesh < meshCount; ++iMesh) {
    G4VScoringMesh* mesh = scoringManager->GetMesh(iMesh);
    if (!mesh) {
      continue;
    }

    const auto applyFilter = [mesh](const G4String& scorerName,
                                    BrachyParentFilter::Category category,
                                    const G4String& filterSuffix) {
      if (!mesh->FindPrimitiveScorer(scorerName)) {
        return;
      }
      mesh->SetCurrentPrimitiveScorer(scorerName);
      auto* filter = new BrachyParentFilter(scorerName + filterSuffix, category);
      mesh->SetFilter(filter);
      mesh->SetNullToCurrentPrimitiveScorer();
    };

    applyFilter("eDepPrimary", BrachyParentFilter::Category::Primary, "Filter");
    applyFilter("eDepSecondary", BrachyParentFilter::Category::Secondary, "Filter");
  }
}





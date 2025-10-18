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
#include "BrachyParentFilter.hh"

#include "BrachyTrackInformation.hh"

#include "G4Step.hh"
#include "G4Track.hh"

BrachyParentFilter::BrachyParentFilter(const G4String& name, Category category)
  : G4VSDFilter(name), fCategory(category)
{}

G4bool BrachyParentFilter::Accept(const G4Step* aStep) const
{
  if (!aStep) {
    return false;
  }

  const auto* track = aStep->GetTrack();
  if (!track) {
    return false;
  }

  const auto* info = dynamic_cast<const BrachyTrackInformation*>(track->GetUserInformation());
  const G4bool isPrimaryDoseCarrier = (info != nullptr) ? info->IsPrimaryDoseCarrier() : false;

  if (fCategory == Category::Primary) {
    return isPrimaryDoseCarrier;
  }

  return !isPrimaryDoseCarrier;
}

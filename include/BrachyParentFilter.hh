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
#ifndef BrachyParentFilter_h
#define BrachyParentFilter_h 1

#include "G4VSDFilter.hh"
#include "globals.hh"

class BrachyTrackInformation;
class G4Step;

// Custom filter that allows separating the dose carriers identified via
// BrachyTrackInformation as primary (first charged secondary) or secondary.
class BrachyParentFilter : public G4VSDFilter
{
public:
  enum class Category { Primary, Secondary };

  BrachyParentFilter(const G4String& name, Category category);
  ~BrachyParentFilter() override = default;

  G4bool Accept(const G4Step* aStep) const override;

private:
  Category fCategory;
};

#endif

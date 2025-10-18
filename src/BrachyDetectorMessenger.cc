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
// Code developed by:
//  S.Guatelli, A. Le
//
//    *********************************
//    *                               *
//    *    BrachyDetectorMessenger.cc *
//    *                               *
//    *********************************
//
//
#include "BrachyDetectorMessenger.hh"
#include "BrachyDetectorConstruction.hh"
#include "G4UIdirectory.hh"
#include "G4UIcmdWithAString.hh"
#include "G4UIcmdWithABool.hh"
#include "G4UIcmdWith3VectorAndUnit.hh"

BrachyDetectorMessenger::BrachyDetectorMessenger(BrachyDetectorConstruction* detector): fDetector(detector)
{ 
  fDetectorDir = new G4UIdirectory("/phantom/");
  fDetectorDir -> SetGuidance(" phantom control.");
      
  fPhantomMaterialCmd = new G4UIcmdWithAString("/phantom/selectMaterial",this);
  fPhantomMaterialCmd -> SetGuidance("Select Material of the phantom.");
  fPhantomMaterialCmd -> SetParameterName("choice",false);
  fPhantomMaterialCmd -> AvailableForStates(G4State_Idle);
  
  fSourceCmd = new G4UIcmdWithAString("/source/switch",this);
  fSourceCmd -> SetGuidance("Assign the selected geometry to G4RunManager."); 
  fSourceCmd -> SetParameterName("choice",true);
  fSourceCmd -> SetDefaultValue(" ");
  fSourceCmd -> SetCandidates("TG186 Flexi Iodine Leipzig Oncura");
  fSourceCmd -> AvailableForStates(G4State_PreInit,G4State_Idle); 

  fHeteroDir = new G4UIdirectory("/phantom/heterogeneity/");
  fHeteroDir->SetGuidance("Control inclusion of a heterogeneity volume inside the phantom.");

  fHeteroEnableCmd = new G4UIcmdWithABool("/phantom/heterogeneity/enable", this);
  fHeteroEnableCmd->SetGuidance("Enable or disable the heterogeneity volume.");
  fHeteroEnableCmd->SetParameterName("enable", true);
  fHeteroEnableCmd->SetDefaultValue(false);
  fHeteroEnableCmd->AvailableForStates(G4State_PreInit, G4State_Idle);

  fHeteroMaterialCmd = new G4UIcmdWithAString("/phantom/heterogeneity/material", this);
  fHeteroMaterialCmd->SetGuidance("Set the material used for the heterogeneity volume.");
  fHeteroMaterialCmd->SetParameterName("choice", false);
  fHeteroMaterialCmd->AvailableForStates(G4State_PreInit, G4State_Idle);

  fHeteroSizeCmd = new G4UIcmdWith3VectorAndUnit("/phantom/heterogeneity/size", this);
  fHeteroSizeCmd->SetGuidance("Set full size (dx dy dz) of the heterogeneity volume.");
  fHeteroSizeCmd->SetParameterName("dx", "dy", "dz", true);
  fHeteroSizeCmd->SetDefaultUnit("cm");
  fHeteroSizeCmd->SetUnitCandidates("mm cm m");
  fHeteroSizeCmd->AvailableForStates(G4State_PreInit, G4State_Idle);

  fHeteroPositionCmd = new G4UIcmdWith3VectorAndUnit("/phantom/heterogeneity/position", this);
  fHeteroPositionCmd->SetGuidance("Set the centre position of the heterogeneity volume.");
  fHeteroPositionCmd->SetParameterName("x", "y", "z", true);
  fHeteroPositionCmd->SetDefaultUnit("cm");
  fHeteroPositionCmd->SetUnitCandidates("mm cm m");
  fHeteroPositionCmd->AvailableForStates(G4State_PreInit, G4State_Idle);
 }

BrachyDetectorMessenger::~BrachyDetectorMessenger()
{
  delete fSourceCmd;
  delete fPhantomMaterialCmd; 
  delete fDetectorDir;
  delete fHeteroEnableCmd;
  delete fHeteroMaterialCmd;
  delete fHeteroSizeCmd;
  delete fHeteroPositionCmd;
  delete fHeteroDir;
}

void BrachyDetectorMessenger::SetNewValue(G4UIcommand* command,G4String newValue)
{ 
  // Change the material of the phantom
  if( command == fPhantomMaterialCmd )
   { fDetector -> SetPhantomMaterial(newValue);}

  // Switch the source in the phantom
  if( command == fSourceCmd )
   {
    if(newValue=="Iodine" || newValue=="TG186"|| newValue=="Leipzig" || newValue== "Flexi" || newValue== "Oncura")
     { 
       fDetector -> SelectBrachytherapicSeed(newValue); 
       fDetector -> SwitchBrachytherapicSeed();
      }
   }

  if (command == fHeteroEnableCmd) {
    fDetector->EnableHeterogeneity(fHeteroEnableCmd->GetNewBoolValue(newValue));
  }

  if (command == fHeteroMaterialCmd) {
    fDetector->SetHeterogeneityMaterial(newValue);
  }

  if (command == fHeteroSizeCmd) {
    fDetector->SetHeterogeneitySize(fHeteroSizeCmd->GetNew3VectorValue(newValue));
  }

  if (command == fHeteroPositionCmd) {
    fDetector->SetHeterogeneityPosition(fHeteroPositionCmd->GetNew3VectorValue(newValue));
  }
}


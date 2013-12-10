/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_ELECTRON_H
#define KAPPA_ELECTRON_H

#include "KTrack.h"
#include "KMetadata.h"
#include "KJetMET.h"

<<<<<<< HEAD

=======
>>>>>>> 7f27c71be8613bbcc8e11ef242b306b780533e20
#include <algorithm>

struct KDataElectron : KDataLV
{
	char charge;
<<<<<<< HEAD
    bool isEB, isEE;


    float dr03TkSumPt;              //track iso deposit with electron footprint removed.
    float dr03EcalRecHitSumEt;      //ecal iso deposit with electron footprint removed.
    float dr03HcalDepth1TowerSumEt; //hcal depht 1 iso deposit with electron footprint removed.
    float dr03HcalDepth2TowerSumEt; //hcal depht 2 iso deposit with electron footprint removed. 

    float dr04TkSumPt;
    float dr04EcalRecHitSumEt;
    float dr04HcalDepth1TowerSumEt;
    float dr04HcalDepth2TowerSumEt; 

    bool ecalDrivenSeed;
    bool ecalDriven;


    bool isEcalEnergyCorrected; //true if ecal energy has been corrected.
    float ecalEnergy;           //the new corrected value, or the supercluster energy.
    float ecalEnergyError;
    //bool isMomentumCorrected;   //true if E-p combination has been applied.
    float trackMomentumError;   //track momentum error from gsf fit.
    //float electronMomentumError;//the final electron momentum error. 


    float mva; // PF data
    int status;
=======

>>>>>>> 7f27c71be8613bbcc8e11ef242b306b780533e20
};
typedef std::vector<KDataElectron> KDataElectrons;

#endif

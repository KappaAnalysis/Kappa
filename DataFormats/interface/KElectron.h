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

#include <algorithm>

struct KDataElectron : KLepton
{
	KDataTrack track;

	bool isEB, isEE;

/* if needed, all these could be easily added in one byte as is done for muons:
https://github.com/cms-sw/cmssw/blob/CMSSW_5_3_X/DataFormats/EgammaCandidates/interface/GsfElectron.h
    bool isEB(): true if the electron is in ECAL Barrel.
    bool isEE(): true if the electron is in ECAL Endcaps.
    bool isEBEEGap(): true if the electron is in the crack between EB and EE.
    bool isEBEtaGap(): true if the electron is in EB, and in the eta gaps between modules.
    bool isEBPhiGap(): true if the electron is in EB, and in the phi gaps between modules.
    bool isEEDeeGap(): true if the electron is in EE, and in the gaps between dees.
    bool isEERingGap(): true if the electron is in EE, and in the gaps between rings.

Within the electron, the corresponding values are grouped into an attribute called fiducialFlags_, of type FiducialFlags. One will see this attribute when TBrowsing an edm ROOT file. The global getter CMS.GsfElectron::fiducialFlags() gives direct access to the attribute. Also, a few more utility methods are combining some of the flags:

    bool isEBGap(): true if isEBEtaGap() or isEBPhiGap().
    bool isEEGap(): true if isEEDeeGap() or isEERingGap().
    bool isGap(): true if isEBEEGap() or isEBGap() or isEEGap().
*/

	float trackIso03;		// dr03TkSumPt: track iso deposit with electron footprint removed.
	float ecalIso03;		// dr03EcalRecHitSumEt: ecal iso deposit with electron footprint removed.
	float hcal1Iso03;		// dr03HcalDepth1TowerSumEt: hcal depht 1 iso deposit with electron footprint removed.
	float hcal2Iso03;		// dr03HcalDepth2TowerSumEt: hcal depht 2 iso deposit with electron footprint removed.

	float trackIso04;
	float ecalIso04;
	float hcal1Iso04;
	float hcal2Iso04;

	bool ecalDrivenSeed;
	bool ecalDriven;


	bool isEcalEnergyCorrected;	//true if ecal energy has been corrected.
	float ecalEnergy;					//the new corrected value, or the supercluster energy.
	float ecalEnergyError;
	//bool isMomentumCorrected;	//true if E-p combination has been applied.
	float trackMomentumError;		//track momentum error from gsf fit.
	//float electronMomentumError;//the final electron momentum error.


	float mva; // PF data
	int status;
	float idMvaTrigV0;
	float idMvaTrigNoIPV0;
	float idMvaNonTrigV0;

	bool hasConversionMatch;
};
typedef std::vector<KDataElectron> KDataElectrons;

#endif

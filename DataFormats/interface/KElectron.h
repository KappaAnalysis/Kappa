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
#include "Math/GenVector/PositionVector3D.h"

struct KElectron : KLepton
{
	/// Isolation variables
	float trackIso03;   // dr03TkSumPt: track iso deposit with electron footprint removed (Delta R = 0.3)
	float ecalIso03;    // dr03EcalRecHitSumEt: ecal iso deposit with electron footprint removed.
	float hcal1Iso03;   // dr03HcalDepth1TowerSumEt: hcal depht 1 iso deposit with electron footprint removed.
	float hcal2Iso03;   // dr03HcalDepth2TowerSumEt: hcal depht 2 iso deposit with electron footprint removed.
	inline float hcalIso03() const { return hcal1Iso03 + hcal2Iso03; };  // dr03HcalTowerSumEt

	float trackIso04;   // same isolations with Delta R = 0.4
	float ecalIso04;
	float hcal1Iso04;
	float hcal2Iso04;
	inline float hcalIso04() const { return hcal1Iso04 + hcal2Iso04; };

    float pfIsoCh;      // PF isolation from PAT electrons isoVals
    float pfIsoEm;
    float pfIsoNh;

	/// Identification
	/// Variables for cutbased electron identification (cf. reco::GsfElectron)
	// https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaCutBasedIdentification
	float deltaEtaSuperClusterTrackAtVtx;  // dEtaIn
	float deltaPhiSuperClusterTrackAtVtx;  // dPhiIn
	float sigmaIetaIeta;
	float hadronicOverEm;
	float fbrem;
	float eSuperClusterOverP;
	float superclusterEnergy;      //supercluster
	RMPoint superclusterPosition;
	bool ecalDrivenSeed;
	bool ecalDriven;
	bool isEcalEnergyCorrected;    //true if ecal energy has been corrected. = isEcalScaleCorrected
	float ecalEnergy;              //the new corrected value, or the supercluster energy.
	float ecalEnergyError;
	bool isMomentumCorrected;      //true if E-p combination has been applied.
	float trackMomentumError;      //track momentum error from gsf fit.
	float electronMomentumError;   //the final electron momentum error.
	bool hasConversionMatch;
	int status;
	/// calculable quantities: p_in and 1/E - 1/p_in:
	inline float trackMomentumAtVtxP() const { return ecalEnergy / eSuperClusterOverP; };
	inline float invEMinusInvP() const { return (1.0f - eSuperClusterOverP) / ecalEnergy; };

	/// cutbased isolation results
	unsigned char cutbasedIDs;
	inline bool cutbasedIdLoose()  const { return (cutbasedIDs & (1 << 0)); };
	inline bool cutbasedIdMedium() const { return (cutbasedIDs & (1 << 1)); };
	inline bool cutbasedIdTight()  const { return (cutbasedIDs & (1 << 2)); };
	inline bool cutbasedIdVeto()   const { return (cutbasedIDs & (1 << 3)); };


	// ECAL region: bits are set according to reco::GsfElectron::FiducialFlags
	unsigned char fiducialFlags;  // container for all 7 bits
	// accessor functions: must be in sync with KElectronProducer
	inline bool isEB()        const { return (fiducialFlags & (1 << 0)); };    // is e in ECAL Barrel (EB)
	inline bool isEE()        const { return (fiducialFlags & (1 << 1)); };    // is e in ECAL Endcaps (EE)
	inline bool isEBEEGap()   const { return (fiducialFlags & (1 << 2)); };    // is e in the crack between EB and EE
	inline bool isEBEtaGap()  const { return (fiducialFlags & (1 << 3)); };    // is e in EB and in the eta gaps between modules
	inline bool isEBPhiGap()  const { return (fiducialFlags & (1 << 4)); };    // is e in EB and in the phi gaps between modules
	inline bool isEEDeeGap()  const { return (fiducialFlags & (1 << 5)); };    // is e in EE and in the gaps between dees
	inline bool isEERingGap() const { return (fiducialFlags & (1 << 6)); };    // is e in EE and in the gaps between rings
	inline bool isEBGap()     const { return isEBEtaGap() || isEBPhiGap(); };  // is e in in any EB gap
	inline bool isEEGap()     const { return isEEDeeGap() || isEERingGap(); }; // is e in any EE gap
	inline bool isGap()       const { return isEBEEGap() || isEBGap() || isEEGap(); };  // is e in any gap

	/// Configurable MVA IDs
	/** Run2: https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
	 *  Full instructions in Producer/interface/KElectrons_cff
	 */
	std::vector<float> electronIds;

	float getId(const std::string &name, const KElectronIdMetadata *idMetadata) const
	{
		for (unsigned int i = 0; i < idMetadata->idNames.size(); ++i)
		{
			if (idMetadata->idNames[i] == name)
				return electronIds[i];
		}
		std::cout << "ElectronId " << name << " not available!" << std::endl;
		exit(1);
	}

};
typedef std::vector<KElectron> KElectrons;

#endif

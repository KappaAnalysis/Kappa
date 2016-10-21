//- Copyright (c) 2013 - All Rights Reserved
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_ELECTRON_H
#define KAPPA_ELECTRON_H

#include "KLepton.h"


struct KElectronMetadata
{
	virtual ~KElectronMetadata() {};

	std::vector<std::string> idNames;  //< names of configurable electron IDs
};

namespace KElectronType { enum Type
{
	ecalEnergyCorrected = 0, //< true if ecal energy has been corrected = isEcalScaleCorrected
	momentumCorrected   = 1, //< true if E-p combination has been applied.
	ecalDriven          = 2, //< 
	trackerDriven       = 3, //<
	cutPreselected      = 4, //<
	mvaPreselected      = 5, //<
	ecalDrivenSeed        = 6, //< can be replaced if space is needed = preselection + ecalDriven
	hasConversionMatch    = 7  //<
};
}


struct KElectron : public KLepton
{
	virtual ~KElectron() {};

	/// identification results
	std::vector<float> electronIds; //< configurable electron IDs (mainly for MVA IDs)

	/// identification variables
	/// Variables for cutbased electron identification (cf. reco::GsfElectron)
	/// https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaCutBasedIdentification?rev=32
	unsigned char fiducialFlags;  //< ECAL region: bits are set according to reco::GsfElectron::FiducialFlags
	unsigned char electronType;   //< cf. enum KElectronType::Type
	float dEtaIn;                 //< deltaEtaSuperClusterTrackAtVtx
	float dPhiIn;                 //< deltaPhiSuperClusterTrackAtVtx
	float dEtaInSeed;
	float sigmaIetaIeta;
	float full5x5_sigmaIetaIeta;
	float hadronicOverEm;
	float fbrem;
	//d0 dz vertexfitprob + missing hits
	float eSuperClusterOverP;
	float superclusterEnergy;      
	float ecalEnergy;             //< the new corrected value, or the supercluster energy.
	float ecalEnergyErr;
	float trackMomentumErr;       //< track momentum error from gsf fit.
	float electronMomentumErr;    //< the final electron momentum error.
	RMPoint superclusterPosition; //< position of the supercluster

	/// Isolation results
	float trackIso;   //< dr03TkSumPt: track iso deposit with electron footprint removed (Delta R = 0.3)
	float ecalIso;    //< dr03EcalRecHitSumEt: ecal iso deposit with electron footprint removed.
	float hcal1Iso;   //< dr03HcalDepth1TowerSumEt: hcal depht 1 iso deposit with electron footprint removed.
	float hcal2Iso;   //< dr03HcalDepth2TowerSumEt: hcal depht 2 iso deposit with electron footprint removed.

	/// calculable quantities:  
	inline float pIn() const { return ecalEnergy / eSuperClusterOverP; };  //< trackMomentumAtVtxP
	inline float invEMinusInvP() const { return (1.0f - eSuperClusterOverP) / ecalEnergy; }; //< 1/E - 1/p_in
	inline float hcalIso() const { return hcal1Iso + hcal2Iso; };  //< dr03HcalTowerSumEt

	/// get configurable (MVA) ID
	float getId(const std::string &name, const KElectronMetadata* meta) const
	{
		for (unsigned int i = 0; i < meta->idNames.size(); ++i)
		{
			if (meta->idNames[i] == name)
				return electronIds[i];
		}
		std::cout << "Electron ID " << name << " not available!" << std::endl;
		exit(1);
	}

	/** Accessor functions to gap values
	 *  must be in sync with KElectronProducer
	 */
	inline bool isEB()        const { return (fiducialFlags & (1 << 0)); };    //< is e in ECAL Barrel (EB)
	inline bool isEE()        const { return (fiducialFlags & (1 << 1)); };    //< is e in ECAL Endcaps (EE)
	inline bool isEBEEGap()   const { return (fiducialFlags & (1 << 2)); };    //< is e in the crack between EB and EE
	inline bool isEBEtaGap()  const { return (fiducialFlags & (1 << 3)); };    //< is e in EB and in the eta gaps between modules
	inline bool isEBPhiGap()  const { return (fiducialFlags & (1 << 4)); };    //< is e in EB and in the phi gaps between modules
	inline bool isEEDeeGap()  const { return (fiducialFlags & (1 << 5)); };    //< is e in EE and in the gaps between dees
	inline bool isEERingGap() const { return (fiducialFlags & (1 << 6)); };    //< is e in EE and in the gaps between rings
	inline bool isEBGap()     const { return isEBEtaGap() || isEBPhiGap(); };  //< is e in in any EB gap
	inline bool isEEGap()     const { return isEEDeeGap() || isEERingGap(); }; //< is e in any EE gap
	inline bool isGap()       const { return isEBEEGap() || isEBGap() || isEEGap(); };  // is e in any gap


};
typedef std::vector<KElectron> KElectrons;

#endif

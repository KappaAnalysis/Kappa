//- Copyright (c) 2014 - All Rights Reserved
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_LEPTON_H
#define KAPPA_LEPTON_H

#include "KTrack.h"

namespace KLeptonFlavour { enum Type
{
	NONE     = 0,
	ELECTRON = 1,
	MUON     = 2,
	TAU      = 3
};
}

namespace KLeptonId { enum Type
{
	ANY    = 0,  //< returns true if the information for any ID was filled
	LOOSE  = 1,  //< e/mu/tau loose ID
	MEDIUM = 2,  //< e/tau medium ID
	TIGHT  = 3,  //< e/mu tight ID
	VETO   = 4,  //< e veto ID
	SOFT   = 5,  //< mu soft ID
	HIGHPT = 6,  //< mu high pt ID
	CUSTOM = 7,  //< empty bit for any userdefined ID
	LOOSEELECTRONREJECTION = 4, // tau discriminator
	LOOSEMUONREJECTION     = 5, // tau discriminator
	TIGHTMUONREJECTION     = 6  // tau discriminator
};
}

struct KLepton : public KLV
{
public:
	unsigned char leptonInfo;  //< bitset containing the flavour, charge and user bits
	unsigned char ids;         //< most relevant IDs of the lepton
	float sumChargedHadronPt;  //< sum pt of charged hadrons for isolation
	float sumNeutralHadronEt;  //< sum Et of neutral hadrons for isolation
	float sumPhotonEt;         //< sum Et of photons for isolation
	float sumPUPt;             //< sum pt of pile-up for isolation
	KTrack track;              //< (main) track of the lepton (e: GSF, mu: inner, tau: lead. PF candidate)

	// access functions for leptonInfo
	/// lepton flavour according to KLeptonFlavour::Type
	inline KLeptonFlavour::Type flavour() const { return KLeptonFlavour::Type(leptonInfo & KLeptonFlavourMask); };
	/// lepton charge (+1 or -1)
	inline int charge() const { return ((leptonInfo & KLeptonChargeMask) ? +1 : -1); };
	/// whether the stored object is reconstructed using PF objects
	inline bool isPF() const { return (leptonInfo & KLeptonPFMask); };
	/// if the normal track is not available, the producer can fill the track information with a second option and set this flag
	inline bool isAlternativeTrack() const { return (leptonInfo & KLeptonAlternativeTrackMask); };

	// access function for ID bitset ids
	/// returns true if the ID is set and valid for this flavour
	inline bool isAvailable() const { return (ids & (1 << KLeptonId::ANY)); };    // e, mu, tau
	inline bool idLoose()     const { return (ids & (1 << KLeptonId::LOOSE)); };  // e, mu, tau
	inline bool idMedium()    const { return (ids & (1 << KLeptonId::MEDIUM)); }; // e, (mu,) tau
	inline bool idTight()     const { return (ids & (1 << KLeptonId::TIGHT)); };  // e, mu, tau
	inline bool idVeto()      const { return (ids & (1 << KLeptonId::VETO)   && (KLeptonFlavour::ELECTRON == (leptonInfo & KLeptonFlavourMask))); }; // e
	inline bool idSoft()      const { return (ids & (1 << KLeptonId::SOFT)   && (KLeptonFlavour::MUON == (leptonInfo & KLeptonFlavourMask))); };     // mu
	inline bool idHighPt()    const { return (ids & (1 << KLeptonId::HIGHPT) && (KLeptonFlavour::MUON == (leptonInfo & KLeptonFlavourMask))); };     // mu
	inline bool idLooseElectronRejection() const { return (ids & (1 << KLeptonId::LOOSEELECTRONREJECTION) && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau
	inline bool idLooseMuonRejection()     const { return (ids & (1 << KLeptonId::LOOSEMUONREJECTION)     && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau
	inline bool idTightMuonRejection()     const { return (ids & (1 << KLeptonId::TIGHTMUONREJECTION)     && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau

	/// PF isolation with delta beta corrections (default fraction of pile-up is 0.5)
	inline double pfIso(const double puFraction=0.5) const
	{
		return sumChargedHadronPt + std::max(0.0,
			sumNeutralHadronEt + sumPhotonEt - puFraction * sumPUPt);
	}

	/// rho effective area isolation (approximation)
	/** this is an alternative method for pile-up subtraction:
	    PFIso = PF(ChHad PFNoPU) + Max(PF(Nh+Ph) - rho’EA), 0.0) with rho'=max(rho,0)
	    approximation: effective area as a circle area
	    rho is usually provided by a KPileupDensity object
	*/
	double pfIsoRho(const double rho = 0.0, const double radius = 0.4) const
	{
		double area = radius * radius * 3.14159;
		return std::max(0.0, pfIso(0.0) - std::max(rho * area, 0.0));
	}
};
typedef std::vector<KLepton> KLeptons;

#endif

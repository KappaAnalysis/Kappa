//- Copyright (c) 2014 - All Rights Reserved
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_LEPTON_H
#define KAPPA_LEPTON_H

#include "Hash.h"
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
	MEDIUM = 2,  //< e/mu/tau medium ID
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
	virtual ~KLepton() {};

	unsigned char leptonInfo;  //< bitset containing the flavour, charge and user bits
	unsigned char ids;         //< most relevant IDs of the lepton
	std::size_t internalId;    //< most relevant IDs of the lepton
	float sumChargedHadronPt;  //< sum pt of charged hadrons for isolation
	float sumNeutralHadronEt;  //< sum Et of neutral hadrons for isolation
	float sumPhotonEt;         //< sum Et of photons for isolation
	float sumPUPt;             //< sum pt of pile-up for isolation
	float sumChargedAllPt;     //< sum pt of charged hadrons for isolation // TODO: not filled. Remove for next dictchange
	float dz;                  //< impact parameter in z direction
	float dxy;                 //< impact parameter in transverse plane
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
	inline bool idMedium()    const { return (ids & (1 << KLeptonId::MEDIUM)); }; // e, mu, tau
	inline bool idTight()     const { return (ids & (1 << KLeptonId::TIGHT)); };  // e, mu, tau
	inline bool idVeto()      const { return (ids & (1 << KLeptonId::VETO)   && (KLeptonFlavour::ELECTRON == (leptonInfo & KLeptonFlavourMask))); }; // e
	inline bool idSoft()      const { return (ids & (1 << KLeptonId::SOFT)   && (KLeptonFlavour::MUON == (leptonInfo & KLeptonFlavourMask))); };     // mu
	inline bool idHighPt()    const { return (ids & (1 << KLeptonId::HIGHPT) && (KLeptonFlavour::MUON == (leptonInfo & KLeptonFlavourMask))); };     // mu
	inline bool idLooseElectronRejection() const { return (ids & (1 << KLeptonId::LOOSEELECTRONREJECTION) && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau
	inline bool idLooseMuonRejection()     const { return (ids & (1 << KLeptonId::LOOSEMUONREJECTION)     && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau
	inline bool idTightMuonRejection()     const { return (ids & (1 << KLeptonId::TIGHTMUONREJECTION)     && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau

	/// PF isolation with delta beta corrections (default fraction of pile-up is 0.5)
	inline float pfIso(const float puFraction=0.5) const
	{
		return sumChargedHadronPt + std::max(0.0f,
			sumNeutralHadronEt + sumPhotonEt - puFraction * sumPUPt);
	}
	
	// (signed) PDG ID
	int pdgId() const
	{
		int pdgId = 0;
		switch (flavour())
		{
			case KLeptonFlavour::ELECTRON: pdgId = 11; break;
			case KLeptonFlavour::MUON: pdgId = 13; break;
			case KLeptonFlavour::TAU: pdgId = 15; break;
			default: pdgId = 0;
		}
		if (charge() > 0)
		{
			pdgId *= -1;
		}
		return pdgId;
	}

	/// rho effective area isolation (approximation)
	/** this is an alternative method for pile-up subtraction:
	    PFIso = PF(ChHad PFNoPU) + Max(PF(Nh+Ph) - rho’EA), 0.0) with rho'=max(rho,0)
	    approximation: effective area as a circle area
	    rho is usually provided by a KPileupDensity object
	*/
	double pfIsoRho(const double rho = 0.0, const double area = 0.5026544) const
	{
		return std::max(0.0, static_cast<double>(pfIso(0.0)) - std::max(rho * area, 0.0));
	}
	
	unsigned int getHash() const
	{
		return getLVChargeHash(p4.Pt(), p4.Eta(), p4.Phi(), p4.mass(), charge());
	}
	
};
typedef std::vector<KLepton> KLeptons;

struct KLeptonPair
{
	virtual ~KLeptonPair() {};

	unsigned int hashLepton1;
	unsigned int hashLepton2;
	
	double dca3D;
	double dca3DError;
	double dca2D;
	double dca2DError;
	
	inline bool operator ==(std::pair<KLepton*, KLepton*> const& leptons) const
	{
		return (((leptons.first->getHash() == hashLepton1) && (leptons.second->getHash() == hashLepton2)) ||
		        ((leptons.first->getHash() == hashLepton2) && (leptons.second->getHash() == hashLepton1)));
	}
	template<class KLeptonPairsIterator>
	inline static KLeptonPairsIterator find(KLeptonPairsIterator const& first, KLeptonPairsIterator const& last,
	                                        std::pair<KLepton*, KLepton*> const& leptons)
	{
		for (KLeptonPairsIterator leptonPair = first; leptonPair != last; ++leptonPair)
		{
			if (*leptonPair == leptons)
			{
				return leptonPair;
			}
		}
		return last;
	}
};
typedef std::vector<KLeptonPair> KLeptonPairs;

#endif

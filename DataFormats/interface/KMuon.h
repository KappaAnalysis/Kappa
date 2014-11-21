/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_MUON_H
#define KAPPA_MUON_H

#include "KTrack.h"
#include <algorithm>

/// isGoodMuon from DataFormats/MuonReco/interface/MuonSelectors.h
namespace KGoodMuon {

enum KGoodMuonType
{
	All = 0,                      //< dummy options - always true
	AllGlobalMuons = 1,           //< checks isGlobalMuon flag
	AllStandAloneMuons = 2,       //< checks isStandAloneMuon flag
	AllTrackerMuons = 3,          //< checks isTrackerMuon flag
	TrackerMuonArbitrated = 4,    //< resolve ambiguity of sharing segments
	AllArbitrated = 5,            //< all muons with the tracker muon arbitrated
	GlobalMuonPromptTight = 6,    //< global muons with tighter fit requirements
	TMLastStationLoose = 7,       //< penetration depth loose selector
	TMLastStationTight = 8,       //< penetration depth tight selector
	TM2DCompatibilityLoose = 9,   //< likelihood based loose selector
	TM2DCompatibilityTight = 10,  //< likelihood based tight selector
	TMOneStationLoose = 11,       //< require one well matched segment
	TMOneStationTight = 12,       //< require one well matched segment
	TMLastStationOptimizedLowPtLoose = 13, //< combination of TMLastStation and TMOneStation
	TMLastStationOptimizedLowPtTight = 14, //< combination of TMLastStation and TMOneStation
	GMTkChiCompatibility = 15,    //< require tk stub have good chi2 relative to glb track
	GMStaChiCompatibility = 16,   //< require sta stub have good chi2 compatibility relative to glb track
	GMTkKinkTight = 17,           //< require a small kink value in the tracker stub
	TMLastStationAngLoose = 18,   //< TMLastStationLoose with additional angular cuts
	TMLastStationAngTight = 19,   //< TMLastStationTight with additional angular cuts
	TMOneStationAngLoose = 20,    //< TMOneStationLoose with additional angular cuts
	TMOneStationAngTight = 21,    //< TMOneStationTight with additional angular cuts
	TMLastStationOptimizedBarrelLowPtLoose = 22, //< combination of TMLastStation and TMOneStation but with low pT optimization in barrel only
	TMLastStationOptimizedBarrelLowPtTight = 23, //< combination of TMLastStation and TMOneStation but with low pT optimization in barrel only
	RPCMuLoose = 24               //< checks isRPCMuon flag (require two well matched hits in different RPC layers)
};
}

struct KMuonMetadata
{
	std::vector<std::string> hltNames;
};

struct KMuon : public KLepton
{
	/*
	virtual ~KMuon() {};
	
	virtual bool isMuon() {
		return true;
	};
	*/
	
	KTrack globalTrack;
	KTrack innerTrack;
	KTrack outerTrack;
	KTrack bestTrack;

	/// type of the muon: bits are set according to reco::Muon::type_;
	unsigned char type;

	inline bool isTrackerMuon() const    { return (type & (1 << 2)); };
	inline bool isCaloMuon() const       { return (type & (1 << 4)); };
	inline bool isStandAloneMuon() const { return (type & (1 << 3)); };
	inline bool isGlobalMuon() const     { return (type & (1 << 1)); };
	inline bool isPFMuon() const         { return (type & (1 << 5)); };

	float hcalIso03;		///< hcal isolation as given by muon.isolationR03().hadEt
	float ecalIso03;		///< ecal isolation as given by muon.isolationR03().emEt
	float trackIso03;		///< tracker isolation as given by muon.isolationR03().sumPt

	float pfIso04;			///< PF isolation

	float hcalIso05;
	float ecalIso05;
	float trackIso05;

	unsigned int isGoodMuon;	///< bitmask

	float caloComp, segComp;

	int nChambers;
	int nMatches;

	unsigned long long hltMatch;

	/// \f$\eta\f$ and \f$\phi\f$ after the propagation to the muon system, this quantity
	/// is necessary for the matching to L1 trigger objects
	float eta_propagated, phi_propagated;

	/// returns whether a given HLT fired
	/** the information is read from the metadata
		@param name Name of the HLT
		@param muonMetadata reference to the meta data object
	*/
	bool hltFired(const std::string& name, const KMuonMetadata* muonMetadata) const
	{
		std::vector<std::string>::const_iterator itSearch = std::lower_bound(muonMetadata->hltNames.begin(), muonMetadata->hltNames.end(), name);
		if (itSearch != muonMetadata->hltNames.end())
			return (hltMatch & (1ull << (itSearch - muonMetadata->hltNames.begin()))) != 0;
		return false; // given HLT does not exist
	}

	double puSubtractedPFIso04(const KPileupDensity* puRho) const
	{
		// jetArea == NULL --> no PU subtraction
		if(puRho == NULL) return pfIso04;

		static const double coneSize = 0.4;
		return std::max(0.0, pfIso04 - puRho->rho * coneSize * coneSize * 3.14159);
	}
};
typedef std::vector<KMuon> KMuons;


struct KL1Muon : public KLV
{
	// bit    meaning
	// 0-2    quality
	// 3      isForward
	// 4      isRPC
	// 5      isMip
	// 6      isIsolated
	// 7-10   bx (15 = value of bx>=14)
	// 11-13  detector
	unsigned short state; // bit map

	int quality() const { return (state & ( 7 )); };
	bool isForward() const { return (state & (1 << 3)); };
	bool isRPC() const { return (state & (1 << 4)); };
	bool isMip() const { return (state & (1 << 5)); };
	bool isIsolated() const { return (state & (1 << 6)); };
	int bx() const { return ((state & (15 << 7)) >> 7) - 7; };
	int detector() const { return ((state & (7 << 11)) >> 11);};
};
typedef std::vector<KL1Muon> KL1Muons;

#endif

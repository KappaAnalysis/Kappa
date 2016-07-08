//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_MUON_H
#define KAPPA_MUON_H

#include "KLepton.h"
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
	virtual ~KMuonMetadata() {};

	std::vector<std::string> hltNames;  //< names of available HLT paths
};

struct KMuon : public KLepton
{
	virtual ~KMuon() {};

	/// global track in addition to KLepton track == innerTrack, no outer or best track
	KTrack globalTrack;

	/// ID variables
	unsigned long isGoodMuonBits; //< isGoodMuon bitmask, used by soft ID
	unsigned char type;           //< type of the muon: bits are set according to reco::Muon::type_ (used by various IDs)

	/// ID var from track: nValidPixelHits, nTrackerLayers
	/// ID var from globalTrack: normalizedChi2=chi2/nDOF, nValidMuonHits
	/// ID var from the bestTrack which is not saved entirely:
	float dxy; //< dxy from vertex using IPTools like PAT
	float dz;  //< dz from vertex using bestTrack->dz(vtx)

	/// muon system information
	short nMatchedStations;
	// unused variables
	short nChambers, nMatches;
	float caloCompatibility, segmentCompatibility;

	/// isolation results
	float trackIso;         //< tracker isolation as given by muon.isolationR03().sumPt
	float hcalIso;          //< hcal detector based isolation as given by muon.isolationR03().hadEt
	float ecalIso;          //< ecal detector basedisolation as given by muon.isolationR03().emEt
	float pfIso03;          //< PF isolation R = 0.3
	float pfIso04;          //< PF isolation R = 0.3
	// deleted: hcalIso03, ecalIso03 and all 05

	/// additional isolation variables for PF isolation which are not stored in a KLepton
	/// DataFormats/MuonReco/interface/MuonPFIsolation.h
	float sumChargedParticlePt;
	float sumNeutralHadronEtHighThreshold;
	float sumPhotonEtHighThreshold;
	float sumChargedParticlePtR04;
	float sumNeutralHadronEtHighThresholdR04;
	float sumPhotonEtHighThresholdR04;
	float sumChargedHadronPtR04;  //< sum pt of charged hadrons for isolation
	float sumNeutralHadronEtR04;  //< sum Et of neutral hadrons for isolation
	float sumPhotonEtR04;         //< sum Et of photons for isolation
	float sumPUPtR04;             //< sum pt of pile-up for isolation
	float sumChargedAllPtR04;     //< sum pt of charged hadrons for isolation

	/// \f$\eta\f$ and \f$\phi\f$ after the propagation to the muon system, this quantity
	/// is necessary for the matching to L1 trigger objects
	float eta_propagated, phi_propagated;

	unsigned long long hltMatch;

	/// variables used in muon id
	float normalizedChiSquare;
	float chiSquareLocalPos;
	float trkKink;
	float validFractionOfTrkHits;
	float relBestTrkErr;

	/// accessor functions to CMSSW muon bitsets
	inline bool isGoodMuon(KGoodMuon::KGoodMuonType bit) const { return (isGoodMuonBits & (1 << bit)); };
	inline bool isGlobalMuon() const     { return (type & (1 << 1)); };
	inline bool isTrackerMuon() const    { return (type & (1 << 2)); };
	inline bool isStandAloneMuon() const { return (type & (1 << 3)); };
	inline bool isCaloMuon() const       { return (type & (1 << 4)); };
	inline bool isPFMuon() const         { return (type & (1 << 5)); };
	inline bool isRPCMuon() const        { return (type & (1 << 6)); };

	float pfIso04high(const float puFraction=0.5) const
	{
		return sumChargedHadronPt + std::max(0.0f,
			sumNeutralHadronEtHighThreshold + sumPhotonEtHighThreshold - puFraction * sumPUPt);
	}

	/// returns whether a given HLT fired
	/** the information is read from the metadata
		@param hltName Name of the HLT
		@param meta reference to the muon meta data object
	*/
	bool hltFired(const std::string& hltName, const KMuonMetadata* meta) const
	{
		std::vector<std::string>::const_iterator itSearch = std::lower_bound(meta->hltNames.begin(), meta->hltNames.end(), hltName);
		if (itSearch != meta->hltNames.end())
			return (hltMatch & (1ull << (itSearch - meta->hltNames.begin()))) != 0;
		return false; // given HLT does not exist
	}
};
typedef std::vector<KMuon> KMuons;


struct KL1Muon : public KLV
{
	virtual ~KL1Muon() {};

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

#ifndef KAPPA_MUON_H
#define KAPPA_MUON_H

#include "KTrack.h"
#include "KMetadata.h"
#include "KJetMET.h"

#include <algorithm>

struct KDataMuon : KDataLV
{
	char charge;

	KDataTrack track;
	KDataTrack globalTrack;
	KDataTrack innerTrack;
	KDataTrack outerTrack;

	// bits are set according to reco::Muon::type_;
	unsigned char type;

	inline bool isTrackerMuon() const    { return (type & (1 << 2)); };
	inline bool isCaloMuon() const       { return (type & (1 << 4)); };
	inline bool isStandAloneMuon() const { return (type & (1 << 3)); };
	inline bool isGlobalMuon() const     { return (type & (1 << 1)); };
	inline bool isPFMuon() const         { return (type & (1 << 5)); };

	float sumPtIso03;		// tracker isolation as given by muon.isolationR03().sumPt
	float hcalIso03;		// hcal isolation as given by muon.isolationR03().hadEt
	float ecalIso03;		// ecal isolation as given by muon.isolationR03().emEt
	float trackIso03;		// user-defined tracker isolation

	float pfIso04;			// PF isolation

	float sumPtIso05;
	float hcalIso05;
	float ecalIso05;
	float trackIso05;

	unsigned int isGoodMuon;	// bitmask

	float caloComp, segComp;

	int numberOfChambers;
	int numberOfMatches;

	unsigned long long hltMatch;

	// eta and phi after the propagation to the muon system, this quantity
	// is necessary for the matching to L1 trigger objects
	float eta_propagated, phi_propagated;

	bool hltFired(const std::string& name, const KLumiMetadata * lumimetadata) const
	{
		std::vector<std::string>::const_iterator itSearch = std::lower_bound(lumimetadata->hltNamesMuons.begin(), lumimetadata->hltNamesMuons.end(), name);
		if (itSearch != lumimetadata->hltNamesMuons.end())
			return (hltMatch & (1ull << (itSearch - lumimetadata->hltNamesMuons.begin()))) != 0;
		return false; // Named HLT does not exist
	}

	double puSubtractedPFIso04(const KJetArea* jetArea) const
	{
		// jetArea == NULL --> no PU subtraction
		if(jetArea == NULL) return pfIso04;

		static const double coneSize = 0.4;
		return std::max(0.0, pfIso04 - jetArea->median * coneSize * coneSize * 3.14159);
	}
};
typedef std::vector<KDataMuon> KDataMuons;

#endif

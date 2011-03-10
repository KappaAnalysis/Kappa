#ifndef KAPPA_MUON_H
#define KAPPA_MUON_H

#include "KTrack.h"
#include "KMetadata.h"

struct KDataMuon : KDataLV
{
	char charge;

	KDataTrack track;
	KDataTrack globalTrack;
	KDataTrack innerTrack;
	KDataTrack outerTrack;

	KDataVertex vertex;

	// Bit 0 - trackerMuon
	// Bit 1 - caloMuon
	// Bit 2 - standaloneMuon
	// Bit 3 - globalMuon
	unsigned char type;

	bool isTrackerMuon() const    { return (type & (1 << 2)); };
	bool isCaloMuon() const       { return (type & (1 << 4)); };
	bool isStandAloneMuon() const { return (type & (1 << 3)); };
	bool isGlobalMuon() const     { return (type & (1 << 1)); };

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
	// both barrel and endcap values are necessary since CSC and DT
	// require different values in the transition region
	float eta_propag_barrel, phi_propag_barrel;
	float eta_propag_endcap, phi_propag_endcap;

	bool hltFired(const std::string& name, const KLumiMetadata * lumimetadata) const
	{
		for(size_t i = 0; i < lumimetadata->hltNamesMuons.size(); ++i)
			if(lumimetadata->hltNamesMuons[i] == name)
				return (hltMatch & (1ull << i)) != 0;
		return false; // Named HLT does not exist
	}
};
typedef std::vector<KDataMuon> KDataMuons;

#endif

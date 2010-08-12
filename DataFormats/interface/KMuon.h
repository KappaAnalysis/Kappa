#ifndef KAPPA_MUON_H
#define KAPPA_MUON_H

#include "KTrack.h"

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

	bool isTrackerMuon()    { return (type & (1 << 2)); };
	bool isCaloMuon()       { return (type & (1 << 4)); };
	bool isStandAloneMuon() { return (type & (1 << 3)); };
	bool isGlobalMuon()     { return (type & (1 << 1)); };

	float sumPtIso03;		// tracker isolation as given by muon.isolationR03().sumPt
	float hcalIso03;		// hcal isolation as given by muon.isolationR03().emEt
	float ecalIso03;		// ecal isolation as given by muon.isolationR03().hadEt
	float trackIso03;		// user-defined tracker isolation

	float sumPtIso05;
	float hcalIso05;
	float ecalIso05;
	float trackIso05;

	unsigned int isGoodMuon;	// bitmask

	float caloComp, segComp;

	int numberOfChambers;
	int numberOfMatches;
	int trackHits;

	int timeNDof;
	float timeAtIpInOut;
	float timeAtIpInOutErr;
	float timeAtIpOutIn;
	float timeAtIpOutInErr;
	int direction;

	unsigned long long hltMatch;
};
typedef std::vector<KDataMuon> KDataMuons;

#endif

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

	bool isTrackerMuon()    { return (type & (1 << 2 )); };
	bool isCaloMuon()       { return (type & (1 << 4 )); };
	bool isStandAloneMuon() { return (type & (1 << 3 )); };
	bool isGlobalMuon()     { return (type & (1 << 1 )); };

	float sumPtIso03;
	float hcalIso03;
	float ecalIso03;
	float trackIso03;

	float sumPtIso05;
	float hcalIso05;
	float ecalIso05;
	float trackIso05;

	float sumPtIso06;
	float hcalIso06;
	float ecalIso06;
	float trackIso06;

	unsigned int isGoodMuon;	// bitmask

	float caloComp, segComp;

	int numberOfChambers;
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

#ifndef KAPPA_TAU_H
#define KAPPA_TAU_H

#include "KBasic.h"

struct KDataTau : KDataLV
{
	char charge;
};
typedef std::vector<KDataTau> KDataTaus;

struct KDataCaloTau : KDataTau
{
	unsigned long long discr;
};
typedef std::vector<KDataCaloTau> KDataCaloTaus;

struct KDataPFTau : KDataTau
{
	float emFraction;

	int cntSignalChargedHadrCands, cntSignalGammaCands, cntSignalNeutrHadrCands, cntSignalCands;

	RMDataLV leadTrack;
	RMDataLV leadChargedHadrTrack;
	RMDataLV leadNeutralTrack;

	//bool longLived
	int cntSignalTracks;

	bool hasID(std::string name, KLumiMetadata * lumimetadata)
	{
		// to be filled...
		return false;
	}
};
typedef std::vector<KDataPFTau> KDataPFTaus;

struct KDataGenTau : KDataTau
{
	RMDataLV p4_vis;		// momenta of visible particles
	int status;
	char decayMode;
	//  0 - undefined
	//	1 - electron
	//	2 - muon
	// >2 - hadronic
	// most significant bit (1<<15):
	//		0 = tau
	//		1 = descendant of a tau
	KDataVertex vertex;
};
typedef std::vector<KDataGenTau> KDataGenTaus;

#endif

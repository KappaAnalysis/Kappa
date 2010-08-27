#ifndef KAPPA_TAU_H
#define KAPPA_TAU_H

#include "KBasic.h"
#include "KMetadata.h"

struct KDataTau : KDataLV
{
	unsigned long long discr;

	char charge;
};
typedef std::vector<KDataTau> KDataTaus;

struct KDataCaloTau : KDataTau
{
	bool hasID(const std::string& name, const KLumiMetadata * lumimetadata) const
	{
		for(size_t i = 0; i < lumimetadata->discrTau.size(); ++i)
			if(lumimetadata->discrTau[i] == name)
				return (discr & (1ull << i)) != 0;
		return false; // Named discriminator does not exist
	}
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

	bool hasID(const std::string& name, const KLumiMetadata * lumimetadata) const
	{
		for(size_t i = 0; i < lumimetadata->discrTauPF.size(); ++i)
			if(lumimetadata->discrTauPF[i] == name)
				return (discr & (1ull << i)) != 0;
		return false; // Named discriminator does not exist
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

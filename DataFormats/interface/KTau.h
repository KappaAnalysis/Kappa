/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_TAU_H
#define KAPPA_TAU_H

#include "KBasic.h"
#include "KMetadata.h"

struct KDataTau : KDataLV
{
	unsigned long long discr;

	char charge;

	bool hasID(const std::string& name, const KTauDiscriminatorMetadata * lumimetadata) const
	{
		for(size_t i = 0; i < lumimetadata->discriminatorNames.size(); ++i)
			if(lumimetadata->discriminatorNames[i] == name)
				return (discr & (1ull << i)) != 0;
		return false; // Named discriminator does not exist
	}
};
typedef std::vector<KDataTau> KDataTaus;

struct KDataCaloTau : KDataTau {};
typedef std::vector<KDataCaloTau> KDataCaloTaus;

struct KDataPFTau : KDataTau
{
	float emFraction;

	int nSignalChargedHadrCands, nSignalGammaCands, nSignalNeutrHadrCands, nSignalPiZeroCands, nSignalCands;
	int nSignalTracks;

	RMDataLV leadCand;
	RMDataLV leadChargedHadrCand;
	RMDataLV leadNeutralCand;

	KDataTrack leadCandTrack;

	//bool longLived
	int hpsDecayMode; // hadronic decay mode as identified by HPS algorithm
};
typedef std::vector<KDataPFTau> KDataPFTaus;

struct KDataGenTau : KGenParticle
{
	RMDataLV p4_vis;		// momenta of visible particles
	unsigned char decayMode;
	//  0 - undefined
	//	1 - electron
	//	2 - muon
	// >2 - hadronic
	//      3 - 1prong
	//      4 - 3prong
	//      5 - >3prong
	// most significant bit (1<<7):
	//		0 = tau
	//		1 = descendant of a tau
	RMPoint vertex;

	static const int DescendantPosition = 7;
	static const int DescendantMask = 1 << DescendantPosition;

	bool isElectronicDecay() const { return (decayMode & ~DescendantMask) == 1; }
	bool isMuonicDecay() const { return (decayMode & ~DescendantMask) == 2; }
	bool isHadronicDecay() const { return (decayMode & ~DescendantMask) > 2; }

	bool isDescendant() const { return (decayMode & DescendantMask) != 0; }
};
typedef std::vector<KDataGenTau> KDataGenTaus;

#endif

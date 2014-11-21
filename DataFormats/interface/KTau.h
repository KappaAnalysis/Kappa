/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_TAU_H
#define KAPPA_TAU_H

#include "KTrack.h"


struct KTauMetadata
{
	std::vector<std::string> binaryDiscriminatorNames;
	std::vector<std::string> floatDiscriminatorNames;
};

/// Basic tau data format
/** This contains the tau discriminators, the decay mode and the em-fraction
    copy from DataFormats/TauReco/interface/PFTau.h
 */
struct KBasicTau : public KLepton
{
	int decayMode;     //< hadronic decay mode as identified by HPS algorithm
	float emFraction;  //< electromagnetic energy fraction

	/// container for tau discriminators with binary values
	unsigned long long binaryDiscriminators;
	/// container for tau discriminators with real (float) values
	std::vector<float> floatDiscriminators;

	/// function to access tau discriminators with binary values
	bool getId(const std::string& name, const KTauMetadata* meta) const
	{
		for(size_t i = 0; i < meta->binaryDiscriminatorNames.size(); ++i)
			if(meta->binaryDiscriminatorNames[i] == name)
				return (binaryDiscriminators & (1ull << i)) != 0;
		return false; // Named discriminator does not exist
	}

	/// function to access tau discriminators with real values
	float getDiscriminator(const std::string& name, const KTauMetadata* meta) const
	{
		for(size_t i = 0; i < meta->floatDiscriminatorNames.size(); ++i)
			if (meta->floatDiscriminatorNames[i] == name)
				return floatDiscriminators[i];
		return -999.0; // Named discriminator does not exist
	}
};
typedef std::vector<KBasicTau> KBasicTaus;


struct KTau : public KBasicTau
{
	float emFraction;

	int nSignalChargedHadrCands, nSignalGammaCands, nSignalPiZeroCands, nSignalCands;
	int nSignalTracks;

	KLV leadCand;
	KLV leadChargedHadrCand;
	KLV leadNeutralCand;

	KPFCandidates signalChargedHadrCands;
	KPFCandidates signalGammaCands;
	KLVs signalPiZeroCands;

	KTrack track;

	//bool longLived
	int hpsDecayMode; // hadronic decay mode as identified by HPS algorithm
	int tauKey;
};
typedef std::vector<KTau> KTaus;

#endif

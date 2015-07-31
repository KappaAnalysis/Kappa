//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_TAU_H
#define KAPPA_TAU_H

#include "KLepton.h"

struct KTauMetadata
{
	std::vector<std::string> binaryDiscriminatorNames; ///< names of tau discriminators with binary values
	std::vector<std::string> floatDiscriminatorNames;  ///< names of tau discriminators with real (float) values
};

/// Basic tau data format
/** This contains the tau discriminators, the decay mode and the em-fraction
    copy from DataFormats/TauReco/interface/PFTau.h
 */
struct KBasicTau : public KLepton
{
	int decayMode;     ///< hadronic decay mode as identified by HPS algorithm
	float emFraction;  ///< electromagnetic energy fraction

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


/// Kappa Tau data format
/** copy from DataFormats/TauReco/interface/PFTau.h */
struct KTau : public KBasicTau
{
	/// four-vectors and full PFCandidates
	KLVs piZeroCandidates;
	KPFCandidates chargedHadronCandidates;
	KPFCandidates gammaCandidates;

	int tauKey;

	inline unsigned long nCandidates()
	{
		return chargedHadronCandidates.size() + gammaCandidates.size();
	}
};
typedef std::vector<KTau> KTaus;


/// Kappa extended Tau data format
/** This contains additional tau quantities which are usually not needed in a
    simple analysis skim, but are required for more detailed studies (e.g., TauPOG) 
 */
struct KExtendedTau : public KTau
{
	/// four-vectors
	KLVs superClusterBarrelCandidates;
	KLVs superClusterEndcapCandidates;
};
typedef std::vector<KExtendedTau> KExtendedTaus;

#endif

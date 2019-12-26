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

#include "DataFormats/TauReco/interface/PFTau.h"


struct KTauMetadata
{
	virtual ~KTauMetadata() {};

	std::vector<std::string> binaryDiscriminatorNames; ///< names of tau discriminators with binary values
	std::vector<std::string> floatDiscriminatorNames;  ///< names of tau discriminators with real (float) values
};

/// Basic tau data format
/** This contains the tau discriminators, the decay mode and the em-fraction
    copy from DataFormats/TauReco/interface/PFTau.h
 */
struct KBasicTau : public KLepton
{
	virtual ~KBasicTau() {};

	int decayMode;     ///< hadronic decay mode as identified by HPS algorithm
	float emFraction;  ///< electromagnetic energy fraction
	
	// (signed) PDG ID of the hadronic resonance
	int resonancePdgId() const
	{
		int pdgId = 0;
		switch (decayMode)
		{
			case reco::PFTau::hadronicDecayMode::kThreeProng0PiZero: pdgId = 20213; break;
			case reco::PFTau::hadronicDecayMode::kOneProng1PiZero: pdgId = 213; break;
			case reco::PFTau::hadronicDecayMode::kOneProng0PiZero: pdgId = 211; break;
			default: pdgId = 0;
		}
		if (charge() > 0)
		{
			pdgId *= -1;
		}
		return pdgId;
	}

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

/// Kappa L1 Tau format for L1 Seeds of Taus
/*  needed for matching Tau trigger objects to their L1 seeds & apply pt cuts,
	as recommended by Tau Trigger group for 2017 to achieve trigger SF's near 1.
	It could be easily/generalized to L1 Muons and Electrons, but for now, that's not needed.
	CMSSW DataFormats reference:
	https://github.com/cms-sw/cmssw/blob/CMSSW_9_4_X/DataFormats/L1Trigger/interface/L1Candidate.h
	https://github.com/cms-sw/cmssw/blob/CMSSW_9_4_X/DataFormats/L1Trigger/interface/Tau.h*/
struct KL1Tau : public KLV
{
	virtual ~KL1Tau() {};
	bool hwIso; // hardware iso: stored as 'int' in MINIAOD; switch to bool since relevant check is hwIso() > 0 in analyses
};
typedef std::vector<KL1Tau> KL1Taus;

/// Kappa Tau data format
/** copy from DataFormats/TauReco/interface/PFTau.h */
struct KTau : public KBasicTau
{
	virtual ~KTau() {};

	/// four-vectors and full PFCandidates
	KLVs piZeroCandidates;
	KPFCandidates chargedHadronCandidates;
	KPFCandidates gammaCandidates;

	KVertex sv;
	ROOT::Math::SVector<double, 7> refittedThreeProngParameters;
	ROOT::Math::SMatrix<float, 7, 7, ROOT::Math::MatRepSym<float, 7> > refittedThreeProngCovariance;
	KTracks refittedChargedHadronTracks;

	int tauKey;

	inline unsigned long nCandidates()
	{
		return chargedHadronCandidates.size() + gammaCandidates.size();
	}
	
	RMFLV sumPiZeroCandidates()
	{
		RMFLV sumP4;
		for (std::vector<KLV>::iterator candidate = piZeroCandidates.begin();
		     candidate != piZeroCandidates.end(); ++candidate)
		{
			sumP4 += candidate->p4;
		}
		return sumP4;
	}
	
	RMFLV sumChargedHadronCandidates()
	{
		RMFLV sumP4;
		for (std::vector<KPFCandidate>::iterator candidate = chargedHadronCandidates.begin();
		     candidate != chargedHadronCandidates.end(); ++candidate)
		{
			sumP4 += candidate->p4;
		}
		return sumP4;
	}
	
	RMFLV sumGammasCandidates()
	{
		RMFLV sumP4;
		for (std::vector<KPFCandidate>::iterator candidate = gammaCandidates.begin();
		     candidate != gammaCandidates.end(); ++candidate)
		{
			sumP4 += candidate->p4;
		}
		return sumP4;
	}
	
	RMFLV piZeroMomentum()
	{
		if (piZeroCandidates.size() > 0)
		{
			return sumPiZeroCandidates();
		}
		else
		{
			return sumGammasCandidates();
		}
	}
};
typedef std::vector<KTau> KTaus;


/// Kappa extended Tau data format
/** This contains additional tau quantities which are usually not needed in a
    simple analysis skim, but are required for more detailed studies (e.g., TauPOG) 
 */
struct KExtendedTau : public KTau
{
	virtual ~KExtendedTau() {};

	/// four-vectors
	KLVs superClusterBarrelCandidates;
	KLVs superClusterEndcapCandidates;
};
typedef std::vector<KExtendedTau> KExtendedTaus;

#endif

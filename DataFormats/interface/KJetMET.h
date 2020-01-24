//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Fabio Colombo <fabio.colombo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Hauth <Thomas.Hauth@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_JETMET_H
#define KAPPA_JETMET_H

#include "KBasic.h"

struct KCaloJet : public KLV
{
	virtual ~KCaloJet() {};

	float area;          //< jet area

	float fEM;           //< energy fraction in the ECAL
	float fHO;           //< energy fraction in HO
	float fHPD;          //< energy fraction from dominant hybrid photo diode
	float fRBX;          //< energy fraction from dominant readout box

	short nConstituents; //< number of constituents (calo towers)
	short n90Hits;       //< number of hits 90% of the jet energy
};
typedef std::vector<KCaloJet> KCaloJets;

struct KBasicJet : public KLV
{
	virtual ~KBasicJet() {};

	float area;
	std::vector<float> corrections;

	float neutralHadronFraction, chargedHadronFraction;
	float muonFraction, photonFraction, electronFraction;
	float hfHadronFraction, hfEMFraction;

	int nConstituents, nCharged;

	RMFLV uncorrectedP4( size_t level)
	{
		return p4 * corrections[level];
	}
};
typedef std::vector<KBasicJet> KBasicJets;

struct KJetMetadata
{
	virtual ~KJetMetadata() {};

	std::vector<std::string> tagNames;  //< names of the float value taggers
	std::vector<std::string> idNames;   //< names of the binary value IDs
	std::vector<std::string> jecLevels;

	inline std::string ReplaceAll(std::string str, const std::string& from, const std::string& to) const
	{
		size_t start_pos = 0;
		while((start_pos = str.find(from, start_pos)) != std::string::npos)
		{
			str.replace(start_pos, from.length(), to);
			start_pos += to.length();
		}
		return str;
	}

	size_t jecLevelNumber(std::string inJecSet, std::string inlevel)
	{

		for(size_t index = 0; index < jecLevels.size(); index++)
		{
			if (inlevel.compare(jecLevels[index]) == 0)
				return index;
		}

		std::cout << "KJetMetadata: Correction factor \"" << inlevel << "\" not available!" << std::endl;
		exit(1);
	}
};

struct KJet : public KBasicJet
{
	virtual ~KJet() {};

	std::vector<float> tags;            //< float value tags (b-tag, etc.)
	unsigned int binaryIds;             //< binary value tags (PU jet ID, etc.)
	int hadronFlavour;
	int partonFlavour;
	bool genMatch;

	float getTag(const std::string& name, const KJetMetadata *jetmetadata, bool check = true) const
	{
		for (unsigned int i = 0; i < jetmetadata->tagNames.size(); ++i)
		{
			if ((jetmetadata->ReplaceAll(jetmetadata->tagNames[i], ":", "") == name) or (jetmetadata->tagNames[i] == name))
			{
				return tags[i];
			}
		}
		if (!check)
			return -999.;
		std::cout << "Tag \"" << name << "\" not available!" << std::endl;
		exit(1);
	}

	bool getId(const std::string& name, const KJetMetadata *jetmetadata, bool check = true) const
	{
		for (unsigned int i = 0; i < jetmetadata->idNames.size(); ++i)
		{
			if (jetmetadata->ReplaceAll(jetmetadata->idNames[i], ":", "") == name)
				return binaryIds & (1 << i);
		}
		if (!check)
			return false;
		std::cout << "Binary ID \"" << name << "\" not available!";
		if(jetmetadata->idNames.size() == 0)
			std::cout << " Sample does not include any IDs at all." << std::endl;
		else
		{
			std::cout << " Available IDs are:" << std::endl;
			for (unsigned int i = 0; i < jetmetadata->idNames.size(); ++i)
			{
				std::cout << jetmetadata->idNames[i] << std::endl;
			}
		}
		exit(1);
	}
};
typedef std::vector<KJet> KJets;

/// This gen jet dataformat is a private one for tau POG studies and might not be stable in future
struct KGenJet : public KLV
{
	virtual ~KGenJet() {};

	int genTauDecayMode;
};
typedef std::vector<KGenJet> KGenJets;

// copied from https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_X/DataFormats/PatCandidates/interface/MET.h#L151-L158
// make sure it's up to date with the current enum found in MET.h
//
// suggestion from http://stackoverflow.com/questions/261963/how-can-i-iterate-over-an-enum/26910769#26910769 used
// to create "iterable enum"
namespace KMETUncertainty { enum Type
{
	JetResUp = 0,
	JetResDown = 1,
	JetEnUp = 2,
	JetEnDown = 3,
	MuonEnUp = 4,
	MuonEnDown = 5,
	ElectronEnUp = 6,
	ElectronEnDown = 7,
	TauEnUp = 8,
	TauEnDown = 9,
	UnclusteredEnUp = 10,
	UnclusteredEnDown = 11,
	PhotonEnUp = 12,
	PhotonEnDown = 13,
	NoShift = 14,
	METUncertaintySize = 15,
	JetResUpSmear = 16,
	JetResDownSmear = 17,
	METFullUncertaintySize = 18
};

static const std::vector<Type> All = {JetResUp,
									  JetResDown,
									  JetEnUp,
									  JetEnDown,
									  MuonEnUp,
									  MuonEnDown,
									  ElectronEnUp,
									  ElectronEnDown,
									  TauEnUp,
									  TauEnDown,
									  UnclusteredEnUp,
									  UnclusteredEnDown,
									  PhotonEnUp,
									  PhotonEnDown,
									  NoShift,
									  METUncertaintySize,
									  JetResUpSmear,
									  JetResDownSmear,
									  METFullUncertaintySize
									 };
}

struct KMET : public KLV
{
	virtual ~KMET() {};

	double sumEt;
	float photonFraction, electronFraction;
	float neutralHadronFraction, chargedHadronFraction;
	float muonFraction;
	float hfHadronFraction, hfEMFraction;
	std::size_t leptonSelectionHash;
	ROOT::Math::SMatrix<double, 2, 2, ROOT::Math::MatRepSym<double, 2> > significance;

	std::map<KMETUncertainty::Type, RMFLV> p4_shiftedByUncertainties;
	std::map<KMETUncertainty::Type, double> sumEt_shiftedByUncertainties;
};
typedef std::vector<KMET> KMETs;

struct KHCALNoiseSummary
{
	virtual ~KHCALNoiseSummary() {};

	bool hasBadRBXTS4TS5;
	float isolatedNoiseSumE;
	float isolatedNoiseSumEt;
	float min25GeVHitTime;
	float minE2Over10TS;
	float minRBXEMF;
	float max25GeVHitTime;
	float maxE2Over10TS;
	int maxHPDHits;
	int maxHPDNoOtherHits;
	int maxRBXHits;
	int maxZeros;
	int numIsolatedNoiseChannels;
};

struct KPileupDensity
{
	virtual ~KPileupDensity() {};
	double rho;
};

#endif

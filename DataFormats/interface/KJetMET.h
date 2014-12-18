/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 *   Thomas Hauth <Thomas.Hauth@cern.ch>
 */

#ifndef KAPPA_JETMET_H
#define KAPPA_JETMET_H

#include "KBasic.h"


struct KCaloJet : public KLV
{
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
	float area;

	float neutralEMFraction, chargedEMFraction;
	float neutralHadronFraction, chargedHadronFraction;
	float muonFraction, photonFraction, electronFraction;
	float hfHadronFraction, hfEMFraction;

	int nConstituents, nCharged;
};
typedef std::vector<KBasicJet> KBasicJets;

struct KJetMetadata
{
	std::vector<std::string> tagNames;  //< names of the float value taggers
	std::vector<std::string> idNames;   //< names of the binary value IDs
};

struct KJet : public KBasicJet
{
	std::vector<float> tags;            //< float value tags (b-tag, etc.)
	unsigned int binaryIds;             //< binary value tags (PU jet ID, etc.)

	float getTag(const std::string& name, const KJetMetadata *jetmetadata, bool check = true) const
	{
		for (unsigned int i = 0; i < jetmetadata->tagNames.size(); ++i)
		{
			if (jetmetadata->tagNames[i] == name)
				return tags[i];
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
			if (jetmetadata->idNames[i] == name)
				return binaryIds & (1 << i);
		}
		if (!check)
			return false;
		std::cout << "Binary ID \"" << name << "\" not available!" << std::endl;
		exit(1);
	}
};
typedef std::vector<KJet> KJets;


struct KBasicMET : public KLV
{
	double sumEt;
	ROOT::Math::SMatrix<double, 2, 2, ROOT::Math::MatRepSym<double, 2> > significance;
};

struct KMET : public KBasicMET
{
	float photonFraction, electronFraction;
	float neutralEMFraction, chargedEMFraction;
	float neutralHadronFraction, chargedHadronFraction;
	float muonFraction;
	float hfHadronFraction, hfEMFraction;
};

struct KHCALNoiseSummary
{
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
	double rho;
	double sigma;
};

#endif

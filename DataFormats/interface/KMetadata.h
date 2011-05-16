#ifndef KAPPA_METADATA_H
#define KAPPA_METADATA_H

#include <map>
#include <vector>
#include <string>

/* RUN METADATA */
struct KProvenance
{
	std::vector<std::string> names;
	std::vector<std::string> branches;
};

/* RUN + LUMI METADATA */
struct KLumiMetadata
{
	unsigned int nLumi;
	unsigned int nRun;
	std::vector<unsigned int> hltPrescales;
	std::vector<std::string> hltNames;
	std::vector<std::string> hltNamesMuons;
	std::vector<std::string> discrTau;
	std::vector<std::string> discrTauPF;
};

struct KGenLumiMetadata : public KLumiMetadata
{
	double filterEff;
	double xSectionExt;
	double xSectionInt;
};

struct KDataLumiMetadata : public KLumiMetadata
{
	float avgInsDelLumi;
	float avgInsDelLumiErr;
	float avgInsRecLumi;
	float avgInsRecLumiErr;
	float deadFrac;
	float lumiSectionLength;
	short lumiSecQual;
};

/* EVENT METADATA */
struct KEventMetadata
{
	unsigned long long bitsL1;
	unsigned long long bitsHLT;
	unsigned int bitsUserFlags;
	unsigned int nEvent;
	unsigned int nLumi;
	unsigned int nRun;
	int nBX;
	bool hltFired (const std::string &name, const KLumiMetadata *lumimetadata) const
	{
		for (size_t i = 0; i < lumimetadata->hltNames.size(); ++i)
			if (lumimetadata->hltNames[i] == name)
				return (bitsHLT & (1ull << i)) != 0;
		return false; // Named HLT does not exist
	}
};

// Nice names for types
typedef unsigned int event_id;
typedef unsigned int lumi_id;
typedef unsigned int run_id;
typedef int bx_id;

// List of user flags
const unsigned int KFlagPhysicsDeclared = 1 << 0;
const unsigned int KFlagHCALLooseNoise = 1 << 1;
const unsigned int KFlagHCALTightNoise = 1 << 2;
const unsigned int KFlagRecoErrors = 1 << 3;
const unsigned int KFlagRecoWarnings = 1 << 4;
const unsigned int KFlagPrescaleError = 1 << 5;

struct KGenEventMetadata : public KEventMetadata
{
	double weight;
	double binValue;
	double alphaQCD;
	unsigned char numPUInteractions;
};

#endif

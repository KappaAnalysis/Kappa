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
	unsigned int bitsUserFlags;
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
	unsigned short nFill; // fill number

	double getLumi() const
	{
		return avgInsRecLumi * lumiSectionLength / 10.0 / 1e6;
	}
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
	inline bool hltFired (const size_t pos) const
	{
		return (bitsHLT & (1ull << pos)) != 0;
	}
};

// Nice names for types
typedef unsigned int event_id;
typedef unsigned int lumi_id;
typedef unsigned int run_id;
typedef unsigned short fill_id;
typedef int bx_id;

// List of user flags for events (KEventFlag...)
const unsigned int KEFPhysicsDeclared = 1 << 0;
const unsigned int KEFHCALLooseNoise = 1 << 1;
const unsigned int KEFHCALTightNoise = 1 << 2;
const unsigned int KEFRecoErrors = 1 << 3;
const unsigned int KEFRecoWarnings = 1 << 4;

// List of user flags for luminosity sections (KLumiFlag...)
const unsigned int KLFPrescaleError = 1 << 0;

struct KGenEventMetadata : public KEventMetadata
{
	double weight;
	double binValue;
	double alphaQCD;
	float numPUInteractionsTruth;	// "true" number of PU interactions
	unsigned char numPUInteractionsM2;	// bx = -2
	unsigned char numPUInteractionsM1;	// bx = -1
	unsigned char numPUInteractions0;	// bx =  0
	unsigned char numPUInteractionsP1;	// bx = +1
	unsigned char numPUInteractionsP2;	// bx = +2
};

#endif

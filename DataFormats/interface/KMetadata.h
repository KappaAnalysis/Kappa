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
	std::vector<std::string> hltNames;
	std::vector<std::string> hltNamesMuons;
	std::vector<std::string> discrTau;
	std::vector<std::string> discrTauPF;
};

struct KGenLumiMetadata : public KLumiMetadata
{
	double xSectionExt;
	double xSectionInt;
};

/* EVENT METADATA */
struct KEventMetadata
{
	unsigned long long bitsL1;
	unsigned long long bitsHLT;
	unsigned long bitsUserFlags;
	unsigned int nEvent;
	unsigned int nLumi;
	unsigned int nRun;
	int nBX;
};

// Nice names for types
typedef unsigned int event_id;
typedef unsigned int lumi_id;
typedef unsigned int run_id;
typedef int bx_id;

// List of user flags
const unsigned long KFlagPhysicsDeclared = 1 << 0;
const unsigned long KFlagHCALLooseNoise = 1 << 1;
const unsigned long KFlagHCALTightNoise = 1 << 2;

struct KGenEventMetadata : public KEventMetadata
{
	double weight;
	double binValue;
	double alphaQCD;
};

#endif

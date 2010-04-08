#ifndef KAPPA_METADATA_H
#define KAPPA_METADATA_H

#include <map>
#include <vector>
#include <string>

/* RUN METADATA */
struct KProvenance
{
public:
	std::vector<std::string> names;
	std::vector<std::string> branches;
};

/* RUN + LUMI METADATA */
struct KLumiMetadata
{
public:
	unsigned long nLumi;
	unsigned long nRun;
	std::vector<int> L1Prescales;
	std::vector<int> hltPrescales;
	std::vector<std::string> hltNames;
	std::vector<std::string> hltNamesMuons;
	std::vector<std::string> discrTau;
	std::vector<std::string> discrTauPF;
};

struct KGenLumiMetadata : public KLumiMetadata
{
public:
	double xSectionExt;
	double xSectionInt;
};

/* EVENT METADATA */
struct KEventMetadata
{
public:
	unsigned long long bitsL1;
	unsigned long long bitsHLT;
	unsigned long bitsUserFlags;
	unsigned long nEvent;
	unsigned long nLumi;
	unsigned long nRun;
	unsigned long nBX;
};

// List of user flags
const unsigned long KFlagPhysicsDeclared = 1 << 0;
const unsigned long KFlagHCALLooseNoise = 1 << 1;
const unsigned long KFlagHCALTightNoise = 1 << 2;

struct KGenEventMetadata : public KEventMetadata
{
public:
	double weight;
	double binValue;
	double alphaQCD;
};

#endif

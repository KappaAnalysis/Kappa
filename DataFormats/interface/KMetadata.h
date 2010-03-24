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
	std::vector<std::string> hltNames;
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
	unsigned long bitsHLT;
	unsigned long bitsUserFlags;
	unsigned long nEvent;
	unsigned long nLumi;
	unsigned long nRun;
	unsigned long nBX;
};

struct KGenEventMetadata : public KEventMetadata
{
public:
	double weight;
	double binValue;
	double alphaQCD;
};

#endif

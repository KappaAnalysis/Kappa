/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_INFO_H
#define KAPPA_INFO_H

#include <map>
#include <string>
#include <vector>

/// RUN METADATA
struct KProvenance
{
	std::vector<std::string> names;
	std::vector<std::string> branches;
};

// RUN + LUMI METADATA
// List of user flags for luminosity sections (KLumiFlag...)
const unsigned int KLFPrescaleError = 1 << 0;

struct KLumiInfo
{
	unsigned int nLumi;
	unsigned int nRun;
	unsigned int bitsUserFlags;
	std::vector<unsigned int> hltPrescales;
	std::vector<std::string> hltNames;
	//std::vector<std::vector<std::string> > filterNames;
};


struct KGenLumiInfo : public KLumiInfo
{
	double filterEff;
	double xSectionExt;
	double xSectionInt;
};

struct KDataLumiInfo : public KLumiInfo
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

/// EVENT METADATA
// List of user flags for events (KEventFlag...)
const unsigned int KEFPhysicsDeclared = 1 << 0;
const unsigned int KEFHCALLooseNoise = 1 << 1;
const unsigned int KEFHCALTightNoise = 1 << 2;
const unsigned int KEFRecoErrors = 1 << 3;
const unsigned int KEFRecoWarnings = 1 << 4;

struct KEventInfo
{
	unsigned long long bitsL1;
	unsigned long long bitsHLT;
	unsigned int bitsUserFlags;
	unsigned int nEvent;
	unsigned int nLumi;
	unsigned int nRun;
	int nBX;
	float randomNumber;
	float minVisPtFilterWeight; // weight necessary to correct embedded events
	bool hltFired (const std::string &name, const KLumiInfo *lumiinfo) const
	{
		for (size_t i = 0; i < lumiinfo->hltNames.size(); ++i)
			if (lumiinfo->hltNames[i] == name)
				return (bitsHLT & (1ull << i)) != 0;
		return false; // Named HLT does not exist
	}

	inline bool hltFired (const size_t pos) const
	{
		return (bitsHLT & (1ull << pos)) != 0;
	}

	inline bool userFlag(const unsigned int mask) const
	{
		return (bitsUserFlags & mask) != 0;
	}
};

// Nice names for types
typedef unsigned int event_id;
typedef unsigned int lumi_id;
typedef unsigned int run_id;
typedef unsigned short fill_id;
typedef int bx_id;


struct KGenEventInfo : public KEventInfo
{
	double weight;                      //< Monte-Carlo weight of the event
	double binValue;                    //< ?
	double alphaQCD;                    //< value of alpha_S for this event
	float nPUMean;        //< mean ("true") number of PU interactions
	unsigned char nPUm2;  // bx = -2
	unsigned char nPUm1;  // bx = -1
	unsigned char nPU;    // bx =  0
	unsigned char nPUp1;  // bx = +1
	unsigned char nPUp2;  // bx = +2
};


#endif

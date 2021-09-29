//- Copyright (c) 2010 - All Rights Reserved
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_INFO_H
#define KAPPA_INFO_H

#include <map>
#include <string>
#include <vector>
#include <assert.h>

// RUN METADATA

/// Provenance information to trace back the branch content to the corresponding EDM product
struct KProvenance
{
	virtual ~KProvenance() {};

	std::vector<std::string> names;         //< product names of the objects in EDM
	std::vector<std::string> branches;      //< branch names in the Events tree in the same ordering
};

// RUN + LUMI METADATA
// List of user flags for luminosity sections (KLumiFlag...)
const unsigned int KLFPrescaleError = 1 << 0;

struct KRunInfo
{
	virtual ~KRunInfo() {};

	unsigned int nRun;                      //< run number
};

struct KGenRunInfo : public KRunInfo
{
	virtual ~KGenRunInfo() {};

	double filterEff;              //< generator filter efficiency
	double xSectionExt;            //< external process cross section
	double xSectionInt;            //< internal process cross section
	
	std::map<std::string, std::string> lheWeightNamesMap; //< human readable names mapped to indices
};

struct KDataRunInfo : public KRunInfo
{
	virtual ~KDataRunInfo() {};
};

struct KLumiInfo
{
	virtual ~KLumiInfo() {};

	unsigned int nLumi;                     //< lumi section number
	unsigned int nRun;                      //< run number
	unsigned int bitsUserFlags;             //< contains a flag for prescale errors
	std::vector<unsigned int> hltPrescales; //< prescales for the triggers in hltNames
	std::vector<std::string> hltNames;      //< names of the HLT triggers
};

struct KGenLumiInfo : public KLumiInfo
{
	virtual ~KGenLumiInfo() {};
};

struct KDataLumiInfo : public KLumiInfo
{
	virtual ~KDataLumiInfo() {};

	float avgInsDelLumi;           //< average of the instantaneous delivered luminosity
	float avgInsDelLumiErr;        //< error on the average of the instantaneous delivered luminosity
	float avgInsRecLumi;           //< average of the instantaneous recorded luminosity
	float avgInsRecLumiErr;        //< error on the average of the instantaneous recorded luminosity
	float deadFrac;                //< dead fraction
	float lumiSectionLength;       //< length of the lumi-section in seconds
	short lumiSecQual;             //<
	unsigned short nFill;          //< fill number

	/// get the integrated luminosity of this lumi-section in pb\f$^{-1}\f$
	double getLumi() const
	{
		// 10: , 1e6: conversion in pb
		return static_cast<double>(avgInsRecLumi) * static_cast<double>(lumiSectionLength) / 10.0 / 1e6;
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
	virtual ~KEventInfo() {};

	unsigned long long bitsL1;     //< trigger bits for the L1 trigger
	std::vector<bool> bitsHLT;    //< trigger bits for the HLT trigger according to hltNames
	unsigned long long nEvent;     //< event number
	unsigned int nLumi;            //< lumi-section number
	unsigned int nRun;             //< run number
	int nBX;                       //< bunch crossing number
	unsigned int bitsUserFlags;    //<
	float minVisPtFilterWeight;    //< weight necessary to correct embedded events

	bool hltFired (const std::string &name, const KLumiInfo *lumiinfo) const
	{
		for (size_t i = 0; i < lumiinfo->hltNames.size(); ++i)
			if (lumiinfo->hltNames[i] == name)
				return bitsHLT[i];
		return false; // Named HLT does not exist
	}

	inline bool hltFired (const size_t pos) const
	{
		return bitsHLT[pos];
	}

	inline bool userFlag(const unsigned int mask) const
	{
		return (bitsUserFlags & mask) != 0;
	}
};

// Nice names for types
typedef unsigned long long event_id;
typedef unsigned int lumi_id;
typedef unsigned int run_id;
typedef unsigned short fill_id;
typedef int bx_id;

struct KGenEventInfoMetadata
{
	std::vector<std::string> lheWeightNames;

	// function that returns the indices of the lheWeights of interest for efficient access
	std::map<std::string, unsigned int> getLheWeightNamesMap(std::vector<std::string> const& requestedNames,
	                                                         std::map<std::string, std::string> const& lheWeightNamesMap=std::map<std::string, std::string>()) const
	{
		std::map<std::string, unsigned int> resultMap;
		for(std::vector<std::string>::const_iterator requestedName = requestedNames.begin(); requestedName != requestedNames.end(); ++requestedName)
		{
			std::string internalName = *requestedName;
			if (lheWeightNamesMap.count(internalName) > 0)
			{
				internalName = lheWeightNamesMap.at(internalName);
			}
			
			bool found = false;
			for(unsigned int lheWeightNameIndex = 0; lheWeightNameIndex < lheWeightNames.size(); lheWeightNameIndex++)
			{
				if (lheWeightNames.at(lheWeightNameIndex).compare(internalName) == 0)
				{
					resultMap[*requestedName] = lheWeightNameIndex;
					assert( !found ); // misconfiguration: the requested name matches more than once
					found = true;
				}
			}
		}
		return resultMap;
	}
};

struct KGenEventInfo : public KEventInfo
{
	virtual ~KGenEventInfo() {};

	double weight;                      //< Monte-Carlo weight of the event
	double binValue;                    //< ?
	double alphaQCD;                    //< value of alpha_S for this event
	double lheHt;                       //< p-T sum of the outgoing partons of the event
	int lheNOutPartons;                 //< number of outgoing partons
	int lhenpNLO;
	float nPUMean;        //< mean ("true") number of PU interactions
	unsigned char nPUm2;  // bx = -2
	unsigned char nPUm1;  // bx = -1
	unsigned char nPU;    // bx =  0
	unsigned char nPUp1;  // bx = +1
	unsigned char nPUp2;  // bx = +2
	double x1;            ///< x of the first parton (used for PDF reweighting)
	double x2;            ///< x of the second parton (used for PDF reweighting)
	double qScale;        ///< q scale of the process (used for PDF reweighting)

	// prefiring weights
	double prefiringWeight;
	double prefiringWeightUp;
	double prefiringWeightDown;

	std::vector<float> lheWeights;

	inline float getLheWeight(unsigned int index) const
	{
		return lheWeights.at(index);
	}
	
	std::vector<float> getLheWeights(std::vector<unsigned int> const& lheWeightIndices) const
	{
		std::vector<float> resultVector;
		for(std::vector<unsigned int>::const_iterator lheWeightIndex = lheWeightIndices.begin();
		    lheWeightIndex != lheWeightIndices.end(); ++lheWeightIndex)
		{
			resultVector.push_back(getLheWeight(*lheWeightIndex));
		}
		return resultVector;
	}
	
	std::map<std::string, float> getLheWeights(std::map<std::string, unsigned int> const& lheWeightNamesMap) const
	{
		std::map<std::string, float> resultMap;
		for(std::map<std::string, unsigned int>::const_iterator lheWeightNameIndex = lheWeightNamesMap.begin();
		    lheWeightNameIndex != lheWeightNamesMap.end(); ++lheWeightNameIndex)
		{
			resultMap[lheWeightNameIndex->first] = getLheWeight(lheWeightNameIndex->second);
		}
		return resultMap;
	}
};


#endif

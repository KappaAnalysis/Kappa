//- Copyright (c) 2010 - All Rights Reserved
//-  * Danilo Piparo <danilo.piparo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Roger Wolf <roger.wolf@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_BASIC_H
#define KAPPA_BASIC_H

#include <vector>
#include <Math/SMatrix.h>
#include <map>

#include "KRoot.h"


struct KLV
{
	RMFLV p4;
};
typedef std::vector<KLV> KLVs;


struct KBeamSpot
{
	RMPoint position;              ///< position of the beam spot
	char type;                     ///< type of beam (usually unknown): Unknown=-1, Fake=0, LHC=1, Tracker=2

	double betaStar;               ///< beta* (always 0 in AOD)
	double beamWidthX, beamWidthY; ///< beam width in x and y direction
	double emittanceX, emittanceY; ///< beam emittance in x and y (always 0)

	double dxdz, dydz;             ///< slopes dx/dz and dy/dz for beam spot position extrapolation
	double sigmaZ;                 ///< sigma in z direction

	ROOT::Math::SMatrix<double, 7, 7, ROOT::Math::MatRepSym<double, 7> > covariance;
};
typedef std::vector<KBeamSpot> KBeamSpots;


struct KVertex
{
	RMPoint position;
	bool valid;
	unsigned int nTracks;
	float chi2;
	float nDOF;

	ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> > covariance;  //< covariance matrix

	inline bool fake() const { return (chi2 <= 0 && nDOF <= 0 && nTracks == 0); };
};
typedef std::vector<KVertex> KVertices;


struct KVertexSummary
{
	KVertex pv;
	unsigned int nVertices;
};


struct KTaupairVerticesMap
{
	std::vector<int> diTauKey;
	std::vector<KVertex> vertices;
};
typedef std::vector<KTaupairVerticesMap> KTaupairVerticesMaps;


struct KHit
{
	double theta, phi, pAbs, energyLoss;
};
typedef std::vector<KHit> KHits;


struct KTriggerObjectMetadata
{
	std::string menu;
	
	/// { hlt1:filter1, ..., hlt1:filterN1, hlt2:filter1, ..., hlt2:filterN2, ...}
	std::vector<std::string> toFilter;
	std::vector<int> nFiltersPerHLT;
	
	size_t getMinFilterIndex(size_t hltIndex)
	{
		assert(hltIndex < nFiltersPerHLT.size());
		size_t minFilterIndex = 0;
		for (size_t tmpHltIndex = 0; tmpHltIndex < hltIndex; ++tmpHltIndex)
		{
			minFilterIndex += nFiltersPerHLT[tmpHltIndex];
		}
		return minFilterIndex;
	}
	
	size_t getMaxFilterIndex(size_t hltIndex)
	{
		assert(hltIndex < nFiltersPerHLT.size());
		size_t maxFilterIndex = 0;
		for (size_t tmpHltIndex = 0; tmpHltIndex <= hltIndex; ++tmpHltIndex)
		{
			maxFilterIndex += nFiltersPerHLT[tmpHltIndex];
		}
		return maxFilterIndex;
	}
};

struct KTriggerObjects
{
	KLVs trgObjects;

	/// { hlt1:idxFilter1, ..., hlt1:idxFilterN1, hlt2:idxFilter1, ..., hlt2:idxFilterN2, ...}
	std::vector<std::vector<int> > toIdxFilter;
};


struct KFilterMetadata
{
	std::vector<std::string> filternames;
};

struct KFilterSummary
{
	unsigned long presence;
	unsigned long decision;

	inline bool passedFilters() const
	{
		return (decision & presence) == presence;
	}

	inline bool passedFilter(const size_t pos) const
	{
		return (decision & presence & (1ul << pos)) == (presence & (1ul << pos));
	}

	inline bool passedFilters(const unsigned long bitmask) const
	{
		return (decision & presence & bitmask) == (bitmask & presence);
	}

	bool passedFilter(const std::string &name, const KFilterMetadata *filtermetadata) const
	{
		for (size_t i = 0; i < filtermetadata->filternames.size(); ++i)
			if (filtermetadata->filternames[i] == name)
				return (decision & presence & (1ul << i)) == (presence & (1ul << i));
		return false; // Filter does not exist
	}

	bool passedFilters(const std::vector<std::string> &names, const KFilterMetadata *filtermetadata) const
	{
		for (std::vector<std::string>::const_iterator name = names.begin(); name != names.end(); name++)
			if (!passedFilter(*name, filtermetadata))
				return false;
		return true; // all filters passed
	}
};

#endif

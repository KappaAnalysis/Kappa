/* Copyright (c) 2010 - All Rights Reserved
 *   Danilo Piparo <danilo.piparo@cern.ch>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_BASIC_H
#define KAPPA_BASIC_H

#include "KLorentzVector.h"
#include <vector>
#include <Math/SMatrix.h>
#include <map>

struct KLV
{
	typedef RMLV KInternalLV;
	RMLV p4;
};
typedef std::vector<KLV> KLVs;

struct KDataLV
{
	typedef RMDataLV KInternalLV;
	RMDataLV p4;
};
typedef std::vector<KDataLV> KDataLVs;

struct KDataVertex
{
	RMPoint position;
	bool fake;

	unsigned int nTracks;
	float chi2, nDOF;

	ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> > covariance;
};
typedef std::vector<KDataVertex> KDataVertices;

struct KUnbiasedDiTauPV
{
	std::vector<KDataVertex> refittedVertices;
	std::vector<int> diTauKey;
};
typedef std::vector<KUnbiasedDiTauPV> KUnbiasedDiTauPVs;

struct KVertexSummary
{
	KDataVertex pv;
	unsigned int nVertices;
};

struct KDataBeamSpot
{
	RMPoint position;
	char type;

	double betaStar;

	double beamWidthX, beamWidthY, emittanceX, emittanceY;

	double dxdz, dydz, sigmaZ;

	ROOT::Math::SMatrix<double, 7, 7, ROOT::Math::MatRepSym<double, 7> > covariance;
};
typedef std::vector<KDataBeamSpot> KDataBeamSpots;

// pdgid = [charge:1][status:3][id:...]
const unsigned int KGenParticleStatusPosition = 28;
const unsigned int KGenParticleChargePosition = 31;
const unsigned int KGenParticleChargeMask = (unsigned int)1 << KGenParticleChargePosition;
const unsigned int KGenParticleStatusMask = (unsigned int)3 << KGenParticleStatusPosition;
const unsigned int KGenParticlePdgIdMask = ((unsigned int)1 << KGenParticleStatusPosition) - (unsigned int)1;

#include "KTrack.h"
struct KLepton : public KDataLV
{
public:
	enum Flavour
	{
		NONE  = 0,
		ELECTRON = 1,
		MUON = 2,
		TAU  = 3
	};
	Flavour flavour;

	char charge;
	KDataTrack track;
};

typedef std::vector<KLepton> KLeptons;

struct KGenParticle : public KDataLV
{
	unsigned int pdgid;
	std::vector<unsigned int> daughterIndices;

	// return daughter i; checks if i<numberOfDaughters; returns -1 in case i is out of bounds
	unsigned int daughterIndex(unsigned int i)
	{
		if (i<daughterIndices.size())
		{
			return daughterIndices.at(i);
		}
		else
		{
			return -1;
		}
	}
	/// return the number of daughters
	int numberOfDaughters()
	{
		return daughterIndices.size();
	}
	int status() const
	{
		return (pdgid & KGenParticleStatusMask) >> KGenParticleStatusPosition;
	}
	int pdgId() const
	{
		return (pdgid & KGenParticleChargeMask ? -1 : 1) * (pdgid & KGenParticlePdgIdMask);
	}
	int sign() const
	{
		return (pdgid & KGenParticleChargeMask ? -1 : 1);
	}

	// particle charge multiplied by 3
	// e.g. 2 for up-quark, -3 for electron
	// valid for quarks, leptons, bosons, diquarks, mesons and baryons
	// no special, technicolor, SUSY, Kaluza-Klein particles, R-hadrons and pentaquarks
	int chargeTimesThree() const
	{
		int pdg = std::abs(pdgId());
		int had = pdg % 10000 / 10;  // quark content of hadrons (digits 2-4)

		if (pdg == 0)
			return 0;
		// quark
		if (pdg < 9)
			return (-3 * (pdg % 2) + 2) * sign();
		// lepton
		if (pdg > 10 && pdg < 19)
			return -3 * (pdg % 2) * sign();
		// boson
		if (pdg > 20 && pdg < 40)
			return (pdg == 24 || pdg == 34 || pdg == 37) ? 3 * sign() : 0;
		// meson
		if (had < 100)
		{
			int q1 = -3 * (had / 10 % 2) + 2;
			int q2 = -3 * (had % 2) + 2;
			return (q1 - q2) * sign();
		}
		// baryon
		else
		{
			int q1 = had / 100;
			int q2 = had / 10 % 10;
			int q3 = had % 10;
			q1 = (q1 == 0) ? 0 : -3 * (q1 % 2) + 2;
			q2 = (q2 == 0) ? 0 : -3 * (q2 % 2) + 2;
			q3 = (q3 == 0) ? 0 : -3 * (q3 % 2) + 2;
			return (q1 + q2 + q3) * sign();
		}
	}
	// particle charge
	double charge() const
	{
		return chargeTimesThree() / 3.;
	}
};
typedef std::vector<KGenParticle> KGenParticles;

struct KGenPhoton : public KDataLV
{
	RMDataLV mother;
	char type;
	bool isPhoton() const { return (type == 1); }
	bool isPi0() const { return (type == 2); }
};
typedef std::vector<KGenPhoton> KGenPhotons;

struct KDataHit
{
	double theta, phi, pAbs, energyLoss;
};
typedef std::vector<KDataHit> KDataHits;

struct KPFCandidate : KDataLV
{
	unsigned int pdgid;
	double deltaP;
	double ecalEnergy, hcalEnergy;

	int pdgId() const
	{
		return (pdgid & KGenParticleChargeMask ? -1 : 1) * (pdgid & KGenParticlePdgIdMask);
	}
	int charge() const
	{
		return (pdgid & KGenParticleChargeMask ? -1 : 1);
	}
};
typedef std::vector<KPFCandidate> KPFCandidates;

struct KL1Muon : KDataLV
{
	// bit    meaning
	// 0-2    quality
	// 3      isForward
	// 4      isRPC
	// 5      isMip
	// 6      isIsolated
	// 7-10   bx (15 = value of bx>=14)
	// 11-13  detector
	unsigned short state; // bit map

	int quality() const { return (state & ( 7 )); };
	bool isForward() const { return (state & (1 << 3)); };
	bool isRPC() const { return (state & (1 << 4)); };
	bool isMip() const { return (state & (1 << 5)); };
	bool isIsolated() const { return (state & (1 << 6)); };
	int bx() const { return ((state & (15 << 7)) >> 7) - 7; };
	int detector() const { return ((state & (7 << 11)) >> 11);};
};
typedef std::vector<KL1Muon> KL1Muons;

struct KTriggerInfos
{
	std::string menu;
	
	// { hlt1:filter1, ..., hlt1:filterN1, hlt2:filter1, ..., hlt2:filterN2, ...}
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
	std::vector<KDataLV> trgObjects;
	
	// { hlt1:idxFilter1, ..., hlt1:idxFilterN1, hlt2:idxFilter1, ..., hlt2:idxFilterN2, ...}
	std::vector<std::vector<int> > toIdxFilter;
};

#endif

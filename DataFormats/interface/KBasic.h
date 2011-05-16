#ifndef KAPPA_BASIC_H
#define KAPPA_BASIC_H

#include "KLorentzVector.h"
#include <vector>
#include "Math/SMatrix.h"

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

struct KVertexSummary
{
	KDataVertex pv;
	unsigned int nVertices;
}

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
const unsigned int KPartonStatusPosition = 28;
const unsigned int KPartonChargePosition = 31;
const unsigned int KPartonChargeMask = (unsigned int)1 << KPartonChargePosition;
const unsigned int KPartonStatusMask = (unsigned int)3 << KPartonStatusPosition;
const unsigned int KPartonPdgIdMask = ((unsigned int)1 << KPartonStatusPosition) - (unsigned int)1;
struct KParton
{
	typedef RMLV KInternalLV;
	RMLV p4;
	unsigned int pdgid;
	unsigned int children;

	int status() const
	{
		return (pdgid & KPartonStatusMask) >> KPartonStatusPosition;
	}
	int pdgId() const
	{
		return (pdgid & KPartonChargeMask ? -1 : 1) * (pdgid & KPartonPdgIdMask);
	}
	int charge() const
	{
		return (pdgid & KPartonChargeMask ? -1 : 1);
	}
};
typedef std::vector<KParton> KPartons;

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
		return (pdgid & KPartonChargeMask ? -1 : 1) * (pdgid & KPartonPdgIdMask);
	}
	int charge() const
	{
		return (pdgid & KPartonChargeMask ? -1 : 1);
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
#endif

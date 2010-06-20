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

#endif

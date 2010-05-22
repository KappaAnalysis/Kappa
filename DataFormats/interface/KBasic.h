#ifndef KAPPA_BASIC_H
#define KAPPA_BASIC_H

#include "KLorentzVector.h"
#include <vector>
#include "Math/SMatrix.h"

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

struct KDataJet : public KDataLV
{
	double emf;
	double area;
	int n90, n90Hits;
	double noiseHCAL;
	double detectorEta;
	double fHPD, fRBX;
	int nTracksAtCalo;
	int nTracksAtVertex;
	int nConst;
};
typedef std::vector<KDataJet> KDataJets;

struct KDataPFJet : public KDataJet
{
	float neutralEmFraction, chargedEmFraction;
	float neutralHadFraction, chargedHadFraction;
};
typedef std::vector<KDataPFJet> KDataPFJets;

struct KLV
{
	typedef RMLV KInternalLV;
	RMLV p4;
};
typedef std::vector<KLV> KLVs;

struct KDataMET : public KDataLV
{
	double sumEt;
};

struct KDataPFMET : public KDataMET
{
	double chargedEMFraction;
};

// pdgid = [charge:1][status:3][id:...]
const unsigned int KPartonPdgIdMask = ((unsigned int)1 << 28) - (unsigned int)1;
const unsigned int KPartonChargeMask = (unsigned int)1 << 31;
const unsigned int KPartonStatusMask = (unsigned int)3 << 28;
const unsigned int KPartonChargePosition = 31;
const unsigned int KPartonStatusPosition = 28;
struct KParton
{
	typedef RMLV KInternalLV;
	RMLV p4;
	unsigned int pdgid;
	unsigned int children;

	int status()
	{
		return (pdgid & KPartonStatusMask) >> KPartonStatusPosition;
	}
	int pdgId()
	{
		return (pdgid & KPartonChargeMask ? -1 : 1) * (pdgid & KPartonPdgIdMask);
	}
};
typedef std::vector<KParton> KPartons;

#endif

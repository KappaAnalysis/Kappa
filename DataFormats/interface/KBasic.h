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

struct KDataTrack : public KDataLV
{
	char charge;
	float chi2, nDOF;
	float errPt, errEta, errPhi;
	float refRho2, refZ;
	int quality;
};
typedef std::vector<KDataTrack> KDataTracks;

struct KDataVertex
{
  RMPoint position;
	bool valid;

	unsigned int cntTracks;
	float chi2, nDOF;
	double chi2prob;

	ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> > covariance;
};
typedef std::vector<KDataVertex> KDataVertices;

struct KDataJet : public KDataLV
{
	double emf;
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

// pdgid = [charge:1][status:3][id:...]
const unsigned int KPartonChargeMask = 31;
const unsigned int KPartonStatusMask = 28;
struct KParton
{
	typedef RMLV KInternalLV;
	RMLV p4;
	unsigned int pdgid;
	unsigned int children;
};
typedef std::vector<KParton> KPartons;

#endif

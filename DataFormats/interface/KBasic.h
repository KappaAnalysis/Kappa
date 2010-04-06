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

struct KDataTrack : public KDataLV
{
	RMPoint ref;	// reference point ("vertex")
	char charge;
	float chi2, nDOF;
	float errPt, errEta, errPhi, errDxy, errDz;
	int nPixelHits,nStripHits; //dp
	int quality;

	double getDxy(KDataVertex * pv)
	{
		if (!pv)
			return -1.;
		return (
				- (ref.x()-pv->position.x()) * p4.y()
				+ (ref.y()-pv->position.y()) * p4.x()
			) / sqrt(p4.Perp2());
	}

	/*
		mode:
			0 - dxy
			1 - dxy/error(track)
			2 - dxy/sqrt(error(track)**2 + error(vertex)**2)
	*/
	double getIP(KDataVertex * pv, unsigned int mode = 0)
	{
		if (!pv)
			return -10000.;

		switch(mode)
		{
			case 0:
				return getDxy(pv);
				break;
			case 1:
				return getDxy(pv) / errDxy;
				break;
			case 2:
				ROOT::Math::SVector<double,3> orthog;
				orthog[0] = p4.y();
				orthog[1] = -p4.x();
				orthog[2] = 0;

				float vtxErr2 = 0; //ROOT::Math::Similarity(pv->covariance, orthog) / p4.Perp2();
				return getDxy(pv) / sqrt(errDxy*errDxy + vtxErr2 );
				break;
		}
		return -10000.;
	}
};
typedef std::vector<KDataTrack> KDataTracks;
enum KTrackQuality
{
	TQ_Loose = 0, TQ_Tight = 1, TQ_HighPurity = 2, TQ_Confirmed = 3, TQ_GoodIterative = 4
};

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

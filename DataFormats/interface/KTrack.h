/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_TRACK_H
#define KAPPA_TRACK_H

#include <Math/GenVector/VectorUtil.h>
#include "KBasic.h"

enum KTrackQuality
{
	TQ_Loose = 1 << 0, TQ_Tight = 1 << 1, TQ_HighPurity = 1 << 2, TQ_Confirmed = 1 << 3, TQ_GoodIterative = 1 << 4
};

struct KTrack : public KLV
{
	RMPoint ref;	// reference point ("vertex")
	char charge;
	float chi2, nDOF;
	float errPt, errEta, errPhi, errDxy, errDz;
	unsigned short nPixelLayers, nStripLayers;
	unsigned short nValidPixelHits, nValidStripHits;
	unsigned short nValidMuonHits, nLostMuonHits, nBadMuonHits;
	unsigned short nValidHits, nLostHits;
	unsigned short nInnerHits, nLostInnerHits;
	int quality;

	double getTrackIsolation(std::vector<KTrack> *tracks, double isoCone = 0.3, double vetoCone = 0.01, double minPt = 1.5)
	{
		double sum = 0.;
		for (std::vector<KTrack>::iterator it = tracks->begin(); it != tracks->end(); it++)
		{
			if (it->p4.pt() > minPt && ROOT::Math::VectorUtil::DeltaR(it->p4, p4) > vetoCone && ROOT::Math::VectorUtil::DeltaR(it->p4, p4) < isoCone)
			{
				// "real" track isolation takes only tracks near the studied track into account
				// (but there is even more magic why one needs isodeposits)
				//if ( std::abs(it->ref.z() - ref.z()) > 0.2 || sqrt( (it->ref.x() - ref.x() )*(it->ref.x() - ref.x() ) + (it->ref.y() - ref.y())*(it->ref.y() - ref.y()) + (it->ref.z() - ref.z())*(it->ref.z() - ref.z()) ) > 0.1 )
				//	continue;
				sum += it->p4.pt();
			}
		}
		return sum;
	}

	double getDxy(const KVertex * pv) const
	{
		if (!pv)
			return -1.;
		return (
			- (ref.x() - pv->position.x()) * p4.y()
			+ (ref.y() - pv->position.y()) * p4.x()
		) / sqrt(p4.Perp2());
	}

	double getDxy(const KBeamSpot *bs) const
	{
		if (!bs)
			return -1.;
		return (
			- (ref.x() - bs->position.x()) * p4.y()
			+ (ref.y() - bs->position.y()) * p4.x()
		) / sqrt(p4.Perp2());
	}

	double getDz(const KVertex *pv) const
	{
		if (!pv)
			return -1.;
		return ref.z() - pv->position.z() - (
				(ref.x() - pv->position.x()) * p4.x() +
				(ref.y() - pv->position.y()) * p4.y()
			) * p4.z() / p4.Perp2();
	}

	double getDz(const KBeamSpot *bs) const
	{
		if (!bs)
			return -1.;
		return ref.z() - bs->position.z() - (
				(ref.x() - bs->position.x()) * p4.x() +
				(ref.y() - bs->position.y()) * p4.y()
			) * p4.z() / p4.Perp2();
	}

	/*
		mode:
			0 - dxy
			1 - dxy/error(track)
			2 - dxy/sqrt(error(track)**2 + error(vertex)**2)
	*/
	double getIP(const KVertex *pv, unsigned int mode = 0) const
	{
		if (!pv)
			return -10000.;

		switch (mode)
		{
			case 0:
				return getDxy(pv);
				break;
			case 1:
				return getDxy(pv) / errDxy;
				break;
			case 2:
				ROOT::Math::SVector<double, 3> orthog;
				orthog[0] = p4.y();
				orthog[1] = -p4.x();
				orthog[2] = 0;

				float vtxErr2 = ROOT::Math::Similarity(pv->covariance, orthog) / p4.Perp2();
				return getDxy(pv) / sqrt(errDxy*errDxy + vtxErr2);
				break;
		}
		return -10000.;
	}

	/*
		mode:
			0 - dxy
			1 - dxy/error(track)
			2 - dxy/sqrt(error(track)**2 + error(vertex)**2)
	*/
	double getIP(const KBeamSpot *bs, unsigned int mode = 0) const
	{
		if (!bs)
			return -10000.;

		switch (mode)
		{
			case 0:
				return getDxy(bs);
				break;
			case 1:
				return getDxy(bs) / errDxy;
				break;
			case 2:
				ROOT::Math::SVector<double, 7> orthog;
				orthog[0] = p4.y();
				orthog[1] = -p4.x();
				for (int i = 2; i < 7; i++)
					orthog[i] = 0;

				float vtxErr2 = ROOT::Math::Similarity(bs->covariance, orthog) / p4.Perp2();
				return getDxy(bs) / sqrt(errDxy*errDxy + vtxErr2);
				break;
		}
		return -10000.;
	}
};
typedef std::vector<KTrack> KTracks;

struct KMuonTriggerCandidate : public KTrack
{
	bool isoDecision;
	float isoQuantity;
};

typedef std::vector<KMuonTriggerCandidate> KMuonTriggerCandidates;

struct KTrackSummary
{
	unsigned int nTracks;
	unsigned int nTracksHQ;
};

struct KLepton : public KLV
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
	KTrack track;
};

typedef std::vector<KLepton> KLeptons;

#endif

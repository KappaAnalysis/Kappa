//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_TRACK_H
#define KAPPA_TRACK_H

#include "KBasic.h"

#include <Math/GenVector/VectorUtil.h>

/** Data format definition for KTracks and KLeptons

 */

/// TrackBase::TrackQuality
/// from DataFormats/TrackReco/interface/TrackBase.h
namespace KTrackQuality {

enum KTrackQualityType
{
	undefQuality = -1, loose = 0, tight = 1, highPurity = 2, confirmed = 3, goodIterative = 4,
	looseSetWithPV = 5, highPuritySetWithPV = 6, qualitySize = 7
};
}

/// Kappa Track data format
/** copy from DataFormats/TrackReco/interface/TrackBase.h
    copy from DataFormats/TrackReco/interface/Track.h */
struct KTrack : public KLV
{
	/// reference point (formerly known as "vertex", not the PV)
	RMPoint ref;

	/// charge and fit quality
	char charge;
	float chi2, nDOF;
	float errPt, errEta, errPhi, errDxy, errDz;

	/// number of hits or tracker layers in detector components (used for lepton IDs)
	/// DataFormats/TrackReco/interface/HitPattern.h (numberOf...)
	/// layers and hits for pixel, strip tracker and muon system
	unsigned short nValidPixelHits;  //< number of valid hits in the pixel detector (for tight muID)
	unsigned short nValidStripHits;  //< number of valid hits in the strip detector
	unsigned short nValidMuonHits;   //< number of valid hits in the muon system (for tight muID)
	unsigned short nPixelLayers, nStripLayers; // for soft/tight muID as trackerLayers
	unsigned short nInnerHits;
	/// functions for combinations
	inline unsigned short nValidHits() const { return nValidPixelHits + nValidStripHits + nValidMuonHits; };
	inline unsigned short nValidTrackerHits() const { return nValidPixelHits + nValidStripHits; };
	inline unsigned short nTrackerLayers() const { return nPixelLayers + nStripLayers; };

	/// quality bitset
	unsigned char qualityBits; // for soft muID
	inline bool quality(KTrackQuality::KTrackQualityType bit) const
	{
		if (bit < 0) return false;
		return (qualityBits & (1 << bit));
	};

	/// distances to primary vertex, beamspot and interaction point
	/// all these function mix float and double precision values
	float getDxy(const KVertex * pv) const
	{
		if (!pv)
			return -1.;
		return (
			- (ref.x() - pv->position.x()) * p4.y()
			+ (ref.y() - pv->position.y()) * p4.x()
		) / sqrtf(p4.Perp2());
	}

	float getDxy(const KBeamSpot *bs) const
	{
		if (!bs)
			return -1.;
		return (
			- (ref.x() - bs->position.x()) * p4.y()
			+ (ref.y() - bs->position.y()) * p4.x()
		) / sqrtf(p4.Perp2());
	}

	float getDz(const KVertex *pv) const
	{
		if (!pv)
			return -1.;
		return ref.z() - pv->position.z() - (
				(ref.x() - pv->position.x()) * p4.x() +
				(ref.y() - pv->position.y()) * p4.y()
			) * p4.z() / p4.Perp2();
	}

	float getDz(const KBeamSpot *bs) const
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
	float getIP(const KVertex *pv, unsigned int mode = 0) const
	{
		if (!pv)
			return -10000.;

		//double error = static_cast<double>(errDxy);
		switch (mode)
		{
			case 0:
				return getDxy(pv);
			case 1:
				return getDxy(pv) / errDxy;
			case 2:
			{
				ROOT::Math::SVector<double, 3> orthog;
				orthog[0] = +p4.y();
				orthog[1] = -p4.x();
				orthog[2] = 0;

				float vtxErr2 = static_cast<float>(ROOT::Math::Similarity(pv->covariance, orthog)) / p4.Perp2();
				return getDxy(pv) / sqrtf(errDxy * errDxy + vtxErr2);
			}
			default:
				return -10000.;
		}
		return -10000.;
	}

	/*
		mode:
			0 - dxy
			1 - dxy/error(track)
			2 - dxy/sqrt(error(track)**2 + error(vertex)**2)
	*/
	float getIP(const KBeamSpot *bs, unsigned int mode = 0) const
	{
		if (!bs)
			return -10000.;

		//double error = static_cast<double>(errDxy);
		switch (mode)
		{
			case 0:
				return getDxy(bs);
			case 1:
				return getDxy(bs) / errDxy;
			case 2:
			{
				ROOT::Math::SVector<double, 7> orthog;
				orthog[0] = p4.y();
				orthog[1] = -p4.x();
				for (int i = 2; i < 7; i++)
					orthog[i] = 0;

				float vtxErr2 = static_cast<float>(ROOT::Math::Similarity(bs->covariance, orthog)) / p4.Perp2();
				return getDxy(bs) / sqrtf(errDxy * errDxy + vtxErr2);
			}
			default:
				return -10000.;
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

const unsigned char KLeptonFlavourMask = 3;
const unsigned char KLeptonChargeMask = 1 << 2;
const unsigned char KLeptonAlternativeTrackMask = 1 << 3;
const unsigned char KLeptonPFMask = 1 << 4;

struct KTrackSummary
{
	unsigned int nTracks;    //< number of tracks in the event
	unsigned int nTracksHQ;  //< number of high quality tracks in the event
};

#endif

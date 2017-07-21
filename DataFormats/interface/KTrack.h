//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_TRACK_H
#define KAPPA_TRACK_H

#include "KBasic.h"

#include <DataFormats/TrackReco/interface/Track.h>
#include <Math/GenVector/VectorUtil.h>
#include <TMath.h>

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
	virtual ~KTrack() {};

	/// reference point (formerly known as "vertex", not the PV)
	RMPoint ref;

	/// charge and fit quality
	short charge;
	float chi2, nDOF;
	float errPt, errEta, errPhi, errDxy, errDz;  ///< errors on four vector and distances
	float d2D, d3D;      ///< impact parameters dxy and d calculated considering the magnetic field
	float err3D, err2D;  ///< errors on the dxy (2D) and d (3D) impact parameters
	KVertex ipVertex;

	/// number of hits or tracker layers in detector components (used for lepton IDs)
	/// DataFormats/TrackReco/interface/HitPattern.h (numberOf...)
	/// layers and hits for pixel, strip tracker and muon system
	unsigned short nValidPixelHits;  //< number of valid hits in the pixel detector (for tight muID)
	unsigned short nValidStripHits;  //< number of valid hits in the strip detector
	unsigned short nValidMuonHits;   //< number of valid hits in the muon system (for tight muID)
	unsigned short nPixelLayers, nStripLayers, nTrackerLayersNew; // for soft/tight muID as trackerLayers
	unsigned short nInnerHits;
	/// functions for combinations
	inline unsigned int nValidHits() const { return nValidPixelHits + nValidStripHits + nValidMuonHits; };
	inline unsigned int nValidTrackerHits() const { return nValidPixelHits + nValidStripHits; };
	/// TODO: nTrackerLayers() should be removed/replaced with nTrackerLayersNew
	/// but this would require a reskim of old samples
	inline unsigned int nTrackerLayers() const { return nPixelLayers + nStripLayers; };

	/// quality bitset
	unsigned char qualityBits; // for soft muID
	inline bool quality(KTrackQuality::KTrackQualityType bit) const
	{
		if (bit < 0) return false;
		return (qualityBits & (1 << bit));
	};
	
	// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/DataFormats/TrackReco/interface/TrackBase.h#L3-L49
	std::vector<float> helixParameters()
	{
		KVertex origin;
		std::vector<float> parameters = { qOverP(), lambda(), phi(), getDxy(&origin), getDsz(&origin) };
		return parameters;
	}
	ROOT::Math::SMatrix<float, reco::Track::dimension, reco::Track::dimension, ROOT::Math::MatRepSym<float, reco::Track::dimension> > helixCovariance;
	
	float qOverP() const
	{
		return charge / p4.P();
	}
	float lambda() const
	{
		return TMath::PiOver2() - p4.Theta();
	}
	float phi() const
	{
		return p4.Phi();
	}

	/// distances to primary vertex, refitted primary vertex, beamspot and interaction point
	/// all these function mix float and double precision values
	template<class T>
	float getDxy(const T* pv) const
	{
		if (!pv)
			return -1.;
		return (
			- (ref.x() - pv->position.x()) * p4.y()
			+ (ref.y() - pv->position.y()) * p4.x()
		) / sqrtf(p4.Perp2());
	}

	template<class T>
	float getDz(const T* pv) const
	{
		if (!pv)
			return -1.;
		return ref.z() - pv->position.z() - (
				(ref.x() - pv->position.x()) * p4.x() +
				(ref.y() - pv->position.y()) * p4.y()
			) * p4.z() / p4.Perp2();
	}

	template<class T>
	float getDsz(const T* pv) const
	{
		if (!pv)
			return -1.;
		return getDz(pv) * std::cos(lambda());
	}

	/*
		mode:
			0 - dxy
			1 - dxy/error(track)
			2 - dxy/sqrt(error(track)**2 + error(vertex)**2)
	*/
	template<class T>
	float getIP(const T* pv, unsigned int mode = 0) const
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
};
typedef std::vector<KTrack> KTracks;

struct KMuonTriggerCandidate : public KTrack
{
	virtual ~KMuonTriggerCandidate() {};

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
	virtual ~KTrackSummary() {};

	unsigned int nTracks;    //< number of tracks in the event
	unsigned int nTracksHQ;  //< number of high quality tracks in the event
};

#endif

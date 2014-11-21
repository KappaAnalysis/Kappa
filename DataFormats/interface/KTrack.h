/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

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

	unsigned short nLostHits;
	unsigned short nPixelLayers, nStripLayers; // for soft/tight muID as trackerLayers
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

const unsigned char KLeptonFlavourMask = 3;
const unsigned char KLeptonChargeMask = 1 << 2;
const unsigned char KLeptonAlternativeTrackMask = 1 << 3;
const unsigned char KLeptonPFMask = 1 << 4;

namespace KLeptonFlavour { enum Type
{
	NONE     = 0,
	ELECTRON = 1,
	MUON     = 2,
	TAU      = 3
};
}

namespace KLeptonId { enum Type
{
	ANY    = 0,  //< returns true if the information for any ID was filled
	LOOSE  = 1,  //< e/mu/tau loose ID
	MEDIUM = 2,  //< e/tau medium ID
	TIGHT  = 3,  //< e/mu tight ID
	VETO   = 4,  //< e veto ID
	SOFT   = 5,  //< mu soft ID
	HIGHPT = 6,  //< mu high pt ID
	CUSTOM = 7,  //< empty bit for any userdefined ID
	LOOSEELECTRONREJECTION = 4, // tau discriminator
	LOOSEMUONREJECTION     = 5, // tau discriminator
	TIGHTMUONREJECTION     = 6  // tau discriminator
};
}

struct KLepton : public KLV
{
public:
	unsigned char leptonInfo;  //< bitset containing the flavour, charge and user bits
	unsigned char ids;         //< most relevant IDs of the lepton
	float sumChargedHadronPt;  //< sum pt of charged hadrons for isolation
	float sumNeutralHadronEt;  //< sum Et of neutral hadrons for isolation
	float sumPhotonEt;         //< sum Et of photons for isolation
	float sumPUPt;             //< sum pt of pile-up for isolation
	KTrack track;              //< (main) track of the lepton (e: GSF, mu: inner, tau: lead. PF candidate)

	// access functions for leptonInfo
	/// lepton flavour according to KLeptonFlavour::Type
	inline KLeptonFlavour::Type flavour() const { return KLeptonFlavour::Type(leptonInfo & KLeptonFlavourMask); };
	/// lepton charge (+1 or -1)
	inline char charge() const { return ((leptonInfo & KLeptonChargeMask) ? +1 : -1); };
	/// whether the stored object is reconstructed using PF objects
	inline bool isPF() const { return (leptonInfo & KLeptonPFMask); };
	/// if the normal track is not available, the producer can fill the track information with a second option and set this flag
	inline bool isAlternativeTrack() const { return (leptonInfo & KLeptonAlternativeTrackMask); };

	/// access function for ID bitset ids
	/// returns true if the ID is set and the flavour is correct
	inline bool isAvailable() const { return (ids & (1 << KLeptonId::ANY)); };    // e, mu, tau
	inline bool idLoose()     const { return (ids & (1 << KLeptonId::LOOSE)); };  // e, mu, tau
	inline bool idMedium()    const { return (ids & (1 << KLeptonId::MEDIUM)); }; // e, (mu,) tau
	inline bool idTight()     const { return (ids & (1 << KLeptonId::TIGHT)); };  // e, mu, tau
	inline bool idVeto()      const { return (ids & (1 << KLeptonId::VETO)   && (KLeptonFlavour::ELECTRON == (leptonInfo & KLeptonFlavourMask))); }; // e
	inline bool idSoft()      const { return (ids & (1 << KLeptonId::SOFT)   && (KLeptonFlavour::MUON == (leptonInfo & KLeptonFlavourMask))); };     // mu
	inline bool idHighPt()    const { return (ids & (1 << KLeptonId::HIGHPT) && (KLeptonFlavour::MUON == (leptonInfo & KLeptonFlavourMask))); };     // mu
	inline bool idLooseElectronRejection() const { return (ids & (1 << KLeptonId::LOOSEELECTRONREJECTION) && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau
	inline bool idLooseMuonRejection()     const { return (ids & (1 << KLeptonId::LOOSEMUONREJECTION)     && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau
	inline bool idTightMuonRejection()     const { return (ids & (1 << KLeptonId::TIGHTMUONREJECTION)     && (KLeptonFlavour::TAU == (leptonInfo & KLeptonFlavourMask))); }; // tau

	/// PF isolation with delta beta corrections (default fraction of pile-up is 0.5)
	inline double pfIso(const double puFraction=0.5) const
	{
		return sumChargedHadronPt + std::max(0.0,
			sumNeutralHadronEt + sumPhotonEt - puFraction * sumPUPt);
	}
	
	/// rho effective area isolation (approximation)
	/** this is an alternative method for pile-up subtraction:
	    PFIso = PF(ChHad PFNoPU) + Max(PF(Nh+Ph) - rho’EA), 0.0) with rho'=max(rho,0)
	    approximation: effective area as a circle area
	    rho is usually provided by a KPileupDensity object
	*/
	double pfIsoRho(const double rho = 0.0, const double radius = 0.4) const
	{
		double area = radius * radius * 3.14159;
		return std::max(0.0, pfIso(0.0) - std::max(rho * area, 0.0));
	}
};
typedef std::vector<KLepton> KLeptons;


struct KTrackSummary
{
	unsigned int nTracks;    //< number of tracks in the event
	unsigned int nTracksHQ;  //< number of high quality tracks in the event
};

#endif

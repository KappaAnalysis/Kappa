//- Copyright (c) 2014 - All Rights Reserved
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_PHOTON_H
#define KAPPA_PHOTON_H

/* IMPORTANT: This data format is not used currently! Changes will not be considered data format changes */

namespace KPhotonId { enum Type
{
	ANY    = 0,  //< returns true if the information for any ID was filled
	LOOSE  = 1,  //< photon loose ID
	MEDIUM = 2,  //< photon medium ID
	TIGHT  = 3,  //< photon tight ID
	VETO   = 4,  //< e veto ID
};
}

/// Photon dataformat
struct KPhoton : public KLV
{
	unsigned char ids;         ///< most relevant IDs of the photon
	float sumChargedHadronPt;  ///< sum pt of charged hadrons for isolation
	float sumNeutralHadronEt;  ///< sum Et of neutral hadrons for isolation
	float sumPhotonEt;         ///< sum Et of photons for isolation
	float sumPUPt;             ///< sum pt of pile-up for isolation	float hadTowerOverEm;

	float sigmaIetaIeta;

	inline bool idVeto() const { return (ids & (1 << KPhotonId::VETO)); };  // electron veto

	/// PF isolation with delta beta corrections (default fraction of pile-up is 0.5)
	inline double pfIso(const double puFraction=0.5) const
	{
		return sumChargedHadronPt + std::max(0.0,
			sumNeutralHadronEt + sumPhotonEt - puFraction * sumPUPt);
	}
};
typedef std::vector<KPhoton> KPhotons;

#endif


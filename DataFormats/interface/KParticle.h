//- Copyright (c) 2014 - All Rights Reserved
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_PARTICLE_H
#define KAPPA_PARTICLE_H

#include "KBasic.h"

/// Particle base class for generator particles or candidates
struct KParticle : public KLV
{
	virtual ~KParticle() {};

	/// bitset containing the status and the signed PDG-ID
	int pdgId;  ///< PDG-ID of the particle

	int sign() const
	{
		return (pdgId > 0) - (pdgId < 0);
	}

	/// particle charge multiplied by 3 (for integer comparisons)
	/** e.g. 2 for up-quark, -3 for electron
	    valid for quarks, leptons, bosons, diquarks, mesons and baryons
	    not valid for special, technicolor, SUSY, Kaluza-Klein particles, R-hadrons and pentaquarks
	*/
	int chargeTimesThree() const
	{
		int pdg = std::abs(pdgId);
		int had = pdg % 10000 / 10;  // quark content of hadrons (digits 2-4)

		if (pdg == 0)
			return 0;
		// quark
		if (pdg < 9)
			return (-3 * (pdg % 2) + 2) * sign();
		// lepton
		if (pdg > 10 && pdg < 19)
			return -3 * (pdg % 2) * sign();
		// boson
		if (pdg > 20 && pdg < 40)
			return (pdg == 24 || pdg == 34 || pdg == 37) ? 3 * sign() : 0;
		// meson
		if (had < 100)
		{
			int q1 = -3 * (had / 10 % 2) + 2;
			int q2 = -3 * (had % 2) + 2;
			return (q1 - q2) * sign();
		}
		// baryon
		else
		{
			int q1 = had / 100;
			int q2 = had / 10 % 10;
			int q3 = had % 10;
			q1 = (q1 == 0) ? 0 : -3 * (q1 % 2) + 2;
			q2 = (q2 == 0) ? 0 : -3 * (q2 % 2) + 2;
			q3 = (q3 == 0) ? 0 : -3 * (q3 % 2) + 2;
			return (q1 + q2 + q3) * sign();
		}
	}

	/// particle charge
	double charge() const
	{
		return chargeTimesThree() / 3.;
	}
};
typedef std::vector<KParticle> KParticles;


/// from DataFormats/HepMCCandidate/interface/GenStatusFlags.h
namespace KGenStatusFlags { enum Type
{
	isPrompt                           = 0,
	isDecayedLeptonHadron              = 1,
	isTauDecayProduct                  = 2,
	isPromptTauDecayProduct            = 3,
	isDirectTauDecayProduct            = 4,
	isDirectPromptTauDecayProduct      = 5,
	isDirectHadronDecayProduct         = 6,
	isHardProcess                      = 7,
	fromHardProcess                    = 8,
	isHardProcessTauDecayProduct       = 9,
	isDirectHardProcessTauDecayProduct = 10,
	isLastCopy                         = 11
};
}

/// particleinfo = [custom: 10 bits][status: 7 bits][flags: 15 bits]
/// particleid   = [id: 32 bits]
const unsigned int KGenParticleCustomPosition = 15 + 7;
const unsigned int KGenParticleStatusPosition = 15;
const unsigned int KGenParticleFlagsMask =  32767u;
const unsigned int KGenParticleStatusMask = 127u << KGenParticleStatusPosition;
const unsigned int KGenParticleCustomMask = 1023u << KGenParticleCustomPosition;

struct KMotherDaughterRelation
{
	virtual ~KMotherDaugtherRelation() {};

	std::vector<unsigned int> daughterIndices;

	/// return the number of daughters
	unsigned long nDaughters() const
	{
		return daughterIndices.size();
	}

	/// return index of daughter i
	/** returns -1 in case i >= numberOfDaughters */
	long daughterIndex(unsigned int i) const
	{
		if (i < daughterIndices.size())
			return static_cast<long>(daughterIndices.at(i));
		else
			return -1;
	}
};


/// Generator particle
struct KGenParticle : public KParticle, public KMotherDaughterRelation
{
	virtual ~KGenParticle() {};

	unsigned int particleinfo;

	/// Monte-Carlo generator status, cf. [KParticle](md_docs_objects.html#obj-particle)
	int status() const
	{
		return (particleinfo & KGenParticleStatusMask) >> KGenParticleStatusPosition;
	}

	inline bool isPrompt()           const { return ((particleinfo & (1 << KGenStatusFlags::isPrompt))); };
	inline bool isPromptFinalState() const { return ((particleinfo & (1 << KGenStatusFlags::isPrompt)) && status() == 1); };
	inline bool isPromptDecayed()    const { return ((particleinfo & (1 << KGenStatusFlags::isPrompt)) && (particleinfo & (1 << KGenStatusFlags::isDecayedLeptonHadron))); };
	inline bool isDirectPromptTauDecayProduct()                const { return ((particleinfo & (1 << KGenStatusFlags::isDirectPromptTauDecayProduct))); };
	inline bool isDirectPromptTauDecayProductFinalState()      const { return ((particleinfo & (1 << KGenStatusFlags::isDirectPromptTauDecayProduct)) && status() == 1); };
	inline bool isDirectHardProcessTauDecayProduct()           const { return ((particleinfo & (1 << KGenStatusFlags::isDirectHardProcessTauDecayProduct))); };
	inline bool isDirectHardProcessTauDecayProductFinalState() const { return ((particleinfo & (1 << KGenStatusFlags::isDirectHardProcessTauDecayProduct)) && status() == 1); };
	inline bool isHardProcess()             const { return ((particleinfo & (1 << KGenStatusFlags::isHardProcess))); };
	inline bool fromHardProcessFinalState() const { return ((particleinfo & (1 << KGenStatusFlags::fromHardProcess)) && status() == 1); };
	inline bool fromHardProcessDecayed()    const { return ((particleinfo & (1 << KGenStatusFlags::fromHardProcess)) && (particleinfo & (1 << KGenStatusFlags::isDecayedLeptonHadron))); };
	inline bool isLastCopy()                const { return ((particleinfo & (1 << KGenStatusFlags::isLastCopy))); };
};
typedef std::vector<KGenParticle> KGenParticles;


/// Generator photon
struct KGenPhoton : public KLV
{
	virtual ~KGenPhoton() {};

	KLV mother;
	char type;
	bool isPhoton() const { return (type == 1); }
	bool isPi0() const { return (type == 2); }
};
typedef std::vector<KGenPhoton> KGenPhotons;


/// Generator tau
struct KGenTau : public KGenParticle
{
	virtual ~KGenTau() {};

	KLV visible;              //< momentum four-vector of visible particles
	RMPoint vertex;           //< vertex

	/// decay mode
	/** bit definition:
	0 - undefined
	1 - electron
	2 - muon
	>2 - hadronic
	    3 - 1prong
	    4 - 3prong
	    5 - >3prong
	most significant bit (1<<7):
	    0 - tau
	    1 - descendant of a tau
	*/
	unsigned char decayMode;

	static const int DescendantMask = 1 << 7;

	bool isElectronicDecay() const { return (decayMode & ~DescendantMask) == 1; }
	bool isMuonicDecay() const { return (decayMode & ~DescendantMask) == 2; }
	bool isHadronicDecay() const { return (decayMode & ~DescendantMask) > 2; }
	bool is1Prong() const { return (decayMode & ~DescendantMask) == 3; }
	bool is3Prong() const { return (decayMode & ~DescendantMask) == 4; }
	bool isXProng() const { return (decayMode & ~DescendantMask) == 5; }
	bool isDescendant() const { return (decayMode & DescendantMask) != 0; }
};
typedef std::vector<KGenTau> KGenTaus;


/// Particle-Flow Candidate
struct KPFCandidate : public KParticle, public KMotherDaughterRelation
{
	virtual ~KPFCandidate() {};

	double deltaP;            //< momentum difference?
	double ecalEnergy;        //< energy deposited in ECAL
	double hcalEnergy;        //< energy deposited in HCAL
	RMPoint vertex;           //< vertex
	KTrack track;
};
typedef std::vector<KPFCandidate> KPFCandidates;

#endif


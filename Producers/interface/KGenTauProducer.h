//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>

#ifndef KAPPA_GENTAUPRODUCER_H
#define KAPPA_GENTAUPRODUCER_H

#include "KGenParticleProducer.h"
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>

class KGenTauProducer : public KBasicGenParticleProducer<KGenTaus>
{
public:
	KGenTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBasicGenParticleProducer<KGenTaus>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "GenTaus"; }

protected:
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		selectStatus(pset.getParameter<int>("selectedStatus"));

		// Select taus only
		const int particles = 15; // tau pdg ID
		selectParticles(&particles, &particles + 1);

		KBasicGenParticleProducer<KGenTaus>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KBasicGenParticleProducer<KGenTaus>::fillSingle(in, out);

		DecayInfo info;
		walkDecayTree(dynamic_cast<const reco::GenParticle&>(in), info);

		out.visible.p4 = info.p4_vis;

		switch(info.mode)
		{
		case DecayInfo::Electronic:
			out.decayMode = 1;
			assert(info.n_charged == 1);
			break;
		case DecayInfo::Muonic:
			out.decayMode = 2;
			assert(info.n_charged == 1);
			break;
		case DecayInfo::Hadronic:
			if(info.n_charged == 1)
				out.decayMode = 3;
			else if(info.n_charged == 3)
				out.decayMode = 4;
			else
				out.decayMode = 5;

			// TODO: Can this happen?
			if( (info.n_charged % 2) == 0)
				printf("Kappa GenTau producer warning: %d charged particles in tau decay!\n", info.n_charged);

			break;
		default:
			assert(false);
			break;
		}

		// Just for the sake of completeness... note that we filter descendant
		// taus anyway in acceptSingle
		if(in.mother() && std::abs(in.mother()->pdgId()) == 15)
			out.decayMode |= KGenTau::DescendantMask;

		out.vertex = in.vertex();
	}

	virtual bool acceptSingle(const SingleInputType& in)
	{
		if(!KBasicGenParticleProducer<KGenTaus>::acceptSingle(in))
			return false;

		// Reject decendant taus as all relevant information is contained in the
		// top-level tau anyway
		if(in.mother() && std::abs(in.mother()->pdgId()) == 15)
			return false;

		// Check one level above the mother, to be sure that the taus don't come
		// from an intermediate gamma emission from another tau
		if(in.mother()->mother() && std::abs(in.mother()->mother()->pdgId()) == 15)
			return false;

		return true;
	}

private:
	struct DecayInfo
	{
		// mode is hadronic as long as we do not find an electron or muon in the
		// first level of the decay chain
		DecayInfo(): p4_vis(0,0,0,0), mode(Hadronic), n_charged(0) {}

		RMDLV p4_vis;
		enum { Electronic, Muonic, Hadronic } mode;
		unsigned int n_charged;
	};

	void walkDecayTree(const reco::GenParticle& in, DecayInfo& info, int level = 0)
	{
		//for(int i = 0; i < level; ++i) printf(" ");
		//printf("PDG %d\tstatus %d", in.pdgId(), in.status());

		RMDLV p4(0,0,0,0);
		if(in.numberOfDaughters() == 0)
		{
			//printf("\n");

			// Check that the final particle of the chain is a direct tau decay product, avoiding,
			// for example, particles coming from intermediate gamma emission, which are listed as
			// tau daughters in prunedGenParticle collections. Method available only from 74X.
#if (CMSSW_MAJOR_VERSION > 7) || (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 4)
			if(in.status() == 1 && !isNeutrino(in.pdgId()) && in.statusFlags().isDirectTauDecayProduct() 
								       && in.statusFlags().isDirectHardProcessTauDecayProduct())
#else
			if(in.status() == 1 && !isNeutrino(in.pdgId()))
#endif
			{
				RMDLV p4;
				copyP4(in.p4(), p4);
				info.p4_vis += p4;

				if(std::abs(in.pdgId()) == 11 && std::abs(in.mother()->pdgId()) == 15) info.mode = DecayInfo::Electronic;
				if(std::abs(in.pdgId()) == 13 && std::abs(in.mother()->pdgId()) == 15) info.mode = DecayInfo::Muonic;

				if(in.charge() != 0) ++info.n_charged;
			}
		}
		else if(in.numberOfDaughters() == 1)
		{
			//printf("\tone child, keeping level... ");
			// Don't increase level since this does not seem to be a "real"
			// decay but just an intermediate generator step
			walkDecayTree(static_cast<const reco::GenParticle&>(*in.daughter(0)), info, level);
		}
		else if(in.numberOfDaughters() == 2 && (
				(std::abs(in.daughter(0)->pdgId()) == 22 && std::abs(in.daughter(1)->pdgId()) == 15) ||
				(std::abs(in.daughter(0)->pdgId()) == 15 && std::abs(in.daughter(1)->pdgId()) == 22))
			   )
		{
			//printf("\tinterm. gamma emission, keeping level... ");
			// Don't increase level since this does not seem to be a "real"
			// decay but just an intermediate emission of a photon
			// Don't follow photon decay path
			if (std::abs(in.daughter(0)->pdgId()) == 15)
				walkDecayTree(dynamic_cast<const reco::GenParticle&>(*in.daughter(0)), info, level);
			else
				walkDecayTree(dynamic_cast<const reco::GenParticle&>(*in.daughter(1)), info, level);
		}
		else if(in.numberOfDaughters() == 2 && std::abs(in.pdgId()) == 111 &&
				std::abs(in.daughter(0)->pdgId()) == 22 && std::abs(in.daughter(1)->pdgId()) == 22)
		{
			//printf("\tneutral pion, stop recursion. ");
			//printf("\n");
			// Neutral pion, save four-momentum in the visible component
			RMDLV p4;
			copyP4(in.p4(), p4);
			info.p4_vis += p4;
		}
		else
		{
			//printf("\t%lu children, recurse...\n", in.numberOfDaughters());
			for(unsigned int i = 0; i < in.numberOfDaughters(); ++i)
				walkDecayTree(dynamic_cast<const reco::GenParticle&>(*in.daughter(i)), info, level + 1);
		}
	}

	static bool isNeutrino(int pdg_id)
	{
		return std::abs(pdg_id) == 12 || std::abs(pdg_id) == 14 || std::abs(pdg_id) == 16;
	}
};

#endif

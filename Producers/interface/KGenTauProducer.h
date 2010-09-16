#ifndef KAPPA_GENTAUPRODUCER_H
#define KAPPA_GENTAUPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>

struct KGenTauProducer_Product
{
	typedef std::vector<KDataGenTau> type;
	static const std::string id() { return "std::vector<KDataGenTau>"; };
	static const std::string producer() { return "KGenTauProducer"; };
};

class KGenTauProducer : public KBasicPartonProducer<KGenTauProducer_Product>
{
public:
	KGenTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBasicPartonProducer<KGenTauProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KGenTauProducer() {};
protected:
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		selectStatus(pset.getParameter<int>("selectedStatus"));

		// Select taus only
		const int particles = 15; // tau pdg ID
		selectParticles(&particles, &particles + 1);

		KBasicPartonProducer<KGenTauProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KBasicPartonProducer<KGenTauProducer_Product>::fillSingle(in, out);

		DecayInfo info;
		walkDecayTree(in, info);

		out.p4_vis = info.p4_vis;

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
				std::cerr << "Kappa GenTau producer warning: %d charged particles in tau decay!" << std::endl;

			break;
		default:
			assert(false);
			break;
		}

		// Just for the sake of completeness... note that we filter descendant
		// taus anyway in acceptSingle
		if(in.mother() && abs(in.mother()->pdgId()) == 15)
			out.decayMode |= KDataGenTau::DescendantMask;

		out.vertex = in.vertex();
	}

	virtual bool acceptSingle(const SingleInputType& in)
	{
		if(!KBasicPartonProducer<KGenTauProducer_Product>::acceptSingle(in))
			return false;

		// Reject decendant taus as all relevant information is contained in the
		// top-level tau anyway
		if(in.mother() && abs(in.mother()->pdgId()) == 15)
			return false;

		return true;
	}

private:
	struct DecayInfo
	{
		// mode is hadronic as long as we do not find an electron or muon in the
		// first level of the decay chain
		DecayInfo(): p4_vis(0,0,0,0), mode(Hadronic), n_charged(0) {}

		RMLV p4_vis;
		enum { Electronic, Muonic, Hadronic } mode;
		unsigned int n_charged;
	};

	void walkDecayTree(const reco::Candidate& in, DecayInfo& info, int level = 0)
	{
		//for(int i = 0; i < level; ++i) printf(" ");
		//printf("PDG %d\tstatus %d", in.pdgId(), in.status());

		RMLV p4(0,0,0,0);
		if(in.numberOfDaughters() == 0)
		{
			//printf("\n");
			if(in.status() == 1 && !isNeutrino(in.pdgId()))
			{
				RMLV p4;
				copyP4(in.p4(), p4);
				info.p4_vis += p4;

				if(abs(in.pdgId()) == 11 && abs(in.mother()->pdgId()) == 15) info.mode = DecayInfo::Electronic;
				if(abs(in.pdgId()) == 13 && abs(in.mother()->pdgId()) == 15) info.mode = DecayInfo::Muonic;

				if(in.charge() != 0) ++info.n_charged;
			}
		}
		else if(in.numberOfDaughters() == 1)
		{
			//printf("\tone child, keeping level... ");
			// Don't increase level since this does not seem to be a "real"
			// decay but just an intermediate generator step
			walkDecayTree(*in.daughter(0), info, level);
		}
		else
		{
			//printf("\t%d children, recurse...\n", in.numberOfDaughters());
			for(unsigned int i = 0; i < in.numberOfDaughters(); ++i)
				walkDecayTree(*in.daughter(i), info, level + 1);
		}
	}

	static bool isNeutrino(int pdg_id)
	{
		return abs(pdg_id) == 12 || abs(pdg_id) == 14 || abs(pdg_id) == 16;
	}
};

#endif

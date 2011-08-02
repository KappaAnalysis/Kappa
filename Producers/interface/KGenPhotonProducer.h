#ifndef KAPPA_GENPHOTONPRODUCER_H
#define KAPPA_GENPHOTONPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>
#include <queue>

struct KGenPhotonProducer_Product
{
	typedef std::vector<KGenPhoton> type;
	static const std::string id() { return "std::vector<KGenPhoton>"; };
	static const std::string producer() { return "KGenPhotonProducer"; };
};

class KGenPhotonProducer : public KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotonProducer_Product>
{
public:
	KGenPhotonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotonProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KGenPhotonProducer() {};

protected:
	virtual void fillSingle(const KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotonProducer_Product>::SingleInputType &in,  KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotonProducer_Product>::SingleOutputType &out)
	{
		copyP4(in, out.p4);

		out.type = 0;
		if (in.pdgId() == 22)
			out.type = 1;
		if (in.pdgId() == 111)
			out.type = 2;
	
		if (in.numberOfMothers() > 0)
		{
			out.mother = RMDataLV();
			
			if (in.pdgId() == 111)
			{
				std::queue<const reco::Candidate *> ancestors;
				ancestors.push(&in);
			
				while (!ancestors.empty())
				{
					int tmpID = std::abs(ancestors.front()->pdgId());
					if (tmpID == 11 || tmpID == 13 || tmpID == 15)
					{
						if (this->verbosity > 2)
							std::cout << "corresponding lepton found: "<< tmpID << "\n";
						copyP4(ancestors.front()->p4(), out.mother);
					}
					else
						for (size_t idx = 0; idx < ancestors.front()->numberOfMothers(); idx++)
							ancestors.push(ancestors.front()->mother(idx));
					ancestors.pop();
				}
			}
			else
				copyP4(in.mother(0)->p4(), out.mother);
		}

		if (this->verbosity > 2)
		{
			std::cout << "child:             " << out.p4 << "\t" << in.pdgId() << "\n";
			std::cout << "mother:            " << in.mother(0)->polarP4() << "\t" << in.mother(0)->pdgId()<< "\n";
			std::cout << "associated mother: " << out.mother << "\n";

			std::cout << "isPhoton? " << out.isPhoton() << "\n";
			std::cout << "   isPi0? " << out.isPi0() << "\n";
		}
	}
	virtual bool acceptSingle(const KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotonProducer_Product>::SingleInputType &in)
	{
		if ( this->verbosity > 2 &&
			(
				std::abs(in.pdgId()) == 11 
				|| std::abs(in.pdgId()) == 13
				|| std::abs(in.pdgId()) == 15
			)
			)
			std::cout << "lepton: " <<in.pdgId() << "\t" << in.status() << "\t"<< in.polarP4() << "\n";

		if (in.numberOfMothers() == 0)
			return false;
		
		// photon radiated by lepton
		if (in.pdgId() == 22
			&& (
				std::abs(in.mother(0)->pdgId()) == 11
				|| std::abs(in.mother(0)->pdgId()) == 13
				|| std::abs(in.mother(0)->pdgId()) == 15
				)	
			)
			return true;

		// photon coming from pi0 - but is pi0 coming from a tau?
		if (
			(in.pdgId() == 22 && std::abs(in.mother(0)->pdgId()) == 111)
			|| in.pdgId() == 111
		)
		{
			std::queue<const reco::Candidate *> ancestors;
			ancestors.push(&in);
			
			while (!ancestors.empty())
			{
				int tmpID = std::abs(ancestors.front()->pdgId());
				if (tmpID == 11 || tmpID == 13 || tmpID == 15)
					return true;
				else
					for (size_t idx = 0; idx < ancestors.front()->numberOfMothers(); idx++)
						ancestors.push(ancestors.front()->mother(idx));
				ancestors.pop();
			}
		}
		
		if (in.pdgId() == 111
			&& (
				std::abs(in.mother(0)->pdgId()) == 11
				|| std::abs(in.mother(0)->pdgId()) == 13
				|| std::abs(in.mother(0)->pdgId()) == 15
				)	
			)
			return true;

		return false;
	}

	void selectStatus(int status)
	{
		selectedStatus = status;
	}

private:
	int selectedStatus; // bit map
	std::vector<int> selectedParticles;
};


#endif

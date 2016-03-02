//- Copyright (c) 2011 - All Rights Reserved
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>

#ifndef KAPPA_GENPHOTONPRODUCER_H
#define KAPPA_GENPHOTONPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include <queue>

class KGenPhotonProducer : public KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotons>
{
public:
	KGenPhotonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotons>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "GenPhotons"; }

protected:
	virtual void fillSingle(const KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotons>::SingleInputType &in,  KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotons>::SingleOutputType &out)
	{
		copyP4(in, out.p4);

		out.type = 0;
		if (in.pdgId() == 22)
			out.type = 1;
		if (in.pdgId() == 111)
			out.type = 2;
	
		if (in.numberOfMothers() > 0)
		{
			out.mother.p4 = RMFLV();
			
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
							std::cout << "KGenPhotonProducer::fillSingle : corresponding lepton found: "<< tmpID << "\n";
						copyP4(ancestors.front()->p4(), out.mother.p4);
					}
					else
						for (size_t idx = 0; idx < ancestors.front()->numberOfMothers(); ++idx)
							ancestors.push(ancestors.front()->mother(idx));
					ancestors.pop();
				}
			}
			else
				copyP4(in.mother(0)->p4(), out.mother.p4);
		}

		if (this->verbosity > 2)
		{
			std::cout << "KGenPhotonProducer::fillSingle :child:             " << out.p4 << "\t" << in.pdgId() << "\n";
			std::cout << "KGenPhotonProducer::fillSingle :mother:            " << in.mother(0)->polarP4() << "\t" << in.mother(0)->pdgId()<< "\n";
			std::cout << "KGenPhotonProducer::fillSingle :associated mother: " << out.mother.p4 << "\n";

			std::cout << "KGenPhotonProducer::fillSingle :isPhoton? " << out.isPhoton() << "\n";
			std::cout << "KGenPhotonProducer::fillSingle :   isPi0? " << out.isPi0() << "\n";
		}
	}
	virtual bool acceptSingle(const KBaseMultiLVProducer<edm::View<reco::Candidate>, KGenPhotons>::SingleInputType &in)
	{
		if ( this->verbosity > 2 &&
			(
				std::abs(in.pdgId()) == 11 
				|| std::abs(in.pdgId()) == 13
				|| std::abs(in.pdgId()) == 15
			)
			)
			std::cout << "KGenPhotonProducer::fillSingle :lepton: " <<in.pdgId() << "\t" << in.status() << "\t"<< in.polarP4() << "\n";

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
					for (size_t idx = 0; idx < ancestors.front()->numberOfMothers(); ++idx)
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

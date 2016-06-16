//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_PackedPFCandidatePRODUCER_H
#define KAPPA_PackedPFCandidatePRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/ParticleFlowCandidate/interface/PFCandidate.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KPackedPFCandidateProducer : public KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>
{
public:
	KPackedPFCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "packedPFCandidates"; }

	virtual void fillProduct(const InputType& in, OutputType& out,
							 const std::string& name, const edm::InputTag* tag, const edm::ParameterSet& pset) override
	{
		if (KBaseProducer::verbosity > 0)
			std::cout << "KPackedPFParticleProducer::fillProduct : " << in.size() <<  "objects in collection " << name << std::endl;

		out.reserve(in.size());

		// fill daughterDict for each PFCandidate
		daughterDict.clear();
		typename InputType::const_iterator lvit;
		for (index = 0, lvit = in.begin(); lvit < in.end(); ++lvit)
		{
			const reco::Candidate* lvptr = dynamic_cast <const reco::Candidate*>(&(*lvit));
			daughterDict[lvptr] = index++;
		}

		for (index = 0, lvit = in.begin(); lvit < in.end(); ++lvit)
		{
			// obtain list of daughter indices
			std::vector<reco::Candidate::index> daughters;
			for (reco::Candidate::index nd = 0; nd < lvit->numberOfDaughters(); ++nd)
			{
				daughters.push_back(daughterDict.find(lvit->daughter(nd))->second);
			}
			out.push_back(SingleOutputType());
			fillPackedPFCandidate(*lvit, out.back(), daughters);
			++index;
		}
		if (maxN > 0)
			out.erase(out.begin() + std::min(out.size(), (size_t)maxN), out.end());
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out) override
	{
		//KPackedPFCandidateProducer::fillPackedPFCandidate(in, out);
	}

	template<class Tin, class Tout>
	static void fillPackedPFCandidate(const Tin &in, Tout &out, const std::vector<reco::Candidate::index>& daughters = std::vector<reco::Candidate::index>())
	{
		copyP4(in, out.p4);
		out.pdgId = in.pdgId();

		//out.deltaP = in.deltaP(); // not included in packedPFCandidates
		//out.hcalEnergy = in.hcalFraction() * in.energy;
		//out.ecalEnergy = (1 - in.ecalFraction()) * in.energy;
		out.vertex = in.vertex();
		if(in.bestTrack())
			KTrackProducer::fillTrack(*in.bestTrack(), out.track);
		out.daughterIndices = daughters;
	}

protected:
	std::map<const reco::Candidate*, reco::Candidate::index> daughterDict;
	reco::Candidate::index index;
};

#endif

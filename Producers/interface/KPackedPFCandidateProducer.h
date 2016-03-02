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
#include "FWCore/Framework/interface/ConsumesCollector.h"

class KPackedPFCandidateProducer : public KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>
{
public:
	KPackedPFCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "packedPFCandidates"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.pdgId = in.pdgId();

		// KParticles are smaller than KPFCandidates
		//out.deltaP = in.deltaP(); // all not included in packedPFCandidates
		//out.hcalEnergy = in.hcalEnergy();
		//out.ecalEnergy = in.ecalEnergy();
	}
};

#endif

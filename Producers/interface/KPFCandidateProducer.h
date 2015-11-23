//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_PFCandidatePRODUCER_H
#define KAPPA_PFCandidatePRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/ParticleFlowCandidate/interface/PFCandidate.h>

class KPFCandidateProducer : public KBaseMultiLVProducer<edm::View<reco::PFCandidate>, KPFCandidates>
{
public:
	KPFCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::PFCandidate>, KPFCandidates>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "PFCandidates"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KPFCandidateProducer::fillPFCandidate(in, out);
	}

	static void fillPFCandidate(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.particleid = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		if (in.pdgId() < 0)
			out.particleinfo |= KParticleSignMask;
		out.deltaP = in.deltaP();
		out.hcalEnergy = in.hcalEnergy();
		out.ecalEnergy = in.ecalEnergy();
	}
};

#endif

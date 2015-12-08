//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_PackedPFCandidatePRODUCER_H
#define KAPPA_PackedPFCandidatePRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/ParticleFlowCandidate/interface/PFCandidate.h>

class KPackedPFCandidateProducer : public KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>
{
public:
	KPackedPFCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "packedPFCandidates"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.particleid = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		if (in.pdgId() < 0)
			out.particleinfo |= KParticleSignMask;
		//out.deltaP = in.deltaP(); // all not included in packedPFCandidates
		//out.hcalEnergy = in.hcalEnergy();
		//out.ecalEnergy = in.ecalEnergy();
	}
};

#endif

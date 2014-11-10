/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_CandidatePRODUCER_H
#define KAPPA_CandidatePRODUCER_H

#include "KBaseMultiLVProducer.h"

class KCandidateProducer : public KBaseMultiLVProducer<edm::View<reco::Candidate>, KCandidates>
{
public:
	KCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::Candidate>, KCandidates>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "Candidates"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KCandidateProducer::fillCandidate(in, out);
	}

	static void fillCandidate(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.particleinfo = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		if (in.pdgId() < 0)
			out.particleinfo |= KParticleSignMask;
	}

};

#endif

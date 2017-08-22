//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_PackedPFCandidatePRODUCER_H
#define KAPPA_PackedPFCandidatePRODUCER_H


#include "KBaseMultiLVProducer.h"
#include <DataFormats/PatCandidates/interface/PackedCandidate.h>
#include <DataFormats/ParticleFlowCandidate/interface/PFCandidate.h>
#include <DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h>
#include <FWCore/Framework/interface/EDProducer.h>

class KPackedPFCandidateProducer : public KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>
{
public:
	KPackedPFCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::PackedCandidate>, KPFCandidates>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "packedPFCandidates"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KPackedPFCandidateProducer::fillPackedPFCandidate(in, out);
	}

	template<class Tin, class Tout>
	static void fillPackedPFCandidate(const Tin &in, Tout &out)
	{
		
		copyP4(in, out.p4);
		out.pdgId = in.pdgId();
		// Cast is needed to access the quantities of pat::PackedCandidate. The edm::View only delivers reco::Candidate,
		// because not defined for pat::PackedCandidate.
		// See e.g. in https://github.com/cms-sw/cmssw/blob/a6eafda7f604bdff36459e9c4ae158c387b77f4f/CommonTools/PileupAlgos/plugins/PuppiProducer.cc
		pat::PackedCandidate casted_in = *(dynamic_cast<const pat::PackedCandidate*>(&in));
		// Definition of the function fromPV():
		// https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2016
		// Have to use fromPV() > 1 for isolation studies and calculation.
		out.fromFirstPVFlag = casted_in.fromPV();
	}
};

#endif

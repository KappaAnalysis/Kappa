//- Copyright (c) 2011 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_REFITVERTEXSUMMARYPRODUCER_H
#define KAPPA_REFITVERTEXSUMMARYPRODUCER_H

#include "KRefitVertexProducer.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KRefitVertexSummaryProducer : public KBaseMultiProducer<edm::View<RefitVertex>, KVertexSummary>
{
public:
	KRefitVertexSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<edm::View<RefitVertex>, KVertexSummary>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "RefitVertexSummary"; }

	virtual void clearProduct(OutputType &output) { output.pv = KVertex(); output.nVertices = 0; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.nVertices = in.size();
		if (out.nVertices > 0)
			KRefitVertexProducer::fillVertex(*in.begin(), out.pv);
	}
};

#endif

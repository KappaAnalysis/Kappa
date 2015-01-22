//- Copyright (c) 2011 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_VERTEXSUMMARYPRODUCER_H
#define KAPPA_VERTEXSUMMARYPRODUCER_H

#include "KVertexProducer.h"

class KVertexSummaryProducer : public KBaseMultiProducer<edm::View<reco::Vertex>, KVertexSummary>
{
public:
	KVertexSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::Vertex>, KVertexSummary>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "VertexSummary"; }

	virtual void clearProduct(OutputType &output) { output.pv = KVertex(); output.nVertices = 0; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.nVertices = in.size();
		if (out.nVertices > 0)
			KVertexProducer::fillVertex(*in.begin(), out.pv);
	}
};

#endif

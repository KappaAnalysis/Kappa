/* Copyright (c) 2011 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 */

#ifndef KAPPA_VERTEXSUMMARYPRODUCER_H
#define KAPPA_VERTEXSUMMARYPRODUCER_H

#include "KVertexProducer.h"

struct KVertexSummaryProducer_Product
{
	typedef KVertexSummary type;
	static const std::string id() { return "KVertexSummary"; };
	static const std::string producer() { return "KVertexSummaryProducer"; };
};

class KVertexSummaryProducer : public KBaseMultiProducer<edm::View<reco::Vertex>, KVertexSummaryProducer_Product>
{
public:
	KVertexSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::Vertex>, KVertexSummaryProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void clearProduct(OutputType &output) { output.pv = KDataVertex(); output.nVertices = 0; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.nVertices = in.size();
		if (out.nVertices > 0)
			KVertexProducer::fillVertex(*in.begin(), out.pv);
	}
};

#endif

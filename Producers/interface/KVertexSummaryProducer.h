//- Copyright (c) 2011 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_VERTEXSUMMARYPRODUCER_H
#define KAPPA_VERTEXSUMMARYPRODUCER_H

#include "KVertexProducer.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KVertexSummaryProducer : public KBaseMultiProducer<edm::View<reco::Vertex>, KVertexSummary>
{
public:
	KVertexSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<edm::View<reco::Vertex>, KVertexSummary>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "VertexSummary"; }

	static unsigned int getValidVertexIndex(std::vector<reco::Vertex> const& vertices = std::vector<reco::Vertex>())
	{
		for (unsigned int  validVertexIndex = 0; validVertexIndex < vertices.size(); validVertexIndex++)
			if (vertices.at(validVertexIndex).isValid())
				return validVertexIndex;
		return -1;
	}

	virtual void clearProduct(OutputType &out)
	{
		out.pv = KVertex();
		out.nVertices = 0;
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.nVertices = in.size();
		//TODO: get access to the Vertex collection and fill the first valid
		if (out.nVertices > 0)
			KVertexProducer::fillVertex(*in.begin(), out.pv);
	}
};

#endif

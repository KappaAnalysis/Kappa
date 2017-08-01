//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_VERTEXPRODUCER_H
#define KAPPA_VERTEXPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/VertexReco/interface/Vertex.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KVertexProducer : public KBaseMultiVectorProducer<edm::View<reco::Vertex>, std::vector<KVertex> >
{
public:
	KVertexProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiVectorProducer<edm::View<reco::Vertex>, std::vector<KVertex> >(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "Vertex"; }

	static void fillVertex(const SingleInputType &in, SingleOutputType &out)
	{
		out.position = in.position();
		out.valid = in.isValid();
		out.nTracks = in.tracksSize();

		out.chi2 = in.chi2();
		out.nDOF = in.ndof();
		out.covariance = in.covariance();
	}
protected:
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		fillVertex(in, out);
	}
};

#endif

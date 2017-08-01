//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_REFITVERTEXPRODUCER_H
#define KAPPA_REFITVERTEXPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KVertexProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 4) || (CMSSW_MAJOR_VERSION > 7)

#include "VertexRefit/TauRefit/interface/RefitVertex.h"

class KRefitVertexProducer : public KBaseMultiVectorProducer<edm::View<RefitVertex>, KRefitVertices >
{
public:
	KRefitVertexProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiVectorProducer<edm::View<RefitVertex>, KRefitVertices >(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "RefitVertex"; }

protected:
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KVertexProducer::fillVertex(in, out);

		// save references to lepton selection in the refitted vertex
		std::size_t hash = 0;
		for(auto name: in.userCandNames())
		{
			edm::Ptr<reco::Candidate> aRecoCand = in.userCand( name );
			boost::hash_combine(hash,aRecoCand.get());
		}
		out.leptonSelectionHash = hash;

	}
};

#endif
#endif

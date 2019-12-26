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
#include "VertexRefit/TauRefit/interface/RefitVertex.h"

class KRefitVertexProducer : public KBaseMultiVectorProducer<edm::View<RefitVertex>, KRefitVertices >
{
public:
	KRefitVertexProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiVectorProducer<edm::View<RefitVertex>,
		KRefitVertices >(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "RefitVertex"; }

protected:
	boost::hash<const reco::Candidate*> hasher;

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		if (this->verbosity >= 3) std::cout << "KRefitVertexProducer fillSingle()\n";
		KVertexProducer::fillVertex(in, out);

		// save references to lepton selection in the refitted vertex
		std::vector<size_t> hashes;
		for(auto name: in.userCandNames())
		{
			edm::Ptr<reco::Candidate> aRecoCand = in.userCand( name );
			size_t hash = hasher(aRecoCand.get());
			hashes.push_back(hash);
		}

		out.leptonSelectionHash1 = hashes[0];
		out.leptonSelectionHash2 = hashes[1];
		if (this->verbosity >= 3) std::cout << "KRefitVertexProducer fillSingle() end\n";
	}
};

#endif

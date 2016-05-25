//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_PATMETSPRODUCER_H
#define KAPPA_PATMETSPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KPatMETProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/PatCandidates/interface/MET.h>
#include "Kappa/DataFormats/interface/Hash.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"
#include "boost/functional/hash.hpp"

class KPatMETsProducer : public KBaseMultiLVProducer<edm::View<pat::MET>, KMETs>
{
public:
	KPatMETsProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::MET>, KMETs>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {
	}

	static const std::string getLabel() { return "PatMETs"; }

	//virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if(in.size() == 0) return;
		KBaseMultiLVProducer<edm::View<pat::MET>, KMETs>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KPatMETProducer::fillMET(in, out);

		// save references to lepton selection from MVA MET
		std::size_t hash = 0;
		for(auto name: in.userCandNames())
		{
			reco::CandidatePtr aRecoCand = in.userCand( name );
			boost::hash_combine(hash,aRecoCand.get());
		}
		out.leptonSelectionHash = hash;
	}
};

#endif

//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>

#ifndef KAPPA_L1MUONPRODUCER_H
#define KAPPA_L1MUONPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/L1Trigger/interface/L1MuonParticle.h>
#include <FWCore/Framework/interface/EDProducer.h>

class KL1MuonProducer : public KBaseMultiLVProducer<edm::View<l1extra::L1MuonParticle>, KL1Muons>
{
public:
	KL1MuonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<l1extra::L1MuonParticle>, KL1MuonProducer_Product>(cfg, _event_tree, _run_tree, std::forward<edm::ConsumesCollector>(consumescollector)) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KL1MuonProducer::fillL1Muon(in, out);
	}

	// Static method for filling Tracks in other producers
	static void fillL1Muon(const SingleInputType &in, SingleOutputType &out)
	{
		out.state = 0;

		copyP4(in, out.p4);

		out.state |= (in.gmtMuonCand().quality() & 7);
		if (in.isForward())
			out.state |= (1 << 3);
		if (in.isRPC())
			out.state |= (1 << 4);
		if (in.isMip())
			out.state |= (1 << 5);
		if (in.isIsolated())
			out.state |= (1 << 6);
		out.state |= ((in.bx() + 7) & 15) << 7;
		out.state |= (in.gmtMuonCand().detector() & 7) << 11;
		
		assert(in.gmtMuonCand().quality() == (unsigned int) out.quality());
		assert(in.isForward() == out.isForward());
		assert(in.isRPC() == out.isRPC());
		assert(in.isMip() == out.isMip());
		assert(in.isIsolated() == out.isIsolated());
		assert(in.bx() == out.bx());
		assert(in.gmtMuonCand().detector() == (unsigned int) out.detector());
	}
};

#endif

#ifndef KAPPA_L1MUONPRODUCER_H
#define KAPPA_L1MUONPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/L1Trigger/interface/L1MuonParticle.h>

struct KL1MuonProducer_Product
{
	typedef std::vector<KL1Muon> type;
	static const std::string id() { return "std::vector<KL1Muon>"; };
	static const std::string producer() { return "KL1MuonProducer"; };
};

class KL1MuonProducer : public KRegexMultiLVProducer<edm::View<l1extra::L1MuonParticle>, KL1MuonProducer_Product>
{
public:
	KL1MuonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KRegexMultiLVProducer<edm::View<l1extra::L1MuonParticle>, KL1MuonProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
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

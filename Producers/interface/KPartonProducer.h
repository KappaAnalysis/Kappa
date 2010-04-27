#ifndef KAPPA_PARTONPRODUCER_H
#define KAPPA_PARTONPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>

struct KPartonProducer_Product
{
	typedef std::vector<KParton> type;
	static const std::string id() { return "std::vector<KParton>"; };
	static const std::string producer() { return "KPartonProducer"; };
};

class KPartonProducer : public KManualMultiLVProducer<edm::View<reco::Candidate>, KPartonProducer_Product>
{
public:
	KPartonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree)
		: KManualMultiLVProducer<edm::View<reco::Candidate>, KPartonProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KPartonProducer() {};
protected:
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		unsigned int id = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		out.pdgid = id | ((in.status() % 4) << KPartonStatusMask);
		if (in.pdgId() < 0)
			out.pdgid |= (1 << KPartonChargeMask);
		out.children = 0;
	}
};

#endif

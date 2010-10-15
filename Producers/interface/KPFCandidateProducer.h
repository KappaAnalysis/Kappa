#ifndef KAPPA_PFCandidatePRODUCER_H
#define KAPPA_PFCandidatePRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/ParticleFlowCandidate/interface/PFCandidate.h>

struct KPFCandidateProducer_Product
{
	typedef std::vector<KPFCandidate> type;
	static const std::string id() { return "std::vector<KPFCandidate>"; };
	static const std::string producer() { return "KPFCandidateProducer"; };
};

class KPFCandidateProducer : public KBaseMultiLVProducer<edm::View<reco::PFCandidate>, KPFCandidateProducer_Product>
{
public:
	KPFCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::PFCandidate>, KPFCandidateProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.pdgid = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		if (in.pdgId() < 0)
			out.pdgid |= KPartonChargeMask;
		out.deltaP = in.deltaP();
		out.hcalEnergy = in.hcalEnergy();
		out.ecalEnergy = in.ecalEnergy();
	}
};

#endif

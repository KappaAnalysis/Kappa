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
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		selectedStatus = pset.getParameter<int>("selectedStatus");
		selectedParticles = pset.getParameter<std::vector<int> >("selectedParticles");
		KManualMultiLVProducer<edm::View<reco::Candidate>, KPartonProducer_Product>::fillProduct(in, out, name, tag, pset);
	}
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		unsigned int id = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		out.pdgid = id | ((in.status() % 4) << KPartonStatusMask);
		if (in.pdgId() < 0)
			out.pdgid |= (1 << KPartonChargeMask);
		out.children = 0;
	}
	virtual bool acceptSingle(const SingleInputType &in)
	{
		bool acceptStatus = false;
		bool acceptPdgId = false;

		if (selectedStatus==0)
			acceptStatus = true;
		else
			acceptStatus = ( (1 << in.status()) & selectedStatus);

		if (selectedParticles.size()==0)
			acceptPdgId = true;
		else
			acceptPdgId = (find(selectedParticles.begin(),selectedParticles.end(),std::abs(in.pdgId())) != selectedParticles.end());

		return (acceptStatus && acceptPdgId);
	}
private:
	int selectedStatus; // bit map
	std::vector<int> selectedParticles;
};

#endif

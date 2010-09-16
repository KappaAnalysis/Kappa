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

template<typename TProduct>
class KBasicPartonProducer : public KManualMultiLVProducer<edm::View<reco::Candidate>, TProduct>
{
public:
	KBasicPartonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiLVProducer<edm::View<reco::Candidate>, TProduct>(cfg, _event_tree, _run_tree) {}
	virtual ~KBasicPartonProducer() {};
protected:
	virtual void fillSingle(const typename KManualMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleInputType &in, typename KManualMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleOutputType &out)
	{
		copyP4(in, out.p4);
		unsigned int id = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		out.pdgid = id | ((in.status() % 4) << KPartonStatusPosition);
		if (in.pdgId() < 0)
			out.pdgid |= KPartonChargeMask;
		out.children = 0;
	}
	virtual bool acceptSingle(const typename KManualMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleInputType &in)
	{
		bool acceptStatus = false;
		bool acceptPdgId = false;

		if (selectedStatus == 0)
			acceptStatus = true;
		else
			acceptStatus = ((1 << in.status()) & selectedStatus);

		if (selectedParticles.size() == 0)
			acceptPdgId = true;
		else
			acceptPdgId = (find(selectedParticles.begin(), selectedParticles.end(), std::abs(in.pdgId())) != selectedParticles.end());

		return (acceptStatus && acceptPdgId);
	}

	void selectStatus(int status)
	{
		selectedStatus = status;
	}

	template<typename InputIterator>
	void selectParticles(InputIterator begin, InputIterator end)
	{
		selectedParticles.assign(begin, end);
	}
private:
	int selectedStatus; // bit map
	std::vector<int> selectedParticles;
};

class KPartonProducer: public KBasicPartonProducer<KPartonProducer_Product>
{
public:
	KPartonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBasicPartonProducer<KPartonProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KPartonProducer() {};

protected:
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		int status = pset.getParameter<int>("selectedStatus");
		std::vector<int> particles = pset.getParameter<std::vector<int> >("selectedParticles");

		selectStatus(status);
		selectParticles(particles.begin(), particles.end());

		KBasicPartonProducer<KPartonProducer_Product>::fillProduct(in, out, name, tag, pset);
	}
};

#endif

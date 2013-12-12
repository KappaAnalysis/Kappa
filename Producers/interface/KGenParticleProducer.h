/* Copyright (c) 2012 - All Rights Reserved
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_PARTONPRODUCER_H
#define KAPPA_PARTONPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>
#include <bitset>

template<typename TProduct>
class KBasicGenParticleProducer : public KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>
{
public:
	KBasicGenParticleProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, const std::string &producerName) :
		KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>(cfg, _event_tree, _run_tree, producerName) {}


protected:
	virtual void fillSingle(const typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleInputType &in, typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleOutputType &out)
	{
		copyP4(in, out.p4);

		unsigned int id = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		out.pdgid = id | ((in.status() % 4) << KGenParticleStatusPosition);
		if (in.pdgId() < 0)
			out.pdgid |= KGenParticleChargeMask;
		out.children = 0;

		if (in.pdgId() != out.pdgId())
			std::cout << "The pdgId is not skimmed correctly! "
				<< "in=" << in.pdgId() << ", out=" << out.pdgId()
				<< std::endl << std::flush;
		assert(in.pdgId() == out.pdgId());
	}
	virtual bool acceptSingle(const typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleInputType &in)
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

class KGenParticleProducer: public KBasicGenParticleProducer<KGenParticles>
{
public:
	KGenParticleProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBasicGenParticleProducer<KGenParticles>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "GenParticles"; }

protected:
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		int status = pset.getParameter<int>("selectedStatus");
		std::vector<int> particles = pset.getParameter<std::vector<int> >("selectedParticles");

		selectStatus(status);
		selectParticles(particles.begin(), particles.end());

		KBasicGenParticleProducer<KGenParticles>::fillProduct(in, out, name, tag, pset);
	}
};

#endif

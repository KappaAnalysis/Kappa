//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Roger Wolf <roger.wolf@cern.ch>

#ifndef KAPPA_PARTONPRODUCER_H
#define KAPPA_PARTONPRODUCER_H

#include <iostream>
#include <map>

#include "KBaseMultiProducer.h"
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>
#include <bitset>

template<typename TProduct>
class KBasicGenParticleProducer : public KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>
{
public:
	KBasicGenParticleProducer(const edm::ParameterSet& cfg, TTree* _event_tree, TTree* _run_tree, const std::string& producerName) :
		KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>(cfg, _event_tree, _run_tree, producerName) {}


protected:
	/// interface for other derived classes like KGenTauProducer, which do not provide information for daughter particles; the list of daughters is filled with an empty  dummy vector in this case
	virtual void fillSingle(const typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleInputType& in, typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleOutputType& out)
	{
		std::vector<reco::Candidate::index> dummy;
		fillSingle(in, out, dummy);
	}

	virtual void fillSingle(const typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleInputType& in, typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleOutputType& out, std::vector<reco::Candidate::index>& daughters)
	{
		copyP4(in, out.p4);

		if (KBaseProducer::verbosity > 3)
		{
			std::cout << "index in out : " << index << std::endl;
			std::cout << "pdgId        : " << in.pdgId() << std::endl;
			std::cout << "N(d)         : " << in.numberOfDaughters() << " | " << daughters.size() << std::endl;
			for (unsigned int nd = 0; nd < in.numberOfDaughters() && nd < daughters.size(); ++nd)
			{
				std::cout << "   - " << nd << " pdgId(daughter): " << in.daughter(nd)->pdgId() << " | index: " << daughters.at(nd) << std::endl;
			}
			std::cout << std::endl << std::endl;
		}

		unsigned int id = (in.pdgId() < 0) ? -in.pdgId() : in.pdgId();
		out.particleid = id;
		out.particleinfo = ((in.status() % 128) << KParticleStatusPosition);
		if (in.status() >= 111)  // Pythia 8 maximum
			out.particleinfo |= (127 << KParticleStatusPosition);
		if (in.pdgId() < 0)
			out.particleinfo |= KParticleSignMask;
		out.daughterIndices = daughters;

#if (CMSSW_MAJOR_VERSION > 7) || (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 4)
		// generator-independent flags
		reco::GenStatusFlags flags = (dynamic_cast<const reco::GenParticle*>(&in))->statusFlags();
		out.particleinfo |= (flags.isPrompt()                           << KGenStatusFlags::isPrompt);
		out.particleinfo |= (flags.isDecayedLeptonHadron()              << KGenStatusFlags::isDecayedLeptonHadron);
		out.particleinfo |= (flags.isTauDecayProduct()                  << KGenStatusFlags::isTauDecayProduct);
		out.particleinfo |= (flags.isPromptTauDecayProduct()            << KGenStatusFlags::isPromptTauDecayProduct);
		out.particleinfo |= (flags.isDirectTauDecayProduct()            << KGenStatusFlags::isDirectTauDecayProduct);
		out.particleinfo |= (flags.isDirectPromptTauDecayProduct()      << KGenStatusFlags::isDirectPromptTauDecayProduct);
		out.particleinfo |= (flags.isDirectHadronDecayProduct()         << KGenStatusFlags::isDirectHadronDecayProduct);
		out.particleinfo |= (flags.isHardProcess()                      << KGenStatusFlags::isHardProcess);
		out.particleinfo |= (flags.fromHardProcess()                    << KGenStatusFlags::fromHardProcess);
		out.particleinfo |= (flags.isHardProcessTauDecayProduct()       << KGenStatusFlags::isHardProcessTauDecayProduct);
		out.particleinfo |= (flags.isDirectHardProcessTauDecayProduct() << KGenStatusFlags::isDirectHardProcessTauDecayProduct);
#endif

		if (in.pdgId() != out.pdgId())
			std::cout << "The pdgId is not skimmed correctly! "
					  << "in=" << in.pdgId() << ", out=" << out.pdgId()
					  << std::endl << std::flush;
		assert(in.pdgId() == out.pdgId());

	}

	virtual bool acceptSingle(const typename KBaseMultiLVProducer<edm::View<reco::Candidate>, TProduct>::SingleInputType& in)
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

protected:
	/// index to determine the position of each genParticle in the output vector
	reco::Candidate::index index;
	/// mapping memory address of each genParticle to the position in the output vector
	std::map<const reco::Candidate*, reco::Candidate::index> daughterDict;

private:
	int selectedStatus; // bit map
	std::vector<int> selectedParticles;
};

class KGenParticleProducer: public KBasicGenParticleProducer<KGenParticles>
{
public:
	KGenParticleProducer(const edm::ParameterSet& cfg, TTree* _event_tree, TTree* _run_tree) :
		KBasicGenParticleProducer<KGenParticles>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel()
	{
		return "GenParticles";
	}

protected:
	virtual void fillProduct(const InputType& in, OutputType& out,
							 const std::string& name, const edm::InputTag* tag, const edm::ParameterSet& pset)
	{
		if (KBaseProducer::verbosity > 0)
			std::cout << in.size() << "KGenParticleProducer::fillProduct :  objects in collection " << name << std::endl;

		out.reserve(in.size());

		// retrieve additional input products
		int status = pset.getParameter<int>("selectedStatus");
		std::vector<int> particles = pset.getParameter<std::vector<int> >("selectedParticles");

		selectStatus(status);
		selectParticles(particles.begin(), particles.end());

		// fill daughterDict for each genParticle
		daughterDict.clear();
		typename InputType::const_iterator lvit;
		for (index = 0, lvit = in.begin(); lvit < in.end(); ++lvit)
		{
			if (acceptSingle(*lvit))
			{
				const reco::Candidate* lvptr = dynamic_cast <const reco::Candidate*>(&(*lvit));
				daughterDict[lvptr] = index++;
			}
		}

		for (index = 0, lvit = in.begin(), index = 0; lvit < in.end(); ++lvit)
		{
			if (acceptSingle(*lvit))
			{
				// obtain list of daughter indices
				std::vector<reco::Candidate::index> daughters;
				for (reco::Candidate::index nd = 0; nd < lvit->numberOfDaughters(); ++nd)
				{
					daughters.push_back(daughterDict.find(lvit->daughter(nd))->second);
				}
				out.push_back(SingleOutputType());
				fillSingle(*lvit, out.back(), daughters);
				++index;
			}
		}
		if (maxN > 0)
			out.erase(out.begin() + std::min(out.size(), (size_t)maxN), out.end());

		if (KBaseProducer::verbosity > 1)
			std::cout << "KGenParticleProducer::fillProduct : \t" << "Number of accepted objects: " << out.size() << "\t";
	}
};

#endif


//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>

#ifndef KAPPA_MULTIPRODUCER_H
#define KAPPA_MULTIPRODUCER_H

#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

#include "KBaseMatchingProducer.h"
#include "../../DataFormats/interface/KBasic.h"

// Subproducers have to override:
//  * void fillProduct(const InputType &input, OutputType &output, const std::string &name, const edm::ParameterSet &pset);
//  * void clearProduct(OutputType &output);
template<typename Tin, typename Tout>
class KBaseMultiProducer : public KBaseMatchingProducer<Tout>
{
public:
	KBaseMultiProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, const std::string &producerName, edm::ConsumesCollector && consumescollector, bool _justOutputName = false) :
		KBaseMatchingProducer<Tout>(cfg, _event_tree, _lumi_tree, _run_tree, producerName, std::forward<edm::ConsumesCollector>(consumescollector)),
		event_tree(_event_tree), justOutputName(_justOutputName)
		{
			this->addPSetRequests();
			
		}
	typedef std::tuple<const edm::ParameterSet, const edm::InputTag, const edm::EDGetTokenT<Tin>> TargetSetupMapContent;
	virtual ~KBaseMultiProducer() {}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		this->cEvent = &event;
		this->cSetup = &setup;

		for (typename std::map<Tout*, TargetSetupMapContent >::iterator
			it = targetSetupMap.begin(); it != targetSetupMap.end(); ++it)
		{
			const edm::ParameterSet &pset = std::get<0>(it->second);
			const edm::InputTag &src = std::get<1>(it->second);
			const std::pair<std::string, std::string> desc = this->nameMap[it->first];

			// Clear previous collection
			Tout &ref = *it->first;
			clearProduct(ref);

			// Try to get product via id
			if (!event.getByToken(std::get<2>(it->second), this->handle))
			{
				std::cout << "Could not get main product! " << desc.second << ".src = " << src.encode() << std::endl;
				continue;
			}

			std::string name = desc.first;
			if ((desc.first != desc.second) && !justOutputName)
				name += " (" + desc.second + ")";
			fillProduct(*(this->handle), ref, name, &src, pset);
		}

		return KBaseProducer::onEvent(event, setup);
	}

	typedef Tout OutputType;
	typedef Tin InputType;

protected:
	virtual bool onMatchingInput(const std::string targetName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		if (!KBaseMatchingProducer<Tout>::onMatchingInput(targetName, inputName, pset, tag))
			return false;
		registerBronch(targetName, inputName, pset, tag);
		return true;
	}

	void registerBronch(const std::string targetName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		// Add branch
		if (this->verbosity > 0)
			std::cout << " => Adding branch: " << targetName << std::endl;

		// Static storage of ROOT bronch target - never changes, only accessed here:
		Tout *target = this->allocateBronch(targetName);
		this->addProvenance(tag.encode(), targetName);

		// Mapping between target and targetName
		nameMap[target] = make_pair(targetName, inputName);

		// Used for fast lookup of selector and lv collection
		this->targetSetupMap.insert(std::pair<Tout*, TargetSetupMapContent>(target, TargetSetupMapContent(pset, tag, this->consumescollector_.template consumes<Tin>(tag))));
	}

	virtual void fillProduct(const InputType &input, OutputType &output,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset) = 0;
	virtual void clearProduct(OutputType &output) = 0;

	typename edm::Handle<Tin> handle;

	TTree *event_tree;
	const edm::Event *cEvent;
	const edm::EventSetup *cSetup;
	
	std::map<Tout*, TargetSetupMapContent > targetSetupMap;
	std::map<Tout*, std::pair<std::string, std::string> > nameMap;

private:
	bool justOutputName;
};

#endif

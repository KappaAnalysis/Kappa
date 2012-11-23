/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 */

#ifndef KAPPA_MULTIPRODUCER_H
#define KAPPA_MULTIPRODUCER_H

#include "KBaseMatchingProducer.h"
#include "../../DataFormats/interface/KBasic.h"

// Subproducers have to override:
//  * void fillProduct(const InputType &input, OutputType &output, const std::string &name, const edm::ParameterSet &pset);
//  * void clearProduct(OutputType &output);
template<typename Tin, typename Tout>
class KBaseMultiProducer : public KBaseMatchingProducer<Tout>
{
public:
	KBaseMultiProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, bool _justOutputName = false) :
		KBaseMatchingProducer<Tout>(cfg, _event_tree, _run_tree),
		event_tree(_event_tree), justOutputName(_justOutputName) {}
	virtual ~KBaseMultiProducer() {}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		this->cEvent = &event;
		this->cSetup = &setup;

		for (typename std::map<typename Tout::type*, std::pair<const edm::ParameterSet, const edm::InputTag> >::iterator
			it = targetSetupMap.begin(); it != targetSetupMap.end(); ++it)
		{
			const edm::ParameterSet &pset = it->second.first;
			const edm::InputTag &src = it->second.second;
			const std::pair<std::string, std::string> desc = this->nameMap[it->first];

			// Clear previous collection
			typename Tout::type &ref = *it->first;
			clearProduct(ref);

			// Try to get product via id
			if (!event.getByLabel(src, this->handle))
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

	typedef typename Tout::type OutputType;
	typedef Tin InputType;

protected:
	virtual void onMatchingInput(const std::string targetName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		KBaseMatchingProducer<Tout>::onMatchingInput(targetName, inputName, pset, tag);
		registerBronch(targetName, inputName, pset, tag);
	}

	void registerBronch(const std::string targetName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		// Add branch
		if (this->verbosity > 0)
			std::cout << " => Adding branch: " << targetName << std::endl;

		// Static storage of ROOT bronch target - never changes, only accessed here:
		typename Tout::type *target = this->allocateBronch(targetName);
		this->addProvenance(tag.encode(), targetName);

		// Mapping between target and targetName
		nameMap[target] = make_pair(targetName, inputName);

		// Used for fast lookup of selector and lv collection
		typedef std::pair<const edm::ParameterSet, const edm::InputTag> TmpType;
		this->targetSetupMap.insert(std::pair<typename Tout::type*, TmpType>(target, TmpType(pset, tag)));
	}

	virtual void fillProduct(const InputType &input, OutputType &output,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset) = 0;
	virtual void clearProduct(OutputType &output) = 0;

	typename edm::Handle<Tin> handle;

	TTree *event_tree;
	const edm::Event *cEvent;
	const edm::EventSetup *cSetup;

	std::map<typename Tout::type*, std::pair<const edm::ParameterSet, const edm::InputTag> > targetSetupMap;
	std::map<typename Tout::type*, std::pair<std::string, std::string> > nameMap;

private:
	bool justOutputName;
};

#endif

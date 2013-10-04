/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 */

#ifndef KAPPA_MULTIPRODUCER_H
#define KAPPA_MULTIPRODUCER_H

#include "KBaseProducer.h"
#include <FWCore/Utilities/interface/InputTag.h>
#include "../../DataFormats/interface/KBasic.h"

// Subproducers have to override:
//  * void fillProduct(const InputType &input, OutputType &output, const std::string &name, const edm::ParameterSet &pset);
//  * void clearProduct(OutputType &output);
template<typename Tin, typename Tout>
class KBaseMultiProducer : public KBaseProducerWP
{
public:
	KBaseMultiProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, bool _justOutputName = false) :
		KBaseProducerWP(cfg, _event_tree, _run_tree, Tout::producer()),
		event_tree(_event_tree), justOutputName(_justOutputName),
		viManual(cfg.getParameter<std::vector<edm::InputTag> >("manual")),

		vsWhitelist(cfg.getParameter<std::vector<std::string> >("whitelist")),
		vsBlacklist(cfg.getParameter<std::vector<std::string> >("blacklist")),

		vsRename(cfg.getParameter<std::vector<std::string> >("rename")),
		vsRenameWhitelist(cfg.getParameter<std::vector<std::string> >("rename_whitelist")),
		vsRenameBlacklist(cfg.getParameter<std::vector<std::string> >("rename_blacklist")) {}
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

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		addPSetRequests(event, setup);
		addRegExRequests(event, setup);
		if (this->verbosity > 0)
			std::cout << "Accepted number of products: " << bronchStorage.size() << std::endl;
		return KBaseProducer::onFirstEvent(event, setup);
	}

	typedef typename Tout::type OutputType;
	typedef Tin InputType;

protected:
	typename Tout::type *allocateBronch(const std::string bronchName)
	{
		// Static storage of ROOT bronch target - never changes, only accessed here:
		bronchStorage[bronchName] = new typename Tout::type();
		event_tree->Bronch(bronchName.c_str(), Tout::id().c_str(), &(bronchStorage[bronchName]));
		return bronchStorage[bronchName];
	}

	void registerBronch(const std::string outputName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		// Add branch
		if (this->verbosity > 0)
			std::cout << " => Adding branch: " << outputName << std::endl;

		// Static storage of ROOT bronch target - never changes, only accessed here:
		typename Tout::type *target = allocateBronch(outputName);
		this->addProvenance(tag.encode(), outputName);

		// Mapping between target and outputName
		nameMap[target] = make_pair(outputName, inputName);

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
	bool addPSetRequests(const edm::Event &event, const edm::EventSetup &setup)
	{
		std::cout << "Requesting entries: ";

		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			std::cout << "\"" << names[i] << "\" ";
			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);
			// Register branch
			this->registerBronch(names[i], names[i], pset, pset.getParameter<edm::InputTag>("src"));
		}
		std::cout << std::endl;

		return true;
	}

	bool addRegExRequests(const edm::Event &event, const edm::EventSetup &setup)
	{
		std::vector<edm::Provenance const*> plist;
		event.getAllProvenance(plist);

		for (std::vector<edm::Provenance const*>::const_iterator piter = plist.begin(); piter < plist.end(); ++piter)
		{
			if (this->verbosity > 1)
				std::cout << "Product: ";

			// Check if branch was selected
			if (!(this->regexMatch((*piter)->branchName(), vsWhitelist, vsBlacklist)
				|| this->tagMatch(*piter, viManual)))
			{
				continue;
			}

			// Rename branch if requested
			if ((this->verbosity > 0) && (vsRename.size() > 0))
			{
				std::cout << " => " + Tout::producer() + " will use: ";
				std::cout.flush();
			}
			const std::string targetName = this->regexRename((*piter)->moduleLabel(), vsRename);
			if ((this->verbosity > 0) && (vsRename.size() > 0))
				std::cout << targetName << " as branch name." << std::endl;

			// Filter on the new name
			if (!this->regexMatch(targetName, vsRenameWhitelist, vsRenameBlacklist))
			{
				if (this->verbosity > 0)
					std::cout << " => Addition of branch was vetoed by post-rename Black/Whitelist!" << std::endl;
				continue;
			}

			// Avoid name collisions: Ignore or Fail
			if (this->event_tree->FindBranch(targetName.c_str()))
			{
				if (this->verbosity > 0)
					std::cout << " => Branch with this name was already added!" << std::endl;
				continue;
			}

			// Crate selection tag
			const edm::InputTag tag((*piter)->moduleLabel(), (*piter)->productInstanceName(), (*piter)->processName());
			if (this->verbosity > 1)
				std::cout << " => Branch will be selected with " << tag << std::endl;

			// Register branch
			this->registerBronch(targetName, (*piter)->branchName(), this->psBase, tag);
		}

		return true;
	}

	bool justOutputName;
	std::vector<edm::InputTag> viManual;

	std::vector<std::string> vsWhitelist;
	std::vector<std::string> vsBlacklist;

	std::vector<std::string> vsRename;
	std::vector<std::string> vsRenameWhitelist;
	std::vector<std::string> vsRenameBlacklist;

	std::map<std::string, typename Tout::type*> bronchStorage;
};

#endif

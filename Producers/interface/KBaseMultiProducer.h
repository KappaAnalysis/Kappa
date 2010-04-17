#ifndef KAPPA_MULTIPRODUCER_H
#define KAPPA_MULTIPRODUCER_H

#include "KBaseProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include "../../DataFormats/interface/KBasic.h"

template<typename Tin, typename Tout>
class KBaseMultiProducer : public KBaseProducerWP<Tout>
{
public:
	KBaseMultiProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseProducerWP<Tout>(cfg, _event_tree, _run_tree) {}
	virtual ~KBaseMultiProducer() {}

	typename Tout::type *allocateBronch(TTree *event_tree, const std::string bronchName)
	{
		// Static storage of ROOT bronch target - never changes, only accessed here:
		bronchStorage[bronchName] = new typename Tout::type();
		event_tree->Bronch(bronchName.c_str(), Tout::id().c_str(), &(bronchStorage[bronchName]));
		return bronchStorage[bronchName];
	}

	void printAcceptedProducts(int verbosity)
	{
		if (verbosity > 0)
			std::cout << "Accepted number of products: " << bronchStorage.size() << std::endl;
	}

private:
	std::map<std::string, typename Tout::type*> bronchStorage;
};

// KManualMultiProducer - input is specified manually in the form of parameter sets,
//   therefore it is possible to specify additional input objects
//   The main input is selected via the inputtag src
//   eg. Jets + JetID objects
// Subproducers have to override:
//  * void fillProduct(const InputType &input, OutputType &output, const std::string &name, const edm::ParameterSet &pset);
//  * void clearProduct(OutputType &output);
template<typename Tin, typename Tout>
class KManualMultiProducer : public KBaseMultiProducer<Tin, Tout>
{
public:
	KManualMultiProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		event_tree(_event_tree)
	{
		std::cout << "Requesting entries: ";
		std::vector<std::string> names = cfg.getParameterNamesForType<edm::ParameterSet>();
		for (size_t i = 0; i < names.size(); ++i)
		{
			std::cout << "\"" << names[i] << "\" ";
			edm::ParameterSet pset = cfg.getParameter<edm::ParameterSet>(names[i]);
			entries[names[i]] = pset;
		}
		std::cout << std::endl;
	}
	virtual ~KManualMultiProducer() {}

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		for (std::map<std::string, edm::ParameterSet>::const_iterator it = entries.begin(); it != entries.end(); ++it)
		{
			// Add branch
			if (this->verbosity > 0)
				std::cout << " => Adding branch: " << it->first << std::endl;
			this->addProvenance(it->second.getParameter<edm::InputTag>("src").encode(), it->first);

			// Static storage of ROOT bronch target - never changes, only accessed here:
			typename Tout::type *target = this->allocateBronch(event_tree, it->first);

			// Mapping between target
			targetIDMap[target] = &(it->second);
			nameMap[target] = it->first;
		}
		printAcceptedProducts(this->verbosity);
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		cEvent = &event;
		cSetup = &setup;

		for (typename std::map<typename Tout::type*, const edm::ParameterSet*>::iterator it = targetIDMap.begin(); it != targetIDMap.end(); ++it)
		{
			const edm::ParameterSet *pset = it->second;
			const edm::InputTag src = pset->getParameter<edm::InputTag>("src");

			// Clear previous collection
			typename Tout::type &ref = *it->first;
			clearProduct(ref);

			// Try to get product via id
			try
			{
				event.getByLabel(src, handle);
			}
			catch (...)
			{
				std::cout << "Could not get main product! " << nameMap[it->first] << ".src = " << src.encode() << std::endl;
				continue;
			}

			fillProduct(*handle, ref, nameMap[it->first], *it->second);
		}
		return true;
	}

	typedef typename Tout::type OutputType;
	typedef Tin InputType;

	virtual void clearProduct(OutputType &output) = 0;
	virtual void fillProduct(const InputType &input, OutputType &output, const std::string &name, const edm::ParameterSet &pset) = 0;

protected:
	typename edm::Handle<Tin> handle;
	const edm::Event *cEvent;
	const edm::EventSetup *cSetup;
	TTree *event_tree;

	std::map<typename Tout::type*, std::string> nameMap;
	std::map<std::string, edm::ParameterSet> entries;
	std::map<typename Tout::type*, const edm::ParameterSet*> targetIDMap;
};


// KRegexMultiProducer - input is specified as regular expressions, most things are automated
// Subproducers have to override:
//  * void fillProduct(const InputType &input, OutputType &output, edm::InputTag *tag)
//  * void clearProduct(OutputType &output);
template<typename Tin, typename Tout>
class KRegexMultiProducer : public KBaseMultiProducer<Tin, Tout>
{
public:
	KRegexMultiProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<Tin, Tout>(cfg, _event_tree, _run_tree),
		viManual(cfg.getParameter<std::vector<edm::InputTag> >("manual")),

		vsWhitelist(cfg.getParameter<std::vector<std::string> >("whitelist")),
		vsBlacklist(cfg.getParameter<std::vector<std::string> >("blacklist")),

		vsRename(cfg.getParameter<std::vector<std::string> >("rename")),
		vsRenameWhitelist(cfg.getParameter<std::vector<std::string> >("rename_whitelist")),
		vsRenameBlacklist(cfg.getParameter<std::vector<std::string> >("rename_blacklist")),

		event_tree(_event_tree) {}
	virtual ~KRegexMultiProducer() {}

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
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
			if (event_tree->FindBranch(targetName.c_str()))
			{
				if (this->verbosity > 0)
					std::cout << " => Branch with this name was already added!" << std::endl;
				continue;
			}

			// Add branch
			if (this->verbosity > 0)
				std::cout << " => Adding branch: " << targetName << " for product ID: " << (*piter)->productID() << std::endl;
			this->addProvenance((*piter)->branchName(), targetName);

			typename Tout::type *target = this->allocateBronch(event_tree, targetName);

			// Crate selection tag
			edm::InputTag *tag = new edm::InputTag((*piter)->moduleLabel(), (*piter)->productInstanceName(), (*piter)->processName());
			if (this->verbosity > 1)
				std::cout << " => Branch will be selected with " << *tag << std::endl;

			// Used to display tuple label
			nameMap[tag] = make_pair(targetName, (*piter)->branchName());

			// Used for fast lookup of selector and lv collection
			targetIDMap[target] = tag;
		}
		printAcceptedProducts(this->verbosity);
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		cEvent = &event;
		cSetup = &setup;

		for (typename std::map<typename Tout::type*, edm::InputTag*>::iterator it = targetIDMap.begin(); it != targetIDMap.end(); ++it)
		{
			// Clear previous collection
			typename Tout::type &ref = *it->first;
			clearProduct(ref);

			// Try to get product via id
			if (!event.getByLabel(*(it->second), handle))
			{
				std::cout << "Could not get product!" << nameMap[it->second].second << std::endl;
				continue;
			}

			fillProduct(*handle, ref, it->second);
		}
		return true;
	}

	typedef typename Tout::type OutputType;
	typedef Tin InputType;

	virtual void clearProduct(OutputType &output) = 0;
	virtual void fillProduct(const InputType &input, OutputType &output, edm::InputTag *tag) = 0;

protected:
	std::vector<edm::InputTag> viManual;

	std::vector<std::string> vsWhitelist;
	std::vector<std::string> vsBlacklist;

	std::vector<std::string> vsRename;
	std::vector<std::string> vsRenameWhitelist;
	std::vector<std::string> vsRenameBlacklist;

	TTree *event_tree;
	const edm::Event *cEvent;
	const edm::EventSetup *cSetup;
	typename edm::Handle<Tin> handle;

	std::map<edm::InputTag*, std::pair<std::string, std::string> > nameMap;
	std::map<typename Tout::type*, edm::InputTag*> targetIDMap;
};

#endif

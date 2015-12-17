//- Copyright (c) 2012 - All Rights Reserved
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_MATCHINGPRODUCER_H
#define KAPPA_MATCHINGPRODUCER_H

#include "KBaseProducer.h"

#include <FWCore/Framework/interface/EDProducer.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <Kappa/DataFormats/interface/Kappa.h>

template<typename Tout>
class KBaseMatchingProducer : public KBaseProducerWP
{
public:
	KBaseMatchingProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, const std::string &producerName, edm::ConsumesCollector && consumescollector) :
		KBaseProducerWP(cfg, _event_tree, _run_tree, producerName, std::forward<edm::ConsumesCollector>(consumescollector)),
		event_tree(_event_tree), matchingCounter(0), producerLabel(producerName),
		viManual(cfg.getParameter<std::vector<edm::InputTag> >("manual")),

		vsWhitelist(cfg.getParameter<std::vector<std::string> >("whitelist")),
		vsBlacklist(cfg.getParameter<std::vector<std::string> >("blacklist")),

		vsRename(cfg.getParameter<std::vector<std::string> >("rename")),
		vsRenameWhitelist(cfg.getParameter<std::vector<std::string> >("rename_whitelist")),
		vsRenameBlacklist(cfg.getParameter<std::vector<std::string> >("rename_blacklist"))
	{
	}
	virtual ~KBaseMatchingProducer() {}

	virtual std::string getProductName() const
	{
		return std::string(TypeName<Tout>::long_name());
	}

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		//addPSetRequests(event, setup);
		//addRegExRequests(event, setup);
		if (this->verbosity > 0)
			std::cout << "KBaseMatchingProducer::onFirstEvent : Accepted number of matched products: " << matchingCounter << std::endl;
		return KBaseProducerWP::onFirstEvent(event, setup);
	}
	


protected:
	bool addPSetRequests()
	{
		if (verbosity > 0)
			std::cout << "Requesting entries: ";

		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			if (verbosity > 0)
				std::cout << "\"" << names[i] << "\" ";
			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);
			// Notify about match
			if (!onMatchingInput(names[i], names[i], pset, pset.getParameter<edm::InputTag>("src")))
				return false;
		}
		if (verbosity > 0)
			std::cout << std::endl;

		if (verbosity > 0 && names.size() == 0)
			std::cout << "Warning! A a PSet was requested but none found. Maybe a config file error?" << std::endl;

		return true;
	}

	virtual bool onMatchingInput(const std::string targetName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		++matchingCounter;
		vsMatched.push_back(targetName);
		return true;
	}

	Tout *allocateBronch(const std::string bronchName)
	{
		// Static storage of ROOT bronch target - never changes, only accessed here:
		bronchStorage[bronchName] = new Tout();
		this->event_tree->Bronch(bronchName.c_str(), this->getProductName().c_str(), &(bronchStorage[bronchName]));
		return bronchStorage[bronchName];
	}

private:
	TTree *event_tree;

	int matchingCounter;
	std::string producerLabel;
	std::vector<edm::InputTag> viManual;
	std::vector<std::string> vsWhitelist;
	std::vector<std::string> vsBlacklist;

	std::vector<std::string> vsRename;
	std::vector<std::string> vsRenameWhitelist;
	std::vector<std::string> vsRenameBlacklist;

	std::vector<std::string> vsMatched;
	std::map<std::string, Tout*> bronchStorage;

	bool addRegExRequests(const edm::Event &event, const edm::EventSetup &setup)
	{
		std::vector<edm::Provenance const*> plist;
		event.getAllProvenance(plist);

		for (std::vector<edm::Provenance const*>::const_iterator piter = plist.begin(); piter < plist.end(); ++piter)
		{
			if (this->verbosity > 1)
				std::cout << "KBaseMatchingProducer::addRegExRequests : Product: ";

			// Check if branch was selected
			if (!(this->regexMatch((*piter)->branchName(), vsWhitelist, vsBlacklist)
				|| this->tagMatch(*piter, viManual)))
			{
				continue;
			}

			// Rename branch if requested
			if ((this->verbosity > 0) && (vsRename.size() > 0))
			{
				std::cout << "\t\t => Producer " + this->producerLabel + " will use: ";
				std::cout.flush();
			}
			const std::string targetName = this->regexRename((*piter)->moduleLabel(), vsRename);
			if ((this->verbosity > 0) && (vsRename.size() > 0))
				std::cout << targetName << "\t\t as matching name." << std::endl;

			// Filter on the new name
			if (!this->regexMatch(targetName, vsRenameWhitelist, vsRenameBlacklist))
			{
				if (this->verbosity > 0)
					std::cout << "\t\t => Branch was vetoed by post-rename Black/Whitelist!" << std::endl;
				continue;
			}

			// Avoid name collisions: Ignore or Fail
			if (std::find(vsMatched.begin(), vsMatched.end(), targetName) != vsMatched.end())
			{
				if (this->verbosity > 0)
					std::cout << "\t\t => Matching name was already processed!" << std::endl;
				continue;
			}

			// Crate selection tag
			const edm::InputTag tag((*piter)->moduleLabel(), (*piter)->productInstanceName(), (*piter)->processName());
			if (this->verbosity > 1)
				std::cout << "\t\t => Branch will be selected with " << tag << std::endl;

			// Notify about match
			if (!onMatchingInput(targetName, (*piter)->branchName(), this->psBase, tag))
				return false;
		}

		return true;
	}
};

#endif

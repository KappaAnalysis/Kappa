/* Copyright (c) 2012 - All Rights Reserved
 *   Joram Berger <joram.berger@cern.ch>
 */

#ifndef KAPPA_FILTERSUMMARYPRODUCER_H
#define KAPPA_FILTERSUMMARYPRODUCER_H

#include "KBaseMatchingProducer.h"
#include "../../DataFormats/interface/KInfo.h"
#include <FWCore/Utilities/interface/InputTag.h>

class KFilterSummaryProducer : public KBaseMatchingProducer<KFilterSummary>
{
public:
	KFilterSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMatchingProducer<KFilterSummary>(cfg, _event_tree, _lumi_tree, getLabel())
	{
		names = new KFilterMetadata;
		_lumi_tree->Bronch("filterMetadata", "KFilterMetadata", &names);
	}

	static const std::string getLabel() { return "FilterSummary"; }

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		summary->presence = 0;
		summary->decision = 0;
		edm::Handle<bool> handle;
		edm::InputTag src;

		for (size_t i = 0; i < tags.size(); ++i)
		{
			src = tags[i];

			if (!event.getByLabel(src, handle))
			{
				std::cout << "Could not get main product! src = " << src.encode() << std::endl;
				continue;
			}

			//bool conventionFail = src.encode().find("trackingPOG");
			summary->presence |= (1ul << i);
			summary->decision |= (*handle << i);
		}
		return true;
	}

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		if (!KBaseMatchingProducer<KFilterSummary>::onFirstEvent(event, setup))
			return false;

		// sort alphabetically
		std::sort(namesAndTags.begin(), namesAndTags.end());
		tags.resize(namesAndTags.size());
		names->filternames.resize(namesAndTags.size());
		for (size_t i = 0; i < namesAndTags.size(); i++)
		{
			tags[i] = namesAndTags[i].tag;
			names->filternames[i] = namesAndTags[i].name;
		}

		summary = this->allocateBronch("filterSummary");
		this->addProvenance(provenance, "KFilterSummary");

		return true;
	}

private:
	struct NameAndTagComparison
	{
		edm::InputTag tag;
		std::string name;
		NameAndTagComparison(std::string n, edm::InputTag t): tag(t), name(n) {}
		bool operator<(NameAndTagComparison const & second) const
		{
			return (this->name.compare(second.name) < 0 );
		}
	};
	std::vector<NameAndTagComparison> namesAndTags;
	std::string provenance;
	KFilterSummary *summary;
	KFilterMetadata *names;
	std::vector<edm::InputTag> tags;

	virtual bool onMatchingInput(const std::string targetName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		if (!KBaseMatchingProducer<KFilterSummary>::onMatchingInput(
				targetName, inputName, pset, tag))
			return false;

		NameAndTagComparison nt(targetName, tag);
		namesAndTags.push_back(nt);
		provenance += tag.encode() + ",";
		return true;
	}
};

#endif

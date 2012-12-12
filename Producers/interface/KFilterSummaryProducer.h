#ifndef KAPPA_FILTERSUMMARYPRODUCER_H
#define KAPPA_FILTERSUMMARYPRODUCER_H

#include "KBaseMatchingProducer.h"
#include "../../DataFormats/interface/KMetadata.h"
#include <FWCore/Utilities/interface/InputTag.h>

struct KFilterSummaryProducer_Product
{
	typedef KFilterSummary type;
	static const std::string id() { return "KFilterSummary"; };
	static const std::string producer() { return "KFilterSummaryProducer"; };
};


class KFilterSummaryProducer : public KBaseMatchingProducer<KFilterSummaryProducer_Product>
{
public:
	KFilterSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMatchingProducer<KFilterSummaryProducer_Product>(cfg, _event_tree, _lumi_tree)
	{
		names = new KFilterMetadata;
		_lumi_tree->Bronch("KFilterMetadata", "KFilterMetadata", &names);
	}
	virtual ~KFilterSummaryProducer() {}

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
		if (!KBaseMatchingProducer<KFilterSummaryProducer_Product>::onFirstEvent(event, setup))
			return false;

		// sort alphabetically
		std::sort(namesAndTags.begin(), namesAndTags.end());
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
	struct nameAndTag {
		edm::InputTag tag;
		std::string name;
		nameAndTag(std::string n, edm::InputTag t): tag(t), name(n) {}
		bool operator<(nameAndTag const & second) const {
			return (this->name < second.name);
		}
	};
	std::vector<nameAndTag> namesAndTags;
	std::string provenance;
	KFilterSummary *summary;
	KFilterMetadata *names;
	std::vector<edm::InputTag> tags;

	virtual bool onMatchingInput(const std::string targetName, const std::string inputName,
		const edm::ParameterSet &pset, const edm::InputTag &tag)
	{
		if (!KBaseMatchingProducer<KFilterSummaryProducer_Product>::onMatchingInput(
				targetName, inputName, pset, tag))
			return false;

		nameAndTag nt(targetName, tag);
		namesAndTags.push_back(nt);
		provenance += tag.encode() + ",";
		return true;
	}
};

#endif

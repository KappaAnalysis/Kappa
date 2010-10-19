#ifndef KAPPA_TRIGGEROBJECTPRODUCER_H
#define KAPPA_TRIGGEROBJECTPRODUCER_H

#include "KBaseMultiProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <DataFormats/MuonReco/interface/Muon.h>
#include <algorithm>

struct KTriggerObjectProducer_Product
{
	typedef std::vector<KDataLV> type;
	static const std::string id() { return "std::vector<KDataLV>"; };
	static const std::string producer() { return "KTriggerObjectProducer"; };
};

class KTriggerObjectProducer : public KBaseMultiProducer<trigger::TriggerEvent, KTriggerObjectProducer_Product>
{
public:
	KTriggerObjectProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<trigger::TriggerEvent, KTriggerObjectProducer_Product>(cfg, _event_tree, _run_tree),
		triggerObjects(cfg.getParameter<std::vector<std::string> >("triggerObjects")),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hltTag")) {};
	virtual ~KTriggerObjectProducer() {};

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		for (std::vector<std::string>::iterator it = triggerObjects.begin(); it != triggerObjects.end(); ++it)
			this->registerBronch("TriggerObject_" + (*it), (*it), this->psBase, tagHLTrigger);
		return true;
	}

protected:
	std::vector<std::string> triggerObjects;
	edm::InputTag tagHLTrigger;

	virtual void fillProduct(const trigger::TriggerEvent &triggerEventHandle, KTriggerObjectProducer_Product::type &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		for (size_t iF = 0; iF < triggerEventHandle.sizeFilters(); ++iF)
		{
			const std::string filterName(triggerEventHandle.filterTag(iF).label());

			if (name != "TriggerObject_"+filterName+" ("+filterName+")")
				continue;

			const trigger::Keys & keys = triggerEventHandle.filterKeys(iF);
			for (size_t iK = 0; iK < keys.size(); ++iK)
			{
				trigger::TriggerObject triggerObject(triggerEventHandle.getObjects().at(keys[iK]));
				KDataLV tmpP4;
				copyP4(triggerObject, tmpP4.p4);
				out.push_back(tmpP4);
			}
		}
	}

	virtual void clearProduct(KTriggerObjectProducer_Product::type& prod)
	{
		prod.clear();
	}
};

#endif

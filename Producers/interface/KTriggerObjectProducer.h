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
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hltTag"))
		{};
	virtual ~KTriggerObjectProducer() {};

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		for (std::vector<std::string>::iterator it = triggerObjects.begin(); it != triggerObjects.end(); it++)
		{
			std::vector<KDataLV> * target = this->allocateBronch(this->event_tree, "TriggerObject_"+(*it));
			targetIDMap[*it] = target;
		}
		return true;
	}

protected:
	std::vector<std::string> triggerObjects;
	std::map<std::string, std::vector<KDataLV> * > targetIDMap;
	edm::InputTag tagHLTrigger;

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		KBaseMultiProducer<trigger::TriggerEvent, KTriggerObjectProducer_Product>::onEvent(event, setup);
		for (std::vector<std::string>::iterator it = triggerObjects.begin(); it != triggerObjects.end(); it++)
			targetIDMap[*it]->clear();

		edm::Handle< trigger::TriggerEvent > triggerEventHandle;
		event.getByLabel(tagHLTrigger, triggerEventHandle);
		if (!triggerEventHandle.isValid())
			return false;

		for(unsigned int iF = 0; iF<triggerEventHandle->sizeFilters(); iF++)
		{
			const std::string nameFilter(triggerEventHandle->filterTag(iF).label());

			if (find(triggerObjects.begin(), triggerObjects.end(), nameFilter) == triggerObjects.end())
				continue;

			const trigger::Keys & keys = triggerEventHandle->filterKeys(iF);
			for(unsigned int iK = 0; iK<keys.size(); iK++)
			{
				trigger::TriggerObject triggerObject( triggerEventHandle->getObjects().at( keys[iK] ) );
				KDataLV tmpP4;
				tmpP4.p4 = RMDataLV(triggerObject.pt(), triggerObject.eta(), triggerObject.phi(), triggerObject.mass());
				targetIDMap[nameFilter]->push_back(tmpP4);
			}
		}
		return true;
	}
};

#endif

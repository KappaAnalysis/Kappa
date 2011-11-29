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
		KBaseMultiProducer<trigger::TriggerEvent, KTriggerObjectProducer_Product>(cfg, _event_tree, _run_tree, true),
		triggerObjects(cfg.getParameter<std::vector<std::string> >("triggerObjects")),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hltTag")),
		autoTriggerObjects(cfg.getParameter<bool>("autoTriggerObjects")),
		firstRun(true)
		{
			std::sort(triggerObjects.begin(), triggerObjects.end());
		};
	virtual ~KTriggerObjectProducer() {};

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		if (firstRun)
		{
			firstRun = false;
			for (std::vector<std::string>::iterator it = triggerObjects.begin(); it != triggerObjects.end(); ++it)
			{
				this->registerBronch("TriggerObject_" + (*it), (*it), this->psBase, tagHLTrigger);
			}

			if (autoTriggerObjects)
			{
				if (verbosity > 0)
					std::cout << "--- Begin of automatic trigger object detection ---\n";
				for (std::vector<std::string>::const_iterator it = KMetadataProducerBase::selectedHLT.begin()+1; it != KMetadataProducerBase::selectedHLT.end(); ++it)
				{
					if (verbosity > 0)
						std::cout << "\t" << (*it) << "\n";
					std::vector<std::string> modules = KMetadataProducerBase::hltConfig.saveTagsModules(*it);
					for (std::vector<std::string>::const_iterator it2 = modules.begin(); it2 != modules.end(); ++it2)
					{
						if (verbosity > 0)
							std::cout << "\t\t"<< (*it2);
						if (std::find(triggerObjects.begin(), triggerObjects.end(), *it2) == triggerObjects.end())
						{
							this->registerBronch("TriggerObject_" + (*it2), (*it2), this->psBase, tagHLTrigger);
						}
						else
						{
							if (verbosity > 0)
								std::cout << "\n";
						}
					}
				}
				if (verbosity > 0)
					std::cout << "--- End of automatic trigger object detection ---\n";
			}
		}

		return true;
	}
protected:
	std::vector<std::string> triggerObjects;
	edm::InputTag tagHLTrigger;
	bool autoTriggerObjects;
	bool firstRun;

	virtual void fillProduct(const trigger::TriggerEvent &triggerEventHandle, KTriggerObjectProducer_Product::type &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		for (size_t iF = 0; iF < triggerEventHandle.sizeFilters(); ++iF)
		{
			const std::string filterName(triggerEventHandle.filterTag(iF).label());
			if (name != "TriggerObject_" + filterName)
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

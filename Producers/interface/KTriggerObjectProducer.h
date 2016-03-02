//- Copyright (c) 2011 - All Rights Reserved
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Georg Sieber <sieber@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_TRIGGEROBJECTPRODUCER_H
#define KAPPA_TRIGGEROBJECTPRODUCER_H

#include "KBaseMultiProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include <DataFormats/MuonReco/interface/Muon.h>
#include <algorithm>

struct KTrgObjSorter
{
	KTrgObjSorter(const KTriggerObjects &_to) : to(_to) {}
	bool operator()(const size_t &a, const size_t &b)
	{
		return (to.trgObjects[a].p4.pt() > to.trgObjects[b].p4.pt());
	}
	const KTriggerObjects &to;
};

class KTriggerObjectProducer : public KBaseMultiProducer<trigger::TriggerEvent, KTriggerObjects>
{
public:
	KTriggerObjectProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<trigger::TriggerEvent, KTriggerObjects>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector), true)
	{
		toMetadata = new KTriggerObjectMetadata;
		_run_tree->Bronch("triggerObjectMetadata", "KTriggerObjectMetadata", &toMetadata);
		this->registerBronch("triggerObjects", "KTriggerObjects", this->psBase,
			cfg.getParameter<edm::InputTag>("hltTag"));
	}

	static const std::string getLabel() { return "TriggerObjects"; }


	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		toMetadata->menu = KInfoProducerBase::hltConfig.tableName();
		toMetadata->toFilter.clear();
		return true;
	}

protected:
	KTriggerObjectMetadata *toMetadata;
	KTriggerObjects *trgObjects;

	virtual void fillProduct(const trigger::TriggerEvent &triggerEventHandle, KTriggerObjects &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		HLTConfigProvider &hltConfig(KInfoProducerBase::hltConfig);
		if (verbosity > 0)
			std::cout << "KTriggerObjectProducer::fillProduct : " << hltConfig.tableName() << std::endl;

		std::map<size_t, size_t> toFWK2Kappa;
		
		out.toIdxFilter.clear();
		toMetadata->nFiltersPerHLT.clear();

		// run over all triggers
		for (size_t i = 0; i < KInfoProducerBase::hltKappa2FWK.size(); ++i)
		{
			if (i == 0)
			{
				toMetadata->nFiltersPerHLT.push_back(0);
				continue;
			}

			// get HLT index
			size_t hltIdx = KInfoProducerBase::hltKappa2FWK[i];
			if (verbosity > 0)
				std::cout << "KTriggerObjectProducer::fillProduct : " << hltConfig.triggerName(hltIdx) << ": ";
			
			const std::vector<std::string>& saveTagsModules = KInfoProducerBase::hltConfig.saveTagsModules(hltIdx);
			//const std::vector<std::string>& saveTagsModules = KInfoProducerBase::hltConfig.moduleLabels(hltIdx);
			
			// allocate memory
			toMetadata->nFiltersPerHLT.push_back(saveTagsModules.size());
			if (toMetadata->toFilter.empty() || toMetadata->toFilter.size() < toMetadata->getMaxFilterIndex(i))
			{
				toMetadata->toFilter.resize(toMetadata->getMaxFilterIndex(i) + 1);
			}
			out.toIdxFilter.resize(toMetadata->getMaxFilterIndex(i) + 1);
			
			// run over all filters for this trigger
			for (size_t m = 0; m < saveTagsModules.size(); ++m)
			{
				// run over all filters in the event and match them with the given filter
				bool found = false;
				for (size_t iF = 0; iF < triggerEventHandle.sizeFilters(); ++iF)
				{
					if (saveTagsModules[m] == triggerEventHandle.filterTag(iF).label())
					{
						found = true;
						if (verbosity > 1)
							std::cout << "<" << saveTagsModules[m] << "> ";
						
						// current index in output vectors
						size_t currentIndex = toMetadata->getMinFilterIndex(i) + m;
						
						// register filter name in the meta data and check possible changes in names within lumi section
						if (toMetadata->toFilter[currentIndex] == "") // Register L1L2 object
						{
							toMetadata->toFilter[currentIndex] = saveTagsModules[m];
							if (verbosity > 0)
								std::cout << "\t" << name << " object: " << toMetadata->toFilter[currentIndex] << std::endl;
						}
						else if (toMetadata->toFilter[currentIndex] != saveTagsModules[m]) // Check existing entry
						{
							bool isPresent = (std::find(KInfoProducerBase::svHLTFailToleranceList.begin(),
												KInfoProducerBase::svHLTFailToleranceList.end(), toMetadata->toFilter[currentIndex])
												!= KInfoProducerBase::svHLTFailToleranceList.end());
							if(!isPresent) //Check if known problem that can be skipped
							{
								std::cout << std::endl << name << " index mismatch! "<< toMetadata->toFilter[currentIndex] << " changed to " << saveTagsModules[m] << std::endl;
								std::cout << "Try blacklisting the trigger " << hltConfig.triggerName(hltIdx) << " or add the trigger objects to the hltFailToleranceList" << std::endl;
								exit(1);
							}
						}
						
						// store reference indices to trigger objects for every event
						const trigger::Keys &keys = triggerEventHandle.filterKeys(iF);
						std::vector<int> toIdxFilter;
						for (size_t iK = 0; iK < keys.size(); ++iK)
						{
							if (toFWK2Kappa.count(keys[iK]) == 0)
								toFWK2Kappa.insert(std::make_pair(keys[iK], toFWK2Kappa.size()));
							if (verbosity > 2)
								std::cout << keys[iK] << "=>" << toFWK2Kappa[keys[iK]]
									<< " (pt=" << triggerEventHandle.getObjects().at(keys[iK]).pt() << ") ";
							toIdxFilter.push_back(toFWK2Kappa[keys[iK]]);
						}
						out.toIdxFilter[currentIndex] = toIdxFilter;
						if (verbosity > 2)
							std::cout << std::endl;
					}
				}
				if ((verbosity > 1) && !found)
					std::cout << saveTagsModules[m] << " ";
			}
			if (verbosity > 0)
				std::cout << std::endl;
		}

		// Save used trigger objects
		out.trgObjects.resize(toFWK2Kappa.size());
		for (std::map<size_t, size_t>::const_iterator it = toFWK2Kappa.begin(); it != toFWK2Kappa.end(); ++it)
		{
			trigger::TriggerObject triggerObject(triggerEventHandle.getObjects().at(it->first));
			copyP4(triggerObject, out.trgObjects[it->second].p4);
		}

		KTrgObjSorter toSorter(out);
		for (size_t i = 0; i < out.toIdxFilter.size(); ++i)
		{
			std::sort(out.toIdxFilter[i].begin(), out.toIdxFilter[i].end(), toSorter);
		}
	}

	virtual void clearProduct(KTriggerObjects &prod)
	{
		prod.trgObjects.clear();
		prod.toIdxFilter.clear();
	}
};

#endif

/* Copyright (c) 2011 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_TRIGGEROBJECTPRODUCER_H
#define KAPPA_TRIGGEROBJECTPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KMetadataProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
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
	KTriggerObjectProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<trigger::TriggerEvent, KTriggerObjects>(cfg, _event_tree, _run_tree, getLabel(), true)
	{
		trgInfos = new KTriggerInfos;
		_run_tree->Bronch("KTriggerInfos", "KTriggerInfos", &trgInfos);
		this->registerBronch("KTriggerObjects", "KTriggerObjects", this->psBase,
			cfg.getParameter<edm::InputTag>("hltTag"));
	}

	static const std::string getLabel() { return "TriggerObjects"; }


	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		trgInfos->menu = KMetadataProducerBase::hltConfig.tableName();
		trgInfos->toFilter.clear();
		for (size_t i = 0; i < KMetadataProducerBase::hltKappa2FWK.size(); ++i)
		{
			trgInfos->toFilter.push_back(std::vector<std::string>());
		}
		return true;
	}

protected:
	KTriggerInfos *trgInfos;
	KTriggerObjects *trgObjects;
	std::vector<int> listL1L2;
	std::vector<int> listHLT;

	void fillTriggerObject(const trigger::TriggerEvent &triggerEventHandle,
		std::string name, std::vector<int> const& fwkIndices, std::map<size_t, size_t> &toFWK2Kappa,
		std::vector<std::string> outputModuleNames, std::vector<std::vector<size_t> > &outputIdxLists,
		std::string triggerName)
	{
		if (verbosity > 2)
			std::cout << "KTriggerObjectProducer::fillTriggerObject : Processing " << name << "..." << std::endl;
		
		for (size_t i = 0; i < fwkIndices.size(); ++i)
		{
			int fwkIdx = fwkIndices.at(i);
			
			// skip filters that have been found on run level but not on event level
			if (fwkIdx < 0)
			{
				continue;
			}
			
			std::string& outputModuleName = outputModuleNames.at(i);
			std::vector<size_t>& outputIdxList = outputIdxLists.at(i);
		
			const std::string currentModuleName = triggerEventHandle.filterTag(fwkIdx).label();
			if (outputModuleName == "") // Register L1L2 object
			{
				outputModuleName = currentModuleName;
				if (verbosity > 0)
					std::cout << "\t" << name << " object: " << outputModuleName << std::endl;
			}
			else
			{
				if (outputModuleName != currentModuleName) // Check existing entry
				{
					bool isPresent = (std::find(KMetadataProducerBase::svHLTFailToleranceList.begin(),
										KMetadataProducerBase::svHLTFailToleranceList.end(), outputModuleName)
										!= KMetadataProducerBase::svHLTFailToleranceList.end());
					if(!isPresent) //Check if known problem that can be skipped
					{
						std::cout << std::endl << name << " index mismatch! "<< outputModuleName << " changed to " << currentModuleName << std::endl;
						std::cout << "Try blacklisting the trigger " << triggerName << " or add the trigger objects to the hltFailToleranceList" << std::endl;
						exit(1);
					}
				}
			}

			// Write trigger obj indices
			const trigger::Keys &keys = triggerEventHandle.filterKeys(fwkIdx);
			for (size_t iK = 0; iK < keys.size(); ++iK)
			{
				if (toFWK2Kappa.count(keys[iK]) == 0)
					toFWK2Kappa.insert(std::make_pair(keys[iK], toFWK2Kappa.size()));
				if (verbosity > 2)
					std::cout << keys[iK] << "=>" << toFWK2Kappa[keys[iK]]
						<< " (pt=" << triggerEventHandle.getObjects().at(keys[iK]).pt() << ") ";
				outputIdxList.push_back(toFWK2Kappa[keys[iK]]);
			}
			if (verbosity > 2)
				std::cout << std::endl;
		}
	}

	virtual void fillProduct(const trigger::TriggerEvent &triggerEventHandle, KTriggerObjects &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		HLTConfigProvider &hltConfig(KMetadataProducerBase::hltConfig);
		if (verbosity > 0)
			std::cout << "KTriggerObjectProducer::fillProduct : " << hltConfig.tableName() << std::endl;

		std::map<size_t, size_t> toFWK2Kappa;

		// run over all triggers
		for (size_t i = 0; i < KMetadataProducerBase::hltKappa2FWK.size(); ++i)
		{
			out.toIdxFilter.push_back(std::vector<std::vector<size_t> >());
			if (i == 0)
			{
				continue;
			}

			// get HLT index
			size_t hltIdx = KMetadataProducerBase::hltKappa2FWK[i];
			if (verbosity > 0)
				std::cout << "KTriggerObjectProducer::fillProduct : " << hltConfig.triggerName(hltIdx) << ": ";
			
			const std::vector<std::string>& saveTagsModules = KMetadataProducerBase::hltConfig.saveTagsModules(hltIdx);
			//const std::vector<std::string>& saveTagsModules = KMetadataProducerBase::hltConfig.moduleLabels(hltIdx);
			
			// indices for filters of a given HLT
			std::vector<int> fwkIndices(saveTagsModules.size(), -1);
			
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
						fwkIndices[m] = iF;
						trgInfos->toFilter[i].resize(saveTagsModules.size());
						out.toIdxFilter[i].resize(saveTagsModules.size());
					}
				}
				if ((verbosity > 1) && !found)
					std::cout << saveTagsModules[m] << " ";
			}
			if (verbosity > 0)
				std::cout << std::endl;

			// Fill Filters
			fillTriggerObject(triggerEventHandle, "Filters", fwkIndices, toFWK2Kappa, trgInfos->toFilter[i], out.toIdxFilter[i], hltConfig.triggerName(hltIdx));
		}

		// Save used trigger objects
		out.trgObjects.resize(toFWK2Kappa.size());
		for (std::map<size_t, size_t>::const_iterator it = toFWK2Kappa.begin(); it != toFWK2Kappa.end(); ++it)
		{
			trigger::TriggerObject triggerObject(triggerEventHandle.getObjects().at(it->first));
			copyP4(triggerObject, out.trgObjects[it->second].p4);
		}

		KTrgObjSorter toSorter(out);
		for (size_t i = 0; i < KMetadataProducerBase::hltKappa2FWK.size(); ++i)
		{
			for (size_t j = 0; j < out.toIdxFilter[i].size(); ++j)
			{
				std::sort(out.toIdxFilter[i][j].begin(), out.toIdxFilter[i][j].end(), toSorter);
			}
		}
	}

	virtual void clearProduct(KTriggerObjects &prod)
	{
		prod.trgObjects.clear();
		prod.toIdxFilter.clear();
	}
};

#endif

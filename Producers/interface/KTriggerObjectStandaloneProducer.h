//- Copyright (c) 2011 - All Rights Reserved
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_TRIGGEROBJECTSTANDALONEPRODUCER_H
#define KAPPA_TRIGGEROBJECTSTANDALONEPRODUCER_H

#include "KBaseMultiProducer.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Math/interface/deltaR.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"

/* Producer mainly written in analogy to
 *
 * https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD#Trigger
 *
 * Prescales are already prepared, although not used at the moment */



class KTriggerObjectStandaloneProducer : public KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KTriggerObjects>
{
public:
	KTriggerObjectStandaloneProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KTriggerObjects>(cfg, _event_tree, _run_tree, getLabel(), true)
	{
		triggerBits_ = cfg.getParameter<edm::InputTag>("bits");
		triggerObjects_ = cfg.getParameter<edm::InputTag>("objects");
		triggerPrescales_ = cfg.getParameter<edm::InputTag>("prescales");

		toMetadata = new KTriggerObjectMetadata;
		_run_tree->Bronch("triggerObjectMetadata", "KTriggerObjectMetadata", &toMetadata);

	}

	static const std::string getLabel() { return "TriggerObjectStandalone"; }


	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		toMetadata->menu = KInfoProducerBase::hltConfig.tableName();
		toMetadata->toFilter.clear();
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup) override
	{
		edm::Handle<edm::TriggerResults> triggerBits;
		edm::Handle<pat::TriggerObjectStandAloneCollection> triggerObjects;
		edm::Handle<pat::PackedTriggerPrescales> triggerPrescales;

		event.getByLabel(triggerBits_, triggerBits);
		event.getByLabel(triggerObjects_, triggerObjects);
		event.getByLabel(triggerPrescales_, triggerPrescales);

		names_ = event.triggerNames(*triggerBits);

		std::vector<size_t> triggerBitsFired;

		for (unsigned int i = 0, n = triggerBits->size(); i < n; ++i) 
		{
			if(verbosity>1)
				std::cout << "Trigger " << names_.triggerName(i) << ", prescale " << triggerPrescales->getPrescaleForIndex(i) << ": " << (triggerBits->accept(i) ? "PASS" : "fail (or not run)") << std::endl;

			if(triggerBits->accept(i))
				triggerBitsFired.push_back(i);
		}

		// check if any triggerObjects at all should be looped on
		signifTriggerBitFired_ = commonTriggerBits(triggerBitsFired, KInfoProducerBase::hltKappa2FWK);

		return KBaseMultiProducer::onEvent(event, setup);
	}

	bool commonTriggerBits(std::vector<size_t> triggerBitsFired, std::vector<size_t> triggerBitsSelected)
	{
		for(auto triggerBitSelected: triggerBitsSelected)
		{
			for(auto triggerBitFired: triggerBitsFired)
			{
				if(triggerBitSelected == triggerBitFired)
					{
					if(verbosity > 1)
						std::cout << "write out TriggerObject. " << triggerBitSelected << std::endl;
					return true;
				}
			}
		}
	return false;
	}

	std::vector<int> getHLTIndices(std::vector<std::string> pathNamesTriggerObject, std::vector<size_t> selectedPathNameIndices)
	{
		std::vector<int> hltIndices;

		HLTConfigProvider &hltConfig(KInfoProducerBase::hltConfig);
		for(auto pathNameTriggerObject : pathNamesTriggerObject)
		{
			for(auto hltIdx: selectedPathNameIndices)
			{
				if (hltConfig.triggerName(hltIdx) == pathNameTriggerObject)
				{
					hltIndices.push_back(hltIdx);
					const std::vector<std::string>& saveTagsModules = KInfoProducerBase::hltConfig.saveTagsModules(hltIdx);
					
					toMetadata->nFiltersPerHLT.push_back(saveTagsModules.size());

				}
			}
		}
		return hltIndices;
	}

	std::vector<int> getFilterIndices(std::vector<std::string> filterLabels)
	{
		std::vector<int> filterIndices;
		for(unsigned int i = 0; i < toMetadata->toFilter.size(); ++i)
		{
			if(toMetadata->toFilter[i] == "")
				continue;

			for(auto filterLabel: filterLabels)
			{
				if(filterLabel==toMetadata->toFilter[i])
					filterIndices.push_back(i);
			}
		}
		return filterIndices;
	}

	void fillMetadata(pat::TriggerObjectStandAlone &obj, KTriggerObjects &out, const std::string &name)
	{
		
		HLTConfigProvider &hltConfig(KInfoProducerBase::hltConfig);
		if (verbosity > 0)
			std::cout << "KTriggerObjectStandaloneProducer::fillProduct : " << hltConfig.tableName() << std::endl;

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
				std::cout << "KTriggerObjectStandaloneProducer::fillProduct : " << hltConfig.triggerName(hltIdx) << ": ";
			
			const std::vector<std::string>& saveTagsModules = KInfoProducerBase::hltConfig.saveTagsModules(hltIdx);
			
			// allocate memory
			toMetadata->nFiltersPerHLT.push_back(saveTagsModules.size());
			if (toMetadata->toFilter.empty() || toMetadata->toFilter.size() < toMetadata->getMaxFilterIndex(i))
			{
				toMetadata->toFilter.resize(toMetadata->getMaxFilterIndex(i) + 1);
			}

			// fillMetadata runs in a loop: resize the vector only at the first iteration
			if (iLoop == 0)
				out.toIdxFilter.resize(toMetadata->getMaxFilterIndex(i) + 1);

			// run over all filters for this trigger
			for (size_t m = 0; m < saveTagsModules.size(); ++m)
			{
				// run over all filters in the event and match them with the given filter
				bool found = false;

				std::vector<std::string> filterLabels  = obj.filterLabels();
				for (size_t iF = 0; iF < filterLabels.size(); ++iF)
				{
					if (saveTagsModules[m] == filterLabels[iF])
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
						if (toFWK2Kappa.count(currentIndex) == 0) {
							std::vector<int> toFWK2KappaSize;
							toFWK2KappaSize.push_back(filterIndex);
							toFWK2Kappa.insert(std::make_pair(currentIndex, toFWK2KappaSize));
						}
						else {
							toFWK2Kappa[currentIndex].push_back(filterIndex);
						}

						out.toIdxFilter[currentIndex] = toFWK2Kappa[currentIndex];
						KLV triggerObject;
						copyP4(obj.p4(), triggerObject.p4);
						out.trgObjects.push_back(triggerObject);

						filterIndex++;

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
	}

protected:
	KTriggerObjectMetadata *toMetadata;
	KTriggerObjects *trgObjects;
	std::map<size_t, std::vector<int>> toFWK2Kappa;
	int filterIndex;
	int iLoop;

	virtual void fillProduct(const InputType &in, KTriggerObjects &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset) override
	{
		if(!signifTriggerBitFired_)
			return;

		filterIndex = 0;
		iLoop = 0;
		toFWK2Kappa.clear();
		out.trgObjects.clear();
		out.toIdxFilter.clear();

		for(auto obj : in)
		{
			obj.unpackPathNames(names_);
			fillMetadata(obj, out, name);

			auto pathNamesAll = obj.pathNames(false);
	
			iLoop++;
		}
	}

	virtual void clearProduct(KTriggerObjects &prod)
	{
		prod.trgObjects.clear();
		prod.toIdxFilter.clear();
	}

private:
	edm::InputTag triggerBits_;
	edm::InputTag triggerObjects_;
	edm::InputTag triggerPrescales_;
	bool signifTriggerBitFired_;
	edm::TriggerNames names_;
};

#endif

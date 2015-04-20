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
	}

	static const std::string getLabel() { return "TriggerObjectStandalone"; }


/*	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		toMetadata->menu = KInfoProducerBase::hltConfig.tableName();
		tometadata->tofilter.clear();
		return true;
	}*/

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

	std::vector<int> getFilterIndices(std::vector<std::string> pathNamesTriggerObject, std::vector<size_t> selectedPathNameIndices)
	{
		std::vector<int> filterIndices;

		HLTConfigProvider &hltConfig(KInfoProducerBase::hltConfig);
		for(auto pathNameTriggerObject : pathNamesTriggerObject)
		{
			for(auto hltIdx: selectedPathNameIndices)
			{
				if (hltConfig.triggerName(hltIdx) == pathNameTriggerObject)
				{
					filterIndices.push_back(hltIdx);
				}
			}
		}
		return filterIndices;
	}

protected:
	KTriggerObjectMetadata *toMetadata;
	KTriggerObjects *trgObjects;

	virtual void fillProduct(const InputType &in, KTriggerObjects &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset) override
	{
		if(!signifTriggerBitFired_)
			return;
		for(auto obj : in)
		{
			obj.unpackPathNames(names_);
			auto pathNamesAll = obj.pathNames(false);
			std::vector<int> filterIndices = getFilterIndices(pathNamesAll, KInfoProducerBase::hltKappa2FWK);

			if(filterIndices.size() > 0)
			{
				KLV triggerObject;
				copyP4(obj.p4(), triggerObject.p4);
				out.trgObjects.push_back(triggerObject);

				out.toIdxFilter.push_back(filterIndices);
			}
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

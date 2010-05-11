#ifndef KAPPA_METADATAPRODUCER_H
#define KAPPA_METADATAPRODUCER_H

#include "KBaseProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include "../../DataFormats/interface/KMetadata.h"

#include <DataFormats/Common/interface/TriggerResults.h>
#include <HLTrigger/HLTcore/interface/HLTConfigProvider.h>
#include <L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h>
#include <DataFormats/METReco/interface/HcalNoiseSummary.h>
#include <DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutRecord.h>
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "DataFormats/HLTReco/interface/TriggerEvent.h"

// real data
struct KMetadata_Product
{
	typedef KLumiMetadata typeLumi;
	typedef KEventMetadata typeEvent;
	static const std::string idLumi() { return "KLumiMetadata"; };
	static const std::string idEvent() { return "KEventMetadata"; };
};

template<typename Tmeta>
class KMetadataProducer : public KBaseProducer
{
public:
	KMetadataProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		tagL1Results(cfg.getParameter<edm::InputTag>("l1Source")),
		tagHLTResults(cfg.getParameter<edm::InputTag>("hltSource")),
		svHLTWhitelist(cfg.getParameter<std::vector<std::string> >("hltWhitelist")),
		svHLTBlacklist(cfg.getParameter<std::vector<std::string> >("hltBlacklist")),
		svMuonTriggerObjects(cfg.getParameter<std::vector<std::string> >("muonTriggerObjects")),
		tagNoiseHCAL(cfg.getParameter<edm::InputTag>("noiseHCAL")),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hlTrigger")),
		printHltList(cfg.getParameter<bool>("printHltList"))
	{
		metaLumi = new typename Tmeta::typeLumi();
		_lumi_tree->Bronch("KLumiMetadata", Tmeta::idLumi().c_str(), &metaLumi);
		metaEvent = new typename Tmeta::typeEvent();
		_event_tree->Bronch("KEventMetadata", Tmeta::idEvent().c_str(), &metaEvent);
	}
	virtual ~KMetadataProducer() {};

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		hltKappa2FWK.clear();
		hltKappa2FWK.push_back(0);
		hltNames.clear();
		hltPrescales.clear();

		if (tagHLTResults.label() == "")
			return true;

		bool hltSetupChanged = false;
		if (!hltConfig.init(run, setup, tagHLTResults.process(), hltSetupChanged))
			return fail(std::cout << "Invalid HLT process selected: " << tagHLTResults.process() << std::endl);

		if (hltSetupChanged)
			std::cout << "HLT setup has changed...";

		int counter = 1;
		hltNames.push_back("fail");
		hltPrescales.push_back(42);

		for (size_t i = 0; i < hltConfig.size(); ++i)
		{
			const std::string &name = hltConfig.triggerName(i);
			const int idx = hltConfig.triggerIndex(name);
			if (verbosity > 1)
				std::cout << "Trigger: " << idx << " = ";
			if (!regexMatch(name, svHLTWhitelist, svHLTBlacklist))
				continue;
			if (verbosity > 0 || printHltList)
				std::cout << " => Adding trigger: " << name << " with ID: " << idx << " as " << counter
					<< " with prescale " << hltConfig.prescaleValue(idx, name) << std::endl;
			hltPrescales.push_back(hltConfig.prescaleValue(idx, name));

			if (hltKappa2FWK.size() < 64)
			{
				hltKappa2FWK.push_back(idx);
				hltNames.push_back(name);
				counter++;
			}
			else
				std::cout << "Too many HLT bits selected! " << name << " discarded!" << std::endl;
		}
		if (verbosity > 0)
			std::cout << "Accepted number of trigger streams: " << counter - 1 << std::endl;
		return true;
	}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		metaLumi = &(metaLumiMap[std::pair<unsigned int, unsigned int>(
			(unsigned int)lumiBlock.run(), (unsigned int)lumiBlock.luminosityBlock())]);
		metaLumi->nRun = lumiBlock.run();
		metaLumi->nLumi = lumiBlock.luminosityBlock();

		firstEventInLumi = true;
		metaLumi->hltNames = hltNames;
		metaLumi->hltPrescales = hltPrescales;
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		if (firstEventInLumi)
		{
			firstEventInLumi = false;
			edm::Handle<trigger::TriggerEvent> triggerEventHandle;
			if ((tagHLTrigger.label() != "") && event.getByLabel(tagHLTrigger, triggerEventHandle))
			{
				const unsigned sizeFilters = triggerEventHandle->sizeFilters();
				int idx=0;
				for(unsigned int iF = 0; iF<sizeFilters; iF++)
				{
					const std::string filterName(triggerEventHandle->filterTag(iF).label());

					bool matched=false;
					for (std::vector<std::string>::iterator it=svMuonTriggerObjects.begin(); it!=svMuonTriggerObjects.end(); it++)
					{
						if (regexMatch(filterName, *it))
							matched=true;
					}
					if (matched)
					{
						metaLumi->hltNamesMuons.push_back(filterName);
						KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap[filterName]=idx;
						std::cout << "muon trigger object: " << idx << " = " << filterName << "\n";
						idx++;
					}
				}
			}
		}

		// Set basic event infos
		metaEvent->nRun = event.id().run();
		metaEvent->nEvent = event.id().event();
		metaEvent->nLumi = event.luminosityBlock();
		metaEvent->nBX = event.bunchCrossing();

		// Set HLT trigger bits
		metaEvent->bitsHLT = 0;
		if (tagHLTResults.label() != "")
		{
			edm::Handle<edm::TriggerResults> hTriggerResults;
			event.getByLabel(tagHLTResults, hTriggerResults);

			bool hltFAIL = false;
			for (size_t i = 1; i < hltKappa2FWK.size(); ++i)
			{
				const size_t idx = hltKappa2FWK[i];
				if (hTriggerResults->accept(idx))
					metaEvent->bitsHLT |= ((unsigned long long)1 << i);
				hltFAIL = hltFAIL || hTriggerResults->error(idx);
			}
			if (hltFAIL)
				metaEvent->bitsHLT |= 1;
		}

		// Set L1 trigger bits
		metaEvent->bitsL1 = 0;
		bool bPhysicsDeclared = true;
		if (tagL1Results.label() != "")
		{
			edm::Handle<L1GlobalTriggerReadoutRecord> hL1Result;
			event.getByLabel(tagL1Results, hL1Result);
			for (size_t i = 0; i < hL1Result->technicalTriggerWord().size(); ++i)
				if (hL1Result->technicalTriggerWord().at(i))
					metaEvent->bitsL1 |= ((unsigned long long)1 << i);
			bPhysicsDeclared = (hL1Result->gtFdlWord().physicsDeclared() == 1);
		}

		// User flags
		metaEvent->bitsUserFlags = 0;

		// Physics declared
		if (bPhysicsDeclared)
			metaEvent->bitsUserFlags |= KFlagPhysicsDeclared;

		if (tagNoiseHCAL.label() != "")
		{
			// HCAL noise
			edm::Handle<HcalNoiseSummary> noiseSummary;
			event.getByLabel(tagNoiseHCAL, noiseSummary);
			if (noiseSummary->passLooseNoiseFilter())
				metaEvent->bitsUserFlags |= KFlagHCALLooseNoise;
			if (noiseSummary->passTightNoiseFilter())
				metaEvent->bitsUserFlags |= KFlagHCALTightNoise;
		}

		return true;
	}

	static std::map<std::string, int> muonTriggerObjectBitMap;

protected:
	bool firstEventInLumi;
	edm::InputTag tagL1Results, tagHLTResults;
	std::vector<std::string> svHLTWhitelist, svHLTBlacklist;
	std::vector<std::string> svMuonTriggerObjects;
	HLTConfigProvider hltConfig;
	std::vector<size_t> hltKappa2FWK;

	edm::InputTag tagNoiseHCAL, tagHLTrigger;
	bool printHltList;

	std::vector<std::string> hltNames;
	std::vector<unsigned int> hltPrescales;

	typename Tmeta::typeLumi *metaLumi;
	typename Tmeta::typeEvent *metaEvent;

	std::map<std::pair<unsigned int, unsigned int>, typename Tmeta::typeLumi> metaLumiMap;
};

template<typename Tmeta>
std::map<std::string, int> KMetadataProducer<Tmeta>::muonTriggerObjectBitMap;

#endif

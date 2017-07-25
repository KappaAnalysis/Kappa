//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Georg Sieber <sieber@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_INFOPRODUCER_H
#define KAPPA_INFOPRODUCER_H

#include <vector>
#include <algorithm>

#include "KBaseProducer.h"
#include "../../DataFormats/interface/KInfo.h"

#include <FWCore/Framework/interface/ConstProductRegistry.h>
#include <FWCore/MessageLogger/interface/ELseverityLevel.h>
#include <FWCore/MessageLogger/interface/ErrorSummaryEntry.h>
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

#include <DataFormats/Common/interface/TriggerResults.h>
#include <DataFormats/HLTReco/interface/TriggerEvent.h>
#include <DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutRecord.h>
#include <L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h>
#include <HLTrigger/HLTcore/interface/HLTConfigProvider.h>

#include <DataFormats/METReco/interface/HcalNoiseSummary.h>

#include <DataFormats/TauReco/interface/CaloTauDiscriminator.h>
#include <DataFormats/TauReco/interface/PFTauDiscriminator.h>

#include <DataFormats/VertexReco/interface/VertexFwd.h>
#include <DataFormats/VertexReco/interface/Vertex.h>

#include <DataFormats/Provenance/interface/ProcessHistory.h>


// real data
struct KInfo_Product
{
	typedef KLumiInfo typeLumi;
	typedef KEventInfo typeEvent;
	static const std::string idLumi() { return "KLumiInfo"; };
	static const std::string idEvent() { return "KEventInfo"; };
};

class KInfoProducerBase : public KBaseProducerWP
{
public:
	KInfoProducerBase(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseProducerWP(cfg, _event_tree, _lumi_tree, "KInfo", std::forward<edm::ConsumesCollector>(consumescollector)) {}

	virtual ~KInfoProducerBase() {};

	static HLTConfigProvider hltConfig;
	static std::vector<size_t> hltKappa2FWK;
	static std::vector<std::string> selectedHLT;
	static std::vector<std::string> svHLTFailToleranceList;
};

HLTConfigProvider KInfoProducerBase::hltConfig;
std::vector<size_t> KInfoProducerBase::hltKappa2FWK;
std::vector<std::string> KInfoProducerBase::selectedHLT;
std::vector<std::string> KInfoProducerBase::svHLTFailToleranceList;


template<typename Tmeta>
class KInfoProducer : public KInfoProducerBase
{
public:
	KInfoProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KInfoProducerBase(cfg, _event_tree, _lumi_tree, std::forward<edm::ConsumesCollector>(consumescollector)),
		tauDiscrProcessName(cfg.getUntrackedParameter<std::string>("tauDiscrProcessName", "")),
		tagL1Results(cfg.getParameter<edm::InputTag>("l1Source")),
		tagHLTResults(cfg.getParameter<edm::InputTag>("hltSource")),
		svHLTWhitelist(cfg.getParameter<std::vector<std::string> >("hltWhitelist")),
		svHLTBlacklist(cfg.getParameter<std::vector<std::string> >("hltBlacklist")),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hlTrigger")),
		tagErrorsAndWarnings(cfg.getParameter<edm::InputTag>("errorsAndWarnings")),
		avoidEaWCategories(cfg.getParameter<std::vector<std::string> >("errorsAndWarningsAvoidCategories")),
		printErrorsAndWarnings(cfg.getParameter<bool>("printErrorsAndWarnings")),
		printHltList(cfg.getParameter<bool>("printHltList")),
		overrideHLTCheck(cfg.getUntrackedParameter<bool>("overrideHLTCheck", false))
	{
		metaLumi = new typename Tmeta::typeLumi();
		_lumi_tree->Bronch("lumiInfo", Tmeta::idLumi().c_str(), &metaLumi);
		metaEvent = new typename Tmeta::typeEvent();
		_event_tree->Bronch("eventInfo", Tmeta::idEvent().c_str(), &metaEvent);

		std::vector<std::string> list = cfg.getParameter<std::vector<std::string> >("hltFailToleranceList");
		for (size_t i = 0; i < list.size(); ++i)
		{
			svHLTFailToleranceList.push_back(list[i]);
		}
		consumescollector.consumes<L1GlobalTriggerReadoutRecord>(tagL1Results);
	 	tagHLTResultsToken = consumescollector.consumes<edm::TriggerResults>(tagHLTResults);
		tokenErrorsAndWarnings = consumescollector.consumes<std::vector<edm::ErrorSummaryEntry>>(tagErrorsAndWarnings);
	}
	virtual ~KInfoProducer() {};

	static const std::string getLabel() { return "Info"; }

	inline void addHLT(const int idx, const std::string name, const int prescale)
	{
		KInfoProducerBase::hltKappa2FWK.push_back(idx);
		hltNames.push_back(name);
		selectedHLT.push_back(name);
		hltPrescales.push_back(prescale);
	}

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		KInfoProducerBase::hltKappa2FWK.clear();
		hltNames.clear();
		hltPrescales.clear();
		addHLT(0, "fail", 42/*, std::vector<std::string>()*/);


               if (tagHLTResults.process() == "")
               {
                       if (verbosity > 0)
                               std::cout << "tagHLTResults is empty" << std::endl
                                       << " -> trying to determine the process name automatically: ";

                       const edm::ProcessHistory& processHistory(run.processHistory());
                       for (edm::ProcessHistory::const_iterator it = processHistory.begin(); it != processHistory.end(); ++it)
                       {
                               if (verbosity > 0)
                                       std::cout << it->processName();
                               edm::ProcessConfiguration processConfiguration;
                               if (processHistory.getConfigurationForProcess(it->processName(), processConfiguration))
                               {
                                       edm::ParameterSet processPSet;
                                       if (edm::pset::Registry::instance()->getMapped(processConfiguration.parameterSetID(), processPSet))
                                       {
                                               if (processPSet.exists("hltTriggerSummaryAOD"))
                                               {
                                                       tagHLTResults = edm::InputTag(tagHLTResults.label(), "", it->processName());
                                                       if (verbosity > 0)
                                                               std::cout << "*";
                                               }
                                       }
                               }
                               if (verbosity > 0)
                                       std::cout << " ";
                       }
                       if (verbosity > 0)
                               std::cout << std::endl;
                       std::cout << "Taking trigger from process " << tagHLTResults.process()
                               << " (label = " << tagHLTResults.label() << ")" << std::endl;
                       this->addProvenance(tagHLTResults.process(), "");
                       if (tagHLTResults.process() == "")
                               return true;
               }

		bool hltSetupChanged = false;
		if (!KInfoProducerBase::hltConfig.init(run, setup, tagHLTResults.process(), hltSetupChanged))
			return fail(std::cout << "Invalid HLT process selected: " << tagHLTResults.process() << std::endl);

		if (verbosity > 0 && hltSetupChanged)
			std::cout << "HLT setup has changed." << std::endl;

		int counter = 1;
		for (size_t i = 0; i < KInfoProducerBase::hltConfig.size(); ++i)
		{
			const std::string &name = KInfoProducerBase::hltConfig.triggerName(i);
			const int hltIdx = KInfoProducerBase::hltConfig.triggerIndex(name);
			
			if (verbosity > 1)
				std::cout << "KInfoProducer::onRun : Trigger: " << hltIdx << " = ";
			if (!regexMatch(name, svHLTWhitelist, svHLTBlacklist))
				continue;
			if (verbosity > 0 || printHltList)
				std::cout << "KInfoProducer::onRun :  => Adding trigger: " << name << " with ID: " << hltIdx << " as " << counter
					<< " with placeholder prescale 0" << std::endl;
			
			addHLT(hltIdx, name, 0/*, KInfoProducerBase::hltConfig.saveTagsModules(i)*/);
			++counter;
		}
		if (verbosity > 0)
			std::cout << "KInfoProducer::onRun : Accepted number of trigger streams: " << counter - 1 << std::endl;

		return true;
	}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		metaLumi = &(metaLumiMap[std::pair<run_id, lumi_id>(lumiBlock.run(), lumiBlock.luminosityBlock())]);
		metaLumi->nRun = lumiBlock.run();
		metaLumi->nLumi = lumiBlock.luminosityBlock();
		metaLumi->bitsUserFlags = 0;

		metaLumi->hltNames = hltNames;
		metaLumi->hltPrescales = hltPrescales;

		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		// Set basic event infos
		metaEvent->nRun = event.id().run();
		metaEvent->nEvent = event.id().event();
		metaEvent->nLumi = event.luminosityBlock();
		metaEvent->nBX = event.bunchCrossing();
		// If we are running on real data then the trigger should
		// always be HLT.
		// Disable the overrideHLTCheck for embedded data
		if (!overrideHLTCheck)
			assert(!event.isRealData() || tagHLTResults.process() == "HLT" || tagHLTResults.process() == "RECO");

		bool triggerPrescaleError = false;
		metaEvent->bitsHLT.clear();
		if (tagHLTResults.label() != "")
               {
                       // set HLT trigger bits
                       edm::Handle<edm::TriggerResults> hTriggerResults;
                       event.getByLabel(tagHLTResults, hTriggerResults);

                       bool hltFAIL = false;
                       metaEvent->bitsHLT.resize(KInfoProducerBase::hltKappa2FWK.size()+1);
                       for (size_t i = 1; i < KInfoProducerBase::hltKappa2FWK.size(); ++i)
                       {
                               const size_t idx = KInfoProducerBase::hltKappa2FWK[i];
                               metaEvent->bitsHLT[i] = hTriggerResults->accept(idx);
                               hltFAIL = hltFAIL || hTriggerResults->error(idx);
                       }
                       metaEvent->bitsHLT[0] = hltFAIL;

                       // set and check trigger prescales
                       for (size_t i = 1; i < KInfoProducerBase::hltKappa2FWK.size(); ++i)
                       {
                               const std::string &name = metaLumi->hltNames[i];
                               unsigned int prescale = 0;
                               if (metaLumi->hltPrescales[i] == 0)
                               {
                                       if (verbosity > 0 || printHltList)
                                               std::cout << "KInfoProducer::onEvent :  => Adding prescale for trigger: '" << name
                                                       << " with value: " << prescale << std::endl;
                                       metaLumi->hltPrescales[i] = prescale;
                               }
                               if (metaLumi->hltPrescales[i] != prescale)
                               {
                                       if (this->verbosity > 0)
                                               std::cout << "KInfoProducer::onEvent :  !!!!!!!!!!! the prescale of " << name << " has changed with respect to the beginning of the luminosity section from " <<metaLumi->hltPrescales<< " to " << prescale << std::endl;
                                       triggerPrescaleError = true;
                               }
                       }
               }
               else
               {
                       for (size_t i = 1; i < KInfoProducerBase::hltKappa2FWK.size(); ++i)
                               metaLumi->hltPrescales[i] = 1;
               }

		
		for (size_t i = 1; i < KInfoProducerBase::hltKappa2FWK.size(); ++i)
			metaLumi->hltPrescales[i] = 1;

		// Set L1 trigger bits
		metaEvent->bitsL1 = 0;
		bool bPhysicsDeclared = true;

		// User flags
		metaEvent->bitsUserFlags = 0;

		// Physics declared
		if (bPhysicsDeclared)
			metaEvent->bitsUserFlags |= KEFPhysicsDeclared;

		// Detection of unexpected trigger prescale change
		if (triggerPrescaleError)
			metaLumi->bitsUserFlags |= KLFPrescaleError;

		edm::Handle<std::vector<edm::ErrorSummaryEntry> > errorsAndWarnings;

		event.getByToken(tokenErrorsAndWarnings, errorsAndWarnings);
		if (errorsAndWarnings.failedToGet())
		{
			metaEvent->bitsUserFlags |= KEFRecoErrors;
			metaEvent->bitsUserFlags |= KEFRecoWarnings;
		}
		else
		{
			for (std::vector<edm::ErrorSummaryEntry>::const_iterator it = errorsAndWarnings->begin(); it != errorsAndWarnings->end(); it++)
			{
				if (avoidEaWCategories.size() != 0 && std::find(avoidEaWCategories.begin(), avoidEaWCategories.end(), it->category) != avoidEaWCategories.end())
					continue;
				if (it->severity.getLevel() == edm::ELseverityLevel::ELsev_error || it->severity.getLevel() == edm::ELseverityLevel::ELsev_error)
					metaEvent->bitsUserFlags |= KEFRecoErrors;
				if (it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning || it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning)
					metaEvent->bitsUserFlags |= KEFRecoWarnings;

				if (printErrorsAndWarnings && (it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning || it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning))
					std::cout << "warning: " << it->category << ", " << it->module << ", " << it->count << "\n";
				if (printErrorsAndWarnings && (it->severity.getLevel() == edm::ELseverityLevel::ELsev_error || it->severity.getLevel() == edm::ELseverityLevel::ELsev_error))
					std::cout << "error: " << it->category << ", " << it->module << ", " << it->count << "\n";
			}
		}

		return true;
	}

protected:
	std::string tauDiscrProcessName;
	edm::InputTag tagL1Results, tagHLTResults;
	edm::EDGetTokenT<edm::TriggerResults> tagHLTResultsToken;
	std::vector<std::string> svHLTWhitelist, svHLTBlacklist;

	edm::InputTag tagHLTrigger;
	edm::InputTag tagErrorsAndWarnings;
	edm::EDGetTokenT<std::vector<edm::ErrorSummaryEntry>> tokenErrorsAndWarnings;
	std::vector<std::string> avoidEaWCategories;
	bool printErrorsAndWarnings;
	bool printHltList;
	bool overrideHLTCheck;

	std::vector<std::string> hltNames;
	std::vector<unsigned int> hltPrescales;

	typename Tmeta::typeLumi *metaLumi;
	typename Tmeta::typeEvent *metaEvent;

	std::map<std::pair<run_id, lumi_id>, typename Tmeta::typeLumi> metaLumiMap;
};
#endif

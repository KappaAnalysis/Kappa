#ifndef KAPPA_METADATAPRODUCER_H
#define KAPPA_METADATAPRODUCER_H

#include <vector>
#include <algorithm>

#include "KBaseProducer.h"
#include "../../DataFormats/interface/KMetadata.h"

#include <FWCore/Framework/interface/ConstProductRegistry.h>
#include <FWCore/MessageLogger/interface/ELseverityLevel.h>
#include <FWCore/MessageLogger/interface/ErrorSummaryEntry.h>
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>

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

#define NEWHLT

// real data
struct KMetadata_Product
{
	typedef KLumiMetadata typeLumi;
	typedef KEventMetadata typeEvent;
	static const std::string idLumi() { return "KLumiMetadata"; };
	static const std::string idEvent() { return "KEventMetadata"; };
};

class KMetadataProducerBase : public KBaseProducerWP
{
public:
	KMetadataProducerBase(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseProducerWP(cfg, _event_tree, _lumi_tree, "KMetadata") {}

	static HLTConfigProvider hltConfig;
	static std::vector<size_t> hltKappa2FWK;
	static std::vector<std::string> selectedHLT;
};

HLTConfigProvider KMetadataProducerBase::hltConfig;
std::vector<size_t> KMetadataProducerBase::hltKappa2FWK;
std::vector<std::string> KMetadataProducerBase::selectedHLT;

template<typename Tmeta>
class KMetadataProducer : public KMetadataProducerBase
{
public:
	KMetadataProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KMetadataProducerBase(cfg, _event_tree, _lumi_tree),
		tauDiscrProcessName(cfg.getUntrackedParameter<std::string>("tauDiscrProcessName", "")),
		tagL1Results(cfg.getParameter<edm::InputTag>("l1Source")),
		tagHLTResults(cfg.getParameter<edm::InputTag>("hltSource")),
		svHLTWhitelist(cfg.getParameter<std::vector<std::string> >("hltWhitelist")),
		svHLTBlacklist(cfg.getParameter<std::vector<std::string> >("hltBlacklist")),
		svMuonTriggerObjects(cfg.getParameter<std::vector<std::string> >("muonTriggerObjects")),
		tagNoiseHCAL(cfg.getParameter<edm::InputTag>("noiseHCAL")),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hlTrigger")),
		tagErrorsAndWarnings(cfg.getParameter<edm::InputTag>("errorsAndWarnings")),
		avoidEaWCategories(cfg.getParameter<std::vector<std::string> >("errorsAndWarningsAvoidCategories")),
		printErrorsAndWarnings(cfg.getParameter<bool>("printErrorsAndWarnings")),
		printHltList(cfg.getParameter<bool>("printHltList")),
		overrideHLTCheck(cfg.getUntrackedParameter<bool>("overrideHLTCheck", false))
	{
		metaLumi = new typename Tmeta::typeLumi();
		_lumi_tree->Bronch("KLumiMetadata", Tmeta::idLumi().c_str(), &metaLumi);
		metaEvent = new typename Tmeta::typeEvent();
		_event_tree->Bronch("KEventMetadata", Tmeta::idEvent().c_str(), &metaEvent);
		std::sort(svMuonTriggerObjects.begin(), svMuonTriggerObjects.end());
	}
	virtual ~KMetadataProducer() {};

	inline void addHLT(const int idx, const std::string name, const int prescale)
	{
		KMetadataProducerBase::hltKappa2FWK.push_back(idx);
		hltNames.push_back(name);
		selectedHLT.push_back(name);
		hltPrescales.push_back(prescale);
	}

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		KMetadataProducerBase::hltKappa2FWK.clear();
		hltNames.clear();
		hltPrescales.clear();
		addHLT(0, "fail", 42);

		// For running over GEN step only:
		if (tagHLTResults.label() == "")
			return true;

		if (tagHLTResults.process() == "")
		{
			std::cout << "tagHLTResults is empty -> trying to determine the process name automatically:" << std::endl;

			edm::Handle<trigger::TriggerEvent> tmpTriggerEventHLT;

			const edm::ProcessHistory& processHistory(run.processHistory());
			for (edm::ProcessHistory::const_iterator it = processHistory.begin(); it != processHistory.end(); ++it)
			{
				std::cout << "\t" << it->processName();
				edm::ProcessConfiguration processConfiguration;
				if (processHistory.getConfigurationForProcess(it->processName(), processConfiguration))
				{
					edm::ParameterSet processPSet;
					if (edm::pset::Registry::instance()->getMapped(processConfiguration.parameterSetID(), processPSet))
					{
						if (processPSet.exists("hltTriggerSummaryAOD"))
						{
							tagHLTResults = edm::InputTag(tagHLTResults.label(), "", it->processName());
							std::cout << "*";
						}
					}
				}
				std::cout << std::endl;
			}
			std::cout << "* process with hltTriggerSummaryAOD" << std::endl;
			std::cout << "selected:" << tagHLTResults << std::endl;
			this->addProvenance(tagHLTResults.process(), "");
			if (tagHLTResults.process() == "")
				return true;
		}
		bool hltSetupChanged = false;
#ifdef NEWHLT
		if (!KMetadataProducerBase::hltConfig.init(run, setup, tagHLTResults.process(), hltSetupChanged))
			return fail(std::cout << "Invalid HLT process selected: " << tagHLTResults.process() << std::endl);
#else
		if (!KMetadataProducerBase::hltConfig.init(tagHLTResults.process()))
			return fail(std::cout << "Invalid HLT process selected: " << tagHLTResults.process() << std::endl);
#endif

		if (hltSetupChanged)
			std::cout << "HLT setup has changed...";

		int counter = 1;
		for (size_t i = 0; i < KMetadataProducerBase::hltConfig.size(); ++i)
		{
			const std::string &name = KMetadataProducerBase::hltConfig.triggerName(i);
			const int idx = KMetadataProducerBase::hltConfig.triggerIndex(name);
			if (verbosity > 1)
				std::cout << "Trigger: " << idx << " = ";
			if (!regexMatch(name, svHLTWhitelist, svHLTBlacklist))
				continue;
			if (verbosity > 0 || printHltList)
				std::cout << " => Adding trigger: " << name << " with ID: " << idx << " as " << counter
					<< " with placeholder prescale 0" << std::endl;
			if (KMetadataProducerBase::hltKappa2FWK.size() < 64)
			{
				addHLT(idx, name, 0);
				counter++;
			}
			else
			{
				std::cout << "The following HLT bits would have been selected:" << std::endl;
				unsigned int cntMatch = 0;
				for (size_t j = 0; j < hltConfig.size(); ++j)
				{
					if (regexMatch(hltConfig.triggerName(j), svHLTWhitelist, svHLTBlacklist))
					{
						std::cout << "\t" << (++cntMatch) << "\t" << hltConfig.triggerName(j) << std::endl;
					}
				}
				throw cms::Exception("Too many HLT bits selected!");
			}
		}
		if (verbosity > 0)
			std::cout << "Accepted number of trigger streams: " << counter - 1 << std::endl;

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

		metaLumi->hltNamesMuons.clear();
		KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap.clear();
		if (svMuonTriggerObjects.size() > 64)
		{
			std::cout << "Too many muon trigger objects selected (" << svMuonTriggerObjects.size() << ">64)!" << std::endl;
			throw cms::Exception("Too many muon trigger objects selected");
		}
		for (std::vector<std::string>::iterator it = svMuonTriggerObjects.begin(); it != svMuonTriggerObjects.end(); it++)
		{
			std::string filterName = *it;
			if (KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap.find(filterName) != KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap.end())
				throw cms::Exception("The muon trigger object '" + filterName + "' exists twice. Please remove one from your configuration!");
			if (metaLumi->hltNamesMuons.size() >= 64)
				throw cms::Exception("Too many muon trigger objects selected!");
			if (verbosity > 0)
				std::cout << filterName << "\n";
			metaLumi->hltNamesMuons.push_back(filterName);
			KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap[filterName] = metaLumi->hltNamesMuons.size() - 1;
			if (verbosity > 0)
				std::cout << "muon trigger object: " << (metaLumi->hltNamesMuons.size() - 1) << " = " << filterName << "\n";
		}

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
		if (!overrideHLTCheck)
			assert(!event.isRealData() || tagHLTResults.process() == "HLT");

		bool triggerPrescaleError = false;
		metaEvent->bitsHLT = 0;
		if (tagHLTResults.label() != "")
		{
			// set HLT trigger bits
			edm::Handle<edm::TriggerResults> hTriggerResults;
			event.getByLabel(tagHLTResults, hTriggerResults);

			bool hltFAIL = false;
			for (size_t i = 1; i < KMetadataProducerBase::hltKappa2FWK.size(); ++i)
			{
				const size_t idx = KMetadataProducerBase::hltKappa2FWK[i];
				if (hTriggerResults->accept(idx))
					metaEvent->bitsHLT |= ((unsigned long long)1 << i);
				hltFAIL = hltFAIL || hTriggerResults->error(idx);
			}
			if (hltFAIL)
				metaEvent->bitsHLT |= 1;

			// set and check trigger prescales
			for (size_t i = 1; i < KMetadataProducerBase::hltKappa2FWK.size(); ++i)
			{
				const std::string &name = metaLumi->hltNames[i];
				unsigned int prescale = 0;
#ifdef NEWHLT
				std::pair<int, int> prescale_L1_HLT = KMetadataProducerBase::hltConfig.prescaleValues(event, setup, name);
				if (prescale_L1_HLT.first < 0 || prescale_L1_HLT.second < 0)
					prescale = 0;
				else
					prescale = prescale_L1_HLT.first * prescale_L1_HLT.second;
#endif
				if (metaLumi->hltPrescales[i] == 0)
				{
					if (verbosity > 0 || printHltList)
						std::cout << " => Adding prescale for trigger: '" << name
							<< " with value: " << prescale << std::endl;
					metaLumi->hltPrescales[i] = prescale;
				}
				if (metaLumi->hltPrescales[i] != prescale)
				{
					if (this->verbosity > 0)
						std::cout << "!!!!!!!!!!! the prescale of " << name << " has changed with respect to the beginning of the luminosity section from " << metaLumi->hltPrescales[i] << " to " << prescale << std::endl;
					triggerPrescaleError = true;
				}
			}
		}
		else
		{
			for (size_t i = 1; i < KMetadataProducerBase::hltKappa2FWK.size(); ++i)
				metaLumi->hltPrescales[i] = 1;
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
			metaEvent->bitsUserFlags |= KEFPhysicsDeclared;

		// Detection of unexpected trigger prescale change
		if (triggerPrescaleError)
			metaLumi->bitsUserFlags |= KLFPrescaleError;

		if (tagNoiseHCAL.label() != "")
		{
			// HCAL noise
			edm::Handle<HcalNoiseSummary> noiseSummary;
			event.getByLabel(tagNoiseHCAL, noiseSummary);
			if (noiseSummary->passLooseNoiseFilter())
				metaEvent->bitsUserFlags |= KEFHCALLooseNoise;
			if (noiseSummary->passTightNoiseFilter())
				metaEvent->bitsUserFlags |= KEFHCALTightNoise;
		}

		edm::Handle<std::vector<edm::ErrorSummaryEntry> > errorsAndWarnings;

		if (tagErrorsAndWarnings.label() != "" && event.getByLabel(tagErrorsAndWarnings, errorsAndWarnings))
		{
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
					if (it->severity.getLevel() == edm::ELseverityLevel::ELsev_error || it->severity.getLevel() == edm::ELseverityLevel::ELsev_error2)
						metaEvent->bitsUserFlags |= KEFRecoErrors;
					if (it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning || it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning2)
						metaEvent->bitsUserFlags |= KEFRecoWarnings;

					if (printErrorsAndWarnings && (it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning || it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning2))
						std::cout << "warning: " << it->category << ", " << it->module << ", " << it->count << "\n";
					if (printErrorsAndWarnings && (it->severity.getLevel() == edm::ELseverityLevel::ELsev_error || it->severity.getLevel() == edm::ELseverityLevel::ELsev_error2))
						std::cout << "error: " << it->category << ", " << it->module << ", " << it->count << "\n";
				}
			}
		}

		return true;
	}

	static std::map<std::string, int> muonTriggerObjectBitMap;

protected:
	std::string tauDiscrProcessName;
	edm::InputTag tagL1Results, tagHLTResults;
	std::vector<std::string> svHLTWhitelist, svHLTBlacklist;

	std::vector<std::string> svMuonTriggerObjects;

	edm::InputTag tagNoiseHCAL, tagHLTrigger;
	edm::InputTag tagErrorsAndWarnings;
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

template<typename Tmeta>
std::map<std::string, int> KMetadataProducer<Tmeta>::muonTriggerObjectBitMap;

#endif

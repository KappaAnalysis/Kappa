#ifndef KAPPA_METADATAPRODUCER_H
#define KAPPA_METADATAPRODUCER_H

#include <vector>
#include <algorithm>

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
#include "DataFormats/TauReco/interface/CaloTauDiscriminator.h"
#include "DataFormats/TauReco/interface/PFTauDiscriminator.h"

#include "DataFormats/HLTReco/interface/TriggerEvent.h"

#include "FWCore/MessageLogger/interface/ELseverityLevel.h"
#include "FWCore/MessageLogger/interface/ErrorSummaryEntry.h"


#define NEWHLT

// real data
struct KMetadata_Product
{
	typedef KLumiMetadata typeLumi;
	typedef KEventMetadata typeEvent;
	static const std::string idLumi() { return "KLumiMetadata"; };
	static const std::string idEvent() { return "KEventMetadata"; };
};

template<typename Tmeta>
class KMetadataProducer : public KBaseProducerWP
{
public:
	KMetadataProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseProducerWP(cfg, _event_tree, _lumi_tree, "KMetadata"),
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
		printHltList(cfg.getParameter<bool>("printHltList"))
	{
		metaLumi = new typename Tmeta::typeLumi();
		_lumi_tree->Bronch("KLumiMetadata", Tmeta::idLumi().c_str(), &metaLumi);
		metaEvent = new typename Tmeta::typeEvent();
		_event_tree->Bronch("KEventMetadata", Tmeta::idEvent().c_str(), &metaEvent);
	}
	virtual ~KMetadataProducer() {};

	inline void addHLT(const int idx, const std::string name, const int prescale)
	{
		hltKappa2FWK.push_back(idx);
		hltNames.push_back(name);
		hltPrescales.push_back(prescale);
	}

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		hltKappa2FWK.clear();
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
			if (run.run() != 1)
			{
				std::cout << metaLumi->nRun << "\n";
				std::cout << "this run seems to be data and the trigger should always be 'HLT' in data -> forcing 'HLT'" << std::endl;
				tagHLTResults = edm::InputTag(tagHLTResults.label(), "", "HLT");
			}

			std::cout << "selected:" << tagHLTResults << std::endl;
			this->addProvenance(tagHLTResults.process(), "");
			if (tagHLTResults.process() == "")
				return true;
		}
		bool hltSetupChanged = false;
#ifdef NEWHLT
		if (!hltConfig.init(run, setup, tagHLTResults.process(), hltSetupChanged))
			return fail(std::cout << "Invalid HLT process selected: " << tagHLTResults.process() << std::endl);
#else
		if (!hltConfig.init(tagHLTResults.process()))
			return fail(std::cout << "Invalid HLT process selected: " << tagHLTResults.process() << std::endl);
#endif

		if (hltSetupChanged)
			std::cout << "HLT setup has changed...";

		int counter = 1;
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
					<< " with placeholder prescale 1" << std::endl;
			if (hltKappa2FWK.size() < 64)
			{
				addHLT(idx, name, 1);
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
		firstEventInLumi = true;

		metaLumi = &(metaLumiMap[std::pair<run_id, lumi_id>(lumiBlock.run(), lumiBlock.luminosityBlock())]);
		metaLumi->nRun = lumiBlock.run();
		metaLumi->nLumi = lumiBlock.luminosityBlock();

		metaLumi->hltNames = hltNames;
		metaLumi->hltPrescales = hltPrescales;

		metaLumi->hltNamesMuons.clear();
		KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap.clear();
		for (std::vector<std::string>::iterator it = svMuonTriggerObjects.begin(); it != svMuonTriggerObjects.end(); it++)
		{
			std::string filterName = *it;
			std::cout << filterName << "\n";
			metaLumi->hltNamesMuons.push_back(filterName);
			KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap[filterName] = metaLumi->hltNamesMuons.size() - 1;
			std::cout << "muon trigger object: " << (metaLumi->hltNamesMuons.size() - 1) << " = " << filterName << "\n";
		}

		// Clear tau discriminator maps, they will be refilled by
		// first event in lumi, see onEvent() below.
		KMetadataProducer<KMetadata_Product>::caloTauDiscriminatorBitMap.clear();
		KMetadataProducer<KMetadata_Product>::pfTauDiscriminatorBitMap.clear();

		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
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

		if ((firstEventInLumi))
		{
			// Set HLT prescales
			if (tagHLTResults.label() != "")
			{
				for (size_t i = 1; i < hltKappa2FWK.size(); ++i)
				{
					const std::string &name = metaLumi->hltNames[i];
					int prescale = 0, prescaleSet = -1;
#ifdef NEWHLT
					prescaleSet = hltConfig.prescaleSet(event, setup);
					if (prescaleSet != -1)
						prescale = hltConfig.prescaleValue(event, setup, name);
#endif
					if (verbosity > 0 || printHltList)
						std::cout << " => Adding prescale for trigger: '" << name
							<< "' from prescale set: " << prescaleSet
							<< " with value: " << prescale << std::endl;
					metaLumi->hltPrescales[i] = prescale;
				}
			}

			// Build tau discriminator maps
			std::vector<edm::Handle<reco::CaloTauDiscriminator> > caloTauDiscriminators;
			event.getManyByType(caloTauDiscriminators);
			assert(metaLumi->discrTau.empty());
			for(unsigned int i = 0; i < caloTauDiscriminators.size(); ++i)
			{
				const std::string& name = caloTauDiscriminators[i].provenance()->moduleLabel();
				metaLumi->discrTau.push_back(name);
				KMetadataProducer<KMetadata_Product>::caloTauDiscriminatorBitMap[name] = metaLumi->discrTau.size() - 1;
				std::cout << "CaloTau discriminator " << i << ": " << name << std::endl;
			}

			std::vector<edm::Handle<reco::PFTauDiscriminator> > pfTauDiscriminators;
			event.getManyByType(pfTauDiscriminators);
			assert(metaLumi->discrTauPF.empty());
			for(unsigned int i = 0; i < pfTauDiscriminators.size(); ++i)
			{
				const std::string& name = pfTauDiscriminators[i].provenance()->moduleLabel();
				metaLumi->discrTauPF.push_back(name);
				KMetadataProducer<KMetadata_Product>::pfTauDiscriminatorBitMap[name] = metaLumi->discrTauPF.size();
				std::cout << "PFTau discriminator " << i << ": " << name << std::endl;
			}

			firstEventInLumi = false;
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

		edm::Handle<std::vector<edm::ErrorSummaryEntry> > errorsAndWarnings;

		if (tagErrorsAndWarnings.label() != "" && event.getByLabel(tagErrorsAndWarnings, errorsAndWarnings))
		{
			if (errorsAndWarnings.failedToGet())
			{
				metaEvent->bitsUserFlags |= KFlagRecoErrors;
				metaEvent->bitsUserFlags |= KFlagRecoWarnings;
			}
			else
			{
				for (std::vector<edm::ErrorSummaryEntry>::const_iterator it = errorsAndWarnings->begin(); it != errorsAndWarnings->end(); it++)
				{
					if (avoidEaWCategories.size() != 0 && std::find(avoidEaWCategories.begin(), avoidEaWCategories.end(), it->category) != avoidEaWCategories.end())
						continue;
					if (it->severity.getLevel() == edm::ELseverityLevel::ELsev_error || it->severity.getLevel() == edm::ELseverityLevel::ELsev_error2)
						metaEvent->bitsUserFlags |= KFlagRecoErrors;
					if (it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning || it->severity.getLevel() == edm::ELseverityLevel::ELsev_warning2)
						metaEvent->bitsUserFlags |= KFlagRecoWarnings;

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

	typedef std::map<std::string, unsigned int> TauDiscriminatorMap;
	static TauDiscriminatorMap caloTauDiscriminatorBitMap;
	static TauDiscriminatorMap pfTauDiscriminatorBitMap;

protected:
	bool firstEventInLumi;
	edm::InputTag tagL1Results, tagHLTResults;
	std::vector<std::string> svHLTWhitelist, svHLTBlacklist;
	std::vector<std::string> svMuonTriggerObjects;
	HLTConfigProvider hltConfig;
	std::vector<size_t> hltKappa2FWK;

	edm::InputTag tagNoiseHCAL, tagHLTrigger;
	edm::InputTag tagErrorsAndWarnings;
	std::vector<std::string> avoidEaWCategories;
	bool printErrorsAndWarnings;
	bool printHltList;

	std::vector<std::string> hltNames;
	std::vector<unsigned int> hltPrescales;

	typename Tmeta::typeLumi *metaLumi;
	typename Tmeta::typeEvent *metaEvent;

	std::map<std::pair<run_id, lumi_id>, typename Tmeta::typeLumi> metaLumiMap;
};

template<typename Tmeta>
std::map<std::string, int> KMetadataProducer<Tmeta>::muonTriggerObjectBitMap;

template<typename Tmeta>
typename KMetadataProducer<Tmeta>::TauDiscriminatorMap KMetadataProducer<Tmeta>::caloTauDiscriminatorBitMap;
template<typename Tmeta>
typename KMetadataProducer<Tmeta>::TauDiscriminatorMap KMetadataProducer<Tmeta>::pfTauDiscriminatorBitMap;

#endif

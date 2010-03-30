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

#include <bitset>

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
		sHLTFilter(cfg.getParameter<std::string>("hltFilter")),

		tagNoiseHCAL(cfg.getParameter<edm::InputTag>("noiseHCAL")),
		tagPVs(cfg.getParameter<edm::InputTag>("srcPVs"))
	{
		metaLumi = new typename Tmeta::typeLumi();
		_lumi_tree->Bronch("KLumiMetadata", Tmeta::idLumi().c_str(), &metaLumi);
		metaEvent = new typename Tmeta::typeEvent();
		_event_tree->Bronch("KEventMetadata", Tmeta::idEvent().c_str(), &metaEvent);
	}
	virtual ~KMetadataProducer() {};

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		metaLumi = &(metaLumiMap[std::pair<unsigned int, unsigned int>(
			(unsigned int)lumiBlock.run(), (unsigned int)lumiBlock.luminosityBlock())]);
		metaLumi->nRun = lumiBlock.run();
		metaLumi->nLumi = lumiBlock.luminosityBlock();

		// Read trigger infos
		if (!hltConfig.init(tagHLTResults.process()))
			return fail(std::cout << "Invalid HLT process selected: " << sHLTProcess << std::endl);
		int counter = 1;
		hltK2FWK.clear();
		hltK2FWK.push_back(0);
		metaLumi->hltNames.push_back("fail");

		for (unsigned int i = 0; i < hltConfig.size(); ++i)
		{
			const std::string &name = hltConfig.triggerName(i);
			const int idx = hltConfig.triggerIndex(name);
			if (verbosity > 1)
				std::cout << "Trigger: " << idx << " = ";
			if (!regexMatch(name, sHLTFilter))
				continue;
			if (verbosity > 0)
				std::cout << " => Adding trigger: " << name << " with ID: " << idx << " as " << counter << std::endl;
			hltK2FWK.push_back(idx);
			metaLumi->hltNames.push_back(name);
			counter++;
		}
		if (verbosity > 0)
			std::cout << "Accepted number of trigger streams: " << counter - 1 << std::endl;
		if (hltK2FWK.size() > 64)
			std::cout << "Too many HLT bits selected!" << std::endl;

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

			bool hltOK = true;
			std::bitset<64> tmpBits;
			for (unsigned int i = 1; i < hltK2FWK.size(); ++i)
			{
				const int idx = hltK2FWK[i];
				tmpBits[i] = hTriggerResults->accept(idx);
				hltOK &= hTriggerResults->error(idx);
			}
			tmpBits[0] = !hltOK;
			metaEvent->bitsHLT = tmpBits.to_ulong();
		}

		// Set L1 trigger bits
		metaEvent->bitsL1 = 0;
		if (tagL1Results.label() != "")
		{
			edm::Handle<L1GlobalTriggerReadoutRecord> hL1Result;
			event.getByLabel(tagL1Results, hL1Result);
			for (size_t i = 0; i < hL1Result->technicalTriggerWord().size(); ++i)
				if (hL1Result->technicalTriggerWord().at(i))
					metaEvent->bitsL1 |= ((long long)1 << i);
		}

		// User flags
		//  * HCAL noise
		metaEvent->bitsUserFlags = 0;
		if (tagNoiseHCAL.label() != "")
		{
			edm::Handle<HcalNoiseSummary> noiseSummary;
			event.getByLabel(tagNoiseHCAL, noiseSummary);
			if (noiseSummary->passLooseNoiseFilter())
				metaEvent->bitsUserFlags |= KFlagHCALLooseNoise;
			if (noiseSummary->passTightNoiseFilter())
				metaEvent->bitsUserFlags |= KFlagHCALTightNoise;
		}

		return true;
	}

protected:
	edm::InputTag tagL1Results, tagHLTResults;
	std::string sHLTProcess;
	std::string sHLTFilter;
	HLTConfigProvider hltConfig;
	std::vector<int> hltK2FWK;

	edm::InputTag tagNoiseHCAL;
	edm::InputTag tagPVs;

	typename Tmeta::typeLumi *metaLumi;
	typename Tmeta::typeEvent *metaEvent;

	std::map<std::pair<unsigned int, unsigned int>, typename Tmeta::typeLumi> metaLumiMap;
};

#endif

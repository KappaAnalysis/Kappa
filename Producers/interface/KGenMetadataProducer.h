#ifndef KAPPA_GENMETADATAPRODUCER_H
#define KAPPA_GENMETADATAPRODUCER_H

#include "KMetadataProducer.h"
#include <SimDataFormats/GeneratorProducts/interface/GenRunInfoProduct.h>
#include <SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h>
#include <SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h>

// MC data
struct KGenMetadata_Product
{
	typedef KGenLumiMetadata typeLumi;
	typedef KGenEventMetadata typeEvent;
	static const std::string idLumi() { return "KGenLumiMetadata"; };
	static const std::string idEvent() { return "KGenEventMetadata"; };
};

template<typename Tmeta>
class KGenMetadataProducer : public KMetadataProducer<Tmeta>
{
public:
	KGenMetadataProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KMetadataProducer<Tmeta>(cfg, _event_tree, _lumi_tree),
		ignoreExtXSec(cfg.getParameter<bool>("ignoreExtXSec")),
		forceLumi(cfg.getParameter<int>("forceLumi")),
		tagSource(cfg.getParameter<edm::InputTag>("genSource")),
		puInfoSource(cfg.getParameter<edm::InputTag>("pileUpInfoSource")) {}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KMetadataProducer<Tmeta>::onLumi(lumiBlock, setup))
			return false;
		if (forceLumi > 0)
			this->metaLumi->nLumi = forceLumi;

		// Read generator infos
		edm::Handle<GenRunInfoProduct> hGenInfo;
		lumiBlock.getRun().getByLabel(tagSource, hGenInfo);

		const bool invalidGenInfo = !hGenInfo.isValid();
		this->metaLumi->filterEff = invalidGenInfo ? -1 : hGenInfo->filterEfficiency();
		this->metaLumi->xSectionInt = invalidGenInfo ? -1 : hGenInfo->internalXSec().value();
		this->metaLumi->xSectionExt = invalidGenInfo ? -1 : hGenInfo->externalXSecLO().value();
		if (ignoreExtXSec)
			this->metaLumi->xSectionExt = -1;
		if (invalidGenInfo)
			return KBaseProducer::fail(std::cout << "Invalid generator info" << std::endl);
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KMetadataProducer<Tmeta>::onEvent(event, setup))
			return false;
		if (forceLumi > 0)
			this->metaEvent->nLumi = forceLumi;

		// Get generator event info:
		edm::Handle<GenEventInfoProduct> hEventInfo;
		event.getByLabel(tagSource, hEventInfo);

		this->metaEvent->binValue = -1;
		if (hEventInfo->binningValues().size() > 0)
			this->metaEvent->binValue = hEventInfo->binningValues()[0];

		this->metaEvent->weight = hEventInfo->weight();
		this->metaEvent->alphaQCD = hEventInfo->alphaQCD();
		//metaEvent->alphaQED = hEventInfo->alphaQED();

		// Get PU infos
		this->metaEvent->numPUInteractionsM2 = 0;
		this->metaEvent->numPUInteractionsM1 = 0;
		this->metaEvent->numPUInteractions0 = 0;
		this->metaEvent->numPUInteractionsP1 = 0;
		this->metaEvent->numPUInteractionsP2 = 0;
		edm::Handle<std::vector<PileupSummaryInfo> > puHandles;
		if (event.getByLabel(puInfoSource, puHandles) && puHandles.isValid())
		{
			for (std::vector<PileupSummaryInfo>::const_iterator it = puHandles->begin(); it != puHandles->end(); ++it)
			{
				unsigned char nPU = (unsigned char)std::min(255, it->getPU_NumInteractions());
				if (it->getBunchCrossing() == -2)
					this->metaEvent->numPUInteractionsM2 = nPU;
				else if (it->getBunchCrossing() == -1)
					this->metaEvent->numPUInteractionsM1 = nPU;
				else if (it->getBunchCrossing() == 0)
					this->metaEvent->numPUInteractions0 = nPU;
				else if (it->getBunchCrossing() == 1)
					this->metaEvent->numPUInteractionsP1 = nPU;
				else if (it->getBunchCrossing() == 2)
					this->metaEvent->numPUInteractionsP2 = nPU;
			}
		}
		else
		{
			// in some versions of CMSSW it's not a vector:
			edm::Handle<PileupSummaryInfo> puHandle;
			if (event.getByLabel(puInfoSource, puHandle) && puHandle.isValid())
				this->metaEvent->numPUInteractions0 = (unsigned char)std::min(255, puHandle->getPU_NumInteractions());
		}

		return true;
	}

protected:
	bool ignoreExtXSec;
	int forceLumi;
	edm::InputTag tagSource, puInfoSource;
};

#endif

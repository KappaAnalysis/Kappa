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

		// We write the PileUp information into the nBX field since it is
		// unused anyway in Monte Carlo. This is a small hack and it will
		// be done right when we make the next dictionary change. See also
		// the dictchanges branch.
		edm::Handle<PileupSummaryInfo> puHandle;
		if (event.getByLabel(puInfoSource, puHandle))
			this->metaEvent->nBX = puHandle->getPU_NumInteractions();
		else
			this->metaEvent->nBX = 0;

		return true;
	}

protected:
	bool ignoreExtXSec;
	int forceLumi;
	edm::InputTag tagSource, puInfoSource;
};

#endif

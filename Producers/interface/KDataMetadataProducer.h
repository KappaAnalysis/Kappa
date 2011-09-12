#ifndef KAPPA_DATAMETADATAPRODUCER_H
#define KAPPA_DATAMETADATAPRODUCER_H

#include "KMetadataProducer.h"
#include <DataFormats/Luminosity/interface/LumiSummary.h>
#include <DataFormats/Common/interface/ConditionsInEdm.h>

// MC data
struct KDataMetadata_Product
{
	typedef KDataLumiMetadata typeLumi;
	typedef KEventMetadata typeEvent;
	static const std::string idLumi() { return "KDataLumiMetadata"; };
	static const std::string idEvent() { return "KEventMetadata"; };
};

template<typename Tmeta>
class KDataMetadataProducer : public KMetadataProducer<Tmeta>
{
public:
	KDataMetadataProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KMetadataProducer<Tmeta>(cfg, _event_tree, _lumi_tree),
		currentRun(0),
		lumiSource(cfg.getParameter<edm::InputTag>("lumiSource")) {}

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		edm::Handle<edm::ConditionsInRunBlock> condInRunBlock;
		if (!run.getByType(condInRunBlock))
			throw cms::Exception("The ConditionsInRunBlock object could not be found!");

		if (condInRunBlock.isValid())
			currentRun = condInRunBlock->lhcFillNumber;
		else
			currentRun = 0;

		return KMetadataProducer<Tmeta>::onRun(run, setup);
	}
	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KMetadataProducer<Tmeta>::onLumi(lumiBlock, setup))
			return false;

		// Read luminosity infos
		edm::Handle<LumiSummary> hLumiSummary;
		lumiBlock.getByLabel(lumiSource, hLumiSummary);

		this->metaLumi->avgInsDelLumi = hLumiSummary->avgInsDelLumi();
		this->metaLumi->avgInsDelLumiErr = hLumiSummary->avgInsDelLumiErr();
		this->metaLumi->avgInsRecLumi = hLumiSummary->avgInsRecLumi();
		this->metaLumi->avgInsRecLumiErr = hLumiSummary->avgInsRecLumiErr();
		this->metaLumi->deadFrac = hLumiSummary->deadFrac();
		this->metaLumi->lumiSectionLength = hLumiSummary->lumiSectionLength();
		this->metaLumi->lumiSecQual = hLumiSummary->lumiSecQual();

		this->metaLumi->nFill = currentRun;

		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		return KMetadataProducer<Tmeta>::onEvent(event, setup);
	}

protected:
	short currentRun;
	edm::InputTag lumiSource;
};

#endif

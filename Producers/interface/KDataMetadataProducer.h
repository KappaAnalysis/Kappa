#ifndef KAPPA_DATAMETADATAPRODUCER_H
#define KAPPA_DATAMETADATAPRODUCER_H

#include "KMetadataProducer.h"
#include <DataFormats/Luminosity/interface/LumiSummary.h>

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
		lumiSource(cfg.getParameter<edm::InputTag>("lumiSource")) {}

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

		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		return KMetadataProducer<Tmeta>::onEvent(event, setup);
	}

protected:
	edm::InputTag lumiSource;
};

#endif

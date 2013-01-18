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
		currentRun(0),
		lumiSource(cfg.getParameter<edm::InputTag>("lumiSource")) {}

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		currentRun = run.run();
		return KMetadataProducer<Tmeta>::onRun(run, setup);
	}
	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KMetadataProducer<Tmeta>::onLumi(lumiBlock, setup))
			return false;

		// Read luminosity infos
		edm::Handle<LumiSummary> hLumiSummary;
		if (lumiBlock.getByLabel(lumiSource, hLumiSummary))
		{
			this->metaLumi->avgInsDelLumi = hLumiSummary->avgInsDelLumi();
			this->metaLumi->avgInsDelLumiErr = hLumiSummary->avgInsDelLumiErr();
			this->metaLumi->avgInsRecLumi = hLumiSummary->avgInsRecLumi();
			this->metaLumi->avgInsRecLumiErr = hLumiSummary->avgInsRecLumiErr();
			this->metaLumi->deadFrac = hLumiSummary->deadFrac();
			this->metaLumi->lumiSectionLength = hLumiSummary->lumiSectionLength();
			this->metaLumi->lumiSecQual = hLumiSummary->lumiSecQual();
		}
		else
		{
			/*
				if the luminosity information is not available, you can add the following module to your path:
					process.lumiProducer=cms.EDProducer("LumiProducer",
						connect=cms.string('frontier://LumiProd/CMS_LUMI_PROD'),
					)
			*/
			edm::LogWarning("KDataMetadataProducer") << "Warning: No edm lumi information found! All lumi values are set to zero.";
			this->metaLumi->avgInsDelLumi = 0.0f;
			this->metaLumi->avgInsDelLumiErr = 0.0f;
			this->metaLumi->avgInsRecLumi = 0.0f;
			this->metaLumi->avgInsRecLumiErr = 0.0f;
			this->metaLumi->deadFrac = 0.0f;
			this->metaLumi->lumiSectionLength = 0;
			this->metaLumi->lumiSecQual = 0;
		}

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

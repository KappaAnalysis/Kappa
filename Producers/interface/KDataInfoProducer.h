//- Copyright (c) 2011 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_DATAINFOPRODUCER_H
#define KAPPA_DATAINFOPRODUCER_H

#include <DataFormats/Luminosity/interface/LumiSummary.h>
#include "KInfoProducer.h"


// MC data
struct KDataInfo_Product
{
	typedef KDataLumiInfo typeLumi;
	typedef KEventInfo typeEvent;
	static const std::string idLumi() { return "KDataLumiInfo"; };
	static const std::string idEvent() { return "KEventInfo"; };
};

template<typename Tmeta>
class KDataInfoProducer : public KInfoProducer<Tmeta>
{
public:
	KDataInfoProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KInfoProducer<Tmeta>(cfg, _event_tree, _lumi_tree),
		currentRun(0),
		lumiSource(cfg.getParameter<edm::InputTag>("lumiSource")),
		isEmbedded(cfg.getParameter<bool>("isEmbedded")) {}

	static const std::string getLabel() { return "DataInfo"; }

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		currentRun = run.run();
		return KInfoProducer<Tmeta>::onRun(run, setup);
	}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KInfoProducer<Tmeta>::onLumi(lumiBlock, setup))
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
			edm::LogWarning("KDataInfoProducer") << "Warning: No edm lumi information found! All lumi values are set to zero.";
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

		// get extra information for pf embedded samples
		if (isEmbedded)
		{
			edm::Handle<GenFilterInfo> hGenFilterInfo;
			event.getByLabel(edm::InputTag("generator", "minVisPtFilter", "EmbeddedRECO"), hGenFilterInfo);
			this->metaEvent->minVisPtFilterWeight = hGenFilterInfo->filterEfficiency();
		}
		else this->metaEvent->minVisPtFilterWeight = 1.0f;
		return KInfoProducer<Tmeta>::onEvent(event, setup);
	}

protected:
	short currentRun;
	edm::InputTag lumiSource;
	bool isEmbedded;
};

#endif

//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_GENINFOPRODUCER_H
#define KAPPA_GENINFOPRODUCER_H

#include <SimDataFormats/GeneratorProducts/interface/GenRunInfoProduct.h>
#include <SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h>
#include <SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h>
#include <SimDataFormats/GeneratorProducts/interface/HepMCProduct.h>
#include <SimDataFormats/GeneratorProducts/interface/GenFilterInfo.h>
#include "SimDataFormats/GeneratorProducts/interface/LHEEventProduct.h"
#include <FWCore/Framework/interface/EDProducer.h>

#include "KInfoProducer.h"


// MC data
struct KGenInfo_Product
{
	typedef KGenLumiInfo typeLumi;
	typedef KGenEventInfo typeEvent;
	static const std::string idLumi() { return "KGenLumiInfo"; };
	static const std::string idEvent() { return "KGenEventInfo"; };
};

template<typename Tmeta>
class KGenInfoProducer : public KInfoProducer<Tmeta>
{
public:
	KGenInfoProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KInfoProducer<Tmeta>(cfg, _event_tree, _lumi_tree, std::forward<edm::ConsumesCollector>(consumescollector)),
		ignoreExtXSec(cfg.getParameter<bool>("ignoreExtXSec")),
		forceLumi(cfg.getParameter<int>("forceLumi")),
		binningMode(cfg.getParameter<std::string>("binningMode")),
		tagSource(cfg.getParameter<edm::InputTag>("genSource")),
		puInfoSource(cfg.getParameter<edm::InputTag>("pileUpInfoSource")),
		lheSource(cfg.getParameter<edm::InputTag>("lheSource"))
		{
			consumescollector.consumes<GenRunInfoProduct, edm::InRun>(tagSource);
			consumescollector.consumes<GenEventInfoProduct>(tagSource);
			consumescollector.consumes<LHEEventProduct>(lheSource);
			consumescollector.consumes<std::vector<PileupSummaryInfo>>(puInfoSource);
		}

	static const std::string getLabel() { return "GenInfo"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KInfoProducer<Tmeta>::onLumi(lumiBlock, setup))
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
		if (!KInfoProducer<Tmeta>::onEvent(event, setup))
			return false;
		if (forceLumi > 0)
			this->metaEvent->nLumi = forceLumi;

		// Get generator level HT
		edm::Handle<LHEEventProduct> lheEventProduct;
		double lheHt = 0.;
		if (event.getByLabel(lheSource, lheEventProduct) && lheEventProduct.isValid())
		{
			const lhef::HEPEUP& lheEvent = lheEventProduct->hepeup();
			std::vector<lhef::HEPEUP::FiveVector> lheParticles = lheEvent.PUP;
			for ( size_t idxParticle = 0; idxParticle < lheParticles.size(); ++idxParticle ) {
				int id = std::abs(lheEvent.IDUP[idxParticle]);
				int status = lheEvent.ISTUP[idxParticle];
				if ( status == 1 && ((id >= 1 && id <= 6) || id == 21) ) { // quarks and gluons
					lheHt += std::sqrt(std::pow(lheParticles[idxParticle][0], 2.) + std::pow(lheParticles[idxParticle][1], 2.));
				}
			}
		}
		
		// Get generator event info:
		edm::Handle<GenEventInfoProduct> hEventInfo;
		event.getByLabel(tagSource, hEventInfo);

		this->metaEvent->binValue = -1;
		if (hEventInfo->binningValues().size() > 0)
		{
			this->metaEvent->binValue = hEventInfo->binningValues()[0];
		}
		else
		{
			if (binningMode == "ht")
			{
				this->metaEvent->binValue = lheHt;
			}
		}

		this->metaEvent->weight = hEventInfo->weight();
		this->metaEvent->alphaQCD = hEventInfo->alphaQCD();
		//metaEvent->alphaQED = hEventInfo->alphaQED();

		// Get PU infos
		this->metaEvent->nPUm2 = 0;
		this->metaEvent->nPUm1 = 0;
		this->metaEvent->nPU   = 0;
		this->metaEvent->nPUp1 = 0;
		this->metaEvent->nPUp2 = 0;
		edm::Handle<std::vector<PileupSummaryInfo> > puHandles;
		if (event.getByLabel(puInfoSource, puHandles) && puHandles.isValid())
		{
			for (std::vector<PileupSummaryInfo>::const_iterator it = puHandles->begin(); it != puHandles->end(); ++it)
			{
				unsigned char nPU = (unsigned char)std::min(255, it->getPU_NumInteractions());
				if (it->getBunchCrossing() == -2)
					this->metaEvent->nPUm2 = nPU;
				else if (it->getBunchCrossing() == -1)
					this->metaEvent->nPUm1 = nPU;
				else if (it->getBunchCrossing() == 0)
					this->metaEvent->nPU = nPU;
				else if (it->getBunchCrossing() == 1)
					this->metaEvent->nPUp1 = nPU;
				else if (it->getBunchCrossing() == 2)
					this->metaEvent->nPUp2 = nPU;

				this->metaEvent->nPUMean = it->getTrueNumInteractions();  // remove this line to compile with CMSSW 4.2.7 or earlier
			}
		}
		else
		{
			// in some versions of CMSSW it's not a vector:
			edm::Handle<PileupSummaryInfo> puHandle;
			if (event.getByLabel(puInfoSource, puHandle) && puHandle.isValid())
				this->metaEvent->nPU = (unsigned char)std::min(255, puHandle->getPU_NumInteractions());
		}

		return true;
	}

protected:
	bool ignoreExtXSec;
	int forceLumi;
	std::string binningMode;
	edm::InputTag tagSource, puInfoSource, lheSource;
};

template<typename Tmeta>
class KHepMCInfoProducer : public KInfoProducer<Tmeta>
{
public:
	KHepMCInfoProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KInfoProducer<Tmeta>(cfg, _event_tree, _lumi_tree, std::forward<edm::ConsumesCollector>(consumescollector)),
		forceXSec(cfg.getParameter<double>("forceXSec")),
		forceLumi(cfg.getParameter<int>("forceLumi")),
		tagSource(cfg.getParameter<edm::InputTag>("genSource"))
		{
		    consumescollector.consumes<edm::HepMCProduct>(tagSource);
		}

	static const std::string getLabel() { return "HepMCInfo"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KInfoProducer<Tmeta>::onLumi(lumiBlock, setup))
			return false;
		if (forceLumi > 0)
			this->metaLumi->nLumi = forceLumi;
		this->metaLumi->filterEff = 1;
		this->metaLumi->xSectionInt = forceXSec;
		this->metaLumi->xSectionExt = forceXSec;
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KInfoProducer<Tmeta>::onEvent(event, setup))
			return false;
		if (forceLumi > 0)
			this->metaEvent->nLumi = forceLumi;

		// Get generator event info:
		edm::Handle<edm::HepMCProduct> hEventInfo;
		event.getByLabel(tagSource, hEventInfo);
		const HepMC::GenEvent &hepmc = hEventInfo->getHepMCData();

		this->metaEvent->binValue = hepmc.event_scale();

		this->metaEvent->weight = 1;
		for (size_t idx = 0; idx < hepmc.weights().size(); ++idx)
			this->metaEvent->weight *= hepmc.weights()[idx];
		this->metaEvent->alphaQCD = hepmc.alphaQCD();
		//metaEvent->alphaQED = hEventInfo->alphaQED();

		// Get PU infos
		this->metaEvent->nPUm2 = 0;
		this->metaEvent->nPUm1 = 0;
		this->metaEvent->nPU   = 0;
		this->metaEvent->nPUp1 = 0;
		this->metaEvent->nPUp2 = 0;

		return true;
	}

protected:
	double forceXSec;
	int forceLumi;
	edm::InputTag tagSource;
};

#endif

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
#include "SimDataFormats/GeneratorProducts/interface/LHERunInfoProduct.h"
#include <FWCore/Framework/interface/EDProducer.h>

#include "KInfoProducer.h"

#include <boost/regex.hpp>
#include <boost/algorithm/string/replace.hpp>
#include <boost/algorithm/string/trim.hpp>

#include <numeric>


// MC data
struct KGenInfo_Product
{
	typedef KLumiInfo typeLumi;
	typedef KGenRunInfo typeRun;
	typedef KGenEventInfo typeEvent;
	static const std::string idRun() { return "KGenRunInfo"; };
	static const std::string idLumi() { return "KLumiInfo"; };
	static const std::string idEvent() { return "KGenEventInfo"; };
};

template<typename Tmeta>
class KGenInfoProducer : public KInfoProducer<Tmeta>
{
public:
	KGenInfoProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KInfoProducer<Tmeta>(cfg, _event_tree, _lumi_tree, _run_tree, std::forward<edm::ConsumesCollector>(consumescollector)),
		ignoreExtXSec(cfg.getParameter<bool>("ignoreExtXSec")),
		forceLumi(cfg.getParameter<int>("forceLumi")),
		binningMode(cfg.getParameter<std::string>("binningMode")),
		tagSource(cfg.getParameter<edm::InputTag>("genSource")),
		puInfoSource(cfg.getParameter<edm::InputTag>("pileUpInfoSource")),
		lheSource(cfg.getParameter<edm::InputTag>("lheSource")),
		runInfo(cfg.getParameter<edm::InputTag>("lheSource")),
		lheWeightRegexes(cfg.getParameter<std::vector<std::string>>("lheWeightNames"))
		{
			this->tokenGenRunInfo = consumescollector.consumes<GenRunInfoProduct, edm::InRun>(tagSource);
			this->tokenSource = consumescollector.consumes<GenEventInfoProduct>(tagSource);
			this->tokenLhe = consumescollector.consumes<LHEEventProduct>(lheSource);
			this->tokenPuInfo = consumescollector.consumes<std::vector<PileupSummaryInfo>>(puInfoSource);
			//this->tokenLHERunInfo = consumescollector.consumes<LHERunInfoProduct, edm::InRun>(runInfo);
			this->tokenRunInfo = consumescollector.consumes<LHERunInfoProduct, edm::InRun>(runInfo);

			genEventInfoMetadata = new KGenEventInfoMetadata();
			_lumi_tree->Bronch("genEventInfoMetadata", "KGenEventInfoMetadata", &genEventInfoMetadata);

			metaRun = new typename Tmeta::typeRun();
			_run_tree->Bronch("runInfo", Tmeta::idRun().c_str(), &metaRun);
		}

	static const std::string getLabel() { return "GenInfo"; }


	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		// Fill data related infos
		if (!KInfoProducer<Tmeta>::onLumi(lumiBlock, setup))
			return false;
		if (forceLumi > 0)
			this->metaLumi->nLumi = forceLumi;
	return true;
	}

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		edm::Handle<LHEEventProduct> lheEventProduct;
		if(lheWeightRegexes.size() > 0 && event.getByToken(tokenLhe, lheEventProduct))
		{
			for(size_t i = 0; i < lheEventProduct->weights().size(); ++i)
			{
				for(auto validIds : lheWeightRegexes)
				{
					if(KBaseProducer::regexMatch(lheEventProduct->weights()[i].id, validIds))
					{
						genEventInfoMetadata->lheWeightNames.push_back(lheEventProduct->weights()[i].id);
					}
				}
			}
		}
		return KBaseProducerWP::onFirstEvent(event, setup);
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
		int lheNOutPartons = 0;
		if (event.getByToken(tokenLhe, lheEventProduct) && lheEventProduct.isValid())
		{
			const lhef::HEPEUP& lheEvent = lheEventProduct->hepeup();
			std::vector<lhef::HEPEUP::FiveVector> lheParticles = lheEvent.PUP;
			for ( size_t idxParticle = 0; idxParticle < lheParticles.size(); ++idxParticle ) {
				int id = std::abs(lheEvent.IDUP[idxParticle]);
				int status = lheEvent.ISTUP[idxParticle];
				if ( status == 1 && ((id >= 1 && id <= 6) || id == 21) ) { // quarks and gluons
					lheHt += std::sqrt(std::pow(lheParticles[idxParticle][0], 2.) + std::pow(lheParticles[idxParticle][1], 2.));
					++lheNOutPartons;
				}
			}
		}
		this->metaEvent->lheHt = lheHt;
		this->metaEvent->lheNOutPartons = lheNOutPartons;
		// Get LHE renormalization and factorization weights
		if((lheWeightRegexes.size() > 0) && event.getByToken(tokenLhe, lheEventProduct) && lheEventProduct.isValid())
		{
			this->metaEvent->lheWeights.clear();
			for(size_t j = 0; j < genEventInfoMetadata->lheWeightNames.size(); j++)
			{
				for(size_t i = 0; i < lheEventProduct->weights().size(); ++i)
				{
					if(lheEventProduct->weights()[i].id.compare(genEventInfoMetadata->lheWeightNames[j]) == 0)
					{
						this->metaEvent->lheWeights.push_back(lheEventProduct->weights()[i].wgt / lheEventProduct->originalXWGTUP() );
						break;
					}
				}
				if (this->metaEvent->lheWeights.size() != j+1) // check that exactly one weight has been added
				{
					if(this->verbosity > 0)
						std::cout << "Warning: Weight with id " << genEventInfoMetadata->lheWeightNames[j] << std::endl;
					this->metaEvent->lheWeights.push_back(-999.0);
				}
			}
			assert( this->metaEvent->lheWeights.size() == this->genEventInfoMetadata->lheWeightNames.size() ); // crosscheck, should never trigger
		}

		// Get generator event info:
		edm::Handle<GenEventInfoProduct> hEventInfo;
		event.getByToken(tokenSource, hEventInfo);

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

		this->metaEvent->x1 = hEventInfo->pdf()->x.first;
		this->metaEvent->x2 = hEventInfo->pdf()->x.second;
		this->metaEvent->qScale = hEventInfo->qScale();
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
		if (event.getByToken(tokenPuInfo, puHandles) && puHandles.isValid())
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
			if (event.getByToken(tokenPuInfo, puHandle) && puHandle.isValid())
				this->metaEvent->nPU = (unsigned char)std::min(255, puHandle->getPU_NumInteractions());
		}

		return true;
	}
	bool endRun(edm::Run const&  run, edm::EventSetup const &setup) override
	{
		// Read generator infos
		edm::Handle<GenRunInfoProduct> hGenInfo;
		run.getByToken(this->tokenGenRunInfo, hGenInfo);

		const bool invalidGenInfo = !hGenInfo.isValid();
		this->metaRun->filterEff = invalidGenInfo ? -1 : hGenInfo->filterEfficiency();
		this->metaRun->xSectionInt = invalidGenInfo ? -1 : hGenInfo->internalXSec().value();
		this->metaRun->xSectionExt = invalidGenInfo ? -1 : hGenInfo->externalXSecLO().value();
		if (ignoreExtXSec)
			this->metaRun->xSectionExt = -1;
		if (invalidGenInfo)
			return KBaseProducer::fail(std::cout << "Invalid generator info" << std::endl);

		// print available lheWeights
		edm::Handle<LHERunInfoProduct> runhandle;
		if((this->verbosity > 1) && run.getByToken( tokenRunInfo, runhandle ))
		{
			LHERunInfoProduct myLHERunInfoProduct = *(runhandle.product());
			for (auto iter=myLHERunInfoProduct.headers_begin(); iter!=myLHERunInfoProduct.headers_end(); iter++)
			{
				std::vector<std::string> lines = iter->lines();
				std::string content = accumulate(lines.begin(), lines.end(), std::string("\n"));
				boost::regex weightGroupRegex("<weightgroup(?:(?!<weight).)*\\htype\\h*=\\h*\"((?:(?!<weight).)*)\"(?:(?!<weight).)*>(?:(?!<weightgroup).)*</weightgroup>");
				for (boost::sregex_token_iterator weightGroup(content.begin(), content.end(), weightGroupRegex, 0);
				     weightGroup != boost::sregex_token_iterator(); ++weightGroup)
				{
					std::string weightGroupStr = *weightGroup;
					std::cout << "\nLHE weights for tag \"" << iter->tag() << "\":" << std::endl;
					
					boost::match_results<std::string::iterator> weightGroupRegexResult;
					std::string weightType;
					if (boost::regex_search(weightGroupStr.begin(), weightGroupStr.end(), weightGroupRegexResult, weightGroupRegex, boost::match_default) &&
					    (weightGroupRegexResult.size() > 1))
					{
						weightType = boost::algorithm::trim_copy(std::string(weightGroupRegexResult[1].first, weightGroupRegexResult[1].second));
					}
					
					boost::regex weightRegex("<weight(?:(?!<weight).)*\\hid\\h*=\\h*\"(\\d+)\"(?:(?!<weight).)*>((?:(?!<weight).)*)</weight>");
					boost::match_results<std::string::iterator> weightRegexResult;
					for (boost::sregex_token_iterator weight(weightGroupStr.begin(), weightGroupStr.end(), weightRegex, 0);
					     weight != boost::sregex_token_iterator(); ++weight)
					{
						std::string weightStr = *weight;
						
						boost::match_results<std::string::iterator> weightRegexResult;
						std::string weightId;
						std::string weightTypeDetail;
						if (boost::regex_search(weightStr.begin(), weightStr.end(), weightRegexResult, weightRegex, boost::match_default) &&
						    (weightRegexResult.size() > 2))
						{
							weightId = boost::algorithm::trim_copy(std::string(weightRegexResult[1].first, weightRegexResult[1].second));
							weightTypeDetail = boost::algorithm::trim_copy(std::string(weightRegexResult[2].first, weightRegexResult[2].second));
						}
						
						std::string weightTypeFull = weightType + "__" + weightTypeDetail;
						boost::replace_all(weightTypeFull, " ", "_");
						boost::replace_all(weightTypeFull, "=", "_");
						boost::replace_all(weightTypeFull, ".", "_");
						
						std::cout << weightId << " -> " << weightTypeFull << std::endl;
					}
				}
			}
		}
		return true;
	}

protected:
	typename Tmeta::typeRun *metaRun;
	bool ignoreExtXSec;
	int forceLumi;
	std::string binningMode;
	edm::InputTag tagSource, puInfoSource, lheSource, runInfo;
	KGenEventInfoMetadata *genEventInfoMetadata;
	std::vector<std::string> lheWeightRegexes;

	edm::EDGetTokenT<GenRunInfoProduct> tokenGenRunInfo;
	edm::EDGetTokenT<GenEventInfoProduct> tokenSource;
	edm::EDGetTokenT<LHEEventProduct> tokenLhe;
	edm::EDGetTokenT<std::vector<PileupSummaryInfo>> tokenPuInfo;
	//edm::EDGetTokenT<LHERunInfoProduct> tokenLHERunInfo;
	edm::EDGetTokenT<LHERunInfoProduct> tokenRunInfo;
};

template<typename Tmeta>
class KHepMCInfoProducer : public KInfoProducer<Tmeta>
{
public:
	KHepMCInfoProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KInfoProducer<Tmeta>(cfg, _event_tree, _lumi_tree, _run_tree, std::forward<edm::ConsumesCollector>(consumescollector)),
		forceXSec(cfg.getParameter<double>("forceXSec")),
		forceLumi(cfg.getParameter<int>("forceLumi")),
		tagSource(cfg.getParameter<edm::InputTag>("genSource"))
		{
		    tokenSource = consumescollector.consumes<edm::HepMCProduct>(tagSource);
			metaRun = new typename Tmeta::typeRun();
			_run_tree->Bronch("runInfo", Tmeta::idRun().c_str(), &metaRun);
		}

	static const std::string getLabel() { return "HepMCInfo"; }

	bool endRun(edm::Run const&  run, edm::EventSetup const &setup) override
	{
		// Fill data related infos
		if (!KInfoProducer<Tmeta>::onRun(run, setup))
			return false;
		this->metaRun->filterEff = 1;
		this->metaRun->xSectionInt = forceXSec;
		this->metaRun->xSectionExt = forceXSec;
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
		event.getByToken(this->tokenSource, hEventInfo);
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
	typename Tmeta::typeRun *metaRun;
	double forceXSec;
	int forceLumi;
	edm::InputTag tagSource;
	edm::EDGetTokenT<edm::HepMCProduct> tokenSource;
};

#endif

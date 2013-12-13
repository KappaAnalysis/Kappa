/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Danilo Piparo <danilo.piparo@cern.ch>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/ParameterSet/interface/Registry.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include <TFile.h>

#include "../interface/KMetadataProducer.h"
#include "../interface/KGenMetadataProducer.h"
#include "../interface/KDataMetadataProducer.h"

#include "../interface/KBeamSpotProducer.h"
#include "../interface/KCaloJetProducer.h"
#include "../interface/KCaloTauProducer.h"
#include "../interface/KFilterSummaryProducer.h"
#include "../interface/KGenParticleProducer.h"
#include "../interface/KGenPhotonProducer.h"
#include "../interface/KGenTauProducer.h"
#include "../interface/KHCALNoiseSummaryProducer.h"
#include "../interface/KHitProducer.h"
#include "../interface/KJetAreaProducer.h"
#include "../interface/KLorentzProducer.h"
#include "../interface/KMETProducer.h"
#include "../interface/KMuonProducer.h"
#include "../interface/KElectronProducer.h"
#include "../interface/KPFCandidateProducer.h"
#include "../interface/KPFJetProducer.h"
#include "../interface/KPFMETProducer.h"
#include "../interface/KPFTaggedJetProducer.h"
#include "../interface/KPFTauProducer.h"
#include "../interface/KTowerProducer.h"
#include "../interface/KTrackProducer.h"
#include "../interface/KTrackSummaryProducer.h"
#include "../interface/KTriggerObjectProducer2.h"
#include "../interface/KVertexProducer.h"
#include "../interface/KVertexSummaryProducer.h"
/* are these still used?
#include "../interface/KHepMCPartonProducer.h"
#include "../interface/KL1MuonProducer.h"
#include "../interface/KL2MuonProducer.h"
#include "../interface/KTriggerObjectProducer.h"
*/

int KBaseProducer::verbosity = 0;

class KTuple : public edm::EDAnalyzer
{
public:
	explicit KTuple(const edm::ParameterSet&);
	~KTuple();

	virtual void beginRun(edm::Run  const &, edm::EventSetup  const &);
	virtual void beginLuminosityBlock(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup);
	virtual void analyze(const edm::Event&, const edm::EventSetup&);
	virtual void endLuminosityBlock(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup);

protected:
	const edm::ParameterSet &psConfig;

	bool first;
	std::vector<KBaseProducer*> producers;
	TTree *event_tree, *lumi_tree;
	TFile *file;

	template<typename Tprod>
	bool addProducer(const std::string sActive, std::string sName = "")
	{
		if (sActive == Tprod::getLabel())
		{
			if (sName == "")
				sName = sActive;
			producers.push_back(new Tprod(psConfig.getParameter<edm::ParameterSet>(sName), event_tree, lumi_tree));
			return true;
		}
		return false;
	}
};

class ROOTContextSentinel
{
public:
	ROOTContextSentinel() : dir(gDirectory), file(gFile) {}
	~ROOTContextSentinel() { gDirectory = dir; gFile = file; }
private:
	TDirectory *dir;
	TFile *file;
};

KTuple::KTuple(const edm::ParameterSet &_psConfig) :
	psConfig(_psConfig)
{
	ROOTContextSentinel ctx;
	std::string outputFile = psConfig.getParameter<std::string>("outputFile");
	if (outputFile == "")
	{
		file = 0;
		edm::Service<TFileService> fs;
		lumi_tree = fs->make<TTree>("Lumis", "Lumis");
		event_tree = fs->make<TTree>("Events", "Events");
	}
	else
	{
		lumi_tree = new TTree("Lumis", "Lumis");
		lumi_tree->SetDirectory(0);
		file = new TFile(outputFile.c_str(), "RECREATE");
		event_tree = new TTree("Events", "Events");
	}

	KBaseProducer::verbosity = std::max(KBaseProducer::verbosity, psConfig.getParameter<int>("verbose"));

	std::vector<std::string> active = psConfig.getParameter<std::vector<std::string> >("active");

	// Make sure there are no duplicates
	bool have_duplicates = false;
	for (size_t i = 0; i < active.size(); ++i)
	{
		for (size_t j = i + 1; j < active.size(); ++j)
		{
			if (active[i] == active[j])
			{
				std::cout << "Duplicate producer found: " << active[i] << std::endl;
				have_duplicates = true;
			}
		}
	}

	if (have_duplicates)
		exit(1);

	// Create metadata producer
	for (size_t i = 0; i < active.size(); ++i)
	{
		std::cout << "Init producer " << active[i] << std::endl;

		if (addProducer<KMetadataProducer<KMetadata_Product> >(active[i], "Metadata"))
			break;
		if (addProducer<KDataMetadataProducer<KDataMetadata_Product> >(active[i], "Metadata"))
			break;
		if (addProducer<KGenMetadataProducer<KGenMetadata_Product> >(active[i], "Metadata"))
			break;
		if (addProducer<KHepMCMetadataProducer<KGenMetadata_Product> >(active[i], "Metadata"))
			break;
	}

	// Create all active producers
	for (size_t i = 0; i < active.size(); ++i)
	{
		std::cout << "Init producer " << active[i] << std::endl;
		if (active[i] == "Metadata")
			continue;
		else if (active[i] == "DataMetadata")
			continue;
		else if (active[i] == "GenMetadata")
			continue;
		else if (active[i] == "HepMCMetadata")
			continue;

		size_t nProducers = producers.size();

		addProducer<KBeamSpotProducer>(active[i]);
		addProducer<KCaloJetProducer>(active[i]);
		addProducer<KCaloTauProducer>(active[i]);
		addProducer<KFilterSummaryProducer>(active[i]);
		addProducer<KGenParticleProducer>(active[i]);
		addProducer<KGenPhotonProducer>(active[i]);
		addProducer<KGenTauProducer>(active[i]);
		addProducer<KHCALNoiseSummaryProducer>(active[i]);
		addProducer<KHitProducer>(active[i]);
		addProducer<KJetAreaProducer>(active[i]);
		addProducer<KLorentzProducer>(active[i]);
		addProducer<KMETProducer>(active[i]);
		addProducer<KMuonProducer>(active[i]);
		addProducer<KElectronProducer>(active[i]);
		addProducer<KPFCandidateProducer>(active[i]);
		addProducer<KPFJetProducer>(active[i]);
		addProducer<KPFMETProducer>(active[i]);
		addProducer<KPFTaggedJetProducer>(active[i]);
		addProducer<KPFTauProducer>(active[i]);
		addProducer<KTowerProducer>(active[i]);
		addProducer<KTrackProducer>(active[i]);
		addProducer<KTrackSummaryProducer>(active[i]);
		addProducer<KTriggerObjectProducer2>(active[i]);
		addProducer<KVertexProducer>(active[i]);
		addProducer<KVertexSummaryProducer>(active[i]);

/* are these still used?
		else if (active[i] == "TriggerObjects")
			addProducer<KTriggerObjectProducer>(psConfig, active[i]);
		else if (active[i] == "L1Muons")
			addProducer<KL1MuonProducer>(psConfig, active[i]);
		else if (active[i] == "L2MuonTrajectorySeed")
			addProducer<KL2MuonTrajectorySeedProducer>(psConfig, active[i]);
		else if (active[i] == "L3MuonTrajectorySeed")
			addProducer<KL3MuonTrajectorySeedProducer>(psConfig, active[i]);
		else if (active[i] == "MuonTriggerCandidates")
			addProducer<KMuonTriggerCandidateProducer>(psConfig, active[i]);
*/
		if (producers.size() > nProducers + 1)
		{
			std::cout << "MULTIPLE PRODUCER CREATED!!! " << active[i] << std::endl;
			exit(1);
		}
		else if (producers.size() != nProducers + 1)
		{
			std::cout << "UNKNOWN PRODUCER!!! " << active[i] << std::endl;
			exit(1);
		}
	}
	first = true;
}

KTuple::~KTuple()
{
	ROOTContextSentinel ctx;
	for (unsigned int i = 0; i < producers.size(); ++i)
		delete producers[i];
	if (file != 0)
	{
		file->cd();
		lumi_tree->SetDirectory(file);
		lumi_tree->Write();
		event_tree->Write();
		file->Close();
	}
}

void KTuple::beginRun(edm::Run const &run, edm::EventSetup const &setup)
{
	ROOTContextSentinel ctx;
	for (unsigned int i = 0; i < producers.size(); ++i)
		producers[i]->onRun(run, setup);
}

void KTuple::beginLuminosityBlock(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
{
	ROOTContextSentinel ctx;
	for (unsigned int i = 0; i < producers.size(); ++i)
		producers[i]->onLumi(lumiBlock, setup);
}

void KTuple::analyze(const edm::Event &event, const edm::EventSetup &setup)
{
	ROOTContextSentinel ctx;
	if (first)
	{
		for (unsigned int i = 0; i < producers.size(); ++i)
			producers[i]->onFirstEvent(event, setup);
		first = false;
	}
	for (unsigned int i = 0; i < producers.size(); ++i)
		producers[i]->onEvent(event, setup);
	event_tree->Fill();
	if (KBaseProducer::verbosity > 0)
		std::cout << std::endl;
}

void KTuple::endLuminosityBlock(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
{
	ROOTContextSentinel ctx;
	lumi_tree->Fill();
}

DEFINE_FWK_MODULE(KTuple);

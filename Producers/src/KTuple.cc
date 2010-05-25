#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include <TFile.h>

#include "../interface/KMetadataProducer.h"
#include "../interface/KGenMetadataProducer.h"
#include "../interface/KLorentzProducer.h"
#include "../interface/KMETProducer.h"
#include "../interface/KPFMETProducer.h"
#include "../interface/KTrackProducer.h"
#include "../interface/KTowerProducer.h"
#include "../interface/KVertexProducer.h"
#include "../interface/KMuonProducer.h"
#include "../interface/KCaloJetProducer.h"
#include "../interface/KPFJetProducer.h"
#include "../interface/KPartonProducer.h"
#include "../interface/KTrackSummaryProducer.h"
#include "../interface/KBeamSpotProducer.h"
// #include "../interface/KHepMCPartonProducer.h"

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
	bool first;
	std::vector<KBaseProducer*> producers;
	TTree *event_tree, *lumi_tree;
	TFile *file;

	template<typename Tprod>
	void addProducer(const edm::ParameterSet &psCfg, const std::string sName)
	{
		producers.push_back(new Tprod(psCfg.getParameter<edm::ParameterSet>(sName), event_tree, lumi_tree));
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

KTuple::KTuple(const edm::ParameterSet &psConfig)
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
		file = new TFile(outputFile.c_str(), "RECREATE");
		lumi_tree = new TTree("Lumis", "Lumis");
		event_tree = new TTree("Events", "Events");
	}

	KBaseProducer::verbosity = std::max(KBaseProducer::verbosity, psConfig.getParameter<int>("verbose"));

	// Create metadata producer
	std::vector<std::string> active = psConfig.getParameter<std::vector<std::string> >("active");
	for (size_t i = 0; i < active.size(); ++i)
	{
		std::cout << "Init producer " << active[i] << std::endl;
		if (active[i] == "Metadata")
		{
			addProducer<KMetadataProducer<KMetadata_Product> >(psConfig, "Metadata");
			break;
		}
		else if (active[i] == "GenMetadata")
		{
			addProducer<KGenMetadataProducer<KGenMetadata_Product> >(psConfig, "Metadata");
			break;
		}
	}

	// Create all active producers
	for (size_t i = 0; i < active.size(); ++i)
	{
		std::cout << "Init producer " << active[i] << std::endl;
		if (active[i] == "Metadata")
			continue;
		else if (active[i] == "GenMetadata")
			continue;
		else if (active[i] == "CaloJets")
			addProducer<KCaloJetProducer>(psConfig, active[i]);
		else if (active[i] == "PFJets")
			addProducer<KPFJetProducer>(psConfig, active[i]);
		else if (active[i] == "Tower")
			addProducer<KTowerProducer>(psConfig, active[i]);
		else if (active[i] == "Muons")
			addProducer<KMuonProducer>(psConfig, active[i]);
		else if (active[i] == "Vertex")
			addProducer<KVertexProducer>(psConfig, active[i]);
		else if (active[i] == "BeamSpot")
			addProducer<KBeamSpotProducer>(psConfig, active[i]);
		else if (active[i] == "Tracks")
			addProducer<KTrackProducer>(psConfig, active[i]);
		else if (active[i] == "TrackSummary")
			addProducer<KTrackSummaryProducer>(psConfig, active[i]);
		else if (active[i] == "MET")
			addProducer<KMETProducer>(psConfig, active[i]);
		else if (active[i] == "PFMET")
			addProducer<KPFMETProducer>(psConfig, active[i]);
		else if (active[i] == "LV")
			addProducer<KLorentzProducer>(psConfig, active[i]);
		else if (active[i] == "Partons")
			addProducer<KPartonProducer>(psConfig, active[i]);
		else
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

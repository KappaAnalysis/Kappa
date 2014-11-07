/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Danilo Piparo <danilo.piparo@cern.ch>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#include <memory>
#include <chrono>  // if the compiler does not support this, just comment out every line with std::chrono

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
#include "../interface/KTreeMetadataProducer.h"

#include "../interface/KBeamSpotProducer.h"
#include "../interface/KCaloJetProducer.h"
#include "../interface/KCaloTauProducer.h"
#include "../interface/KFilterSummaryProducer.h"
#include "../interface/KGenParticleProducer.h"
#include "../interface/KLHEProducer.h"
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
#include "../interface/KUnbiasedDiTauPVsProducer.h"
#include "../interface/KTowerProducer.h"
#include "../interface/KTrackProducer.h"
#include "../interface/KTrackSummaryProducer.h"
#include "../interface/KTriggerObjectProducer.h"
#include "../interface/KVertexProducer.h"
#include "../interface/KVertexSummaryProducer.h"
/* are these still used?
#include "../interface/KHepMCPartonProducer.h"
#include "../interface/KL1MuonProducer.h"
#include "../interface/KL2MuonProducer.h"
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
	bool doProfile;
	std::chrono::high_resolution_clock::time_point t1, t2;
	double fillRuntime;
	long nRuns, nLumis, nEvents, nFirsts;
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
			producers.back()->runRuntime = 0;
			producers.back()->lumiRuntime = 0;
			producers.back()->firstRuntime = 0;
			producers.back()->eventRuntime = 0;
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
	psConfig(_psConfig), doProfile(true), fillRuntime(0), nRuns(0), nLumis(0), nEvents(0), nFirsts(0)
{
	ROOTContextSentinel ctx;
	std::cout << "Start Kappa producer KTuple" << std::endl;

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
	doProfile = psConfig.getParameter<bool>("profile");
	if (doProfile)
		std::cout << "Profiling is turned on." << std::endl;

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
		addProducer<KLHEProducer>(active[i]);
		addProducer<KGenPhotonProducer>(active[i]);
		addProducer<KGenTauProducer>(active[i]);
		addProducer<KHCALNoiseSummaryProducer>(active[i]);
		addProducer<KHitProducer>(active[i]);
		addProducer<KPileupDensityProducer>(active[i]);
		addProducer<KLorentzProducer>(active[i]);
		addProducer<KBasicMETProducer>(active[i]);
		addProducer<KMuonProducer>(active[i]);
		addProducer<KElectronProducer>(active[i]);
		addProducer<KPFCandidateProducer>(active[i]);
		addProducer<KBasicJetProducer>(active[i]);
		addProducer<KMETProducer>(active[i]);
		addProducer<KJetProducer>(active[i]);
		addProducer<KTauProducer>(active[i]);
		addProducer<KUnbiasedDiTauPVsProducer>(active[i]);
		addProducer<KTowerProducer>(active[i]);
		addProducer<KTrackProducer>(active[i]);
		addProducer<KTrackSummaryProducer>(active[i]);
		addProducer<KTriggerObjectProducer>(active[i]);
		addProducer<KVertexProducer>(active[i]);
		addProducer<KVertexSummaryProducer>(active[i]);
		addProducer<KTreeMetadataProducer >(active[i]);
/* are these still used?
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
			std::cout << "Multiple producers '" << active[i] << "' created!" << std::endl;
			exit(1);
		}
		else if (producers.size() != nProducers + 1)
		{
			std::cout << "Unknown producer '" << active[i] << "'!" << std::endl;
			exit(1);
		}
	}
	first = true;
}

KTuple::~KTuple()
{
	ROOTContextSentinel ctx;
	std::vector<std::string> active = psConfig.getParameter<std::vector<std::string> >("active");
	if (doProfile)  // profiling header
	{
		std::cout.precision(3);
		std::cout << std::endl << std::fixed << std::right
			<< "Kappa timing information (times in ms) ---------------------------------------" << std::endl
			<< "KProducer     : time per run | time per lumi | time 1st event | time per event" << std::endl
			<< "No. of entries:"
			<< std::setw(13) << nRuns
			<< std::setw(16) << nLumis
			<< std::setw(17) << nFirsts
			<< std::setw(17) << nEvents << std::endl
			<< "Fill tree     :                                                 " << fillRuntime << std::endl;
	}
	for (unsigned int i = 0; i < producers.size(); ++i)
	{
		if (doProfile)  // profiling per producer
			std::cout << std::left << std::setw(14) << active[i] << ":" << std::right
				<< std::setw(13) << (producers[i]->runRuntime   / nRuns   * 1000)
				<< std::setw(16) << (producers[i]->lumiRuntime  / nLumis  * 1000)
				<< std::setw(17) << (producers[i]->firstRuntime / nFirsts * 1000)
				<< std::setw(17) << (producers[i]->eventRuntime / nEvents * 1000) << std::endl;
		delete producers[i];
	}
	if (doProfile)
		t1 = std::chrono::high_resolution_clock::now();
	if (file != 0)
	{
		file->cd();
		lumi_tree->SetDirectory(file);
		lumi_tree->Write();
		event_tree->Write();
		file->Close();
	}
	if (doProfile)
	{
		t2 = std::chrono::high_resolution_clock::now();
		std::chrono::duration<double> time_span = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
		std::cout << "Write file    : " << time_span.count() << std::endl;
	}
}

void KTuple::beginRun(edm::Run const &run, edm::EventSetup const &setup)
{
	ROOTContextSentinel ctx;
	nRuns++;
	for (unsigned int i = 0; i < producers.size(); ++i)
	{
		if (doProfile)
			t1 = std::chrono::high_resolution_clock::now();
		producers[i]->onRun(run, setup);
		if (doProfile)
		{
			t2 = std::chrono::high_resolution_clock::now();
			std::chrono::duration<double> time_span = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
			producers[i]->runRuntime += time_span.count();
		}
	}
}

void KTuple::beginLuminosityBlock(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
{
	ROOTContextSentinel ctx;
	nLumis++;
	for (unsigned int i = 0; i < producers.size(); ++i)
	{
		if (doProfile)
			t1 = std::chrono::high_resolution_clock::now();
		producers[i]->onLumi(lumiBlock, setup);
		if (doProfile)
		{
			t2 = std::chrono::high_resolution_clock::now();
			std::chrono::duration<double> time_span = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
			producers[i]->lumiRuntime += time_span.count();
		}
	}
}

void KTuple::analyze(const edm::Event &event, const edm::EventSetup &setup)
{
	ROOTContextSentinel ctx;
	if (first)
	{
		nFirsts++;
		for (unsigned int i = 0; i < producers.size(); ++i)
		{
			if (doProfile)
				t1 = std::chrono::high_resolution_clock::now();
			producers[i]->onFirstEvent(event, setup);
			if (doProfile)
			{
				t2 = std::chrono::high_resolution_clock::now();
				std::chrono::duration<double> time_span = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
				producers[i]->firstRuntime += time_span.count();
			}
		}
		first = false;
	}
	nEvents++;
	for (unsigned int i = 0; i < producers.size(); ++i)
	{
		if (doProfile)
			t1 = std::chrono::high_resolution_clock::now();
		producers[i]->onEvent(event, setup);
		if (doProfile)
		{
			t2 = std::chrono::high_resolution_clock::now();
			std::chrono::duration<double> time_span = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
			producers[i]->eventRuntime += time_span.count();
		}
	}
	if (doProfile)
		t1 = std::chrono::high_resolution_clock::now();
	event_tree->Fill();
	if (doProfile)
	{
		t2 = std::chrono::high_resolution_clock::now();
		std::chrono::duration<double> time_span = std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1);
		fillRuntime += time_span.count();
	}
	if (KBaseProducer::verbosity > 0)
		std::cout << std::endl;

}

void KTuple::endLuminosityBlock(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
{
	ROOTContextSentinel ctx;
	lumi_tree->Fill();
}

DEFINE_FWK_MODULE(KTuple);

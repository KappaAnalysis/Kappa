//- Copyright (c) 2013 - All Rights Reserved
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Fabio Colombo <fabio.colombo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_JETPRODUCER_H
#define KAPPA_JETPRODUCER_H

#include "KBasicJetProducer.h"
#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KJetMET.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/BTauReco/interface/JetTag.h>
#include <FWCore/Framework/interface/EDProducer.h>

class KJetProducer : public KBaseMultiLVProducer<reco::PFJetCollection, KJets>
{
public:
	KJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<reco::PFJetCollection, KJets>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector))
{
		names = new KJetMetadata;
		_lumi_tree->Bronch("jetMetadata", "KJetMetadata", &names);

		std::vector<std::string> jetnames = cfg.getParameterNamesForType<edm::ParameterSet>();
		for (auto akt_jet : jetnames ){
		 std::cout<< akt_jet<<std::endl;
		 edm::ParameterSet akt_set = cfg.getParameter<edm::ParameterSet>(akt_jet);
		 edm::InputTag akt_iput_tag = akt_set.getParameter<edm::InputTag>("PUJetID");
		 std::cout<<akt_iput_tag.label()<<std::endl;
		 consumescollector.consumes<edm::ValueMap<float> >(edm::InputTag(akt_iput_tag.label(),"fullDiscriminant"));
		 consumescollector.consumes<edm::ValueMap<int> >(edm::InputTag(akt_iput_tag.label(),"fullId"));

		}
				
}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		return KBaseMultiLVProducer<reco::PFJetCollection, KJets>::onLumi(lumiBlock, setup);
	}

	static const std::string getLabel() { return "Jets"; }

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{

		Btagger = pset.getParameter<edm::InputTag>("Btagger");
		QGtagger = pset.getParameter<edm::InputTag>("QGtagger");
		PUJetID = pset.getParameter<edm::InputTag>("PUJetID");
		PUJetID_full = pset.getParameter<edm::InputTag>("PUJetID_full");

		// Continue normally
		KBaseMultiLVProducer<reco::PFJetCollection, KJets>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::PFJetCollection>(handle, this->nCursor));

		std::vector<bool> puJetID;


		for (unsigned int i = 0; i < puJetID.size(); ++i)
			out.binaryIds |= puJetID[i] << i;

		// PF variables:
		copyP4(in, out.p4);

		out.area = in.jetArea();
		out.nConstituents = in.nConstituents();
		out.nCharged = in.chargedMultiplicity();
		out.flavour = 0;

		double sumFractions =
			in.neutralHadronEnergyFraction() +
			in.chargedHadronEnergyFraction() +
			in.muonEnergyFraction() +
			in.photonEnergyFraction() +
			in.electronEnergyFraction() +
			in.HFEMEnergyFraction();
		out.neutralHadronFraction = in.neutralHadronEnergyFraction() / sumFractions;
		out.chargedHadronFraction = in.chargedHadronEnergyFraction() / sumFractions;
		out.muonFraction = in.muonEnergyFraction() / sumFractions;
		out.photonFraction = in.photonEnergyFraction() / sumFractions;
		out.electronFraction = in.electronEnergyFraction() / sumFractions;
		out.hfHadronFraction = in.HFHadronEnergyFraction() / sumFractions;
		out.hfEMFraction = in.HFEMEnergyFraction() / sumFractions;

		// JEC factor (a member of PFJet would be better, but if everything is right, this should be equivalent)
		out.corrections.push_back(sumFractions);

// fractions should add up to unity
		assert(out.neutralHadronFraction >= out.hfHadronFraction);
		assert(std::abs(out.neutralHadronFraction + out.chargedHadronFraction +
			out.muonFraction + out.photonFraction + out.electronFraction +
			out.hfEMFraction - 1.0f) < 0.001f);
		assert(std::abs(in.neutralEmEnergyFraction() - in.photonEnergyFraction() -
			in.HFEMEnergyFraction()) < 0.001f);
		assert(std::abs(in.chargedEmEnergyFraction() - in.electronEnergyFraction()) < 0.001f);
	}

private:
	KJetMetadata *names;

	edm::InputTag QGtagger;
	edm::InputTag Btagger;
	edm::InputTag PUJetID;
	edm::InputTag PUJetID_full;

	edm::Handle<reco::JetTagCollection> TrackCountingHighEffBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> TrackCountingHighPurBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> JetProbabilityBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> JetBProbabilityBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> SoftElectronBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> SoftMuonBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> SoftMuonByIP3dBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> SoftMuonByPtBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> SimpleSecondaryVertexBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> CombinedSecondaryVertexBJetTags_Handle;
	edm::Handle<reco::JetTagCollection> CombinedSecondaryVertexMVABJetTags_Handle;

	edm::Handle< edm::ValueMap<float> > QGTagsHandleMLP;
	edm::Handle< edm::ValueMap<float> > QGTagsHandleLikelihood;

	edm::Handle< edm::ValueMap<int> > puJetIDfull_Handle;
	edm::Handle< edm::ValueMap<int> > puJetIDcutbased_Handle;
	edm::Handle< edm::ValueMap<int> > puJetIDMET_Handle;
	edm::Handle< edm::ValueMap<float> > puJetIDfullDiscriminant_Handle;
	edm::Handle< edm::ValueMap<float> > puJetIDcutbasedDiscriminant_Handle;


	float getsignedvalue(const float value){ return value; }

};

#endif

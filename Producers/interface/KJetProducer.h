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
#include "../../Producers/interface/Consumes.h"

class KJetProducer : public KBaseMultiLVProducer<reco::PFJetCollection, KJets>
{
public:
	KJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<reco::PFJetCollection, KJets>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		 tagger(cfg.getParameter<std::vector<std::string> >("taggers"))
{
		names = new KJetMetadata;
		_run_tree->Bronch("jetMetadata", "KJetMetadata", &names);
}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		for (size_t i = 0; i < tagger.size(); ++i)
		{
			if ( (tagger[i] == "puJetIDFullLoose")
				|| (tagger[i] == "puJetIDFullMedium")
				|| (tagger[i] == "puJetIDFullTight")
				|| (tagger[i] == "puJetIDCutbasedLoose")
				|| (tagger[i] == "puJetIDCutbasedMedium")
				|| (tagger[i] == "puJetIDCutbasedTight")
				|| (tagger[i] == "puJetIDMET") )
				names->idNames.push_back(tagger[i]);
			else
				names->tagNames.push_back(tagger[i]);
		}
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

		for (size_t i = 0; i < tagger.size(); ++i)
		{
			if (tagger[i] == "QGlikelihood")
				cEvent->getByLabel(QGtagger.label(),"qgLikelihood", QGTagsHandleLikelihood);
			else if (tagger[i] == "QGmlp")
				cEvent->getByLabel(QGtagger.label(),"qgMLP", QGTagsHandleMLP);
			else if (tagger[i] == "TrackCountingHighEffBJetTags")
				cEvent->getByLabel(Btagger.label()+"TrackCountingHighEffBJetTags", TrackCountingHighEffBJetTags_Handle);
			else if (tagger[i] == "TrackCountingHighPurBJetTags")
				cEvent->getByLabel(Btagger.label()+"TrackCountingHighPurBJetTags", TrackCountingHighPurBJetTags_Handle);
			else if (tagger[i] == "JetProbabilityBJetTags")
				cEvent->getByLabel(Btagger.label()+"JetProbabilityBJetTags", JetProbabilityBJetTags_Handle);
			else if (tagger[i] == "JetBProbabilityBJetTags")
				cEvent->getByLabel(Btagger.label()+"JetBProbabilityBJetTags", JetBProbabilityBJetTags_Handle);
			else if (tagger[i] == "SoftElectronBJetTags")
				cEvent->getByLabel(Btagger.label()+"SoftElectronBJetTags", SoftElectronBJetTags_Handle);
			else if (tagger[i] == "SoftMuonBJetTags")
				cEvent->getByLabel(Btagger.label()+"SoftMuonBJetTags", SoftMuonBJetTags_Handle);
			else if (tagger[i] == "SoftMuonByIP3dBJetTags")
				cEvent->getByLabel(Btagger.label()+"SoftMuonByIP3dBJetTags", SoftMuonByIP3dBJetTags_Handle);
			else if (tagger[i] == "SoftMuonByPtBJetTags")
				cEvent->getByLabel(Btagger.label()+"SoftMuonByPtBJetTags", SoftMuonByPtBJetTags_Handle);
			else if (tagger[i] == "SimpleSecondaryVertexBJetTags")
				cEvent->getByLabel(Btagger.label()+"SimpleSecondaryVertexBJetTags", SimpleSecondaryVertexBJetTags_Handle);
			else if (tagger[i] == "CombinedSecondaryVertexBJetTags")
				cEvent->getByLabel(Btagger.label()+"CombinedSecondaryVertexBJetTags", CombinedSecondaryVertexBJetTags_Handle);
			else if (tagger[i] == "CombinedSecondaryVertexMVABJetTags")
				cEvent->getByLabel(Btagger.label()+"CombinedSecondaryVertexMVABJetTags", CombinedSecondaryVertexMVABJetTags_Handle);
			else if (tagger[i] == "puJetIDMET")
				cEvent->getByLabel(PUJetID.label(), "metId", puJetIDMET_Handle);
			else if (tagger[i] == "puJetIDFullDiscriminant")
				cEvent->getByLabel(PUJetID.label(), PUJetID_full.label()+"Discriminant", puJetIDfullDiscriminant_Handle);
			else if (tagger[i] == "puJetIDCutbasedDiscriminant")
				cEvent->getByLabel(PUJetID.label(), "cutbasedDiscriminant", puJetIDcutbasedDiscriminant_Handle);
			else if (tagger[i].find( "puJetIDFull") != std::string::npos)
				cEvent->getByLabel(PUJetID.label(), PUJetID_full.label()+"Id", puJetIDfull_Handle);
			else if (tagger[i].find( "puJetIDCutbased") != std::string::npos)
				cEvent->getByLabel(PUJetID.label(), "cutbasedId", puJetIDcutbased_Handle);
			else
			{
				std::cout << "Tagger '" << tagger[i] << "' not found! " << std::endl;
				exit(1);
			}
		}

		tagmap_b["TrackCountingHighEffBJetTags"] = TrackCountingHighEffBJetTags_Handle;
		tagmap_b["TrackCountingHighPurBJetTags"] = TrackCountingHighPurBJetTags_Handle;
		tagmap_b["JetProbabilityBJetTags"] = JetProbabilityBJetTags_Handle;
		tagmap_b["JetBProbabilityBJetTags"] = JetBProbabilityBJetTags_Handle;
		tagmap_b["SoftElectronBJetTags"] = SoftElectronBJetTags_Handle;
		tagmap_b["SoftMuonBJetTags"] = SoftMuonBJetTags_Handle;
		tagmap_b["SoftMuonByIP3dBJetTags"] = SoftMuonByIP3dBJetTags_Handle;
		tagmap_b["SoftMuonByPtBJetTags"] = SoftMuonByPtBJetTags_Handle;
		tagmap_b["SimpleSecondaryVertexBJetTags"] = SimpleSecondaryVertexBJetTags_Handle;
		tagmap_b["CombinedSecondaryVertexBJetTags"] = CombinedSecondaryVertexBJetTags_Handle;
		tagmap_b["CombinedSecondaryVertexMVABJetTags"] = CombinedSecondaryVertexMVABJetTags_Handle;
		tagmap_qg["QGlikelihood"] = QGTagsHandleLikelihood;
		tagmap_qg["QGmlp"] = QGTagsHandleMLP;
		tagmap_pu["puJetIDFullDiscriminant"] = puJetIDfullDiscriminant_Handle;
		tagmap_pu["puJetIDCutbasedDiscriminant"] = puJetIDcutbasedDiscriminant_Handle;

		// Continue normally
		KBaseMultiLVProducer<reco::PFJetCollection, KJets>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::PFJetCollection>(handle, this->nCursor));

		std::vector<bool> puJetID;

		for (size_t i = 0; i < tagger.size(); ++i)
		{
			if ( (tagger[i] == "QGlikelihood") || (tagger[i] == "QGmlp"))
				out.tags.push_back(getvalue( (*tagmap_qg[tagger[i]])[jetRef] ) );
			else if ((tagger[i] == "puJetIDFullDiscriminant") || (tagger[i] == "puJetIDCutbasedDiscriminant"))
				out.tags.push_back(getsignedvalue( (*tagmap_pu[tagger[i]])[jetRef] ) );
			else if (tagger[i] == "puJetIDFullLoose")
				puJetID.push_back(( (*puJetIDfull_Handle)[jetRef] & (1 << 2) ) != 0);
			else if (tagger[i] == "puJetIDFullMedium")
				puJetID.push_back(( (*puJetIDfull_Handle)[jetRef] & (1 << 1) ) != 0);
			else if (tagger[i] == "puJetIDFullTight")
				puJetID.push_back(( (*puJetIDfull_Handle)[jetRef] & (1 << 0) ) != 0);
			else if (tagger[i] == "puJetIDCutbasedLoose")
				puJetID.push_back(( (*puJetIDcutbased_Handle)[jetRef] & (1 << 2) ) != 0);
			else if (tagger[i] == "puJetIDCutbasedMedium")
				puJetID.push_back(( (*puJetIDcutbased_Handle)[jetRef] & (1 << 1) ) != 0);
			else if (tagger[i] == "puJetIDCutbasedTight")
				puJetID.push_back(( (*puJetIDcutbased_Handle)[jetRef] & (1 << 0) ) != 0);
			else if (tagger[i] == "puJetIDMET")
				puJetID.push_back(( (*puJetIDMET_Handle)[jetRef] & (1 << 2) ) != 0);
			else
			{
				const reco::JetTagCollection & tags = *(tagmap_b[tagger[i]].product());
				out.tags.push_back(getvalue( tags[this->nCursor].second ) );
			}
		}

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
#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION < 3) || (CMSSW_MAJOR_VERSION < 7)
			in.HFHadronEnergyFraction() +
#endif
			in.HFEMEnergyFraction();
		out.neutralHadronFraction = in.neutralHadronEnergyFraction() / sumFractions;
		out.chargedHadronFraction = in.chargedHadronEnergyFraction() / sumFractions;
		out.muonFraction = in.muonEnergyFraction() / sumFractions;
		out.photonFraction = in.photonEnergyFraction() / sumFractions;
		out.electronFraction = in.electronEnergyFraction() / sumFractions;
		out.hfHadronFraction = in.HFHadronEnergyFraction() / sumFractions;
		out.hfEMFraction = in.HFEMEnergyFraction() / sumFractions;

		// JEC factor (a member of PFJet would be better, but if everything is right, this should be equivalent)
		out.correction = sumFractions;

// energy fraction definitions have changed in CMSSW 7.3.X
// fractions should add up to unity
#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 3) || (CMSSW_MAJOR_VERSION > 7) 
		assert(out.neutralHadronFraction >= out.hfHadronFraction);
		assert(std::abs(out.neutralHadronFraction + out.chargedHadronFraction +
			out.muonFraction + out.photonFraction + out.electronFraction +
			out.hfEMFraction - 1.0f) < 0.001f);
#else
		assert(std::abs(out.neutralHadronFraction + out.chargedHadronFraction +
			out.muonFraction + out.photonFraction + out.electronFraction +
			out.hfHadronFraction + out.hfEMFraction - 1.0f) < 0.001f);
#endif
		assert(std::abs(in.neutralEmEnergyFraction() - in.photonEnergyFraction() -
			in.HFEMEnergyFraction()) < 0.001f);
		assert(std::abs(in.chargedEmEnergyFraction() - in.electronEnergyFraction()) < 0.001f);
	}

private:
	std::vector<std::string> tagger;

	KJetMetadata *names;

	std::map< std::string, edm::Handle<edm::ValueMap<float>> > tagmap_qg;
	std::map< std::string, edm::Handle<edm::ValueMap<float>> > tagmap_pu;
	std::map< std::string, edm::Handle<reco::JetTagCollection> > tagmap_b;

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

	static constexpr float default_for_not_defined_tagger_value = -999.;

	float getvalue(const float value){ return (value<0.) ? default_for_not_defined_tagger_value : value; }
	float getsignedvalue(const float value){ return value; }

};

#endif

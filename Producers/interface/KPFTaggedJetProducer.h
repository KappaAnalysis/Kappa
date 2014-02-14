#ifndef KAPPA_PFTAGGEDJETPRODUCER_H
#define KAPPA_PFTAGGEDJETPRODUCER_H

#include "KPFJetProducer.h"
#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KJetMET.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/BTauReco/interface/JetTag.h>

class KPFTaggedJetProducer : public KBaseMultiLVProducer<reco::PFJetCollection, KDataPFTaggedJets>
{
public:
	KPFTaggedJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<reco::PFJetCollection, KDataPFTaggedJets>(cfg, _event_tree, _run_tree, getLabel()),
		 tagger(cfg.getParameter<std::vector<std::string> >("taggers"))
{
		names = new KTaggerMetadata;
		_run_tree->Bronch("KTaggerMetadata", "KTaggerMetadata", &names);
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
				names->pujetidnames.push_back(tagger[i]);
			else
				names->taggernames.push_back(tagger[i]);
		}
		return KBaseMultiLVProducer<reco::PFJetCollection, KDataPFTaggedJets>::onLumi(lumiBlock, setup);
	}

	static const std::string getLabel() { return "PFTaggedJets"; }

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

		// Continue normally
		KBaseMultiLVProducer<reco::PFJetCollection, KDataPFTaggedJets>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::PFJetCollection>(handle, this->nCursor));

		std::vector<bool> puJetID;

		for (size_t i = 0; i < tagger.size(); ++i)
		{
			if ( (tagger[i] == "QGlikelihood") || (tagger[i] == "QGmlp"))
				out.taggers.push_back(getvalue( (*tagmap_qg[tagger[i]])[jetRef] ) );
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
				out.taggers.push_back(getvalue( tags[this->nCursor].second ) );
			}
		}

		for (unsigned int i = 0; i < puJetID.size(); ++i)
			out.puJetID |= puJetID[i] << i;		

		// PF variables:
		copyP4(in, out.p4);

		out.area = in.jetArea();
		out.nConst = in.nConstituents();
		out.nCharged = in.chargedMultiplicity();
		out.neutralEMFraction = in.neutralEmEnergyFraction();
		out.chargedEMFraction = in.chargedEmEnergyFraction();
		out.neutralHadFraction = in.neutralHadronEnergyFraction();
		out.chargedHadFraction = in.chargedHadronEnergyFraction();
		out.muonFraction = in.muonEnergyFraction();
		out.photonFraction = in.photonEnergyFraction();
		out.electronFraction = in.electronEnergyFraction();
		out.HFHadFraction = in.HFHadronEnergyFraction();
		out.HFEMFraction = in.HFEMEnergyFraction();
	}

private:
	std::vector<std::string> tagger;

	KTaggerMetadata *names;

	std::map< std::string, edm::Handle<edm::ValueMap<float>> > tagmap_qg;
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

	static constexpr float default_for_not_defined_tagger_value = -999.;

	float getvalue(const float value){ return (value<0.) ? default_for_not_defined_tagger_value : value; }

};

#endif

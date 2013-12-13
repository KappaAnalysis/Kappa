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
		KBaseMultiLVProducer<reco::PFJetCollection, KDataPFTaggedJets>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "PFTaggedJets"; }

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{

        QGtagger = pset.getParameter<edm::InputTag>("QGtagger");
        if (QGtagger.label() != "")
		{	
            cEvent->getByLabel(QGtagger.label(),"qgMLP", QGTagsHandleMLP);
            cEvent->getByLabel(QGtagger.label(),"qgLikelihood", QGTagsHandleLikelihood);
        }


        Btagger = pset.getParameter<edm::InputTag>("Btagger");
        if (Btagger.label() != "")
        {
            cEvent->getByLabel(Btagger.label()+"TrackCountingHighEffBJetTags",
                        TrackCountingHighEffBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"TrackCountingHighPurBJetTags",
                        TrackCountingHighPurBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"JetProbabilityBJetTags",
                        JetProbabilityBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"JetBProbabilityBJetTags",
                        JetBProbabilityBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"SoftElectronBJetTags",
                        SoftElectronBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"SoftMuonBJetTags",
                        SoftMuonBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"SoftMuonByIP3dBJetTags",
                        SoftMuonByIP3dBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"SoftMuonByPtBJetTags",
                        SoftMuonByPtBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"SimpleSecondaryVertexBJetTags",
                        SimpleSecondaryVertexBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"CombinedSecondaryVertexBJetTags",
                        CombinedSecondaryVertexBJetTags_Handle);
            cEvent->getByLabel(Btagger.label()+"CombinedSecondaryVertexMVABJetTags",
                        CombinedSecondaryVertexMVABJetTags_Handle);
        }

        PUJetID = pset.getParameter<edm::InputTag>("PUJetID");
        PUJetID_full = pset.getParameter<edm::InputTag>("PUJetID_full");
        if (PUJetID.label() != "")
        {
            cEvent->getByLabel(PUJetID.label(), PUJetID_full.label()+"Discriminant", puJetMVAfull_Handle);
            cEvent->getByLabel(PUJetID.label(), PUJetID_full.label()+"Id", puJetIDfull_Handle);

            cEvent->getByLabel(PUJetID.label(), "cutbasedDiscriminant", puJetMVAcutbased_Handle);
            cEvent->getByLabel(PUJetID.label(), "cutbasedId", puJetIDcutbased_Handle);
        }

		// Continue normally
		KBaseMultiLVProducer<reco::PFJetCollection, KDataPFTaggedJets>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{

        // Some of the tagging variable have -1 if undefined, others have -10 or -99 ...
        // -> initialize all tagging variables with -1 and change only if defined


        out.qgLikelihood = -1;
        out.qgMLP = -1;

        out.trackCountingHighEffBTag = -1;
        out.trackCountingHighPurBTag = -1;
        out.jetProbabilityBTag = -1;
        out.jetBProbabilityBTag = -1;
        out.softElectronBTag = -1;
        out.softMuonBTag = -1;
        out.softMuonByIP3dBTag = -1;
        out.softMuonByPtBTag = -1;
        out.simpleSecondaryVertexBTag = -1;
        out.combinedSecondaryVertexBTag = -1;
        out.combinedSecondaryVertexMVABTag = -1;

        out.puJetFull = -1;
        out.puJetIDFull = -1;

        out.puJetCutbased = -1;
        out.puJetIDCutbased = -1;

        // get the QG Tag 
        if (QGtagger.label() != "")
        {   
        	edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::PFJetCollection>(handle, this->nCursor));
            out.qgLikelihood = (*QGTagsHandleLikelihood)[jetRef];
            if ((*QGTagsHandleMLP)[jetRef] != -999.)
                out.qgMLP = (*QGTagsHandleMLP)[jetRef];
        }

        // get the B tags from the according handles
        if (Btagger.label() != "")
        {
            const reco::JetTagCollection & TrackCountingHighEffBJetTags = *(TrackCountingHighEffBJetTags_Handle.product());
            if (TrackCountingHighEffBJetTags[this->nCursor].second != -100.)
                out.trackCountingHighEffBTag = TrackCountingHighEffBJetTags[this->nCursor].second;
            const reco::JetTagCollection & TrackCountingHighPurBJetTags = *(TrackCountingHighPurBJetTags_Handle.product());
            if (TrackCountingHighPurBJetTags[this->nCursor].second != -100.)
                out.trackCountingHighPurBTag = TrackCountingHighPurBJetTags[this->nCursor].second;
            const reco::JetTagCollection & JetProbabilityBJetTags = *(JetProbabilityBJetTags_Handle.product());
                out.jetProbabilityBTag = JetProbabilityBJetTags[this->nCursor].second;
            const reco::JetTagCollection & JetBProbabilityBJetTags = *(JetBProbabilityBJetTags_Handle.product());
                out.jetBProbabilityBTag = JetBProbabilityBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftElectronBJetTags = *(SoftElectronBJetTags_Handle.product());
                out.softElectronBTag = SoftElectronBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftMuonBJetTags = *(SoftMuonBJetTags_Handle.product());
                out.softMuonBTag = SoftMuonBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftMuonByIP3dBJetTags = *(SoftMuonByIP3dBJetTags_Handle.product());
                out.softMuonByIP3dBTag = SoftMuonByIP3dBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftMuonByPtBJetTags = *(SoftMuonByPtBJetTags_Handle.product());
                out.softMuonByPtBTag = SoftMuonByPtBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SimpleSecondaryVertexBJetTags = *(SimpleSecondaryVertexBJetTags_Handle.product());
                out.simpleSecondaryVertexBTag = SimpleSecondaryVertexBJetTags[this->nCursor].second;
            const reco::JetTagCollection & CombinedSecondaryVertexBJetTags = *(CombinedSecondaryVertexBJetTags_Handle.product());
            if (CombinedSecondaryVertexBJetTags[this->nCursor].second != -10.)
                out.combinedSecondaryVertexBTag = CombinedSecondaryVertexBJetTags[this->nCursor].second;
            const reco::JetTagCollection & CombinedSecondaryVertexMVABJetTags = *(CombinedSecondaryVertexMVABJetTags_Handle.product());
            if (CombinedSecondaryVertexMVABJetTags[this->nCursor].second != -10.)
                out.combinedSecondaryVertexMVABTag = CombinedSecondaryVertexMVABJetTags[this->nCursor].second;
        }

        // get the PU-ID and discriminator
        if (PUJetID.label() != "")
        {
        	edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::PFJetCollection>(handle, this->nCursor));

            out.puJetFull = (*puJetMVAfull_Handle)[jetRef];
            out.puJetIDFull = (*puJetIDfull_Handle)[jetRef];

            out.puJetIDFullLoose = (( (*puJetIDfull_Handle)[jetRef] & (1 << 2) ) != 0);
            out.puJetIDFullMedium = (( (*puJetIDfull_Handle)[jetRef] & (1 << 1) ) != 0);
            out.puJetIDFullTight = (( (*puJetIDfull_Handle)[jetRef] & (1 << 0) ) != 0);

            out.puJetCutbased = (*puJetMVAcutbased_Handle)[jetRef];
            out.puJetIDCutbased = (*puJetIDcutbased_Handle)[jetRef];

            out.puJetIDCutbasedLoose = (( (*puJetIDcutbased_Handle)[jetRef] & (1 << 2) ) != 0);
            out.puJetIDCutbasedMedium = (( (*puJetIDcutbased_Handle)[jetRef] & (1 << 1) ) != 0);
            out.puJetIDCutbasedTight = (( (*puJetIDcutbased_Handle)[jetRef] & (1 << 0) ) != 0);

        }

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

    edm::Handle<edm::ValueMap<float> >  QGTagsHandleMLP;
    edm::Handle<edm::ValueMap<float> >  QGTagsHandleLikelihood;

    edm::Handle<edm::ValueMap<float> > puJetMVAfull_Handle;
    edm::Handle<edm::ValueMap<int> > puJetIDfull_Handle;
    edm::Handle<edm::ValueMap<float> > puJetMVAcutbased_Handle;
    edm::Handle<edm::ValueMap<int> > puJetIDcutbased_Handle;
};

#endif

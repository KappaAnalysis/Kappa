#ifndef KAPPA_PFJETTAGGEDPRODUCER_H
#define KAPPA_PFJETTAGGEDPRODUCER_H

#include "KPFJetProducer.h"
#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KJetMET.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/BTauReco/interface/JetTag.h>


struct KPFJetTaggedProducer_Product
{
	typedef std::vector<KDataPFJetTagged> type;
	static const std::string id() { return "std::vector<KDataPFJetTagged>"; };
	static const std::string producer() { return "KPFJetTaggedProducer"; };
};

class KPFJetTaggedProducer : public KBaseMultiLVProducer<reco::PFJetCollection, KPFJetTaggedProducer_Product>
{
public:
	KPFJetTaggedProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<reco::PFJetCollection, KPFJetTaggedProducer_Product>(cfg, _event_tree, _run_tree) {}


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
		KBaseMultiLVProducer<reco::PFJetCollection, KPFJetTaggedProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{

        // Some of the tagging variable have -1 if undefined, others have -10 or -99 ...
        // -> initialize all tagging variables with -1 and change only if defined


        out.QGLikelihood = -1;
        out.QGMLP = -1;

        out.TrackCountingHighEffBJetTag = -1;
        out.TrackCountingHighPurBJetTag = -1;
        out.JetProbabilityBJetTag = -1;
        out.JetBProbabilityBJetTag = -1;
        out.SoftElectronBJetTag = -1;
        out.SoftMuonBJetTag = -1;
        out.SoftMuonByIP3dBJetTag = -1;
        out.SoftMuonByPtBJetTag = -1;
        out.SimpleSecondaryVertexBJetTag = -1;
        out.CombinedSecondaryVertexBJetTag = -1;
        out.CombinedSecondaryVertexMVABJetTag = -1;

        out.PUJetMVAfull = -1;
        out.PUJetIDfull = -1;

        out.PUJetMVAcutbased = -1;
        out.PUJetIDcutbased = -1;

        // get the QG Tag 
        if (QGtagger.label() != "")
        {   
        	edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::PFJetCollection>(handle, this->nCursor));
            out.QGLikelihood = (*QGTagsHandleLikelihood)[jetRef];
            if ((*QGTagsHandleMLP)[jetRef] != -999.)
                out.QGMLP = (*QGTagsHandleMLP)[jetRef];
        }

        // get the B tags from the according handles
        if (Btagger.label() != "")
        {
            const reco::JetTagCollection & TrackCountingHighEffBJetTags = *(TrackCountingHighEffBJetTags_Handle.product());
            if (TrackCountingHighEffBJetTags[this->nCursor].second != -100.)
                out.TrackCountingHighEffBJetTag = TrackCountingHighEffBJetTags[this->nCursor].second;
            const reco::JetTagCollection & TrackCountingHighPurBJetTags = *(TrackCountingHighPurBJetTags_Handle.product());
            if (TrackCountingHighPurBJetTags[this->nCursor].second != -100.)
                out.TrackCountingHighPurBJetTag = TrackCountingHighPurBJetTags[this->nCursor].second;
            const reco::JetTagCollection & JetProbabilityBJetTags = *(JetProbabilityBJetTags_Handle.product());
                out.JetProbabilityBJetTag = JetProbabilityBJetTags[this->nCursor].second;
            const reco::JetTagCollection & JetBProbabilityBJetTags = *(JetBProbabilityBJetTags_Handle.product());
                out.JetBProbabilityBJetTag = JetBProbabilityBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftElectronBJetTags = *(SoftElectronBJetTags_Handle.product());
                out.SoftElectronBJetTag = SoftElectronBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftMuonBJetTags = *(SoftMuonBJetTags_Handle.product());
                out.SoftMuonBJetTag = SoftMuonBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftMuonByIP3dBJetTags = *(SoftMuonByIP3dBJetTags_Handle.product());
                out.SoftMuonByIP3dBJetTag = SoftMuonByIP3dBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SoftMuonByPtBJetTags = *(SoftMuonByPtBJetTags_Handle.product());
                out.SoftMuonByPtBJetTag = SoftMuonByPtBJetTags[this->nCursor].second;
            const reco::JetTagCollection & SimpleSecondaryVertexBJetTags = *(SimpleSecondaryVertexBJetTags_Handle.product());
                out.SimpleSecondaryVertexBJetTag = SimpleSecondaryVertexBJetTags[this->nCursor].second;
            const reco::JetTagCollection & CombinedSecondaryVertexBJetTags = *(CombinedSecondaryVertexBJetTags_Handle.product());
            if (CombinedSecondaryVertexBJetTags[this->nCursor].second != -10.)
                out.CombinedSecondaryVertexBJetTag = CombinedSecondaryVertexBJetTags[this->nCursor].second;
            const reco::JetTagCollection & CombinedSecondaryVertexMVABJetTags = *(CombinedSecondaryVertexMVABJetTags_Handle.product());
            if (CombinedSecondaryVertexMVABJetTags[this->nCursor].second != -10.)
                out.CombinedSecondaryVertexMVABJetTag = CombinedSecondaryVertexMVABJetTags[this->nCursor].second;
        }

        // get the PU-ID and discriminator
        if (PUJetID.label() != "")
        {
        	edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::PFJetCollection>(handle, this->nCursor));

            out.PUJetMVAfull = (*puJetMVAfull_Handle)[jetRef];
            out.PUJetIDfull = (*puJetIDfull_Handle)[jetRef];

            out.PUJetIDfull_passloose = (( (*puJetIDfull_Handle)[jetRef] & (1 << 2) ) != 0);
            out.PUJetIDfull_passmedium = (( (*puJetIDfull_Handle)[jetRef] & (1 << 1) ) != 0);
            out.PUJetIDfull_passtight = (( (*puJetIDfull_Handle)[jetRef] & (1 << 0) ) != 0);

            out.PUJetMVAcutbased = (*puJetMVAcutbased_Handle)[jetRef];
            out.PUJetIDcutbased = (*puJetIDcutbased_Handle)[jetRef];

            out.PUJetIDcutbased_passloose = (( (*puJetIDcutbased_Handle)[jetRef] & (1 << 2) ) != 0);
            out.PUJetIDcutbased_passmedium = (( (*puJetIDcutbased_Handle)[jetRef] & (1 << 1) ) != 0);
            out.PUJetIDcutbased_passtight = (( (*puJetIDcutbased_Handle)[jetRef] & (1 << 0) ) != 0);

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

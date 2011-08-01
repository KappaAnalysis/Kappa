#ifndef KAPPA_CALOJETPRODUCER_H
#define KAPPA_CALOJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/JetReco/interface/JetID.h>

struct KCaloJetProducer_Product
{
	typedef std::vector<KDataJet> type;
	static const std::string id() { return "std::vector<KDataJet>"; };
	static const std::string producer() { return "KCaloJetProducer"; };
};

class KCaloJetProducer : public KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>
{
public:
	KCaloJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>(cfg, _event_tree, _run_tree)) {}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		tagJetID = pset.getParameter<edm::InputTag>("srcJetID");
		if (tagJetID.label() != "")
			cEvent->getByLabel(tagJetID, hJetID);

		// Continue normally
		KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJetProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.area = in.jetArea();
		out.fEM = in.emEnergyFraction();
		out.nConst = in.getJetConstituents().size();

		// Jet ID variables
		out.n90Hits = -2;
		out.fHPD = -2;
		out.fRBX = -2;
		out.fHO = -2;
		if (tagJetID.label() != "")
		{
			edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::CaloJetCollection>(handle, this->nCursor));
			const reco::JetID &jetID = (*hJetID)[jetRef];
			out.n90Hits = (int)(jetID.n90Hits);
			// energy fraction from dominant hybrid photo diode
			out.fHPD = jetID.fHPD;
			// energy fraction from dominant readout box
			out.fRBX = jetID.fRBX;
			// energy fraction in HO
			out.fHO = jetID.fHO;
		}
	}

private:
	edm::InputTag tagJetID;
	edm::Handle<edm::ValueMap<reco::JetID> > hJetID;
};

#endif

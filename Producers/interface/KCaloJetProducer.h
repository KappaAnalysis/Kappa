//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Danilo Piparo <danilo.piparo@cern.ch>
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_CALOJETPRODUCER_H
#define KAPPA_CALOJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/JetReco/interface/JetID.h>

class KCaloJetProducer : public KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJets>
{
public:
	KCaloJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJets>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "CaloJets"; }

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		//tagJetID = pset.getParameter<edm::InputTag>("srcJetID");
		//if (tagJetID.label() != "")
		//	cEvent->getByLabel(tagJetID, hJetID);

		// Continue normally
		KBaseMultiLVProducer<reco::CaloJetCollection, KCaloJets>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
		out.area = in.jetArea();
		out.fEM = in.emEnergyFraction();
		out.nConstituents = in.getJetConstituents().size();

		// Jet ID variables
		out.n90Hits = -2;
		out.fHPD = -2;
		out.fRBX = -2;
		out.fHO = -2;
		//if (tagJetID.label() != "")
		//{
		//	edm::RefToBase<reco::Jet> jetRef(edm::Ref<reco::CaloJetCollection>(handle, this->nCursor));
		//	const reco::JetID &jetID = (*hJetID)[jetRef];
		//	out.n90Hits = static_cast<int>(jetID.n90Hits);
		//	out.fHPD = jetID.fHPD;
		//	out.fRBX = jetID.fRBX;
		//	out.fHO = jetID.fHO;
		//}
	}

private:
	//edm::InputTag tagJetID;
	//edm::Handle<edm::ValueMap<reco::JetID> > hJetID;
};

#endif

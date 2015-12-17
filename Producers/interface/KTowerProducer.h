//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_TOWERPRODUCER_H
#define KAPPA_TOWERPRODUCER_H

#include "KBaseMultiProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/VertexReco/interface/Vertex.h>
#include <DataFormats/VertexReco/interface/VertexFwd.h>
#include <FWCore/Framework/interface/EDProducer.h>

class KTowerProducer : public KBaseMultiLVProducer<CaloTowerCollection, KLVs>
{
public:
	KTowerProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<CaloTowerCollection, KLVs>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		srcPVs(cfg.getParameter<edm::InputTag>("srcPVs")) {}

	static const std::string getLabel() { return "Tower"; }

protected:
	edm::InputTag srcPVs;

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Get information for vertex correction
		edm::Handle<reco::VertexCollection> pvCollection;
		cEvent->getByLabel(srcPVs, pvCollection);
		if (pvCollection->size() > 0)
			vertex = pvCollection->begin()->position();
		else
			vertex = reco::Jet::Point(0, 0, 0);

		KBaseMultiVectorProducer<CaloTowerCollection, KLVs>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		math::PtEtaPhiMLorentzVector ct(in.p4(vertex));
		copyP4(ct, out.p4);
	}

private:
	reco::Jet::Point vertex;
	KLVSorter<KLV> towersorter_pt;
};

#endif

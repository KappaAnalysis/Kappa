#ifndef KAPPA_TOWERPRODUCER_H
#define KAPPA_TOWERPRODUCER_H

#include "KBaseMultiProducer.h"
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/VertexReco/interface/Vertex.h>
#include <DataFormats/VertexReco/interface/VertexFwd.h>

struct KTowerProducer_Product
{
	typedef std::vector<KDataLV> type;
	static const std::string id() { return "std::vector<KDataLV>"; };
	static const std::string producer() { return "KTowerProducer"; };
};

class KTowerProducer : public KBaseMultiLVProducer<CaloTowerCollection, KTowerProducer_Product>
{
public:
	KTowerProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<CaloTowerCollection, KTowerProducer_Product>(cfg, _event_tree, _run_tree),
		srcPVs(cfg.getParameter<edm::InputTag>("srcPVs")) {}
	virtual ~KTowerProducer() {};

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

		KBaseMultiVectorProducer<reco::CaloJetCollection, KCaloJetProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		math::PtEtaPhiMLorentzVector ct(in.p4(vertex));
		copyP4(ct, output.p4);
	}

private:
	reco::Jet::Point vertex;
	KLVSorter<KDataLV> towersorter_pt;
};

#endif

#ifndef KAPPA_PFJETPRODUCER_H
#define KAPPA_PFJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/PFJet.h>

struct KPFJetProducer_Product
{
	typedef std::vector<KDataPFJet> type;
	static const std::string id() { return "std::vector<KDataPFJet>"; };
	static const std::string producer() { return "KPFJetProducer"; };
};

class KPFJetProducer : public KRegexMultiLVProducer<reco::PFJetCollection, KPFJetProducer_Product>
{
public:
	KPFJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KRegexMultiLVProducer<reco::PFJetCollection, KPFJetProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);

		out.emf = in.neutralEmEnergyFraction() + in.chargedEmEnergyFraction();
		out.area = in.jetArea();;
		out.n90 = in.nCarrying(0.9);
		out.n90Hits = -1;
		out.noiseHCAL = -1;
		out.detectorEta = in.detectorP4(in.vertex(), in).eta();
		out.fHPD = -1.;
		out.fRBX = -1.;
		out.nTracksAtCalo = -1;
		out.nTracksAtVertex = -1;
		out.nConst = in.nConstituents();
		out.neutralEmFraction = in.neutralEmEnergyFraction();
		out.chargedEmFraction = in.chargedEmEnergyFraction();
		out.neutralHadFraction = in.neutralHadronEnergyFraction();
		out.chargedHadFraction = in.chargedHadronEnergyFraction();
	}
};

#endif

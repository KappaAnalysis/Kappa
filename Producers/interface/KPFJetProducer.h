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

class KPFJetProducer : public KBaseMultiLVProducer<reco::PFJetCollection, KPFJetProducer_Product>
{
public:
	KPFJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<reco::PFJetCollection, KPFJetProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
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
};

#endif

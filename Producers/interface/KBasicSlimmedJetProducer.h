//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Fabio Colombo <fabio.colombo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Hauth <Thomas.Hauth@cern.ch>

#ifndef KAPPA_BASICJETPRODUCER_H
#define KAPPA_BASICJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/PFJet.h>

class KBasicJetProducer : public KBaseMultiLVProducer<reco::PFJetCollection, std::vector<KBasicJet> >
{
public:
	KBasicJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<reco::PFJetCollection, KBasicJets>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "BasicJets"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);

		out.area = in.jetArea();
		out.nConstituents = in.nConstituents();
		out.nCharged = in.chargedMultiplicity();
		out.neutralHadronFraction = in.neutralHadronEnergyFraction();
		out.chargedHadronFraction = in.chargedHadronEnergyFraction();
		out.muonFraction = in.muonEnergyFraction();
		out.photonFraction = in.photonEnergyFraction();
		out.electronFraction = in.electronEnergyFraction();
		out.hfHadronFraction = in.HFHadronEnergyFraction();
		out.hfEMFraction = in.HFEMEnergyFraction();
	}
};

#endif

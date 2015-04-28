//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Fabio Colombo <fabio.colombo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Hauth <Thomas.Hauth@cern.ch>

#ifndef KAPPA_PATJETPRODUCER_H
#define KAPPA_PATJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KGenJetProducer.h"
#include <DataFormats/PatCandidates/interface/Jet.h>

class KPatJetProducer : public KBaseMultiLVProducer<edm::View<pat::Jet>, KJets >
{
public:
	KPatJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<pat::Jet>, KJets>(cfg, _event_tree, _run_tree, getLabel())
	{
		genJet = new KGenJet;
		_event_tree->Bronch("genJet", "KGenJet", &genJet);
	}

	static const std::string getLabel() { return "PatJets"; }

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


		//write out generator information
		//todo: catch if some daughters of genJets are not in genParticles collection
		//in this case, the determination of the decay mode fails and the cmsRun exits with "product not found"
		/*
		const reco::GenJet* recoGenJet = in.genJet();
		if (recoGenJet == NULL) // catch if null pointer is delivered from pat::Jet::genJet() and use an empty GenJet instead
			recoGenJet = new reco::GenJet;
		std::cout << recoGenJet->isJet() << std::endl;
		KGenJetProducer::fillGenJet(*recoGenJet, *genJet); */
	}
private:
	KGenJet* genJet;

};

#endif

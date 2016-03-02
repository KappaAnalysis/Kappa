//- Copyright (c) 2015 - All Rights Reserved
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_GENJETPRODUCER_H
#define KAPPA_GENJETPRODUCER_H

#include "DataFormats/JetReco/interface/GenJet.h"
#include "PhysicsTools/JetMCUtils/interface/JetMCTag.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

#include "KBaseMultiLVProducer.h"


class KGenJetProducer : public KBaseMultiLVProducer<edm::View<reco::GenJet>, KGenJets>
{
public:
	KGenJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<reco::GenJet>, KGenJets>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector))
	{
	}

	static const std::string getLabel() { return "GenJets"; }

	static bool allDaughtersValid(const SingleInputType &in)
	{
		const auto daughters = in.daughterPtrVector();
		for ( auto daughter : daughters )
		{
			if (!daughter.isNonnull())
				return false;
		}
		return true;
	}

	static void fillGenJet(const SingleInputType &in, SingleOutputType &out)
	{	/// momentum:
		copyP4(in, out.p4);
		// check if inputs are valid. Status April 15: Some miniAOD samples do not fill their daughters properly
		std::string genTauDecayModeString = allDaughtersValid(in) ? JetMCTagUtils::genTauDecayMode(in) : "invalid";
		if      (genTauDecayModeString == "oneProng0Pi0")     out.genTauDecayMode = 0;
		else if (genTauDecayModeString == "oneProng1Pi0")     out.genTauDecayMode = 1;
		else if (genTauDecayModeString == "oneProng2Pi0")     out.genTauDecayMode = 2;
		else if (genTauDecayModeString == "oneProngOther")    out.genTauDecayMode = 7;
		else if (genTauDecayModeString == "threeProng0Pi0")   out.genTauDecayMode = 3;
		else if (genTauDecayModeString == "threeProng1Pi0")   out.genTauDecayMode = 4;
		else if (genTauDecayModeString == "threeProngOther")  out.genTauDecayMode = 8;
		else if (genTauDecayModeString == "electron")         out.genTauDecayMode = 5;
		else if (genTauDecayModeString == "muons")            out.genTauDecayMode = 6;
		else out.genTauDecayMode = -1;
	}


	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		fillGenJet(in, out);
	}
};

#endif

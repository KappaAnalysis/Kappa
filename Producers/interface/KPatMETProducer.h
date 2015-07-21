//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_PATMETPRODUCER_H
#define KAPPA_PATMETPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KBasicMETProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/PFMET.h>
#include <DataFormats/PatCandidates/interface/MET.h>
#include "Kappa/DataFormats/interface/Hash.h"

class KPatMETProducer : public KBaseMultiLVProducer<edm::View<pat::MET>, KMETs>
{
public:
	KPatMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<pat::MET>, KMETs>(cfg, _event_tree, _run_tree, getLabel()) {
		genMet = new KBasicMET;
		_event_tree->Bronch("genmetTrue", "KBasicMET", &genMet);
	}

	static const std::string getLabel() { return "PatMET"; }

	//virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// fill GenMET
		if(in.size() == 0) return;

		if(in.at(0).genMET())
		{
			const reco::GenMET* recoGenMet = in.at(0).genMET();
			KBasicMETProducer::fillMET<reco::GenMET>(*recoGenMet, *genMet);
		}
		KBaseMultiLVProducer<edm::View<pat::MET>, KMETs>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KBasicMETProducer::fillMET<pat::MET>(in, out);
		if(in.isPFMET())
		{
			// additional PF properties
			out.photonFraction = in.NeutralEMFraction(); // Todo: check if equivalent to photonEtFraction
			out.neutralHadronFraction = in.NeutralHadEtFraction();
			out.electronFraction = in.ChargedEMEtFraction();
			out.chargedHadronFraction = in.ChargedHadEtFraction();
			out.muonFraction = in.MuonEtFraction();
			out.hfHadronFraction = in.Type6EtFraction();
			out.hfEMFraction = in.Type7EtFraction();
		}
		// save references to lepton selection from MVA MET
		int hash = 0;
		for(auto name: in.userCandNames())
		{
			reco::CandidatePtr aRecoCand = in.userCand( name );
			hash = hash ^ getLVChargeHash( aRecoCand->p4().Pt(),
				                           aRecoCand->p4().Eta(),
				                           aRecoCand->p4().Phi(),
				                           aRecoCand->p4().M(),
				                           aRecoCand->charge() );
		}
		out.leptonSelectionHash = hash;
	}

private:
	TTree* _event_tree_pointer;
	KBasicMET* genMet;
};

#endif

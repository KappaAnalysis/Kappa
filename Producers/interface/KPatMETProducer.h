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

class KPatMETProducer : public KBaseMultiProducer<edm::View<pat::MET>, KMET>
{
public:
	KPatMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<pat::MET>, KMET>(cfg, _event_tree, _run_tree, getLabel()) {
		genMet = new KBasicMET;
		_event_tree->Bronch("genmetTrue", "KBasicMET", &genMet);
	}

	static const std::string getLabel() { return "PatMET"; }

	static void fillMET(const pat::MET &in, KMET &out)
	{
		// fill properties of basic MET
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
	}

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() != 1)
		{
			if (verbosity > 1)
				std::cout << "KMETProducer::fillProduct: Found " << in.size() << " pat::MET objects!" << std::endl;
			return;
		}

		fillMET(in.at(0), out);
		// fill GenMET
		if(in.at(0).genMET())
		{
			const reco::GenMET* recoGenMet = in.at(0).genMET();
			KBasicMETProducer::fillMET<reco::GenMET>(*recoGenMet, *genMet);
		}
	}

private:
	TTree* _event_tree_pointer;
	KBasicMET* genMet;
};

#endif

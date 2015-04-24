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

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() == 1)
		{
			// fill properties of basic MET
			KBasicMETProducer::fillMET<pat::MET>(in.at(0), out);
			if(in.at(0).isPFMET())
			{
				// additional PF properties
				out.photonFraction = in.at(0).NeutralEMFraction(); // Todo: check if equivalent to photonEtFraction
				out.neutralHadronFraction = in.at(0).NeutralHadEtFraction();
				out.electronFraction = in.at(0).ChargedEMEtFraction();
				out.chargedHadronFraction = in.at(0).ChargedHadEtFraction();
				out.muonFraction = in.at(0).MuonEtFraction();
				out.hfHadronFraction = in.at(0).Type6EtFraction();
				out.hfEMFraction = in.at(0).Type7EtFraction();
			}

			//fill GenMET
			const reco::GenMET* recoGenMet = in.at(0).genMET();
			KBasicMETProducer::fillMET<reco::GenMET>(*recoGenMet, *genMet);

		}
		else if (verbosity > 1)
			std::cout << "KMETProducer::fillProduct: Found " << in.size() << " pat::MET objects!" << std::endl;
	}
private:
	TTree* _event_tree_pointer;
	KBasicMET* genMet;
};

#endif

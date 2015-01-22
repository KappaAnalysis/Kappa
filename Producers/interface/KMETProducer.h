//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_METPRODUCER_H
#define KAPPA_METPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KBasicMETProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/PFMET.h>

class KMETProducer : public KBaseMultiProducer<edm::View<reco::PFMET>, KMET>
{
public:
	KMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::PFMET>, KMET>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "MET"; }

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() == 1)
		{
			// fill properties of basic MET
			KBasicMETProducer::fillMET<InputType>(in, out);

			// additional PF properties
			out.photonFraction = in.at(0).photonEtFraction();
			out.neutralHadronFraction = in.at(0).neutralHadronEtFraction();
			out.electronFraction = in.at(0).electronEtFraction();
			out.chargedHadronFraction = in.at(0).chargedHadronEtFraction();
			out.muonFraction = in.at(0).muonEtFraction();
			out.hfHadronFraction = in.at(0).HFHadronEtFraction();
			out.hfEMFraction = in.at(0).HFEMEtFraction();
		}
		else if (verbosity > 1)
			std::cout << "KMETProducer::fillProduct: Found " << in.size() << " PFMET objects!" << std::endl;
	}
};

#endif

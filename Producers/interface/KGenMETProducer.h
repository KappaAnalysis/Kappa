//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_GENMETPRODUCER_H
#define KAPPA_GENMETPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KMETProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include <DataFormats/METReco/interface/MET.h>

class KGenMETProducer : public KBaseMultiProducer<edm::View<reco::MET>, KMET>
{
public:
	KGenMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<edm::View<reco::MET>, KMET>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "GenMET"; }

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() == 1)
			KMETProducer::fillMET<reco::MET>(in.at(0), out);
		else if (verbosity > 1)
			std::cout << "KGenMETProducer::fillProduct: Found " << in.size() << " MET objects!" << std::endl;
	}
};

#endif

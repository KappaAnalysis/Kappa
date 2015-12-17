//- Copyright (c) 2011 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>

#ifndef KAPPA_JETAREAPRODUCER_H
#define KAPPA_JETAREAPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KJetMET.h"
#include "../../DataFormats/interface/KDebug.h"
#include <FWCore/Framework/interface/EDProducer.h>

class KPileupDensityProducer : public KBaseMultiProducer<double, KPileupDensity>
{
public:
	KPileupDensityProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<double, KPileupDensity>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "PileupDensity"; }

protected:
	virtual void clearProduct(OutputType &output) { output.rho = 0; output.sigma = 0; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.rho = in;

		edm::InputTag tmpLabel(tag->label(), "sigma", tag->process());
		edm::Handle<double> hSigma;
		if (this->cEvent->getByLabel(tmpLabel, hSigma))
			out.sigma = *hSigma;
		else
			out.sigma = 0;
	}
};

#endif

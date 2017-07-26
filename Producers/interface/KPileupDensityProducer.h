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
#include "../../Producers/interface/Consumes.h"

class KPileupDensityProducer : public KBaseMultiProducer<double, KPileupDensity>
{
public:
	KPileupDensityProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<double, KPileupDensity>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "PileupDensity"; }

protected:
	virtual void clearProduct(OutputType &output) { output.rho = 0; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.rho = in;
	}
};

#endif

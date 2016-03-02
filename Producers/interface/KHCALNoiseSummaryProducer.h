//- Copyright (c) 2012 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>

#ifndef KAPPA_HCALNOISEPRODUCER_H
#define KAPPA_HCALNOISEPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/HcalNoiseSummary.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KHCALNoiseSummaryProducer : public KBaseMultiProducer<HcalNoiseSummary, KHCALNoiseSummary>
{
public:
	KHCALNoiseSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<HcalNoiseSummary, KHCALNoiseSummary>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "HCALNoiseSummary"; }

protected:
	virtual void clearProduct(OutputType &output)
	{
		output.hasBadRBXTS4TS5 = false;
		output.isolatedNoiseSumE = -1;
		output.isolatedNoiseSumEt = -1;
		output.max25GeVHitTime = -1;
		output.maxE2Over10TS = -1;
		output.maxHPDHits = -1;
		output.maxHPDNoOtherHits = -1;
		output.maxRBXHits = -1;
		output.maxZeros = -1;
		output.min25GeVHitTime = -1;
		output.minE2Over10TS = -1;
		output.minRBXEMF = -1;
		output.numIsolatedNoiseChannels = -1;
	}

	virtual void fillProduct(const InputType &input, OutputType &output,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		output.hasBadRBXTS4TS5 = input.HasBadRBXTS4TS5();
		output.isolatedNoiseSumE = input.isolatedNoiseSumE();
		output.isolatedNoiseSumEt = input.isolatedNoiseSumEt();
		output.max25GeVHitTime = input.max25GeVHitTime();
		output.maxE2Over10TS = input.maxE2Over10TS();
		output.maxHPDHits = input.maxHPDHits();
		output.maxHPDNoOtherHits = input.maxHPDNoOtherHits();
		output.maxRBXHits = input.maxRBXHits();
		output.maxZeros = input.maxZeros();
		output.min25GeVHitTime = input.min25GeVHitTime();
		output.minE2Over10TS = input.minE2Over10TS();
		output.minRBXEMF = input.minRBXEMF();
		output.numIsolatedNoiseChannels = input.numIsolatedNoiseChannels();
	}
};

#endif

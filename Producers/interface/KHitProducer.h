//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_HITPRODUCER_H
#define KAPPA_HITPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <SimDataFormats/TrackingHit/interface/PSimHit.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KHitProducer : public KBaseMultiVectorProducer<edm::View<PSimHit>, KHits>
{
public:
	KHitProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiVectorProducer<edm::View<PSimHit>, KHits>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "Hits"; }

protected:
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		out.theta = in.thetaAtEntry();
		out.phi = in.phiAtEntry();
		out.pAbs = in.pabs();
		out.energyLoss = in.energyLoss();
	}
};

#endif

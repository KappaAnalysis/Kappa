//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>

#ifndef KAPPA_BEAMSPOTPRODUCER_H
#define KAPPA_BEAMSPOTPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"
#include <DataFormats/BeamSpot/interface/BeamSpot.h>

class KBeamSpotProducer : public KBaseMultiProducer<reco::BeamSpot, KBeamSpot>
{
public:
	KBeamSpotProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<reco::BeamSpot, KBeamSpot>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}
	virtual ~KBeamSpotProducer() {};

	static const std::string getLabel() { return "BeamSpot"; }

protected:
	virtual void clearProduct(OutputType &output) { output.position.SetCoordinates(0, 0, 0); output.type = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.position = in.position();
		out.type = in.type();

		out.betaStar = in.betaStar();
		out.beamWidthX = in.BeamWidthX();
		out.beamWidthY = in.BeamWidthY();
		out.emittanceX = in.emittanceX();
		out.emittanceY = in.emittanceY();

		out.dxdz	 = in.dxdz();
		out.dydz	 = in.dydz();
		out.sigmaZ = in.sigmaZ();

		out.covariance = in.covariance();
	}
};

#endif

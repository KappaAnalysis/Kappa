/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 */

#ifndef KAPPA_LORENTZPRODUCER_H
#define KAPPA_LORENTZPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/METReco/interface/HcalNoiseRBX.h>
#include <DataFormats/TrackReco/interface/Track.h>

class KLorentzProducer : public KBaseMultiLVProducer<edm::View<reco::Candidate>, KDataLVs>
{
public:
	KLorentzProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::Candidate>, KDataLVs>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "LV"; }

protected:
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
	}
};

#endif

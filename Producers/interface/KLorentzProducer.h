//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_LORENTZPRODUCER_H
#define KAPPA_LORENTZPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/METReco/interface/HcalNoiseRBX.h>
#include <DataFormats/TrackReco/interface/Track.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KLorentzProducer : public KBaseMultiLVProducer<edm::View<reco::Candidate>, KLVs>
{
public:
	KLorentzProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<reco::Candidate>, KLVs>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "LV"; }

protected:
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);
	}
};

#endif

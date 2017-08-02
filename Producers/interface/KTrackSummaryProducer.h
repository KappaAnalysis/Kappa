//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_TRACKSUMMARYPRODUCER_H
#define KAPPA_TRACKSUMMARYPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/TrackReco/interface/Track.h>
#include <FWCore/Framework/interface/EDProducer.h>

class KTrackSummaryProducer : public KBaseMultiProducer<edm::View<reco::Track>, KTrackSummary>
{
public:
	KTrackSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<edm::View<reco::Track>, KTrackSummary>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "TrackSummary"; }

	virtual void clearProduct(OutputType &output)
	{
		output.nTracks = 0;
		output.nTracksHQ = 0; 
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.nTracks = in.size();
		InputType::const_iterator lvit;
		for (lvit = in.begin(); lvit < in.end(); ++lvit)
			if (lvit->qualityMask() & KTrackQuality::highPurity)
				++out.nTracksHQ;
	}
};

#endif

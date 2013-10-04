/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 */

#ifndef KAPPA_TRACKSUMMARYPRODUCER_H
#define KAPPA_TRACKSUMMARYPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/TrackReco/interface/Track.h>

struct KTrackSummaryProducer_Product
{
	typedef KTrackSummary type;
	static const std::string id() { return "KTrackSummary"; };
	static const std::string producer() { return "KTrackSummaryProducer"; };
};

class KTrackSummaryProducer : public KBaseMultiProducer<edm::View<reco::Track>, KTrackSummaryProducer_Product>
{
public:
	KTrackSummaryProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::Track>, KTrackSummaryProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void clearProduct(OutputType &output) { output.nTracks = 0; output.nTracksHQ = 0; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.nTracks = in.size();
		InputType::const_iterator lvit;
		for (lvit = in.begin(); lvit < in.end(); ++lvit)
			if (lvit->qualityMask() & TQ_HighPurity)
				++out.nTracksHQ;
	}
};

#endif

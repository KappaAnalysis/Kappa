//- Copyright (c) 2010 - All Rights Reserved
//-  * Danilo Piparo <danilo.piparo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_TRACKPRODUCER_H
#define KAPPA_TRACKPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/TrackReco/interface/Track.h>
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KTrackProducer : public KBaseMultiLVProducer<edm::View<reco::Track>, KTracks>
{
public:
	KTrackProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<reco::Track>, KTracks>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "Tracks"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KTrackProducer::fillTrack(in, out);
	}

	// Static method for filling Tracks in other producers
	static void fillTrack(const SingleInputType &in, SingleOutputType &out, std::vector<reco::Vertex> vertices = std::vector<reco::Vertex>(), edm::ESHandle<TransientTrackBuilder> builder = edm::ESHandle<TransientTrackBuilder>())
	{
		// Momentum:
		out.p4.SetCoordinates(in.pt(), in.eta(), in.phi(), 0);
		out.errPt = in.ptError();
		out.errEta = in.etaError();
		out.errPhi = in.phiError();

		// Reference point:
		out.ref = in.referencePoint();

		// Charge, ...
		out.charge = in.charge();
		out.chi2 = in.chi2();
		out.nDOF = in.ndof();
		out.qualityBits = in.qualityMask();
		out.errDxy = in.dxyError();
		out.errDz = in.dzError();

		// hit pattern information
		out.nValidPixelHits = in.hitPattern().numberOfValidPixelHits();
		out.nValidStripHits = in.hitPattern().numberOfValidStripHits();
		out.nValidMuonHits = in.hitPattern().numberOfValidMuonHits();
		out.nPixelLayers = in.hitPattern().pixelLayersWithMeasurement();
		out.nStripLayers = in.hitPattern().stripLayersWithMeasurement();
		out.nTrackerLayersNew = in.hitPattern().trackerLayersWithMeasurement();
#if (CMSSW_MAJOR_VERSION >= 7 && CMSSW_MINOR_VERSION >= 2) || CMSSW_MAJOR_VERSION >= 8
		out.nInnerHits = in.hitPattern().numberOfHits(reco::HitPattern::MISSING_INNER_HITS);
#else
		out.nInnerHits = in.trackerExpectedHitsInner().numberOfHits();
#endif

		// check for builder
		if(vertices.size() == 1)
		{
			reco::TransientTrack transientTrack = builder->build(in);
			out.d3D = IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(0)).second.value();
			out.d2D = IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(0)).second.value();
			out.err3D = IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(0)).second.error();
			out.err2D = IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(0)).second.error();
		}
	}
};

#endif

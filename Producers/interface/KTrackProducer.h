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
#include "../../Producers/interface/KVertexProducer.h"


class KTrackProducer : public KBaseMultiLVProducer<edm::View<reco::Track>, KTracks>
{
public:
	KTrackProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<reco::Track>, KTracks>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "Tracks"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KTrackProducer::fillTrack(in, out);
	}

	// Static method for filling Tracks in other producers
	static void fillTrack(const SingleInputType &in, SingleOutputType &out,
	                      std::vector<reco::Vertex> const& vertices = std::vector<reco::Vertex>(),
	                      edm::ESHandle<TransientTrackBuilder> const& builder = edm::ESHandle<TransientTrackBuilder>())
	{
		// Momentum:
		out.p4.SetCoordinates(in.pt(), in.eta(), in.phi(), 0);

		// Reference point:
		out.ref = in.referencePoint();

		// Charge, ...
		out.charge = in.charge();
		out.chi2 = in.chi2();
		out.nDOF = in.ndof();
		out.qualityBits = in.qualityMask();

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

		// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/DataFormats/TrackReco/interface/TrackBase.h#L3-L49
		for (unsigned int index1 = 0; index1 < reco::Track::dimension; ++index1)
		{
			for (unsigned int index2 = 0; index2 < reco::Track::dimension; ++index2)
			{
				out.helixCovariance(index1, index2) = in.covariance(index1, index2);
			}
		}
		
		// check for builder is missing - be carefull to pass it to this function together with verticies
		if (vertices.size() > 0)
		{
			int validVertexIndex = -1;
			for (unsigned int i = 0; i < vertices.size(); i++)
				if (vertices.at(i).isValid())
				{
					KVertexProducer::fillVertex(vertices.at(i), out.ipVertex);
					validVertexIndex = i;
					break;
				}
			if (validVertexIndex >= 0)
			{
				reco::TransientTrack transientTrack = builder->build(in);
				out.d3D = IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(validVertexIndex)).second.value();
				out.d2D = IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(validVertexIndex)).second.value();
				out.err3D = IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(validVertexIndex)).second.error();
				out.err2D = IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(validVertexIndex)).second.error();
			}
		}
	}
};

#endif

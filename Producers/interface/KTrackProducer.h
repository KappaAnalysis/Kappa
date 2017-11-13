//- Copyright (c) 2010 - All Rights Reserved
//-  * Danilo Piparo <danilo.piparo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_TRACKPRODUCER_H
#define KAPPA_TRACKPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KVertexSummaryProducer.h"
#include <DataFormats/TrackReco/interface/Track.h>
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/KVertexProducer.h"
#include "../../Producers/interface/KRefitVertexProducer.h"


class KTrackProducer : public KBaseMultiLVProducer<edm::View<reco::Track>, KTracks>
{
public:
	KTrackProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<reco::Track>, KTracks>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "Tracks"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		if (KBaseProducer::verbosity == 3) std::cout << "KTracksProducer::fillSingle\n";
		KTrackProducer::fillTrack(in, out);
		if (KBaseProducer::verbosity == 3) std::cout << "KTracksProducer::fillSingle end\n";
	}

	// Static method for filling Tracks in other producers
	static void fillTrack(const SingleInputType &in, SingleOutputType &out,
	                      std::vector<reco::Vertex> const& vertices = std::vector<reco::Vertex>(),
	                      const TransientTrackBuilder* trackBuilder = nullptr)
	{
		if (KBaseProducer::verbosity == 3) std::cout << "KTracksProducer::fillTrack\n";
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
		out.nInnerHits = in.hitPattern().numberOfHits(reco::HitPattern::MISSING_INNER_HITS);

		// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/DataFormats/TrackReco/interface/TrackBase.h#L3-L49
		for (unsigned int index1 = 0; index1 < reco::Track::dimension; ++index1)
		{
			for (unsigned int index2 = 0; index2 < reco::Track::dimension; ++index2)
			{
				out.helixCovariance(index1, index2) = in.covariance(index1, index2);
			}
		}
		
		// https://github.com/cms-sw/cmssw/blob/09c3fce6626f70fd04223e7dacebf0b485f73f54/TrackingTools/TransientTrack/interface/TransientTrackBuilder.h
		out.magneticField = (trackBuilder ? trackBuilder->field()->inInverseGeV(GlobalPoint(out.ref.X(), out.ref.Y(), out.ref.Z())).z() : 0.0);
		
		// check for builder is missing - be carefull to pass it to this function together with verticies
		if (vertices.size() > 0)
		{
			int validVertexIndex = KVertexSummaryProducer::getValidVertexIndex(vertices);
			if (validVertexIndex >= 0)
			{
				reco::TransientTrack transientTrack = trackBuilder->build(in);
				out.d3D = IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(validVertexIndex)).second.value();
				out.d2D = IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(validVertexIndex)).second.value();
				out.err3D = IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(validVertexIndex)).second.error();
				out.err2D = IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(validVertexIndex)).second.error();
			}
		}
		if (KBaseProducer::verbosity == 3) std::cout << "KTracksProducer::fillTrack end\n";
	}


	// fill vectors of IPmag and corresponding error calculated wrt refitted PVs
	static void fillIPInfo(const SingleInputType &in, SingleOutputType &out,
	                      std::vector<RefitVertex> const& vertices = std::vector<RefitVertex>(),
	                      //std::vector<reco::Vertex> const& vertices = std::vector<reco::Vertex>(),
	                      const TransientTrackBuilder* trackBuilder = nullptr)
	{
		if (KBaseProducer::verbosity == 3) std::cout << "KTracksProducer::fillIPInfo\n";
		if (vertices.size() > 0 && trackBuilder != nullptr)
		{
			
			reco::TransientTrack transientTrack = trackBuilder->build(in);
			
			for (unsigned int i=0; i<vertices.size(); ++i)
			{
				out.d3DnewPV.push_back(IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(i)).second.value());
				out.err3DnewPV.push_back(IPTools::absoluteImpactParameter3D(transientTrack, vertices.at(i)).second.error());
				out.d2DnewPV.push_back(IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(i)).second.value());
				out.err2DnewPV.push_back(IPTools::absoluteTransverseImpactParameter(transientTrack, vertices.at(i)).second.error());
			}
		}
		if (KBaseProducer::verbosity == 3) std::cout << "KTracks::fillIPInfo end\n";
	}


};

	


#endif

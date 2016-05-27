//- Copyright (c) 2014 - All Rights Reserved
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_UNBIASEDDITAUPVPRODUCER_H
#define KAPPA_UNBIASEDDITAUPVPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KVertexProducer.h"
#include "KTauProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/VertexReco/interface/Vertex.h>
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "RecoVertex/VertexPrimitives/interface/TransientVertex.h"
#include "RecoVertex/AdaptiveVertexFit/interface/AdaptiveVertexFitter.h"
#include "DataFormats/Math/interface/deltaR.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KTaupairVerticesMapProducer : public KBaseMultiVectorProducer<edm::View<reco::Vertex>, KTaupairVerticesMaps>
{
public:
	KTaupairVerticesMapProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiVectorProducer<edm::View<reco::Vertex>, KTaupairVerticesMaps>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "TaupairVerticesMap"; }

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		setup.get<TransientTrackRecord>().get("TransientTrackBuilder",this->theB);
		return true;
	}


	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		this->deltaRThreshold = pset.getParameter<double>("deltaRThreshold");
		this->beamSpotSource = pset.getParameter<edm::InputTag>("beamSpotSource");
		this->pfTauCollection = pset.getParameter<edm::InputTag>("src");
		this->fitMethod = pset.getParameter<int>("fitMethod");
		this->includeOriginalPV = pset.getParameter<bool>("includeOrginalPV");
		assert((this->fitMethod == 1) || (this->fitMethod == 0));
		edm::Handle<reco::BeamSpot> beamSpotHandle;
		this->cEvent->getByLabel(this->beamSpotSource, beamSpotHandle);
		beamSpot = *beamSpotHandle;

		// Continue normally
		KBaseMultiVectorProducer<edm::View<reco::Vertex>, KTaupairVerticesMaps>::fillProduct(in, out, name, tag, pset);
	}


	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		if(this->includeOriginalPV)
		{
			KVertex tmpVertex;
			out.diTauKey.push_back(0);
			KVertexProducer::fillVertex(in, tmpVertex);
			out.vertices.push_back( tmpVertex);
		}

		std::vector<const reco::Track*> recoTracks;
		getTrackRefs(recoTracks, in);
		std::vector<reco::PFTau> commonTaus;

		if( getCommonTaus(commonTaus, recoTracks) >= 2)
		{
			std::vector<std::pair<reco::PFTau, reco::PFTau>> diTauPairs;
			if (getDiTauPairs(diTauPairs, commonTaus) >= 1)
			{
				std::map<int, reco::Vertex> refittedVertices;
				getRefittedVertices(refittedVertices, diTauPairs, in);

				for(std::map<int, reco::Vertex>::iterator vertex = refittedVertices.begin();
		    		vertex != refittedVertices.end(); ++vertex)
				{
					KVertex tmpVertex;
					KVertexProducer::fillVertex(vertex->second, tmpVertex);
					out.diTauKey.push_back(vertex->first);
					out.vertices.push_back(tmpVertex);
				}
			}
		}
	}

private:

	const void getRefittedVertices(std::map<int, reco::Vertex> &refittedVertices, 
	                         const std::vector<std::pair<reco::PFTau, reco::PFTau>> &diTauPairs, 
	                         const SingleInputType &in)
	{
		for(size_t i = 0; i < diTauPairs.size(); ++i)
		{
			std::vector<const reco::Track*> recoTracks;
			getTrackRefs(recoTracks, in);
			removeTauTracks(diTauPairs[i].first, recoTracks);
			removeTauTracks(diTauPairs[i].second, recoTracks);
			std::vector<const reco::Track*> cleanedRecoTracks;
			for(size_t j = 0; j < recoTracks.size(); ++j)
			{
				if(recoTracks[j] != NULL)
				{
					cleanedRecoTracks.push_back(recoTracks[j]);
				}
			}

			std::vector<reco::TransientTrack> transientTracks;
			getTransientTracks(transientTracks, cleanedRecoTracks);
			AdaptiveVertexFitter theFitter;
			TransientVertex refittedTransientVertex;
			if(fitMethod == 0)
			{
				refittedTransientVertex = theFitter.vertex(transientTracks, beamSpot);  // if you want the beam constraint
			}else if(fitMethod == 1)
			{
				refittedTransientVertex = theFitter.vertex(transientTracks);  // if you don't want the beam constraint
			}
			int key1 =createTauHash(diTauPairs[i].first);
			int key2 =createTauHash(diTauPairs[i].second);
			int diTauKey = key1 ^ key2;
			// converte Transient->reco
			reco::Vertex refittedVertex = reco::Vertex(refittedTransientVertex);
			refittedVertices.insert( std::pair<int, reco::Vertex>(diTauKey, refittedVertex ));
		}
		return;
	}


	const void removeTauTracks(const reco::PFTau tau, std::vector<const reco::Track*> &recoTracks)
	{
#if CMSSW_MAJOR_VERSION >= 7
		const std::vector<edm::Ptr<reco::PFCandidate> > tauPFCHD = tau.signalPFChargedHadrCands();
		for(std::vector<edm::Ptr<reco::PFCandidate> >::const_iterator chargedHadronCand = tauPFCHD.begin();
			    chargedHadronCand != tauPFCHD.end(); ++chargedHadronCand)
#else
		const reco::PFCandidateRefVector tauPFCHD = tau.signalPFChargedHadrCands();
		for(reco::PFCandidateRefVector::const_iterator chargedHadronCand = tauPFCHD.begin();
			    chargedHadronCand != tauPFCHD.end(); ++chargedHadronCand)
#endif
		{
			for(size_t i = 0; i < recoTracks.size(); ++i)
			{
				if( recoTracks[i] == NULL)
					continue;
				if (reco::deltaR((**chargedHadronCand), *recoTracks[i]) < this->deltaRThreshold)
				{
					recoTracks[i] = NULL;
				}
			}
		}
	}

	const int getCommonTaus(std::vector<reco::PFTau> &commonTaus, const std::vector<const reco::Track*> recoTracks)
	{
		edm::Handle<std::vector<reco::PFTau>> tauHandle;
		this->cEvent->getByLabel(this->pfTauCollection, tauHandle);
		// check wich tau is from the current PV
		for(std::vector<reco::PFTau>::const_iterator tau = tauHandle->begin();
		    tau != tauHandle->end(); ++tau)
		{
			if( tau->charge() == 0) //don't consider "neutral taus" to speed things up
			{
				continue;
			}
			unsigned int commonTracks = 0;
			// if all chargedHadronCands of a tau have tracks in common with the PV, take this tau and add it to lists
#if CMSSW_MAJOR_VERSION >= 7
			const std::vector<edm::Ptr<reco::PFCandidate> > tauPFCHD = tau->signalPFChargedHadrCands();
			for(std::vector<edm::Ptr<reco::PFCandidate> >::const_iterator chargedHadronCand = tauPFCHD.begin();
			    chargedHadronCand != tauPFCHD.end(); ++chargedHadronCand)
#else
			const reco::PFCandidateRefVector tauPFCHD = tau->signalPFChargedHadrCands();
			for(reco::PFCandidateRefVector::const_iterator chargedHadronCand = tauPFCHD.begin();
			    chargedHadronCand != tauPFCHD.end(); ++chargedHadronCand)
#endif
			{
				for(size_t i = 0; i < recoTracks.size(); ++i)
				{
					if (reco::deltaR((**chargedHadronCand), *recoTracks[i]) < this->deltaRThreshold)
						commonTracks++;
				}
			}
			if( commonTracks == tauPFCHD.size() )
				commonTaus.push_back(*tau);
		}
		return commonTaus.size();
	}


	const int getDiTauPairs(std::vector<std::pair<reco::PFTau, reco::PFTau>> &diTauPairs, 
	                  const std::vector<reco::PFTau> commonTaus)
	{
		for(size_t i = 0; i < commonTaus.size()-1; ++i)
		{
			for(size_t j = i + 1; j < commonTaus.size(); ++j)
			{
				if( (commonTaus[i].charge() > 0) && ( commonTaus[j].charge() < 0))
				{
					if( commonTaus[i].charge() > 0)
						diTauPairs.push_back(std::pair<reco::PFTau, reco::PFTau>(commonTaus[i], commonTaus[j]));
					else if( (commonTaus[i].charge() < 0) && ( commonTaus[j].charge() > 0))
						diTauPairs.push_back(std::pair<reco::PFTau, reco::PFTau>(commonTaus[j], commonTaus[i]));
				}
			}
		}
		return diTauPairs.size();
	}


	inline void getTrackRefs(std::vector<const reco::Track*> &trackRefs, const SingleInputType &in)
	{
		for (reco::Vertex::trackRef_iterator track = in.tracks_begin();
		    track != in.tracks_end(); ++track)
			trackRefs.push_back(track->castTo<reco::TrackRef>().get());
	}


	void getTransientTracks(std::vector<reco::TransientTrack> &transientTracks, const std::vector<const reco::Track*> &trackRefs)
	{
		for(size_t i = 0; i < trackRefs.size(); ++i)
		{
			reco::TransientTrack transientTrack = this->theB->build(trackRefs[i]); 
			transientTrack.setBeamSpot(beamSpot);
			transientTracks.push_back(transientTrack);
		}
	}


	edm::ESHandle<TransientTrackBuilder> theB;
	reco::BeamSpot beamSpot;
	edm::InputTag beamSpotSource;
	edm::InputTag pfTauCollection;
	double deltaRThreshold;
	int fitMethod;
	bool includeOriginalPV;
};

#endif

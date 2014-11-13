/* Copyright (c) 2010 - All Rights Reserved
 *   Raphael Friese <raphael.friese@cern.ch>
 */

#ifndef KAPPA_UNBIASEDDITAUPVPRODUCER_H
#define KAPPA_UNBIASEDDITAUPVPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KVertexProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/VertexReco/interface/Vertex.h>
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "RecoVertex/VertexPrimitives/interface/TransientVertex.h"
#include "RecoVertex/AdaptiveVertexFit/interface/AdaptiveVertexFitter.h"
#include "DataFormats/Math/interface/deltaR.h"

class KUnbiasedDiTauPVsProducer : public KBaseMultiVectorProducer<edm::View<reco::Vertex>, std::vector<KUnbiasedDiTauPV>>
{
public:
	KUnbiasedDiTauPVsProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiVectorProducer<edm::View<reco::Vertex>, std::vector<KUnbiasedDiTauPV> >(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "UnbiasedDiTauPVs"; }

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
		assert((this->fitMethod == 1) || (this->fitMethod == 0));
		std::cout << "Event" << std::endl;
		edm::Handle<reco::BeamSpot> beamSpotHandle;
		this->cEvent->getByLabel(this->beamSpotSource, beamSpotHandle);
		beamSpot = *beamSpotHandle;

		// Continue normally
		KBaseMultiVectorProducer<edm::View<reco::Vertex>, std::vector<KUnbiasedDiTauPV> >::fillProduct(in, out, name, tag, pset);
	}


	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		std::vector<const reco::Track*> recoTracks;
		getTrackRefs(recoTracks, in);

		std::vector<reco::PFTau> commonTaus;
		if (getCommonTaus(commonTaus, recoTracks) == 0)
			return;
		//get the tau Tracks that are contained in the transientTracks
		std::vector<std::pair<reco::PFTau, reco::PFTau>> diTauPairs;
		if (getDiTauPairs(diTauPairs, commonTaus) == 0)
			return;
		std::cout << "Di-Tau pairs: " << diTauPairs.size() << std::endl;
		std::map<int, reco::Vertex> refittedVertices;
		getRefittedVertices(refittedVertices, diTauPairs, in);
		std::cout << "map empty: " << refittedVertices.empty() << std::endl;
		std::cout << "map size: " << refittedVertices.size() << std::endl;

		// iterate over refittedVertices and write <int, KDataVertex>
		for(std::map<int, reco::Vertex>::iterator vertex = refittedVertices.begin();
		    vertex != refittedVertices.end(); ++vertex)
		{
			KDataVertex tmpVertex;
			KVertexProducer::fillVertex(vertex->second, tmpVertex);
			out.refittedVertices.insert( std::pair<int, KDataVertex>(vertex->first, tmpVertex));
		}
	}

private:

	const void getRefittedVertices(std::map<int, reco::Vertex> &refittedVertices, 
	                         const std::vector<std::pair<reco::PFTau, reco::PFTau>> &diTauPairs, 
	                         const SingleInputType &in)
	{
		std::cout << " hier1" << std::endl;
		for(size_t i = 0; i < diTauPairs.size(); ++i)
		{
		std::cout << " hier2" << i << std::endl;
			std::vector<const reco::Track*> recoTracks;
			getTrackRefs(recoTracks, in);
			removeTauTracks(diTauPairs[i].first, recoTracks);
			removeTauTracks(diTauPairs[i].second, recoTracks);
			std::vector<const reco::Track*> cleanedRecoTracks;
		std::cout << " hier3" << std::endl;
			for(size_t j = 0; j < recoTracks.size(); ++j)
			{
				if(recoTracks[j] != NULL)
				{
					cleanedRecoTracks.push_back(recoTracks[j]);
				}
			}

		std::cout << " hier5" << std::endl;
			std::vector<reco::TransientTrack> transientTracks;
			getTransientTracks(transientTracks, cleanedRecoTracks);
			AdaptiveVertexFitter theFitter;
			TransientVertex refittedTransientVertex;
		std::cout << " hier6" << std::endl;
			if(fitMethod == 0)
			{
				refittedTransientVertex = theFitter.vertex(transientTracks, beamSpot);  // if you want the beam constraint
			}else if(fitMethod == 0)
			{
				refittedTransientVertex = theFitter.vertex(transientTracks);  // if you don't want the beam constraint
			}
			//std::cout << "Vertex has " << transientTracks.size() << " Tracks" 
			 //   "\t dX = " << (in.position().x() - myVertex.position().x())/in.position().x() << 
			  //  "\t dY = " << (in.position().y() - myVertex.position().y())/in.position().y() << 
			    //"\t dZ = " << (in.position().z() - myVertex.position().z())/in.position().z() << 
			    //"\t isValid = " << in.isValid() << myVertex.isValid() << 
			    //"\t chi2 = " << (in.normalizedChi2() - myVertex.normalisedChiSquared())/in.normalizedChi2() << 
		    	//std::endl;
			int key1 = KPFTauProducer::createRecoPFTauHash(diTauPairs[i].first);
			int key2 = KPFTauProducer::createRecoPFTauHash(diTauPairs[i].second);
			int diTauKey = key1 ^ key2;
			// converte Transient->reco
			reco::Vertex refittedVertex = reco::Vertex(refittedTransientVertex);
			refittedVertices.insert( std::pair<int, reco::Vertex>(diTauKey, refittedVertex ));
		}
		return;
	}


	const void removeTauTracks(const reco::PFTau tau, std::vector<const reco::Track*> &recoTracks)
	{
		std::cout << " hiera" << std::endl;
		const reco::PFCandidateRefVector tauPFCHD = tau.signalPFChargedHadrCands();
		for(reco::PFCandidateRefVector::const_iterator chargedHadronCand = tauPFCHD.begin();
			    chargedHadronCand != tauPFCHD.end(); ++chargedHadronCand)
		{
			std::cout << " hiera2" << std::endl;
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
		std::cout << " hiera6" << std::endl;
	}

	const int getCommonTaus(std::vector<reco::PFTau> &commonTaus, const std::vector<const reco::Track*> recoTracks)
	{

		edm::Handle<std::vector<reco::PFTau>> tauHandle;
		this->cEvent->getByLabel(this->pfTauCollection, tauHandle);
		std::cout << "taus: " << tauHandle->size() << std::endl;
		// check wich tau is from the current PV
		for(std::vector<reco::PFTau>::const_iterator tau = tauHandle->begin();
		    tau != tauHandle->end(); ++tau)
		{
			std::cout << "new tau" << std::endl;
			if( tau->charge() == 0) //don't consider "neutral taus" to speed things up
			{
				continue;
			}
			const reco::PFCandidateRefVector tauPFCHD = tau->signalPFChargedHadrCands();
			// if all chargedHadronCands of a tau have tracks in common with the PV, take this tau and add it to lists
			unsigned int commonTracks = 0;
			for(reco::PFCandidateRefVector::const_iterator chargedHadronCand = tauPFCHD.begin();
			    chargedHadronCand != tauPFCHD.end(); ++chargedHadronCand)
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
};

#endif

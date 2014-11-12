/* Copyright (c) 2010 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
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

	int createRecoPFTauHash(const reco::PFTau tau)
	{
		return ( std::hash<double>()(tau.leadPFCand()->px()) ^
		         std::hash<double>()(tau.leadPFCand()->py()) ^ 
		         std::hash<double>()(tau.leadPFCand()->pz()) ^
		         std::hash<bool>()(tau.leadPFCand()->charge()) );
	}

protected:

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		std::cout << "Event" << std::endl;
		edm::Handle<reco::BeamSpot> beamSpotHandle;
		this->cEvent->getByLabel("offlineBeamSpot", beamSpotHandle);
		_beamSpot = *beamSpotHandle;

		// Continue normally
		KBaseMultiVectorProducer<edm::View<reco::Vertex>, std::vector<KUnbiasedDiTauPV> >::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		std::vector<const reco::Track*> recoTracks = getTrackRefs(in);

		std::vector<reco::PFTau> commonTaus = getCommonTaus(recoTracks);
		//get the tau Tracks that are contained in the transientTracks
		std::vector<std::pair<reco::PFTau, reco::PFTau>> diTauPairs = getDiTauPairs(commonTaus);

		std::map<int, reco::Vertex> refittedVertices = getRefittedVertices(diTauPairs, in);
		std::cout << "map empty: " << refittedVertices.empty() << std::endl;
		std::cout << "map size: " << refittedVertices.size() << std::endl;

		// iterate over refittedVertices and write <int, KDataVertex>
		for(std::map<int, reco::Vertex>::iterator vertex = refittedVertices.begin();
		    vertex != refittedVertices.end(); ++vertex)
		{
			KDataVertex tmpVertex;
			KVertexProducer::fillVertex(vertex->second, &tmpVertex);
			out.refittedVertices.insert( std::pair<int, KDataVertex>(vertex->first, tmpVertex));
		}
	}



	std::map<int, reco::Vertex> getRefittedVertices(const std::vector<std::pair<reco::PFTau, reco::PFTau>> diTauPairs, const SingleInputType &in)
	{
		std::map<int, reco::Vertex> refittedVertices;
		//get the inputs
		//loop over diTauPairs
		for(size_t i = 0; i < diTauPairs.size(); ++i)
		{
			std::vector<const reco::Track*> recoTracks = getTrackRefs(in);
			recoTracks = removeTauTracks(diTauPairs[i].first, recoTracks);
			recoTracks = removeTauTracks(diTauPairs[i].second, recoTracks);
			std::vector<const reco::Track*> cleanedRecoTracks;
			for(size_t j = 0; j < recoTracks.size(); ++j)
			{
				if(recoTracks[j] != NULL)
				{
					cleanedRecoTracks.push_back(recoTracks[j]);
				}
			}

			std::vector<reco::TransientTrack> transientTracks = getTransientTracks(cleanedRecoTracks);
			bool includeBeamspot = false;
			// perform the fit
			AdaptiveVertexFitter theFitter;
			TransientVertex refittedTransientVertex;
			if(includeBeamspot)
			{
				refittedTransientVertex = theFitter.vertex(transientTracks, _beamSpot);  // if you want the beam constraint
			}else
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
			int key1 = createRecoPFTauHash(diTauPairs[i].first);
			int key2 = createRecoPFTauHash(diTauPairs[i].second);
			int diTauKey = key1 ^ key2;
			// converte Transient->reco
			reco::Vertex refittedVertex = reco::Vertex(refittedTransientVertex);
			refittedVertices.insert( std::pair<int, reco::Vertex>(diTauKey, refittedVertex ));
		}
		return refittedVertices;
	}


	std::vector<const reco::Track*> removeTauTracks(const reco::PFTau tau, std::vector<const reco::Track*> recoTracks)
	{
		double deltaRThreshold = 0.0001;
		const reco::PFCandidateRefVector tauPFCHD = tau.signalPFChargedHadrCands();
		for(reco::PFCandidateRefVector::const_iterator chargedHadronCand = tauPFCHD.begin();
			    chargedHadronCand != tauPFCHD.end(); ++chargedHadronCand)
		{
			for(size_t i = 0; i < recoTracks.size(); ++i)
			{
				if (reco::deltaR((**chargedHadronCand), *recoTracks[i]) < deltaRThreshold)
				{
					recoTracks[i] = NULL;
				}
			}
		}
		return recoTracks;
	}

	std::vector<reco::PFTau> getCommonTaus(const std::vector<const reco::Track*> recoTracks)
	{

		edm::Handle<std::vector<reco::PFTau>> tauHandle;
		this->cEvent->getByLabel("hpsPFTauProducer", tauHandle);// ToDo: Umstellen auf vorgefilterte Collection
		std::cout << "taus: " << tauHandle->size() << std::endl;
		double deltaRThreshold = 0.0001;
		std::vector<reco::PFTau> commonTaus;
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
				std::cout << "PFCHD: " << (**chargedHadronCand).phi() << std::endl;
				for(size_t i = 0; i < recoTracks.size(); ++i)
				{
					//std::cout << "recoTracks:" << recoTracks[i]->charge() << ";   ";
					//std::cout << reco::deltaR((**chargedHadronCand), *recoTracks[i])<< std::endl;
					if (reco::deltaR((**chargedHadronCand), *recoTracks[i]) < deltaRThreshold)
					{
						commonTracks++;
					}
			//		if (*chargedHadronCand == recoTracks[i])
			//			std::cout << "found common Track!" << std::endl;
				}
			}
			// if all charged pf candidates are from the PV, select this tau
			std::cout << "Found " << commonTracks << " out of " << tauPFCHD.size() << std::endl;
			if( commonTracks == tauPFCHD.size() )
			{
				commonTaus.push_back(*tau);
			}
		}

	return commonTaus;
	}



	std::vector<std::pair<reco::PFTau, reco::PFTau>> getDiTauPairs(const std::vector<reco::PFTau> commonTaus)
	{
		std::vector<std::pair<reco::PFTau, reco::PFTau>> diTauPairs;
		for(size_t i = 0; i < commonTaus.size()-1; ++i)
		{
			for(size_t j = i + 1; j < commonTaus.size(); ++j)
			{
				if( commonTaus[i].charge() == (-1.0 * commonTaus[j].charge()))
				{
					diTauPairs.push_back(std::pair<reco::PFTau, reco::PFTau>(commonTaus[i], commonTaus[j]));
				}
			std::cout << "Tau" << i << " has charge " << commonTaus[i].charge() <<std::endl;
			}
		}
	return diTauPairs;
	}

	std::vector<const reco::Track*> getTrackRefs(const SingleInputType &in)
	{
		std::vector<const reco::Track*> trackRefs;
		
		for (reco::Vertex::trackRef_iterator track = in.tracks_begin();
		    track != in.tracks_end(); ++track)
		{
			reco::TrackRef recoTrackRef = track->castTo<reco::TrackRef>();
			const reco::Track *recoTrack = recoTrackRef.get();
			trackRefs.push_back(recoTrack);

		}
		return trackRefs;
	}

	std::vector<reco::TransientTrack> getTransientTracks(const std::vector<const reco::Track*> &trackRefs)
	{
		std::vector<reco::TransientTrack> transientTracks;
		for(size_t i = 0; i < trackRefs.size(); ++i)
		{
			reco::TransientTrack transientTrack = this->theB->build(trackRefs[i]); 
			transientTrack.setBeamSpot(_beamSpot);
			transientTracks.push_back(transientTrack);
		}
		return transientTracks;
	}

	edm::ESHandle<TransientTrackBuilder> theB;
	reco::BeamSpot _beamSpot;
};

#endif

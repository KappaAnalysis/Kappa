
#ifndef KAPPA_TRACKPAIRPRODUCER_H
#define KAPPA_TRACKPAIRPRODUCER_H

#include <Math/Functions.h>
#include <Math/SVector.h>
#include <Math/SMatrix.h>

#include <DataFormats/TrackReco/interface/Track.h>
#include <TrackingTools/TransientTrack/interface/TransientTrackBuilder.h>
#include <TrackingTools/PatternTools/interface/TwoTrackMinimumDistance.h>
#include <RecoVertex/KinematicFitPrimitives/interface/KinematicParticleFactoryFromTransientTrack.h>
#include <FWCore/Framework/interface/EDProducer.h>

#include "KBaseMultiProducer.h"
#include "Kappa/DataFormats/interface/Hash.h"


class KLeptonPairProducer : public KBaseMultiProducer<edm::View<reco::Track>, KLeptonPairs>
{

public:
	KLeptonPairProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<edm::View<reco::Track>, KLeptonPairs>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		electronsTag(cfg.getParameter<edm::InputTag>("electrons")),
		muonsTag(cfg.getParameter<edm::InputTag>("muons"))
	{
		if (this->verbosity == 3) std::cout << "KLeptonPairProducer ()\n";
		this->electronsCollectionToken = consumescollector.consumes<edm::View<pat::Electron> >(electronsTag);
		this->muonsCollectionToken = consumescollector.consumes<edm::View<reco::Muon> >(muonsTag);
		if (this->verbosity == 3) std::cout << "KLeptonPairProducer () end\n";
	}

	static const std::string getLabel() { return "LeptonPair"; }

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
               if (this->verbosity == 3) std::cout << "KLeptonPairProducer onRun()\n";
		setup.get<TransientTrackRecord>().get("TransientTrackBuilder", this->transientTrackBuilder);
		if (this->verbosity == 3) std::cout << "KLeptonPairProducer onRun() end\n";
		return true;
	}

	virtual void clearProduct(OutputType &output)
	{
		output.clear();
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (this->verbosity == 3) std::cout << "KLeptonPairProducer fillProduct()\n";
		// get electron and muon collections
		if (electronsTag.label() != "")
		{
			cEvent->getByToken(electronsCollectionToken, electrons);
		}
		if (muonsTag.label() != "")
		{
			cEvent->getByToken(muonsCollectionToken, muons);
		}
		
		// loop over electrons
		for (edm::View<pat::Electron>::const_iterator particle1 = electrons->begin(); particle1 < electrons->end(); ++particle1)
		{
			for (edm::View<pat::Electron>::const_iterator particle2 = particle1 + 1; particle2 < electrons->end(); ++particle2)
			{
				std::pair<KLeptonPair, bool> leptonPair = getLeptonPair(particle1, particle2);
				if (leptonPair.second)
				{
					out.push_back(leptonPair.first);
				}
			}
		}
		
		// loop over muons
		for (edm::View<reco::Muon>::const_iterator particle1 = muons->begin(); particle1 < muons->end(); ++particle1)
		{
			for (edm::View<reco::Muon>::const_iterator particle2 = particle1 + 1; particle2 < muons->end(); ++particle2)
			{
				std::pair<KLeptonPair, bool> leptonPair = getLeptonPair(particle1, particle2);
				if (leptonPair.second)
				{
					out.push_back(leptonPair.first);
				}
			}
		}
		
		// loop over electrons and muons
		for (edm::View<pat::Electron>::const_iterator particle1 = electrons->begin(); particle1 < electrons->end(); ++particle1)
		{
			for (edm::View<reco::Muon>::const_iterator particle2 = muons->begin(); particle2 < muons->end(); ++particle2)
			{
				std::pair<KLeptonPair, bool> leptonPair = getLeptonPair(particle1, particle2);
				if (leptonPair.second)
				{
					out.push_back(leptonPair.first);
				}
			}
		}
		if (this->verbosity == 3) std::cout << "KLeptonPairProducer fillProduct() end\n";
	}

private:
	edm::InputTag electronsTag;
	edm::InputTag muonsTag;
	
	edm::EDGetTokenT<edm::View<pat::Electron> > electronsCollectionToken;
	edm::EDGetTokenT<edm::View<reco::Muon> > muonsCollectionToken;
	
	edm::ESHandle<TransientTrackBuilder> transientTrackBuilder;
	
	edm::Handle<edm::View<pat::Electron> > electrons;
	edm::Handle<edm::View<reco::Muon> > muons;
	
	template<class T1, class T2>
	std::pair<KLeptonPair, bool> getLeptonPair(T1 particle1, T2 particle2)
	{
		if (this->verbosity == 3) std::cout << "KLeptonPairProducer getLeptonPair()\n";
		KinematicParticleFactoryFromTransientTrack particleFactory;
		
		const reco::Track* track1 = KLeptonPairProducer::getTrack(particle1);
		if (track1 == 0)
		{
			return std::pair<KLeptonPair, bool>(KLeptonPair(), false);
		}
		reco::TransientTrack transientTrack1 = this->transientTrackBuilder->build(track1);
		FreeTrajectoryState freeTrajectoryState1 = transientTrack1.impactPointTSCP().theState();
		ParticleMass particleMass1 = particle1->mass();
		float particleMassSigma1 = particleMass1 * 1.e-6;
		float chi1 = 0.0; //initial chi2 before kinematic fits.
		float ndf1 = 0.0; //initial ndf before kinematic fits.
		RefCountedKinematicParticle kinParticle1 = particleFactory.particle(transientTrack1, particleMass1, chi1, ndf1, particleMassSigma1);
		
		const reco::Track* track2 = KLeptonPairProducer::getTrack(particle2);
		if (track2 == 0)
		{
			return std::pair<KLeptonPair, bool>(KLeptonPair(), false);
		}
		reco::TransientTrack transientTrack2 = this->transientTrackBuilder->build(track2);
		FreeTrajectoryState freeTrajectoryState2 = transientTrack2.impactPointTSCP().theState();
		ParticleMass particleMass2 = particle2->mass();
		float particleMassSigma2 = particleMass2 * 1.e-6;
		float chi2 = 0.0; //initial chi2 before kinematic fits.
		float ndf2 = 0.0; //initial ndf before kinematic fits.
		RefCountedKinematicParticle kinParticle2 = particleFactory.particle(transientTrack2, particleMass2, chi2, ndf2, particleMassSigma2);
		
		TwoTrackMinimumDistance twoTrackMinimumDistance;
		twoTrackMinimumDistance.calculate(freeTrajectoryState1, freeTrajectoryState2);
		if (twoTrackMinimumDistance.status())
		{
			std::pair<GlobalPoint, GlobalPoint> pcas = twoTrackMinimumDistance.points();
			Vector3DBase<float, GlobalTag> dcaVector = pcas.second - pcas.first;
			ROOT::Math::SVector<double, 3> dcaVectorConverted(
					dcaVector.x(),
					dcaVector.y(),
					dcaVector.z()
			);
			
			auto totCov = kinParticle1->stateAtPoint(pcas.first).kinematicParametersError().matrix() +
			              kinParticle2->stateAtPoint(pcas.second).kinematicParametersError().matrix();
			ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> > totCovConverted;
			for (int i = 0; i < 3; ++i)
			{
				for (int j = 0; j < 3; ++j)
				{
					totCovConverted(i, j) = totCov(i, j);
				}
			}
			
			double dca3D = ROOT::Math::Mag(dcaVectorConverted); // twoTrackMinimumDistance.distance();
			double dca3DError = sqrt(ROOT::Math::Similarity(totCovConverted, dcaVectorConverted)) / dca3D;
			
			ROOT::Math::SVector<double, 3> transverseDcaVectorConverted = dcaVectorConverted;
			transverseDcaVectorConverted(2) = 0.0;
			double dca2D = ROOT::Math::Mag(transverseDcaVectorConverted);
			double dca2DError = sqrt(ROOT::Math::Similarity(totCovConverted, transverseDcaVectorConverted)) / dca2D;
			
			KLeptonPair leptonPair;
			leptonPair.hashLepton1 = getLVChargeHash(particle1->pt(), particle1->eta(), particle1->phi(), particle1->mass(), particle1->charge());
			leptonPair.hashLepton2 = getLVChargeHash(particle2->pt(), particle2->eta(), particle2->phi(), particle2->mass(), particle2->charge());
			leptonPair.dca3D = dca3D;
			leptonPair.dca3DError = dca3DError;
			leptonPair.dca2D = dca2D;
			leptonPair.dca2DError = dca2DError;
			//std::cout << "dca3D = " << leptonPair.dca3D << " +/- " << leptonPair.dca3DError << ", "
			//          << "dca2D = " << leptonPair.dca2D << " +/- " << leptonPair.dca2DError << std::endl;
			if (this->verbosity == 3) std::cout << "KLeptonPairProducer getLeptonPair() end1\n";
			return std::pair<KLeptonPair, bool>(leptonPair, true);
		}
		else
		{
			if (this->verbosity == 3) std::cout << "KLeptonPairProducer getLeptonPair() end2\n";
			return std::pair<KLeptonPair, bool>(KLeptonPair(), false);
		}
	}
	
	static const reco::Track* getTrack(edm::View<pat::Electron>::const_iterator particle)
	{
		if (particle->gsfTrack().isNonnull())
		{
			return &(*(particle->gsfTrack()));
		}
		return 0;
	}
	static const reco::Track* getTrack(edm::View<reco::Muon>::const_iterator particle)
	{
		if (particle->innerTrack().isNonnull())
		{
			return &(*(particle->innerTrack()));
		}
		else if (particle->track().isNonnull())
		{
			return &(*(particle->track()));
		}
		return 0;
	}
};

#endif

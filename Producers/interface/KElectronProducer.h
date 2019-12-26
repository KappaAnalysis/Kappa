//- Copyright (c) 2013 - All Rights Reserved
//-  * Benjamin Treiber <benjamin.treiber@gmail.com>
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_ELECTRONPRODUCER_H
#define KAPPA_ELECTRONPRODUCER_H

#include "KBaseMultiLVProducer.h"

#include <DataFormats/PatCandidates/interface/Electron.h>
#include <RecoEgamma/EgammaTools/interface/ConversionTools.h>
#include <DataFormats/BeamSpot/interface/BeamSpot.h>
#include <TrackingTools/TransientTrack/interface/TransientTrackBuilder.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "boost/functional/hash.hpp"
#include "EgammaAnalysis/ElectronTools/interface/EGammaCutBasedEleId.h"
#include "../../Producers/interface/KRefitVertexProducer.h"
#include "EgammaAnalysis/ElectronTools/interface/ElectronEffectiveArea.h"


class KElectronProducer : public KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>
{
public:
	KElectronProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::Electron>,
		KElectrons>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		tagConversionSource(cfg.getParameter<edm::InputTag>("allConversions")),
		beamSpotSource(cfg.getParameter<edm::InputTag>("offlineBeamSpot")),
		VertexCollectionSource(cfg.getParameter<edm::InputTag>("vertexcollection")),
		rhoIsoTag(cfg.getParameter<edm::InputTag>("rhoIsoInputTag")),
		isoValInputTags(cfg.getParameter<std::vector<edm::InputTag> >("isoValInputTags")),
		tagOfIds(cfg.getParameter<std::vector<edm::InputTag> >("ids")),
		tagOfUserFloats(cfg.getParameter<std::vector<edm::InputTag> >("userFloats")),
		srcIds_(cfg.getParameter<std::string>("srcIds")),
		doPfIsolation_(true),
		doCutbasedIds_(true),
		RefitVerticesSource(cfg.getParameter<edm::InputTag>("refitvertexcollection"))
	{
		if (this->verbosity >= 3) std::cout << "KElectronProducer ()\n";
		electronMetadata = new KElectronMetadata;
		_lumi_tree->Bronch("electronMetadata", "KElectronMetadata", &electronMetadata);

		doMvaIds_ = (srcIds_ == "pat");
		doAuxIds_ = (srcIds_ == "standalone");

		this->tokenConversionSource = consumescollector.consumes<reco::ConversionCollection>(tagConversionSource);
		this->tokenBeamSpot = consumescollector.consumes<reco::BeamSpot>(beamSpotSource);
		this->tokenVertexCollection = consumescollector.consumes<reco::VertexCollection>(VertexCollectionSource);
		this->tokenRhoIso = consumescollector.consumes<double>(rhoIsoTag);
		this->tokenRefitVertices = consumescollector.consumes<RefitVertexCollection>(RefitVerticesSource);

		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);
			for(size_t j = 0; j < this->isoValInputTags.size(); ++j)
				tokenIsoValInputTags.push_back(consumescollector.consumes<edm::ValueMap<double>>(this->isoValInputTags.at(j)));
		}

		for (size_t j = 0; j < tagOfIds.size(); ++j)
			tokenOfIds.push_back(consumescollector.consumes<edm::ValueMap<float> >(tagOfIds[j]));

		if (this->verbosity >= 3) std::cout << "KElectronProducer () end\n";
	}

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		if (this->verbosity >= 3) std::cout << "KElectronProducer onrun\n";
		setup.get<TransientTrackRecord>().get("TransientTrackBuilder", this->trackBuilder);
		if (this->verbosity >= 3) std::cout << "KElectronProducer end onrun\n";
		return true;
	}

	static const std::string getLabel() { return "Electrons"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		for (size_t j = 0; j < tagOfIds.size(); ++j)
		{
			electronMetadata->idNames.push_back(this->tagOfIds[j].label()+":"+this->tagOfIds[j].instance());
		}
		for (size_t j = 0; j < tagOfUserFloats.size(); ++j)
		{
			electronMetadata->idNames.push_back(this->tagOfUserFloats[j].label()+":"+this->tagOfUserFloats[j].instance());
		}
		return KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>::onLumi(lumiBlock, setup);
	}
	

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Get additional objects for the cutbased IDs
		if (this->verbosity >= 3) std::cout << "KElectron::fillProduct \n";
		cEvent->getByToken(this->tokenConversionSource, this->hConversions);
		cEvent->getByToken(this->tokenBeamSpot, this->BeamSpot);
		cEvent->getByToken(this->tokenVertexCollection, this->VertexCollection);
		// cEvent->getByToken(this->tokenRefitVertices, this->RefitVertices);

		this->isoVals.resize(this->isoValInputTags.size());
		for (size_t j = 0; j < this->isoValInputTags.size(); ++j)
		{
			cEvent->getByToken(this->tokenIsoValInputTags[j], this->isoVals[j]);

			if (this->isoVals[j].failedToGet()) doPfIsolation_ = false;
		}

		cEvent->getByToken(tokenRhoIso, rhoIso_h);

		// TODO: change to getByToken
		/*art::Handle<StepPointMCCollection> stepsHandle;
		event.getByLabel("g4run","tracker",stepsHandle);
		StepPointMCCollection const& steps(*stepsHandle);
		*/
		/*try {
			iEvent.getByLabel(l1GTReadoutRecTag_,L1GTRR);
		} catch (...) {;}
		if ( L1GTRR.isValid() ) { // exists
		
		edm::Handle<edm::TriggerResults> trh;
		try {iEvent.getByLabel(triggerInputTag_,trh);}
			catch( cms::Exception& ex ) { LogWarning("HWWTreeDumper") << "Trigger results: " << triggerInputTag_ << " not found"; }
		if (!trh.isValid())
			throw cms::Exception("ProductNotValid") << "TriggerResults product not valid";
		*/

		// Continue with main product: PAT-electrons

		// Prepare IDs for miniAOD
		electronIDValueMap.resize(tokenOfIds.size());
		for (size_t j = 0; j < tokenOfIds.size(); ++j)
		{
			cEvent->getByToken(this->tokenOfIds[j], this->electronIDValueMap[j]);
		}

		// call base class
		KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>::fillProduct(in, out, name, tag, pset);
		if (this->verbosity >= 3) std::cout << "KElectron::fillProduct end\n";
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		if (this->verbosity >= 3) std::cout << "KElectron::fillSingle\n";
		// momentum:
		copyP4(in, out.p4);
		// hash of pointer as Id
		out.internalId = hasher(&in);

		// charge and flavour (lepton type)
		assert(in.charge() == 1 || in.charge() == -1);
		out.leptonInfo = KLeptonFlavour::ELECTRON;

		if (in.charge() > 0) out.leptonInfo |= KLeptonChargeMask;
		if (in.isPF())       out.leptonInfo |= KLeptonPFMask;

		if (VertexCollection->size() == 0) throw cms::Exception("VertexCollection in KElectronProducer is empty");
		reco::Vertex vtx = (*VertexCollection).at(0);
		// electron track and impact parameter
		if (in.gsfTrack().isNonnull())
		{
			KTrackProducer::fillTrack(*in.gsfTrack(), out.track, std::vector<reco::Vertex>(), this->trackBuilder.product());
			// KTrackProducer::fillIPInfo(*in.gsfTrack(), out.track, *RefitVertices, trackBuilder.product());
			out.dxy = in.gsfTrack()->dxy(vtx.position());
			out.dz = in.gsfTrack()->dz(vtx.position());
		}

		// ECAL region: bits are set according to reco::GsfElectron::FiducialFlags
		// the last bit is set to show that this bitset is filled.
		out.fiducialFlags = in.isEB() | in.isEE() << 1 | in.isEBEEGap() << 2 |
			in.isEBEtaGap() << 3 | in.isEBPhiGap() << 4 |
			in.isEEDeeGap() << 5 | in.isEERingGap() << 6 | 1 << 7;

		//cutbased ID related stuff
		out.dEtaIn = in.deltaEtaSuperClusterTrackAtVtx();
		out.dPhiIn = in.deltaPhiSuperClusterTrackAtVtx();
		out.sigmaIetaIeta = in.sigmaIetaIeta();
		out.full5x5_sigmaIetaIeta = in.full5x5_sigmaIetaIeta();
		out.hadronicOverEm = in.hadronicOverEm();
		out.fbrem = in.fbrem();
		if (in.superCluster().isNonnull())
		{
			out.eSuperClusterOverP = in.eSuperClusterOverP();
			out.superclusterEnergy = in.superCluster()->energy();
			out.superclusterPosition = in.superCluster()->position();
			// Definition from RecoEgamma/ElectronIdentification/plugins/cuts/GsfDEtaInSeedCut.cc
			if (in.superCluster()->seed().isNonnull())
				out.dEtaInSeed = in.deltaEtaSuperClusterTrackAtVtx() - in.superCluster()->eta() + in.superCluster()->seed()->eta();
			else
				out.dEtaInSeed = std::numeric_limits<float>::max();
		}
		else
		{
			out.eSuperClusterOverP = std::numeric_limits<float>::max();
			out.superclusterEnergy = 0.;
			out.dEtaInSeed = std::numeric_limits<float>::max();
		}
		out.ecalEnergy = in.ecalEnergy();
		out.ecalEnergyErr = in.ecalEnergyError();
		out.trackMomentumErr = in.trackMomentumError();

		// fill electronType
		out.electronType = 0;
		out.electronType |= in.isEcalEnergyCorrected() << KElectronType::ecalEnergyCorrected;
		out.electronType |= in.ecalDriven()          << KElectronType::ecalDriven;
		out.electronType |= in.ecalDrivenSeed()        << KElectronType::ecalDrivenSeed;
		// Conversion Veto pre-calculated in PAT
		// https://github.com/cms-sw/cmssw/blob/69cd7ee90ab313f3736eea98316545635c8ca44c/PhysicsTools/PatAlgos/plugins/PATElectronProducer.cc#L453-L462
		// TODO: check if change from hasConversionMatch to passConversionVeto works
		out.electronType |= !(in.passConversionVeto())   << KElectronType::hasConversionMatch;
		

		// isolation
		out.trackIso = in.dr03TkSumPt();
		out.ecalIso = in.dr03EcalRecHitSumEt();
		out.hcal1Iso = in.dr03HcalDepth1TowerSumEt();
		out.hcal2Iso = in.dr03HcalDepth2TowerSumEt();

		if (doPfIsolation_) doPFIsolation(in, out);
		else
		{
			// fall back on built-in methods, where available
			out.sumChargedHadronPt = in.pfIsolationVariables().sumChargedHadronPt;
			out.sumPhotonEt        = in.pfIsolationVariables().sumPhotonEt;
			out.sumNeutralHadronEt = in.pfIsolationVariables().sumNeutralHadronEt;
			out.sumPUPt            = in.pfIsolationVariables().sumPUPt;
		}
		if (doPfIsolation_ && doCutbasedIds_ && !doAuxIds_) doCutbasedIds(in,out);
		if (doMvaIds_) doMvaIds(in, out);
		if (doAuxIds_) doAuxIds(in, out);
		if (this->verbosity >= 3) std::cout << "end KElectron::fillSingle\n";
	}

protected:

	virtual void doAuxIds(const SingleInputType &in, SingleOutputType &out)
	{
		edm::Ref<edm::View<pat::Electron>> pe(this->handle, this->nCursor);

		for (size_t i = 0; i < tagOfIds.size(); ++i)
			out.electronIds.push_back((*(electronIDValueMap)[i])[pe]);
	}

	// Modification for new MVA Electron ID for Run 2
	// https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
	// Full instructions in Producer/KElectrons_cff
	virtual void doMvaIds(const SingleInputType &in, SingleOutputType &out)
	{
		out.electronIds.clear();

		for (size_t i = 0; i < tagOfIds.size(); ++i)
		{
			out.electronIds.push_back(in.electronID(tagOfIds[i].instance()));
		}
		for (size_t i = 0; i < tagOfUserFloats.size(); ++i)
		{
			out.electronIds.push_back(in.userFloat(tagOfUserFloats[i].instance()));
		}


	}

	// cutbased IDs (cf. header)
	// ElectronTools/interface/ElectronEffectiveArea.h: ElectronEffectiveAreaTarget::kEleEAData2011,kEleEASummer11MC,kEleEAFall11MC,kEleEAData2012
	// in analogy to https://github.com/cms-analysis/EgammaAnalysis-ElectronTools/blob/master/src/EGammaCutBasedEleIdAnalyzer.cc
	virtual void doCutbasedIds(const SingleInputType &in, SingleOutputType &out)
	{
		const reco::BeamSpot &tmpbeamSpot = *(BeamSpot.product());
		const reco::GsfElectron* eGSF = dynamic_cast<const reco::GsfElectron*>(in.originalObjectRef().get());

		double rhoIso = *(rhoIso_h.product());
		bool cutbasedIDloose = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::LOOSE,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDmedium = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::MEDIUM,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDtight = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::TIGHT,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDveto = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::VETO,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		out.ids = 1 << KLeptonId::ANY;  // mark it as filled
		out.ids |= cutbasedIDloose << KLeptonId::LOOSE;
		out.ids |= cutbasedIDmedium << KLeptonId::MEDIUM;
		out.ids |= cutbasedIDtight << KLeptonId::TIGHT;
		out.ids |= cutbasedIDveto << KLeptonId::VETO;
		assert(out.ids < 32);   // other bits should be zero
	}

	virtual void doPFIsolation(const SingleInputType &in, SingleOutputType &out)
	{
		// we need the Ref, cf. example EgammaAnalysis/ElectronTools/src/EGammaCutBasedEleIdAnalyzer.cc
		edm::Ref<edm::View<pat::Electron>> pe(this->handle, this->nCursor);
		
		// isolation values (PF is used for IDs later)
		out.sumChargedHadronPt = (*(this->isoVals)[0])[pe];
		out.sumPhotonEt        = (*(this->isoVals)[1])[pe];
		out.sumNeutralHadronEt = (*(this->isoVals)[2])[pe];
		out.sumPUPt            = (*(this->isoVals)[3])[pe];
	}

private:

	KElectronMetadata *electronMetadata;
	boost::hash<const pat::Electron*> hasher;

	std::vector<edm::Handle<edm::ValueMap<double> > > isoVals;
	edm::Handle<reco::ConversionCollection> hConversions;
	edm::Handle<reco::BeamSpot> BeamSpot;
	edm::Handle<reco::VertexCollection> VertexCollection;
	edm::Handle<RefitVertexCollection> RefitVertices;
	edm::ESHandle<TransientTrackBuilder> trackBuilder;
	edm::Handle<double> rhoIso_h;

	edm::InputTag tagConversionSource;
	edm::InputTag beamSpotSource;
	edm::InputTag VertexCollectionSource;
	edm::InputTag rhoIsoTag;
	std::vector<edm::InputTag>  isoValInputTags;
	std::vector<edm::InputTag> tagOfIds;
	std::vector<edm::InputTag> tagOfUserFloats;
	
	edm::EDGetTokenT<reco::ConversionCollection> tokenConversionSource;
	edm::EDGetTokenT<reco::BeamSpot> tokenBeamSpot;
	edm::EDGetTokenT<reco::VertexCollection> tokenVertexCollection;
	edm::EDGetTokenT<double> tokenRhoIso; 
	std::vector<edm::EDGetTokenT<edm::ValueMap<double>>> tokenIsoValInputTags ;
	std::vector<edm::EDGetTokenT<edm::ValueMap<float>>> tokenOfIds;

	std::string srcIds_;
	bool doPfIsolation_;
	bool doCutbasedIds_;
	bool doMvaIds_;
	bool doAuxIds_;

	edm::InputTag RefitVerticesSource;
	edm::EDGetTokenT<RefitVertexCollection> tokenRefitVertices;

	std::vector<edm::Handle<edm::ValueMap<float> > > electronIDValueMap;

};

#endif

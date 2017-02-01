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
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"
#include "boost/functional/hash.hpp"
#include "EgammaAnalysis/ElectronTools/interface/EGammaCutBasedEleId.h"
#if (CMSSW_MAJOR_VERSION == 5 && CMSSW_MINOR_VERSION == 3 && CMSSW_REVISION >= 15) || (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 2) || CMSSW_MAJOR_VERSION >= 8
	#include "EgammaAnalysis/ElectronTools/interface/ElectronEffectiveArea.h"
#endif


class KElectronProducer : public KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>
{
public:
	KElectronProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::Electron>,
		KElectrons>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		namesOfIds(cfg.getParameter<std::vector<std::string> >("ids")),
		srcIds_(cfg.getParameter<std::string>("srcIds")),
		doPfIsolation_(true),
		doCutbasedIds_(true)
{
	electronMetadata = new KElectronMetadata;
	_lumi_tree->Bronch("electronMetadata", "KElectronMetadata", &electronMetadata);

	doMvaIds_ = (srcIds_ == "pat");
	doAuxIds_ = (srcIds_ == "standalone");

	const edm::ParameterSet &psBase = this->psBase;
	std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

	for (size_t i = 0; i < names.size(); ++i)
	{
		const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);
		if(pset.existsAs<edm::InputTag>("allConversions")) consumescollector.consumes<reco::ConversionCollection>(pset.getParameter<edm::InputTag>("allConversions"));
		if(pset.existsAs<edm::InputTag>("offlineBeamSpot")) consumescollector.consumes<reco::BeamSpot>(pset.getParameter<edm::InputTag>("offlineBeamSpot"));
		if(pset.existsAs<edm::InputTag>("vertexcollection")) consumescollector.consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertexcollection"));
		if(pset.existsAs<edm::InputTag>("rhoIsoInputTag")) consumescollector.consumes<double>(pset.getParameter<edm::InputTag>("rhoIsoInputTag"));
		if(pset.existsAs<std::vector<edm::InputTag>>("isoValInputTags"))
		{
			for(size_t j = 0; j < pset.getParameter<std::vector<edm::InputTag>>("isoValInputTags").size(); ++j) consumescollector.consumes<edm::ValueMap<double>>(pset.getParameter<std::vector<edm::InputTag>>("isoValInputTags").at(j));
		}
	}
	for (size_t j = 0; j < namesOfIds.size(); ++j)
	{
		consumescollector.consumes<edm::ValueMap<float> >(edm::InputTag(namesOfIds[j]));
	}
}

	static const std::string getLabel() { return "Electrons"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		for (std::vector<std::string>::const_iterator id = namesOfIds.begin(); id != namesOfIds.end(); ++id)
		{
			electronMetadata->idNames.push_back(*id);
		}
		return KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>::onLumi(lumiBlock, setup);
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Get additional objects for the cutbased IDs
		edm::InputTag tagConversionSource = pset.getParameter<edm::InputTag>("allConversions");
		cEvent->getByLabel(tagConversionSource, hConversions);

		edm::InputTag beamSpotSource = pset.getParameter<edm::InputTag>("offlineBeamSpot");
		cEvent->getByLabel(beamSpotSource, BeamSpot);

		edm::InputTag VertexCollectionSource = pset.getParameter<edm::InputTag>("vertexcollection");
		cEvent->getByLabel(VertexCollectionSource, VertexCollection);

		std::vector<edm::InputTag>  isoValInputTags = pset.getParameter<std::vector<edm::InputTag> >("isoValInputTags");
		isoVals.resize(isoValInputTags.size());
		for (size_t j = 0; j < isoValInputTags.size(); ++j)
		{
			cEvent->getByLabel(isoValInputTags[j], isoVals[j]);
			if (isoVals[j].failedToGet())
			{
				doPfIsolation_ = false;
			}
		}
		
		cEvent->getByLabel(pset.getParameter<edm::InputTag>("rhoIsoInputTag"), rhoIso_h);
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
		edm::InputTag electronIdsInputTag;
		electronIDValueMap.resize(namesOfIds.size());
		for (size_t j = 0; j < namesOfIds.size(); ++j)
		{
			electronIdsInputTag = edm::InputTag(namesOfIds[j]);
			cEvent->getByLabel(electronIdsInputTag, electronIDValueMap[j]);
		}
		
		// call base class
		KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// momentum:
		copyP4(in, out.p4);
		// hash of pointer as Id
		out.internalId = hasher(&in);

		// charge and flavour (lepton type)
		assert(in.charge() == 1 || in.charge() == -1);
		out.leptonInfo = KLeptonFlavour::ELECTRON;
		if (in.charge() > 0)
			out.leptonInfo |= KLeptonChargeMask;
		if (in.isPF())
			out.leptonInfo |= KLeptonPFMask;

		reco::Vertex vtx = (*VertexCollection).at(0);
		// electron track and impact parameter
		if (in.gsfTrack().isNonnull())
		{
			KTrackProducer::fillTrack(*in.gsfTrack(), out.track);
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
#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 1) || CMSSW_MAJOR_VERSION >= 8
		out.full5x5_sigmaIetaIeta = in.full5x5_sigmaIetaIeta();
#endif
		out.hadronicOverEm = in.hadronicOverEm();
		out.fbrem = in.fbrem();
		if(in.superCluster().isNonnull())
		{
			out.eSuperClusterOverP = in.eSuperClusterOverP();
			out.superclusterEnergy = in.superCluster()->energy();
			out.superclusterPosition = in.superCluster()->position();
			// Definition from RecoEgamma/ElectronIdentification/plugins/cuts/GsfDEtaInSeedCut.cc
			if(in.superCluster()->seed().isNonnull())
			{
				out.dEtaInSeed = in.deltaEtaSuperClusterTrackAtVtx() - in.superCluster()->eta() + in.superCluster()->seed()->eta();
			}
			else
			{
				out.dEtaInSeed = std::numeric_limits<float>::max();
			}
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

		if (doPfIsolation_)
			doPFIsolation(in, out);
#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 4) || (CMSSW_MAJOR_VERSION > 7)
		else {
			// fall back on built-in methods, where available
			out.sumChargedHadronPt = in.pfIsolationVariables().sumChargedHadronPt;
			out.sumPhotonEt        = in.pfIsolationVariables().sumPhotonEt;
			out.sumNeutralHadronEt = in.pfIsolationVariables().sumNeutralHadronEt;
			out.sumPUPt            = in.pfIsolationVariables().sumPUPt;
		}
#endif
		if (doPfIsolation_ && doCutbasedIds_ && !doAuxIds_)
			doCutbasedIds(in,out);
		if(doMvaIds_)
			doMvaIds(in, out);
		if(doAuxIds_)
			doAuxIds(in, out);
	}


protected:
	virtual void doAuxIds(const SingleInputType &in, SingleOutputType &out)
	{
		edm::Ref<edm::View<pat::Electron>> pe(this->handle, this->nCursor);
		for (size_t i = 0; i < namesOfIds.size(); ++i)
		{
			out.electronIds.push_back((*(electronIDValueMap)[i])[pe]);
		}
	}
	virtual void doMvaIds(const SingleInputType &in, SingleOutputType &out)
	{
		/* Modification for new MVA Electron ID for Run 2
		 * https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
		 * Full instructions in Producer/KElectrons_cff
		 */
		out.electronIds.clear();
		for (size_t i = 0; i < namesOfIds.size(); ++i)
		{
			out.electronIds.push_back(in.electronID(namesOfIds[i]));
		}
	}

	virtual void doCutbasedIds(const SingleInputType &in, SingleOutputType &out)
	// cutbased IDs (cf. header)
	// ElectronTools/interface/ElectronEffectiveArea.h: ElectronEffectiveAreaTarget::kEleEAData2011,kEleEASummer11MC,kEleEAFall11MC,kEleEAData2012
	{
		// in analogy to https://github.com/cms-analysis/EgammaAnalysis-ElectronTools/blob/master/src/EGammaCutBasedEleIdAnalyzer.cc
		const reco::BeamSpot &tmpbeamSpot = *(BeamSpot.product());
	
		const reco::GsfElectron* eGSF = dynamic_cast<const reco::GsfElectron*>(in.originalObjectRef().get());

		double rhoIso = *(rhoIso_h.product());
#if (CMSSW_MAJOR_VERSION == 5 && CMSSW_MINOR_VERSION == 3 && CMSSW_REVISION >= 15) || (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 2) || CMSSW_MAJOR_VERSION >= 8
		bool cutbasedIDloose = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::LOOSE,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDmedium = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::MEDIUM,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDtight = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::TIGHT,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDveto = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::VETO,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso, ElectronEffectiveArea::kEleEAData2012);
#else
		bool cutbasedIDloose = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::LOOSE,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso);
		bool cutbasedIDmedium = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::MEDIUM,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso);
		bool cutbasedIDtight = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::TIGHT,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso);
		bool cutbasedIDveto = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::VETO,
			*eGSF, hConversions, tmpbeamSpot, VertexCollection, out.sumChargedHadronPt, out.sumPhotonEt, out.sumNeutralHadronEt, rhoIso);
#endif
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
		out.sumChargedHadronPt = (*(isoVals)[0])[pe];
		out.sumPhotonEt        = (*(isoVals)[1])[pe];
		out.sumNeutralHadronEt = (*(isoVals)[2])[pe];
		out.sumPUPt            = (*(isoVals)[3])[pe];
	}

private:
	std::vector<std::string> namesOfIds;
	KElectronMetadata *electronMetadata;
	boost::hash<const pat::Electron*> hasher;

	std::vector<edm::Handle<edm::ValueMap<double> > > isoVals;
	edm::Handle<reco::ConversionCollection> hConversions;
	edm::Handle<reco::BeamSpot> BeamSpot;
	edm::Handle<reco::VertexCollection> VertexCollection;
	edm::Handle<double> rhoIso_h;
	std::string srcIds_;
	bool doPfIsolation_;
	bool doCutbasedIds_;
	bool doMvaIds_;
	bool doAuxIds_;

	std::vector<edm::Handle<edm::ValueMap<float> > > electronIDValueMap;
};

#endif

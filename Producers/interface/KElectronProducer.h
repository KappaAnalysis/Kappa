/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_ELECTRONPRODUCER_H
#define KAPPA_ELECTRONPRODUCER_H

#include "KBaseMultiLVProducer.h"

//#include <DataFormats/EgammaCandidates/interface/GsfElectron.h>
#include <DataFormats/PatCandidates/interface/Electron.h>
#include <bitset>
#include <TMath.h>
#include <RecoEgamma/EgammaTools/interface/ConversionTools.h>
#include <DataFormats/BeamSpot/interface/BeamSpot.h>
#include "EgammaAnalysis/ElectronTools/interface/EGammaCutBasedEleId.h"
#include "EgammaAnalysis/ElectronTools/interface/ElectronEffectiveArea.h"


class KElectronProducer : public KBaseMultiLVProducer<edm::View<pat::Electron>, KDataElectrons>
{
public:
	KElectronProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMultiLVProducer<edm::View<pat::Electron>, KDataElectrons>(cfg, _event_tree, _lumi_tree, getLabel()),
		 namesOfIds(cfg.getParameter<std::vector<std::string> >("IDs"))
{
		names = new KElectronIdMetadata;
		_lumi_tree->Bronch("electronIdMetadata", "KElectronIdMetadata", &names);
}

	static const std::string getLabel() { return "Electrons"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		for (std::vector<std::string>::const_iterator id = namesOfIds.begin(); id != namesOfIds.end(); ++id)
		{
			names->idNames.push_back(*id);
		}
		return KBaseMultiLVProducer<edm::View<pat::Electron>, KDataElectrons>::onLumi(lumiBlock, setup);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{	
		out.flavour = KLepton::ELECTRON;
	
		// Momentum:
		copyP4(in, out.p4);

		// Charge, ...
		out.charge = in.charge();

		// electron track
		KTrackProducer::fillTrack(*in.gsfTrack(), out.track);

		// ECAL region: bits are set according to reco::GsfElectron::FiducialFlags
		out.fiducialFlags = in.isEB() | in.isEE() << 1 | in.isEBEEGap() << 2 |
			in.isEBEtaGap() << 3 | in.isEBPhiGap() << 4 |
			in.isEEDeeGap() << 5 | in.isEERingGap() << 6;

		out.status = in.status();

		out.ecalDrivenSeed = in.ecalDrivenSeed();
		out.ecalDriven = in.ecalDriven();

		// isolation
		out.trackIso03 = in.dr03TkSumPt();
		out.ecalIso03 = in.dr03EcalRecHitSumEt();
		out.hcal1Iso03 = in.dr03HcalDepth1TowerSumEt();
		out.hcal2Iso03 = in.dr03HcalDepth2TowerSumEt();

		out.trackIso04 = in.dr04TkSumPt();
		out.ecalIso04 = in.dr04EcalRecHitSumEt();
		out.hcal1Iso04 = in.dr04HcalDepth1TowerSumEt();
		out.hcal2Iso04 = in.dr04HcalDepth2TowerSumEt();

		//cutbased ID related stuff
		out.deltaEtaSuperClusterTrackAtVtx = in.deltaEtaSuperClusterTrackAtVtx();
		out.deltaPhiSuperClusterTrackAtVtx = in.deltaPhiSuperClusterTrackAtVtx();
		out.sigmaIetaIeta = in.sigmaIetaIeta();
		out.hadronicOverEm = in.hadronicOverEm();
		out.fbrem = in.fbrem();
		out.eSuperClusterOverP = in.eSuperClusterOverP();
		
		//supercluster
		out.superclusterEnergy = in.superCluster()->energy();
		out.superclusterPosition = in.superCluster()->position();

		// Corrections
		out.isEcalEnergyCorrected = in.isEcalEnergyCorrected();
		out.ecalEnergy = in.ecalEnergy();
		out.ecalEnergyError = in.ecalEnergyError();
		/////////out.isMomentumCorrected = in.isMomentumCorrected();
		out.trackMomentumError = in.trackMomentumError();
		/////////out.electronMomentumError = in.electronMomentumError();

		/* Modification for new MVA Electron ID for Run 2
		 * https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
		 * Full instructions in Producer/KElectrons_cff
		 */
		for (size_t i = 0; i < namesOfIds.size(); ++i)
		{
		out.electronIds.push_back(in.electronID(namesOfIds[i]));
		}

		const reco::GsfElectron* tmpGsfElectron = dynamic_cast<const reco::GsfElectron*>(in.originalObjectRef().get());
		out.hasConversionMatch = ConversionTools::hasMatchedConversion(*tmpGsfElectron, hConversions, BeamSpot->position(), true, 2.0, 1e-6, 0);

		const reco::BeamSpot &tmpbeamSpot = *(BeamSpot.product());
		// we need the Ref
		edm::Ref<edm::View<pat::Electron>> pe(this->handle, this->nCursor);

		// Get the PF isolation values
		double iso_ch = (*(isoVals)[0])[pe];
		double iso_em = (*(isoVals)[1])[pe];
		double iso_nh = (*(isoVals)[2])[pe];
		double rhoIso = *(rhoIso_h.product());

		out.pfIsoCh = iso_ch;
		out.pfIsoEm = iso_em;
		out.pfIsoNh = iso_nh;

		// cutbased ID
		/** defined in
		EgammaAnalysis/ElectronTools/interface/EGammaCutBasedEleId.h
		*/

		bool cutbasedIDloose = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::LOOSE,
		*tmpGsfElectron, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_em, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDmedium = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::MEDIUM,
		*tmpGsfElectron, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_em, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDtight = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::TIGHT,
		*tmpGsfElectron, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_em, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);
		bool cutbasedIDveto = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::VETO,
		*tmpGsfElectron, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_em, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);

		out.cutbasedIDs = cutbasedIDloose;
		out.cutbasedIDs |= cutbasedIDmedium << 1;
		out.cutbasedIDs |= cutbasedIDtight << 2 ;
		out.cutbasedIDs |= cutbasedIDveto << 3;
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		//todo: fill hConversions
		edm::InputTag tagConversionSource = pset.getParameter<edm::InputTag>("allConversions");
		cEvent->getByLabel(tagConversionSource, hConversions);

		edm::InputTag beamSpotSource = pset.getParameter<edm::InputTag>("offlineBeamSpot");
		cEvent->getByLabel(beamSpotSource, BeamSpot);

		edm::InputTag VertexCollectionSource = pset.getParameter<edm::InputTag>("vertexcollection");
		cEvent->getByLabel(VertexCollectionSource, VertexCollection);

		std::vector<edm::InputTag>  isoValInputTags_ = pset.getParameter<std::vector<edm::InputTag> >("isoValInputTags");
		isoVals.resize(isoValInputTags_.size());
		for (size_t j = 0; j < isoValInputTags_.size(); ++j)
		{
			cEvent->getByLabel(isoValInputTags_[j], isoVals[j]);
		}

		// Continue normally
		KBaseMultiLVProducer<edm::View<pat::Electron>, KDataElectrons>::fillProduct(in, out, name, tag, pset);

	}
private:
	std::vector<std::string> namesOfIds;
	KElectronIdMetadata *names;

	std::vector< edm::Handle< edm::ValueMap<double> > > isoVals;
	edm::Handle<reco::ConversionCollection> hConversions;
	edm::Handle<reco::BeamSpot> BeamSpot;
	edm::Handle<reco::VertexCollection> VertexCollection;
	edm::Handle<double> rhoIso_h;

};

#endif

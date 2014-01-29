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



class KElectronProducer : public KBaseMultiLVProducer<edm::View<pat::Electron>, KDataElectrons>
{
public:
	KElectronProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMultiLVProducer<edm::View<pat::Electron>, KDataElectrons>(cfg, _event_tree, _lumi_tree, getLabel()) {}

	static const std::string getLabel() { return "Electrons"; }

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Momentum:
		copyP4(in, out.p4);

		// Charge, ...
		out.charge = in.charge();

		// electron track
		KTrackProducer::fillTrack(*in.gsfTrack(), out.track);

		out.isEB = in.isEB();
		out.isEE = in.isEE();

		out.mva = in.mva();
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

		// Corrections
		out.isEcalEnergyCorrected = in.isEcalEnergyCorrected();
		out.ecalEnergy = in.ecalEnergy();
		out.ecalEnergyError = in.ecalEnergyError();
		//out.isMomentumCorrected = in.isMomentumCorrected();
		out.trackMomentumError = in.trackMomentumError();
		//out.electronMomentumError = in.electronMomentumError();
		out.idMvaTrigV0 = in.electronID("mvaTrigV0");
		out.idMvaTrigNoIPV0 = in.electronID("mvaTrigNoIPV0");
		out.idMvaNonTrigV0 = in.electronID("mvaNonTrigV0");

		out.nLostHits = in.gsfTrack()->trackerExpectedHitsInner().numberOfHits();

	const reco::GsfElectron* tmpGsfElectron = dynamic_cast<const reco::GsfElectron*>(in.originalObjectRef().get());
	out.hasConversionMatch = ConversionTools::hasMatchedConversion(*tmpGsfElectron, hConversions, BeamSpot->position(), true, 2.0, 1e-6, 0);

	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		//todo: fill hConversions
		edm::InputTag tagConversionSource = pset.getParameter<edm::InputTag>("allConversions");
		cEvent->getByLabel(tagConversionSource, hConversions);

		edm::InputTag beamSpotSource = pset.getParameter<edm::InputTag>("offlineBeamSpot");
		cEvent->getByLabel(beamSpotSource, BeamSpot);

		// Continue normally
		KBaseMultiLVProducer<edm::View<pat::Electron>, KDataElectrons>::fillProduct(in, out, name, tag, pset);

	}
private:
	edm::Handle<reco::ConversionCollection> hConversions;
	edm::Handle<reco::BeamSpot> BeamSpot;

};

#endif

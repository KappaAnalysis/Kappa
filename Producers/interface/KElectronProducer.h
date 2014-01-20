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

        out.isEB = in.isEB();
        out.isEE = in.isEE();

        out.mva = in.mva();
        out.status = in.status();

        out.ecalDrivenSeed = in.ecalDrivenSeed();
        out.ecalDriven = in.ecalDriven();

        // isolation
        out.dr03TkSumPt = in.dr03TkSumPt();
        out.dr03EcalRecHitSumEt = in.dr03EcalRecHitSumEt();
        out.dr03HcalDepth1TowerSumEt = in.dr03HcalDepth1TowerSumEt();
        out.dr03HcalDepth2TowerSumEt = in.dr03HcalDepth2TowerSumEt();

        out.dr04TkSumPt = in.dr04TkSumPt();
        out.dr04EcalRecHitSumEt = in.dr04EcalRecHitSumEt();
        out.dr04HcalDepth1TowerSumEt = in.dr04HcalDepth1TowerSumEt();
        out.dr04HcalDepth2TowerSumEt = in.dr04HcalDepth2TowerSumEt();

        // Corrections
        out.isEcalEnergyCorrected = in.isEcalEnergyCorrected();
        out.ecalEnergy = in.ecalEnergy();
        out.ecalEnergyError = in.ecalEnergyError();
        //out.isMomentumCorrected = in.isMomentumCorrected();
        out.trackMomentumError = in.trackMomentumError();
        //out.electronMomentumError = in.electronMomentumError();
        out.electronIDmvaTrigV0 = in.electronID("mvaTrigV0");
        out.electronIDmvaTrigNoIPV0 = in.electronID("mvaTrigNoIPV0");
        out.electronIDmvaNonTrigV0 = in.electronID("mvaNonTrigV0");

        out.numberOfLostHits = in.gsfTrack()->trackerExpectedHitsInner().numberOfHits();
	}

};

#endif

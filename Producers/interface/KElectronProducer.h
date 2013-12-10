/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_ELECTRONPRODUCER_H
#define KAPPA_ELECTRONPRODUCER_H

#include "KBaseMultiLVProducer.h"

<<<<<<< HEAD
#include <DataFormats/EgammaCandidates/interface/GsfElectron.h>

=======
>>>>>>> 7f27c71be8613bbcc8e11ef242b306b780533e20
#include <bitset>
#include <TMath.h>

struct KElectronProducer_Product
{
	typedef std::vector<KDataElectron> type;
	static const std::string id() { return "std::vector<KDataElectron>"; };
	static const std::string producer() { return "KElectronProducer"; };
};

class KElectronProducer : public KBaseMultiLVProducer<edm::View<reco::GsfElectron>, KElectronProducer_Product>
{
public:
	KElectronProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMultiLVProducer<edm::View<reco::GsfElectron>, KElectronProducer_Product>(cfg, _event_tree, _lumi_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Momentum:
		copyP4(in, out.p4);

		// Charge, ...
		out.charge = in.charge();
<<<<<<< HEAD

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

=======
>>>>>>> 7f27c71be8613bbcc8e11ef242b306b780533e20
	}

};

#endif

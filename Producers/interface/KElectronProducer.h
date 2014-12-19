/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_ELECTRONPRODUCER_H
#define KAPPA_ELECTRONPRODUCER_H

#include "KBaseMultiLVProducer.h"

#include <DataFormats/PatCandidates/interface/Electron.h>
#include <RecoEgamma/EgammaTools/interface/ConversionTools.h>
#include <DataFormats/BeamSpot/interface/BeamSpot.h>
#include "EgammaAnalysis/ElectronTools/interface/EGammaCutBasedEleId.h"
#if (CMSSW_MAJOR_VERSION == 5 && CMSSW_MINOR_VERSION == 3 && CMSSW_REVISION >= 15) || (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 2)
	#include "EgammaAnalysis/ElectronTools/interface/ElectronEffectiveArea.h"
#endif


class KElectronProducer : public KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>
{
public:
	KElectronProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMultiLVProducer<edm::View<pat::Electron>,
		KElectrons>(cfg, _event_tree, _lumi_tree, getLabel()),
		namesOfIds(cfg.getParameter<std::vector<std::string> >("ids")),
		doPfIsolation(true),
		doCutbasedIds(true),
		doMvaIds(true)
{
		electronMetadata = new KElectronMetadata;
		_lumi_tree->Bronch("electronMetadata", "KElectronMetadata", &electronMetadata);
		
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

		std::vector<edm::InputTag>  isoValInputTags_ = pset.getParameter<std::vector<edm::InputTag> >("isoValInputTags");
		isoVals.resize(isoValInputTags_.size());
		for (size_t j = 0; j < isoValInputTags_.size(); ++j)
		{
			cEvent->getByLabel(isoValInputTags_[j], isoVals[j]);
			if (isoVals[j].failedToGet())
			{
				doPfIsolation = false;
			}
		}
		
		cEvent->getByLabel(pset.getParameter<edm::InputTag>("rhoIsoInputTag"), rhoIso_h);
		//std::cout << "Do iso " << doPfIsolation << std::endl << std::flush;
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
		KBaseMultiLVProducer<edm::View<pat::Electron>, KElectrons>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// momentum:
		copyP4(in, out.p4);

		// charge and flavour (lepton type)
		assert(in.charge() == 1 || in.charge() == -1);
		out.leptonInfo = KLeptonFlavour::ELECTRON;
		if (in.charge() > 0)
			out.leptonInfo |= KLeptonChargeMask;
		if (in.isPF())
			out.leptonInfo |= KLeptonPFMask;

		// electron track
		if (in.gsfTrack().isNonnull())
			KTrackProducer::fillTrack(*in.gsfTrack(), out.track);
		else if (in.gsfTrack().isNonnull())
		{
			KTrackProducer::fillTrack(*in.gsfTrack(), out.track);
			out.leptonInfo |= KLeptonAlternativeTrackMask;
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
		out.hadronicOverEm = in.hadronicOverEm();
		out.fbrem = in.fbrem();
		out.eSuperClusterOverP = in.eSuperClusterOverP();
		out.superclusterEnergy = in.superCluster()->energy();
		out.superclusterPosition = in.superCluster()->position();
		out.ecalEnergy = in.ecalEnergy();
		out.ecalEnergyErr = in.ecalEnergyError();
		out.trackMomentumErr = in.trackMomentumError();

		// fill electronType
		const reco::GsfElectron* eGSF = dynamic_cast<const reco::GsfElectron*>(in.originalObjectRef().get());
		out.electronType = 0;
		out.electronType |= in.isEcalEnergyCorrected() << KElectronType::ecalEnergyCorrected;
		//out.electronType |= in.isMomentumCorrected()   << KElectronType::momentumCorrected;
		out.electronType |= in.ecalDriven()          << KElectronType::ecalDriven;
		//out.electronType |= in.trackerDriven()       << KElectronType::trackerDriven;
		//out.electronType |= in.cutPreselected()      << KElectronType::cutPreselected;
		//out.electronType |= in.mvaPreselected()      << KElectronType::mvaPreselected;
		out.electronType |= in.ecalDrivenSeed()        << KElectronType::ecalDrivenSeed;
		out.electronType |= ConversionTools::hasMatchedConversion(
			*eGSF, hConversions, BeamSpot->position(), true, 2.0, 1e-6, 0)
			<< KElectronType::hasConversionMatch;

		// isolation
		out.trackIso = in.dr03TkSumPt();
		out.ecalIso = in.dr03EcalRecHitSumEt();
		out.hcal1Iso = in.dr03HcalDepth1TowerSumEt();
		out.hcal2Iso = in.dr03HcalDepth2TowerSumEt();

		if (doPfIsolation)
		{
			const reco::BeamSpot &tmpbeamSpot = *(BeamSpot.product());
			// we need the Ref, cf. example EgammaAnalysis/ElectronTools/src/EGammaCutBasedEleIdAnalyzer.cc
			edm::Ref<edm::View<pat::Electron>> pe(this->handle, this->nCursor);
			
			// isolation values (PF is used for IDs later)
			double iso_ch = (*(isoVals)[0])[pe];
			double iso_ph = (*(isoVals)[1])[pe];
			double iso_nh = (*(isoVals)[2])[pe];
			double iso_pu = (*(isoVals)[3])[pe];
			double rhoIso = *(rhoIso_h.product());

			out.sumChargedHadronPt = iso_ch;
			out.sumNeutralHadronEt = iso_nh;
			out.sumPhotonEt = iso_ph;
			out.sumPUPt = iso_pu;

			// cutbased IDs (cf. header)
			// ElectronTools/interface/ElectronEffectiveArea.h: ElectronEffectiveAreaTarget::kEleEAData2011,kEleEASummer11MC,kEleEAFall11MC,kEleEAData2012
			if (doCutbasedIds)
			{
#if (CMSSW_MAJOR_VERSION == 5 && CMSSW_MINOR_VERSION == 3 && CMSSW_REVISION >= 15) || (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 2)
				bool cutbasedIDloose = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::LOOSE,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);
				bool cutbasedIDmedium = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::MEDIUM,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);
				bool cutbasedIDtight = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::TIGHT,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);
				bool cutbasedIDveto = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::VETO,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso, ElectronEffectiveArea::kEleEAData2012);
#else
				bool cutbasedIDloose = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::LOOSE,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso);
				bool cutbasedIDmedium = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::MEDIUM,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso);
				bool cutbasedIDtight = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::TIGHT,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso);
				bool cutbasedIDveto = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::VETO,
				*eGSF, hConversions, tmpbeamSpot, VertexCollection, iso_ch, iso_ph, iso_nh, rhoIso);
#endif
				out.ids = 1 << KLeptonId::ANY;  //< mark it as filled
				out.ids |= cutbasedIDloose << KLeptonId::LOOSE;
				out.ids |= cutbasedIDmedium << KLeptonId::MEDIUM;
				out.ids |= cutbasedIDtight << KLeptonId::TIGHT;
				out.ids |= cutbasedIDveto << KLeptonId::VETO;
				assert(out.ids < 32);   // other bits should be zero
			}
		}
		/* Modification for new MVA Electron ID for Run 2
		 * https://twiki.cern.ch/twiki/bin/viewauth/CMS/MultivariateElectronIdentificationRun2
		 * Full instructions in Producer/KElectrons_cff
		 */
		out.electronIds.clear();
		if (doMvaIds)
			for (size_t i = 0; i < namesOfIds.size(); ++i)
			{
				out.electronIds.push_back(in.electronID(namesOfIds[i]));
			}
	}

private:
	std::vector<std::string> namesOfIds;
	KElectronMetadata *electronMetadata;

	std::vector<edm::Handle<edm::ValueMap<double> > > isoVals;
	edm::Handle<reco::ConversionCollection> hConversions;
	edm::Handle<reco::BeamSpot> BeamSpot;
	edm::Handle<reco::VertexCollection> VertexCollection;
	edm::Handle<double> rhoIso_h;
	bool doPfIsolation;
	bool doCutbasedIds;
	bool doMvaIds;
};

#endif

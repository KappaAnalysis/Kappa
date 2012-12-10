#ifndef KAPPA_MUONPRODUCER_H
#define KAPPA_MUONPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KTrackProducer.h"

#include <bitset>
#include <TMath.h>
#include <Math/GenVector/VectorUtil.h>
#include <DataFormats/Common/interface/Ref.h>
#include <DataFormats/Common/interface/ValueMap.h>
#include <DataFormats/GeometrySurface/interface/Cylinder.h>
#include <DataFormats/GeometrySurface/interface/Plane.h>
#include <DataFormats/HLTReco/interface/TriggerEvent.h>
#include <DataFormats/MuonReco/interface/MuonFwd.h>
#include <DataFormats/MuonReco/interface/Muon.h>
#include <DataFormats/MuonReco/src/MuonSelectors.cc>
#include <DataFormats/RecoCandidate/interface/IsoDepositVetos.h>
#include <HLTriggerOffline/Muon/src/PropagateToMuon.cc>
#include <PhysicsTools/IsolationAlgos/interface/IsoDepositVetoFactory.h>
#include <TrackingTools/GeomPropagators/interface/Propagator.h>
#include <TrackingTools/Records/interface/TrackingComponentsRecord.h>
#include <TrackingTools/Records/interface/TransientTrackRecord.h>
#include <TrackingTools/TransientTrack/interface/TransientTrackBuilder.h>

struct KMuonProducer_Product
{
	typedef std::vector<KDataMuon> type;
	static const std::string id() { return "std::vector<KDataMuon>"; };
	static const std::string producer() { return "KMuonProducer"; };
};

class KMuonProducer : public KBaseMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>
{
public:
	KMuonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>(cfg, _event_tree, _lumi_tree),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hlTrigger")),
		hltMaxdR(cfg.getParameter<double>("hltMaxdR")),
		hltMaxdPt_Pt(cfg.getParameter<double>("hltMaxdPt_Pt")),
		selectedMuonTriggerObjects(cfg.getParameter<std::vector<std::string> >("muonTriggerObjects")),
		noPropagation(cfg.getParameter<bool>("noPropagation")),
		propagatorToMuonSystem(cfg)
	{
		std::sort(selectedMuonTriggerObjects.begin(), selectedMuonTriggerObjects.end());
		std::vector<std::string>::iterator tempIt = std::unique (selectedMuonTriggerObjects.begin(), selectedMuonTriggerObjects.end());
		selectedMuonTriggerObjects.resize(tempIt - selectedMuonTriggerObjects.begin());

		muonMetadata = new KMuonMetadata();
		_lumi_tree->Bronch("KMuonMetadata", "KMuonMetadata", &muonMetadata);

	}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		propagatorToMuonSystem.init(setup);

		muonMetadata->hltNames.clear();
		muonTriggerObjectBitMap.clear();

		if (selectedMuonTriggerObjects.size() > 64)
		{
			std::cout << "Too many muon trigger objects selected (" << selectedMuonTriggerObjects.size() << ">64)!" << std::endl;
			throw cms::Exception("Too many muon trigger objects selected");
		}

		for (std::vector<std::string>::iterator it = selectedMuonTriggerObjects.begin(); it != selectedMuonTriggerObjects.end(); it++)
		{
			std::string filterName = *it;
			if (muonTriggerObjectBitMap.find(filterName) != muonTriggerObjectBitMap.end())
				throw cms::Exception("The muon trigger object '" + filterName + "' exists twice. Please remove one from your configuration!");
			if (muonMetadata->hltNames.size() >= 64)
				throw cms::Exception("Too many muon trigger objects selected!");
			if (verbosity > 0)
				std::cout << filterName << "\n";
			muonMetadata->hltNames.push_back(filterName);
			muonTriggerObjectBitMap[filterName] = muonMetadata->hltNames.size() - 1;
			if (verbosity > 0)
				std::cout << "muon trigger object: " << (muonMetadata->hltNames.size() - 1) << " = " << filterName << "\n";
		}

		return KBaseMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>::onLumi(lumiBlock, setup);
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		edm::InputTag tagMuonIsolationPF = pset.getParameter<edm::InputTag>("srcMuonIsolationPF");

		if (tagMuonIsolationPF.label() != "")
			cEvent->getByLabel(tagMuonIsolationPF, isoDepsPF);

		if (tagHLTrigger.label() != "")
			cEvent->getByLabel(tagHLTrigger, triggerEventHandle);

		pfIsoVetoCone = pset.getParameter<double>("pfIsoVetoCone");
		pfIsoVetoMinPt = pset.getParameter<double>("pfIsoVetoMinPt");

		// Continue normally
		KBaseMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Momentum:
		copyP4(in, out.p4);

		// Tracks
		if (in.track().isNonnull())
			KTrackProducer::fillTrack(*in.track(), out.track);
		if (in.globalTrack().isNonnull())
			KTrackProducer::fillTrack(*in.globalTrack(), out.globalTrack);
		if (in.innerTrack().isNonnull())
			KTrackProducer::fillTrack(*in.innerTrack(), out.innerTrack);
		if (in.outerTrack().isNonnull())
			KTrackProducer::fillTrack(*in.outerTrack(), out.outerTrack);
		if (in.bestTrack())
			KTrackProducer::fillTrack(*in.bestTrack(), out.bestTrack);


		// Charge, ...
		out.charge = in.charge();
		out.numberOfChambers = in.numberOfChambers();
		out.numberOfMatches = in.numberOfMatches();
		out.caloComp = in.caloCompatibility();
		out.segComp = muon::segmentCompatibility(in);

		assert(in.type() <= 255);
		out.type = in.type();

		// muon ID selection, described in AN-2008/098
		// http://cms-service-sdtweb.web.cern.ch/cms-service-sdtweb/doxygen/CMSSW_3_3_6/doc/html/dd/de0/MuonSelectors_8cc-source.html#l00005
		std::bitset<32> tmpBits;
		for (size_t i = 0; i < 16; ++i)
			tmpBits.set(i, muon::isGoodMuon(in, (muon::SelectionType)i));
		out.isGoodMuon = (unsigned int)tmpBits.to_ulong();

		// Isolation
		edm::RefToBase<reco::Muon> muonref(edm::Ref<edm::View<reco::Muon> >(handle, this->nCursor));
		reco::IsoDeposit muonIsoDepositPF = (*isoDepsPF)[muonref];

		reco::isodeposit::Direction dir = reco::isodeposit::Direction(in.eta(), in.phi());
		reco::isodeposit::ConeVeto pf_cone_veto(dir, pfIsoVetoCone);
		reco::isodeposit::ThresholdVeto pf_threshold_veto(pfIsoVetoMinPt);

		std::vector<reco::isodeposit::AbsVeto*> vetosPF;
		vetosPF.push_back(&pf_cone_veto);
		vetosPF.push_back(&pf_threshold_veto);

		out.ecalIso03				= in.isolationR03().emEt;
		out.hcalIso03				= in.isolationR03().hadEt;
		out.trackIso03				= in.isolationR03().sumPt;

		out.pfIso04				= muonIsoDepositPF.depositWithin(0.4, vetosPF);

		out.ecalIso05				= in.isolationR05().emEt;
		out.hcalIso05				= in.isolationR05().hadEt;
		out.trackIso05				= in.isolationR05().sumPt;

		out.eta_propagated = -1000.;
		out.phi_propagated = -1000.;

		// propagated values
		if (in.innerTrack().isNonnull() && !noPropagation)
		{
			TrajectoryStateOnSurface prop = propagatorToMuonSystem.extrapolate(in);
			if (prop.isValid())
			{
				out.eta_propagated = prop.globalPosition().eta();
				out.phi_propagated = prop.globalPosition().phi();
			}
		}

		out.hltMatch = getHLTInfo(out.p4);
	}

private:
	edm::InputTag tagHLTrigger;
	double hltMaxdR, hltMaxdPt_Pt;
	double pfIsoVetoCone, pfIsoVetoMinPt;
	std::vector<std::string> selectedMuonTriggerObjects;
	bool noPropagation;
	PropagateToMuon propagatorToMuonSystem;
	edm::Handle< edm::ValueMap<reco::IsoDeposit> > isoDepsPF;

	edm::Handle< trigger::TriggerEvent > triggerEventHandle;

	KMuonMetadata *muonMetadata;

	std::map<std::string, int> muonTriggerObjectBitMap;

	unsigned long long getHLTInfo(const RMDataLV p4)
	{
		if (!triggerEventHandle.isValid())
			return 0;
		unsigned long long ret = 0;

		const size_t sizeFilters = triggerEventHandle->sizeFilters();

		for (size_t iF = 0; iF < sizeFilters; ++iF)
		{
			const std::string nameFilter(triggerEventHandle->filterTag(iF).label());
			const trigger::Keys & keys = triggerEventHandle->filterKeys(iF);

			if (muonTriggerObjectBitMap.find(nameFilter) == muonTriggerObjectBitMap.end())
				continue;

			for (size_t iK = 0; iK < keys.size(); ++iK)
			{
				trigger::TriggerObject triggerObject(triggerEventHandle->getObjects().at(keys[iK]));
				RMDataLV tmpP4(triggerObject.pt(), triggerObject.eta(), triggerObject.phi(), triggerObject.mass());

				if ((ROOT::Math::VectorUtil::DeltaR(p4, tmpP4) < hltMaxdR) && (std::abs(p4.pt() - tmpP4.pt()) / tmpP4.pt() < hltMaxdPt_Pt))
				{
					ret |= ((unsigned long long)1 << muonTriggerObjectBitMap[nameFilter]);
				}
			}
		}
		return ret;
	}
};

#endif

#ifndef KAPPA_MUONPRODUCER_H
#define KAPPA_MUONPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KTrackProducer.h"
#include <DataFormats/MuonReco/interface/Muon.h>
#include <DataFormats/MuonReco/interface/MuonFwd.h>
#include <DataFormats/MuonReco/src/MuonSelectors.cc>
#include <DataFormats/RecoCandidate/interface/IsoDepositVetos.h>
#include <bitset>
#include "PhysicsTools/IsolationAlgos/interface/IsoDepositVetoFactory.h"
#include <DataFormats/Common/interface/ValueMap.h>

#include "DataFormats/HLTReco/interface/TriggerEvent.h"
#include "Math/GenVector/VectorUtil.h"

struct KMuonProducer_Product
{
	typedef std::vector<KDataMuon> type;
	static const std::string id() { return "std::vector<KDataMuon>"; };
	static const std::string producer() { return "KMuonProducer"; };
};

class KMuonProducer : public KManualMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>
{
public:
	KMuonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>(cfg, _event_tree, _run_tree),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hlTrigger")),
		hltMaxdR(cfg.getParameter<double>("hltMaxdR")),
		hltMaxdPt_Pt(cfg.getParameter<double>("hltMaxdPt_Pt")) {}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		tagMuonIsolation = pset.getParameter<edm::InputTag>("srcMuonIsolation");

		if (tagMuonIsolation.label() != "")
			cEvent->getByLabel(tagMuonIsolation, isoDeps);

		if (tagHLTrigger.label() != "")
			cEvent->getByLabel(tagHLTrigger, triggerEventHandle);

		isoVetoCone = pset.getParameter<double>("isoVetoCone");
		isoVetoMinPt = pset.getParameter<double>("isoVetoMinPt");

		// Continue normally
		KManualMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>::fillProduct(in, out, name, tag, pset);
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

		// Charge, ...
		out.charge = in.charge();
		out.numberOfChambers = in.numberOfChambers();
		out.numberOfMatches = in.numberOfMatches();
		out.caloComp = in.caloCompatibility();
		out.segComp = muon::segmentCompatibility(in);
		if (!in.track())
			out.trackHits = -1;
		else
			out.trackHits = in.track()->recHitsSize();

		out.type = in.type();

		// muon ID selection, described in AN-2008/098
		// http://cms-service-sdtweb.web.cern.ch/cms-service-sdtweb/doxygen/CMSSW_3_3_6/doc/html/dd/de0/MuonSelectors_8cc-source.html#l00005
		std::bitset<32> tmpBits;
		for (size_t i = 0; i < 16; ++i)
			tmpBits.set(i, muon::isGoodMuon(in, (muon::SelectionType)i));
		out.isGoodMuon = (unsigned int)tmpBits.to_ulong();

		// Isolation
		edm::RefToBase<reco::Muon> muonref(edm::Ref<edm::View<reco::Muon> >(handle, this->nCursor));
		reco::IsoDeposit muonIsoDeposit = (*isoDeps)[muonref];
		reco::isodeposit::Direction dir = reco::isodeposit::Direction(in.eta(), in.phi());
		std::vector<reco::isodeposit::AbsVeto*>  vetosTrk;
		vetosTrk.push_back(new reco::isodeposit::ConeVeto(dir, isoVetoCone));
		vetosTrk.push_back(new reco::isodeposit::ThresholdVeto(isoVetoMinPt));

		out.sumPtIso03				= in.isolationR03().sumPt;
		out.ecalIso03					= in.isolationR03().emEt;
		out.hcalIso03					= in.isolationR03().hadEt;
		out.trackIso03				= muonIsoDeposit.sumWithin(0.3, vetosTrk);

		out.sumPtIso05				= in.isolationR05().sumPt;
		out.ecalIso05					= in.isolationR05().emEt;
		out.hcalIso05					= in.isolationR05().hadEt;
		out.trackIso05				= muonIsoDeposit.sumWithin(0.5, vetosTrk);

		// Vertex
		out.vertex = KDataVertex();
		out.vertex.fake = false;
		out.vertex.position = in.vertex();
		out.vertex.chi2 = in.vertexChi2();
		out.vertex.nDOF = in.vertexNdof();
		out.vertex.nTracks = 1;
		out.vertex.covariance = ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> >();

		// Time information
		out.timeNDof =	in.time().nDof;
		out.timeAtIpInOut = in.time().timeAtIpInOut;
		out.timeAtIpInOutErr = in.time().timeAtIpInOutErr;
		out.timeAtIpOutIn = in.time().timeAtIpOutIn;
		out.timeAtIpOutInErr = in.time().timeAtIpOutInErr;
		out.direction = getDirection(out.timeNDof, out.timeAtIpInOutErr, out.timeAtIpOutInErr);

		out.hltMatch = getHLTInfo(out.p4);
	}

	int getDirection(int timeNDof, float timeAtIpInOutErr, float timeAtIpOutInErr)
	{
		if (timeNDof < 2)
			return 0;						// undefined
		if (timeAtIpInOutErr > timeAtIpOutInErr)
			return -1;		// OutsideIn
		return 1;				// InsideOut
	}

private:
	edm::InputTag tagMuonIsolation, tagHLTrigger;
	double hltMaxdR, hltMaxdPt_Pt, isoVetoCone, isoVetoMinPt;
	edm::Handle< edm::ValueMap<reco::IsoDeposit> > isoDeps;

	edm::Handle< trigger::TriggerEvent > triggerEventHandle;

	unsigned long long getHLTInfo(const RMDataLV p4)
	{
		if (!triggerEventHandle.isValid())
			return 0;
		unsigned long long ret = 0;

		// KMetadataProducer<KMetadata_Product>::metaLumi->hltNamesMuons
		const size_t sizeFilters = triggerEventHandle->sizeFilters();

		int idx = 0;
		for (size_t iF = 0; iF < sizeFilters; ++iF)
		{
			const std::string nameFilter(triggerEventHandle->filterTag(iF).label());
			const trigger::Keys & keys = triggerEventHandle->filterKeys(iF);

			if (KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap.find(nameFilter) == KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap.end())
				continue;

			++idx;

			for (size_t iK = 0; iK < keys.size(); ++iK)
			{
				trigger::TriggerObject triggerObject(triggerEventHandle->getObjects().at(keys[iK]));
				RMDataLV tmpP4(triggerObject.pt(), triggerObject.eta(), triggerObject.phi(), triggerObject.mass());

				if ((ROOT::Math::VectorUtil::DeltaR(p4, tmpP4) < hltMaxdR) && (std::abs(p4.pt() - tmpP4.pt()) / tmpP4.pt() < hltMaxdPt_Pt))
				{
					ret |= ((unsigned long long)1 << KMetadataProducer<KMetadata_Product>::muonTriggerObjectBitMap[nameFilter]);
				}
			}
		}
		return ret;
	}
};

#endif

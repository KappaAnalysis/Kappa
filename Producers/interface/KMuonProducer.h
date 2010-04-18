#ifndef KAPPA_MUONPRODUCER_H
#define KAPPA_MUONPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KTrackProducer.h"
#include <DataFormats/MuonReco/interface/Muon.h>
#include <DataFormats/MuonReco/interface/MuonFwd.h>
#include <DataFormats/MuonReco/src/MuonSelectors.cc>
#include <bitset>
#include "PhysicsTools/IsolationAlgos/interface/IsoDepositVetoFactory.h"
#include <DataFormats/Common/interface/ValueMap.h>

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
		KManualMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>(cfg, _event_tree, _run_tree)
		{}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		tagMuonIsolation = pset.getParameter<edm::InputTag>("srcMuonIsolation");

		if (tagMuonIsolation.label() != "")
		  cEvent->getByLabel(tagMuonIsolation,isoDeps);

		isoVetos = pset.getParameter<std::vector<std::string> >("isoVetos");
		isoParams.clear();
		for ( std::vector<std::string>::const_iterator veto = isoVetos.begin(); veto != isoVetos.end(); ++veto )
			isoParams.push_back(IsoDepositVetoFactory::make(veto->data()));

		// Continue normally
		KManualMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>::fillProduct(in, out, name, pset);
	}
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Momentum:
		out.p4.SetCoordinates(in.pt(), in.eta(), in.phi(), 0);

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
		out.caloComp = in.caloCompatibility();
		out.segComp = muon::segmentCompatibility(in);
		if (!in.track())
			out.trackHits = -1;
		else
			out.trackHits = in.track()->recHitsSize();

		out.type = 8*in.isGlobalMuon()+4*in.isStandAloneMuon()+2*in.isCaloMuon()+in.isTrackerMuon();
		out.isTrackerMuon			= in.isTrackerMuon();
		out.isCaloMuon				= in.isCaloMuon();
		out.isStandAloneMuon	= in.isStandAloneMuon();
		out.isGlobalMuon			= in.isGlobalMuon();

 		// muon ID selection, described in AN-2008/098
		// http://cms-service-sdtweb.web.cern.ch/cms-service-sdtweb/doxygen/CMSSW_3_3_6/doc/html/dd/de0/MuonSelectors_8cc-source.html#l00005
		std::bitset<32> tmpBits;
		for (size_t i = 0; i < 16; ++i)
			tmpBits.set(i, muon::isGoodMuon( in, (muon::SelectionType) i ) );
		out.isGoodMuon = (unsigned int)tmpBits.to_ulong();

		// Isolation
		edm::RefToBase<reco::Muon> muonref(edm::Ref<edm::View<reco::Muon> >(handle, this->nCursor));
		reco::IsoDeposit muonIsoDeposit = (*isoDeps)[muonref];

		out.sumPtIso03				= in.isolationR03().sumPt;
		out.ecalIso03					= in.isolationR03().emEt;
		out.hcalIso03					= in.isolationR03().hadEt;
		out.trackIso03					= muonIsoDeposit.depositWithin(0.3, isoParams, false);

		out.sumPtIso05				= in.isolationR05().sumPt;
		out.ecalIso05					= in.isolationR05().emEt;
		out.hcalIso05					= in.isolationR05().hadEt;
		out.trackIso05					= muonIsoDeposit.depositWithin(0.5, isoParams, false);

		//out.sumPtIso06;
		//out.hcalIso06;
		//out.ecalIso06;
		out.trackIso06					= muonIsoDeposit.depositWithin(0.6, isoParams, false);

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

		// TODO: hltMatch (matching with HLT objects)
	}

	int getDirection(int timeNDof, float timeAtIpInOutErr, float timeAtIpOutInErr)
	{
		if (timeNDof<2)
			return 0;						// undefined
		if ( timeAtIpInOutErr > timeAtIpOutInErr )
			return -1;		// OutsideIn
		return 1;				// InsideOut
	}

	private:
		edm::InputTag tagMuonIsolation;
		edm::Handle< edm::ValueMap<reco::IsoDeposit> > isoDeps;
		std::vector<std::string> isoVetos;
		std::vector<reco::isodeposit::AbsVeto *> isoParams;
};

#endif

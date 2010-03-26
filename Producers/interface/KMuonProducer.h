#ifndef KAPPA_MUONPRODUCER_H
#define KAPPA_MUONPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/MuonReco/interface/Muon.h>
//#include <DataFormats/TrackReco/interface/Track.h>
#include <DataFormats/MuonReco/src/MuonSelectors.cc>
#include <bitset>

struct KMuonProducer_Product
{
	typedef std::vector<KDataMuon> type;
	static const std::string id() { return "std::vector<KDataMuon>"; };
	static const std::string producer() { return "KMuonProducer"; };
};

class KMuonProducer : public KBaseMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>
{
public:
	KMuonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Momentum:
		out.p4.SetCoordinates(in.pt(), in.eta(), in.phi(), 0);

		// Tracks
		out.track=getMTATrack(in.track());
		out.globalTrack=getMTATrack(in.globalTrack());
		out.innerTrack=getMTATrack(in.innerTrack());

		// Charge, ...
		out.charge = in.charge();
		out.numberOfChambers = in.numberOfChambers();
		out.caloComp = in.caloCompatibility();
		out.segComp = muon::segmentCompatibility(in);
		if (!in.track())
			out.trackHits				= -1;
		else
			out.trackHits				= in.track()->recHitsSize();

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
		// FIXME: wie komme ich an die muonref ran?
		// edm::RefToBase<reco::Muon> muonref(muons, it-muons->begin());
		//reco::IsoDeposit muonIsoDeposit = (*isoDeps)[muonref];

		out.ecalIso03					= in.isolationR03().emEt;
		out.hcalIso03					= in.isolationR03().hadEt;
		//out.trackIso03=muonIsoDeposit.depositWithin(0.3, isoParams, false);

		out.ecalIso05					= in.isolationR05().emEt;
		out.hcalIso05					= in.isolationR05().hadEt;
		//out.trackIso05=muonIsoDeposit.depositWithin(0.5, isoParams, false);

		//out.hcalIso06;
		//out.ecalIso06;
		//out.trackIso06=muonIsoDeposit.depositWithin(0.6, isoParams, false);

		// Vertex
		if (in.vertex().x()*in.vertex().x()+in.vertex().y()*in.vertex().y()+in.vertex().z()*in.vertex().z() != 0)
		{
			out.vertex.valid = true;

			out.vertex.position		=	in.vertex();
			out.vertex.chi2				=	in.vertexChi2();
			out.vertex.nDOF				=	in.vertexNdof();
			out.vertex.cntTracks	= 1;

			out.vertex.covariance = in.vertexCovariance();
		}
		else
			out.vertex = KDataVertex();

		// Time information
		out.timeNDof =	in.time().nDof;
		out.timeAtIpInOut =	in.time().timeAtIpInOut;
		out.timeAtIpInOutErr =	in.time().timeAtIpInOutErr;
		out.timeAtIpOutIn =	in.time().timeAtIpOutIn;
		out.timeAtIpOutInErr =	in.time().timeAtIpOutInErr;
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

	KDataTrack getMTATrack(reco::TrackRef trk)
	{
		KDataTrack tmpTrk;
		if (trk.isNonnull())
			return tmpTrk;

		tmpTrk.p4.SetCoordinates(trk->pt(), trk->eta(), trk->phi(), 0);
		tmpTrk.charge = trk->charge();
		tmpTrk.chi2 = trk->chi2();
		tmpTrk.nDOF = trk->ndof();

		tmpTrk.errPt = trk->ptError();
		tmpTrk.errEta = trk->etaError();
		tmpTrk.errPhi = trk->phiError();

		tmpTrk.ref = trk->referencePoint();
		tmpTrk.quality=trk->qualityMask();

		return tmpTrk;
	}
};

#endif

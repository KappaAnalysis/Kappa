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


#include <DataFormats/Common/interface/Ref.h>
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "DataFormats/GeometrySurface/interface/Cylinder.h"
#include "DataFormats/GeometrySurface/interface/Plane.h"
#include "TrackingTools/GeomPropagators/interface/Propagator.h"
#include "TrackingTools/Records/interface/TrackingComponentsRecord.h"
#include "TMath.h"

class MuPropagator{
	public:
		MuPropagator();
		~MuPropagator();
		inline double get_phi_endcap(){ return propagated_phi_endcap; };
		inline double get_eta_endcap(){ return propagated_eta_endcap; };
		inline double get_phi_barrel(){ return propagated_phi_barrel; };
		inline double get_eta_barrel(){ return propagated_eta_barrel; };

		void setup(edm::EventSetup const &setup);

		void propagate_track(reco::TrackRef inner_track, KDataMuon * muon);
	private:
		TrajectoryStateOnSurface cylExtrapTrkSam(reco::TrackRef track, double rho);
		TrajectoryStateOnSurface surfExtrapTrkSam(reco::TrackRef track, double z);
		FreeTrajectoryState freeTrajStateMuon(reco::TrackRef track);
		double propagated_phi_barrel;
		double propagated_phi_endcap;
		double propagated_eta_barrel;
		double propagated_eta_endcap;

		// The Magnetic field
		edm::ESHandle<MagneticField> theBField;

		// Extrapolator to cylinder
		edm::ESHandle<Propagator> propagatorAlong;
		edm::ESHandle<Propagator> propagatorOpposite;
};

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

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		muPropagator.setup(setup);
		return KManualMultiLVProducer<edm::View<reco::Muon>, KMuonProducer_Product>::onLumi(lumiBlock, setup);
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

		out.sumPtIso03				= in.isolationR03().sumPt;
		out.ecalIso03				= in.isolationR03().emEt;
		out.hcalIso03				= in.isolationR03().hadEt;
		out.trackIso03				= 0.0f;

		out.pfIso04				= muonIsoDepositPF.depositWithin(0.4, vetosPF);

		out.sumPtIso05				= in.isolationR05().sumPt;
		out.ecalIso05				= in.isolationR05().emEt;
		out.hcalIso05				= in.isolationR05().hadEt;
		out.trackIso05				= 0.0f;

		// Vertex
		out.vertex = KDataVertex();
		out.vertex.fake = false;
		out.vertex.position = in.vertex();
		out.vertex.chi2 = in.vertexChi2();
		out.vertex.nDOF = in.vertexNdof();
		out.vertex.nTracks = 1;
		out.vertex.covariance = ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> >();

		out.eta_propag_barrel = -1000.;
		out.eta_propag_endcap = -1000.;
		out.phi_propag_barrel = -1000.;
		out.phi_propag_endcap = -1000.;

		// propagated values
		if (in.innerTrack().isNonnull())
			muPropagator.propagate_track(in.innerTrack(), &out);

		out.hltMatch = getHLTInfo(out.p4);
	}

private:
	MuPropagator muPropagator;

	edm::InputTag tagHLTrigger;
	double hltMaxdR, hltMaxdPt_Pt;
	double pfIsoVetoCone, pfIsoVetoMinPt;
	edm::Handle< edm::ValueMap<reco::IsoDeposit> > isoDepsPF;

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

// ------------------------------------------------

MuPropagator::MuPropagator()
{
}

MuPropagator::~MuPropagator()
{
}

void MuPropagator::setup(edm::EventSetup const &setup)
{
	// Get the propagators
	setup.get<TrackingComponentsRecord>().get("SmartPropagatorAnyRK", propagatorAlong   );
	setup.get<TrackingComponentsRecord>().get("SmartPropagatorAnyOpposite", propagatorOpposite);

	//Get the Magnetic field from the setup
	setup.get<IdealMagneticFieldRecord>().get(theBField);
}

//// Phi Propagation from inner to outer .....
void MuPropagator::propagate_track(reco::TrackRef inner_track, KDataMuon * muon)
{
	// z planes
	int endcapPlane=0;
	if (inner_track->eta() > 0) endcapPlane =  1;
	if (inner_track->eta() < 0) endcapPlane = -1;

	float zzPlaneME2  = endcapPlane*830;
	float zzPlaneME1  = endcapPlane*695; //ME1/3 615

	double muons_glb_phi_mb2=0;
	double muons_glb_eta_mb2=0;
	double muons_glb_phi_me1=0;
	double muons_glb_eta_me1=0;
	double muons_glb_eta_me2=0;
	double muons_glb_phi_me2=0;
	float pig = TMath::Pi();

	TrajectoryStateOnSurface tsos;
	tsos = cylExtrapTrkSam(inner_track, 500);  // track at MB2 radius - extrapolation
	if (tsos.isValid()) {
		double xx = tsos.globalPosition().x();
		double yy = tsos.globalPosition().y();
		double zz = tsos.globalPosition().z();

		//muons_glb_z_mb2 = zz;

		double rr = sqrt(xx*xx + yy*yy);
		double cosphi = xx/rr;
		if(yy>=0)
			muons_glb_phi_mb2 = acos(cosphi);
		else
			muons_glb_phi_mb2 = 2*pig-acos(cosphi);

		double abspseta = -log( tan( atan(fabs(rr/zz))/2.0 ) );
		if(zz>=0)
			muons_glb_eta_mb2 = abspseta;
		else
			muons_glb_eta_mb2 = -abspseta;
	}

	// track at ME1 surface, +/-6.15 m - extrapolation
	tsos = surfExtrapTrkSam(inner_track, zzPlaneME1);
	if (tsos.isValid()) {
		double xx = tsos.globalPosition().x();
		double yy = tsos.globalPosition().y();
		double zz = tsos.globalPosition().z();

		double rr     = sqrt(xx*xx + yy*yy);
		double cosphi = xx/rr;
		if(yy>=0) muons_glb_phi_me1 = acos(cosphi);
		else      muons_glb_phi_me1 = 2*pig-acos(cosphi);


		double abspseta = -log( tan( atan(fabs(rr/zz))/2.0 ) );
		if(zz>=0) muons_glb_eta_me1 = abspseta;
		else      muons_glb_eta_me1 = -abspseta;
	}

	//
	tsos = surfExtrapTrkSam(inner_track, zzPlaneME2);   // track at ME2+/- plane - extrapolation
	if (tsos.isValid()) {
		double xx = tsos.globalPosition().x();
		double yy = tsos.globalPosition().y();
		double zz = tsos.globalPosition().z();

		double rr = sqrt(xx*xx + yy*yy);

		//muons_glb_r_me2 = rr;

		double cosphi = xx/rr;
		if (yy>=0)
			muons_glb_phi_me2 = acos(cosphi);
		else
			muons_glb_phi_me2 = 2*pig-acos(cosphi);

		double abspseta = -log( tan( atan(fabs(rr/zz))/2.0 ) );
		if (zz>=0) muons_glb_eta_me2 = abspseta;
		else       muons_glb_eta_me2 = -abspseta;
	}

	if(muons_glb_phi_mb2 > pig)
		propagated_phi_barrel = muons_glb_phi_mb2-2*pig;
	else
		propagated_phi_barrel = muons_glb_phi_mb2;

	if(muons_glb_phi_me2 > pig)
		propagated_phi_endcap = muons_glb_phi_me2-2*pig;
	else
		propagated_phi_endcap = muons_glb_phi_me2;

	propagated_eta_barrel = muons_glb_eta_mb2;
	propagated_eta_endcap = muons_glb_eta_me2;

	muon->eta_propag_barrel = propagated_eta_barrel;
	muon->eta_propag_endcap = propagated_eta_endcap;
	muon->phi_propag_barrel = propagated_phi_barrel;
	muon->phi_propag_endcap = propagated_phi_endcap;
}

// to get the track position info at a particular rho
TrajectoryStateOnSurface MuPropagator::cylExtrapTrkSam(reco::TrackRef track, double rho)
{
	Cylinder::PositionType pos(0, 0, 0);
	Cylinder::RotationType rot;
	Cylinder::CylinderPointer myCylinder = Cylinder::build(pos, rot, rho);

	FreeTrajectoryState recoStart = freeTrajStateMuon(track);
	TrajectoryStateOnSurface recoProp;
	recoProp = propagatorAlong->propagate(recoStart, *myCylinder);
	if (!recoProp.isValid()) {
		recoProp = propagatorOpposite->propagate(recoStart, *myCylinder);
	}
	return recoProp;
}

// to get track position at a particular (xy) plane given its z
TrajectoryStateOnSurface MuPropagator::surfExtrapTrkSam(reco::TrackRef track, double z)
{
	Plane::PositionType pos(0, 0, z);
	Plane::RotationType rot;
	Plane::PlanePointer myPlane = Plane::build(pos, rot);

	FreeTrajectoryState recoStart = freeTrajStateMuon(track);
	TrajectoryStateOnSurface recoProp;
	recoProp = propagatorAlong->propagate(recoStart, *myPlane);
	if (!recoProp.isValid()) {
		recoProp = propagatorOpposite->propagate(recoStart, *myPlane);
	}
	return recoProp;
}



FreeTrajectoryState MuPropagator::freeTrajStateMuon(reco::TrackRef track)
{
	GlobalPoint  innerPoint(track->innerPosition().x(), track->innerPosition().y(),  track->innerPosition().z());
	GlobalVector innerVec  (track->innerMomentum().x(), track->innerMomentum().y(),  track->innerMomentum().z());

	FreeTrajectoryState recoStart(innerPoint, innerVec, track->charge(), &*theBField);

	return recoStart;
}

#endif

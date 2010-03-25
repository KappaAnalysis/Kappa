#ifndef KAPPA_TRACKPRODUCER_H
#define KAPPA_TRACKPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/JetReco/interface/CaloJet.h>
#include <DataFormats/METReco/interface/HcalNoiseRBX.h>
#include <DataFormats/TrackReco/interface/Track.h>

struct KTrackProducer_Product
{
	typedef std::vector<KDataTrack> type;
	static const std::string id() { return "std::vector<KDataTrack>"; };
	static const std::string producer() { return "KTrackProducer"; };
};

class KTrackProducer : public KBaseMultiLVProducer<edm::View<reco::Track>, KTrackProducer_Product>
{
public:
	KTrackProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::Track>, KTrackProducer_Product>(cfg, _event_tree, _run_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Momentum:
		out.p4.SetCoordinates(in.pt(), in.eta(), in.phi(), 0);
		out.errPt = in.ptError();
		out.errEta = in.etaError();
		out.errPhi = in.phiError();

		// Reference point:
		reco::Track::Point ref = in.referencePoint();
		out.refRho2 = ref.perp2();
		out.refZ = ref.z();		

		// Charge, ...
		out.charge = in.charge();
		out.chi2 = in.chi2();
		out.nDOF = in.ndof();
		out.quality = in.qualityMask();
	}
};

#endif

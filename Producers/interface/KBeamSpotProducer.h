#ifndef KAPPA_BEAMSPOTPRODUCER_H
#define KAPPA_BEAMSPOTPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/BeamSpot/interface/BeamSpot.h>

struct KBeamSpotProducer_Product
{
	typedef std::vector<KDataBeamSpot> type;
	static const std::string id() { return "vector<KDataBeamSpot>"; };
	static const std::string producer() { return "KBeamSpotProducer"; };
};

class KBeamSpotProducer :
	public KManualMultiProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>,
	public KCommonVectorProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>
{
public:
	KBeamSpotProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>(cfg, _event_tree, _run_tree),
		KCommonVectorProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>(cfg) {}
	virtual ~KBeamSpotProducer() {};
protected:
	virtual void clearProduct(KManualMultiProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>::OutputType &out) { out.clear(); }

	virtual void fillProduct(
		const KManualMultiProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>::InputType &in,
		KManualMultiProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>::OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		KCommonVectorProducer<edm::View<reco::BeamSpot>, KBeamSpotProducer_Product>::fillProduct(in, out, name);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		fillBeamspot(in, out);
	}

	// Static method for filling a beam spot in other producers
	static void fillBeamspot(const SingleInputType &in, SingleOutputType &out)
	{
		out.position = in.position();
		
		out.type = in.type();

		out.betaStar = in.betaStar();
		
		out.beamWidthX = in.BeamWidthX();	
		out.beamWidthY = in.BeamWidthY();	
		out.emittanceX = in.emittanceX();	
		out.emittanceY = in.emittanceY();

		out.dxdz	 = in.dxdz();
		out.dydz	 = in.dydz();
		out.sigmaZ = in.sigmaZ();

		out.covariance = in.covariance();
	}
};

#endif

#ifndef KAPPA_BEAMSPOTPRODUCER_H
#define KAPPA_BEAMSPOTPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/BeamSpot/interface/BeamSpot.h>

struct KBeamSpotProducer_Product
{
	typedef KDataBeamSpot type;
	static const std::string id() { return "KDataBeamSpot"; };
	static const std::string producer() { return "KDataBeamSpotProducer"; };
};

class KBeamSpotProducer : public KRegexMultiProducer<reco::BeamSpot, KBeamSpotProducer_Product>
{
public:
	KBeamSpotProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree)
		: KRegexMultiProducer<reco::BeamSpot, KBeamSpotProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KBeamSpotProducer() {};
protected:
	virtual void clearProduct(OutputType &output) { output.position.SetCoordinates(0,0,0); output.type=-1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
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

	}
};

#endif

#ifndef KAPPA_VERTEXPRODUCER_H
#define KAPPA_VERTEXPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/VertexReco/interface/Vertex.h>

struct KVertexProducer_Product
{
	typedef std::vector<KDataVertex> type;
	static const std::string id() { return "vector<KDataVertex>"; };
	static const std::string producer() { return "KVertexProducer"; };
};

class KVertexProducer : public KBaseMultiVectorProducer<edm::View<reco::Vertex>, KVertexProducer_Product>
{
public:
	KVertexProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiVectorProducer<edm::View<reco::Vertex>, KVertexProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KVertexProducer() {};
protected:
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		out.position = in.position();
		out.fake = in.isFake();
		out.nTracks = in.tracksSize();

		out.chi2 = in.chi2();
		out.nDOF = in.ndof();
		out.covariance = in.covariance();
	}
};

#endif

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

class KVertexProducer :
	public KManualMultiProducer<edm::View<reco::Vertex>, KVertexProducer_Product>,
	public KCommonVectorProducer<edm::View<reco::Vertex>, KVertexProducer_Product>
{
public:
	KVertexProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KManualMultiProducer<edm::View<reco::Vertex>, KVertexProducer_Product>(cfg, _event_tree, _run_tree),
		KCommonVectorProducer<edm::View<reco::Vertex>, KVertexProducer_Product>(cfg) {}
	virtual ~KVertexProducer() {};
protected:
	virtual void clearProduct(KManualMultiProducer<edm::View<reco::Vertex>, KVertexProducer_Product>::OutputType &out) { out.clear(); }

	virtual void fillProduct(
		const KManualMultiProducer<edm::View<reco::Vertex>, KVertexProducer_Product>::InputType &in,
		KManualMultiProducer<edm::View<reco::Vertex>, KVertexProducer_Product>::OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		KCommonVectorProducer<edm::View<reco::Vertex>, KVertexProducer_Product>::fillProduct(in, out, name);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		fillVertex(in, out);
	}

	// Static method for filling a vertex in other producers
	static void fillVertex(const SingleInputType &in, SingleOutputType &out)
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

#ifndef KAPPA_METPRODUCER_H
#define KAPPA_METPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/MET.h>

struct KMETProducer_Product
{
	typedef KDataMET type;
	static const std::string id() { return "KDataMET"; };
	static const std::string producer() { return "KMETProducer"; };
};

class KMETProducer : public KBaseMultiProducer<edm::View<reco::MET>, KMETProducer_Product>
{
public:
	KMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::MET>, KMETProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KMETProducer() {};

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() == 1)
		{
			copyP4(in.at(0), out.p4);
			out.sumEt = in.at(0).sumEt();

			TMatrixD mat = in.at(0).getSignificanceMatrix();
			assert(mat(0,1) == mat(1,0));
			out.significance(0,0) = mat(0,0);
			out.significance(0,1) = mat(0,1);
			assert(out.significance(1,0) == mat(1,0));
			out.significance(1,1) = mat(1,1);
		}
		else
			if (verbosity > 1)
				std::cout << "Found " << in.size() << " MET objects!" << std::endl;
	}
};

#endif

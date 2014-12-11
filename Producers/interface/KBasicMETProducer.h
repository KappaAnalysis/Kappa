/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 */

#ifndef KAPPA_BASICMETPRODUCER_H
#define KAPPA_BASICMETPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/MET.h>

class KBasicMETProducer : public KBaseMultiProducer<edm::View<reco::MET>, KBasicMET>
{
public:
	KBasicMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::MET>, KBasicMET>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "BasicMET"; }

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() == 1)
		{
			copyP4(in.at(0), out.p4);
			out.sumEt = in.at(0).sumEt();

#if CMSSW_MAJOR_VERSION >= 7 && CMSSW_MINOR_VERSION >= 2
			reco::METCovMatrix mat = in.at(0).getSignificanceMatrix();
#else
			TMatrixD mat = in.at(0).getSignificanceMatrix();
#endif
			if (mat(0,1) != mat(1,0))
				std::cout << "KBasicMETProducer::fillProduct: Matrix is not symmetric: " << mat(0,1) << " != " << mat(1,0) << std::endl;
			out.significance(0,0) = mat(0,0);
			out.significance(0,1) = mat(0,1);
			if (out.significance(1,0) != mat(1,0))
				std::cout << "KBasicMETProducer::fillProduct: Significance matrix is not identical to input:"
					<< out.significance(1,0) << " != " << mat(1,0) << std::endl;
			out.significance(1,1) = mat(1,1);
		}
		else if (verbosity > 1)
			std::cout << "KBasicMETProducer::fillProduct: Found " << in.size() << " PFMET objects!" << std::endl;
	}
};

#endif

//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_METPRODUCER_H
#define KAPPA_METPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/PFMET.h>

class KMETProducer : public KBaseMultiProducer<edm::View<reco::PFMET>, KMET>
{
public:
	KMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::PFMET>, KMET>(cfg, _event_tree, _run_tree, getLabel()) {}

	static const std::string getLabel() { return "MET"; }

	template<typename Tin>
	static void fillMET(const Tin &in, OutputType &out)
	{
		copyP4(in, out.p4);
		out.sumEt = in.sumEt();

#if CMSSW_MAJOR_VERSION >= 7 && CMSSW_MINOR_VERSION >= 2
		reco::METCovMatrix mat = in.getSignificanceMatrix();
#else
		TMatrixD mat = in.getSignificanceMatrix();
#endif
		if (mat(0,1) != mat(1,0))
        	std::cout << "KMETProducer::fillMET: Matrix is not symmetric: "
        	          << mat(0,1) << " != " << mat(1,0) << std::endl;
		out.significance(0,0) = mat(0,0);
		out.significance(0,1) = mat(0,1);
		if (out.significance(1,0) != mat(1,0))
			std::cout << "KMETProducer::fillMET: Significance matrix is not identical to input:"
			          << out.significance(1,0) << " != " << mat(1,0) << std::endl;
		out.significance(1,1) = mat(1,1);
	}

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() == 1)
		{
			// fill basic MET properties of reco::MET
			fillMET<reco::PFMET>(in.at(0), out);
			// additional PF properties of reco::PFMET
			out.photonFraction = in.at(0).photonEtFraction();
			out.neutralHadronFraction = in.at(0).neutralHadronEtFraction();
			out.electronFraction = in.at(0).electronEtFraction();
			out.chargedHadronFraction = in.at(0).chargedHadronEtFraction();
			out.muonFraction = in.at(0).muonEtFraction();
			out.hfHadronFraction = in.at(0).HFHadronEtFraction();
			out.hfEMFraction = in.at(0).HFEMEtFraction();
		}
		else if (verbosity > 1)
			std::cout << "KMETProducer::fillProduct: Found " << in.size() << " PFMET objects!" << std::endl;
	}
};

#endif

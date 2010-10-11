#ifndef KAPPA_PFMETPRODUCER_H
#define KAPPA_PFMETPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/PFMET.h>

struct KPFMETProducer_Product
{
	typedef KDataPFMET type;
	static const std::string id() { return "KDataPFMET"; };
	static const std::string producer() { return "KPFMETProducer"; };
};

class KPFMETProducer : public KBaseMultiProducer<edm::View<reco::PFMET>, KPFMETProducer_Product>
{
public:
	KPFMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<edm::View<reco::PFMET>, KPFMETProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KPFMETProducer() {};

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() == 1)
		{
			copyP4(in.at(0), out.p4);
			out.sumEt = in.at(0).sumEt();

			out.chargedEMEtFraction = in.at(0).ChargedEMEtFraction();
			out.chargedHadEtFraction = in.at(0).ChargedHadEtFraction();
			out.muonEtFraction = in.at(0).MuonEtFraction();
			out.neutralEMEtFraction = in.at(0).NeutralEMEtFraction();
			out.neutralHadEtFraction = in.at(0).NeutralHadEtFraction();
			out.type6EtFraction = in.at(0).Type6EtFraction();
			out.type7EtFraction = in.at(0).Type7EtFraction();

			if (verbosity > 3)
				std::cout << tag->encode() << "\t" << out << std::endl;
		}
		else
			if (verbosity > 1)
				std::cout << "Found " << in.size() << " PFMET objects!" << std::endl;
	}
};

#endif

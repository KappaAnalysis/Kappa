#ifndef KAPPA_METPRODUCER_H
#define KAPPA_METPRODUCER_H

#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include "DataFormats/METReco/interface/MET.h"

struct KMETProducer_Product
{
	typedef KDataMET type;
	static const std::string id() { return "KDataMET"; };
	static const std::string producer() { return "KMETProducer"; };
};

class KMETProducer : public KBaseMultiProducer<edm::View<reco::MET>, KMETProducer_Product>
{
public:
	KMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree)
		: KBaseMultiProducer<edm::View<reco::MET>, KMETProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KMETProducer() {};
protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0,0,0,0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &input, OutputType &output, edm::InputTag *tag)
	{
		if (input.size() == 1)
		{
			output.p4.SetCoordinates(input.at(0).pt(), input.at(0).eta(), input.at(0).phi(), input.at(0).mass());
			output.sumEt = input.at(0).sumEt();
			if (verbosity > 3)
				std::cout << tag->encode() << "\t" << output << std::endl;
		}
		else
			if (verbosity > 1)
				std::cout << "Found " << input.size() << " MET objects!" << std::endl;
	}
};

#endif

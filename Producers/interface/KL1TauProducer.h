#ifndef KAPPA_L1TAUPRODUCER_H
#define KAPPA_L1TAUPRODUCER_H

#include "KBaseMultiProducer.h"
#include <DataFormats/L1Trigger/interface/Tau.h>
#include <FWCore/Framework/interface/EDProducer.h>

class KL1TauProducer : public KBaseMultiProducer<l1t::TauBxCollection, KL1Taus>
{
	protected:
		typedef typename KBaseMultiProducer<l1t::TauBxCollection, KL1Taus>::InputType::value_type SingleInputType; //?
		typedef typename KBaseMultiProducer<l1t::TauBxCollection, KL1Taus>::OutputType::value_type SingleOutputType;

	public:
		KL1TauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
				KBaseMultiProducer<l1t::TauBxCollection, KL1Taus>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}
		
		virtual void clearProduct(typename KBaseMultiProducer<l1t::TauBxCollection, KL1Taus>::OutputType &output) { output.clear(); }
		
		virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup) { return true; }
		
		static const std::string getLabel() { return "L1Taus"; }

		virtual void fillProduct(const typename KBaseMultiProducer<l1t::TauBxCollection, KL1Taus>::InputType &input,
				typename KBaseMultiProducer<l1t::TauBxCollection, KL1Taus>::OutputType &output,
				const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
		{
				int n_l1taus = input.size();
				output.reserve(n_l1taus);
				
				if (this->verbosity > 0)
					std::cout << "Number of L1 taus in this event: " << n_l1taus << std::endl;

				for(l1t::TauBxCollection::const_iterator bx0TauIt = input.begin(0); bx0TauIt != input.end(0); bx0TauIt++)
				{
					SingleOutputType out;
					out.p4 = (*bx0TauIt).p4();
					out.hwIso = (*bx0TauIt).hwIso();

					if (this->verbosity > 0)
						std::cout << "\t 4-vector of L1 tau: " << out.p4 << ", hardware iso: (input) " << (*bx0TauIt).hwIso() << " (output) " << out.hwIso << std::endl;

					output.push_back(out);
				}
		}
};
#endif
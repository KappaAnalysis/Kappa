//- Copyright (c) 2014 - All Rights Reserved
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_LHEPRODUCER_H
#define KAPPA_LHEPRODUCER_H

#include <SimDataFormats/GeneratorProducts/interface/LHEEventProduct.h>
#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KLHEProducer : public KBaseMultiProducer<LHEEventProduct, KGenParticles>
{
public:
	KLHEProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector):
		KBaseMultiProducer<LHEEventProduct, KGenParticles>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}
	virtual ~KLHEProducer() {};

	static const std::string getLabel() { return "LHE"; }

protected:
	virtual void clearProduct(OutputType &output) { output.clear(); }

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		for (int i = 0; i < in.hepeup().NUP; i++)
		{
			if (in.hepeup().ISTUP[i] < 0)
				continue;

			KGenParticle p;

			// kinematics
			lhef::HEPEUP::FiveVector fv = in.hepeup().PUP[i];
			p.p4.SetPxPyPzE(fv[0], fv[1], fv[2], fv[3]);

			// particle id and status
			p.pdgId = in.hepeup().IDUP[i];
			p.particleinfo = ((in.hepeup().ISTUP[i] % 128) << KGenParticleStatusPosition);
			if (in.hepeup().ISTUP[i] >= 111)  // Pythia 8 maximum
				p.particleinfo |= (127 << KGenParticleStatusPosition);

			out.push_back(p);
		}
	}
};

#endif


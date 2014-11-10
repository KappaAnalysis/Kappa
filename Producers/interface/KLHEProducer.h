/* Copyright (c) 2014 - All Rights Reserved
 *   Dominik Haitz <dominik.haitz@cern.ch>
 */

#ifndef KAPPA_LHEPRODUCER_H
#define KAPPA_LHEPRODUCER_H

#include <SimDataFormats/GeneratorProducts/interface/LHEEventProduct.h>
#include "KBaseMultiProducer.h"
#include "../../DataFormats/interface/KBasic.h"

class KLHEProducer : public KBaseMultiProducer<LHEEventProduct, KGenParticles>
{
public:
	KLHEProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree):
		KBaseMultiProducer<LHEEventProduct, KGenParticles>(cfg, _event_tree, _run_tree, getLabel()) {}
	virtual ~KLHEProducer() {};

	static const std::string getLabel() { return "LHE"; }

protected:
	virtual void clearProduct(OutputType &output) 
	{output.clear();}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		for (int i = 0; i < in.hepeup().NUP; i++)
		{
			KGenParticle p;

			if (in.hepeup().ISTUP[i] < 0)
				continue;

			//kinematics
			lhef::HEPEUP::FiveVector fv = in.hepeup().PUP[i];
			p.p4.SetPxPyPzE (fv[0], fv[1], fv[2], fv[3]);

			// particle id and status
			unsigned int id = (in.hepeup().IDUP[i] < 0) ? -in.hepeup().IDUP[i] : in.hepeup().IDUP[i];
			p.particleinfo = id | ((in.hepeup().ISTUP[i] % 4) << KParticleStatusPosition);
			if (in.hepeup().IDUP[i] < 0)
				p.particleinfo |= KParticleSignMask;

			if (in.hepeup().IDUP[i] != p.pdgId())
				std::cout << "The pdgId is not skimmed correctly! "
						  << "in=" << in.hepeup().IDUP[i] << ", out=" << p.pdgId()
						  << std::endl << std::flush;
			assert(in.hepeup().IDUP[i] == p.pdgId());

			out.push_back(p);
		}
	}
};

#endif


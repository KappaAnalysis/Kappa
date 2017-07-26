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

class KLHEProducer : public KBaseMultiProducer<LHEEventProduct, KLHEParticles>
{
public:
	KLHEProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector):
		KBaseMultiProducer<LHEEventProduct, KLHEParticles>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}
	virtual ~KLHEProducer() {};

	static const std::string getLabel() { return "LHE"; }

protected:
	virtual void clearProduct(OutputType &output)
	{
		output.particles.clear();
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// https://github.com/cms-cvs-history/SimDataFormats-GeneratorProducts/blob/master/interface/LesHouches.h#L128-L263
		
		for (int indexParticle = 0; indexParticle < in.hepeup().NUP; indexParticle++)
		{
			KLHEParticle particle;
			
			lhef::HEPEUP::FiveVector momentum = in.hepeup().PUP[indexParticle];
			particle.p4.SetPxPyPzE(momentum[0], momentum[1], momentum[2], momentum[3]);
			
			particle.pdgId = in.hepeup().IDUP[indexParticle];
			particle.status = in.hepeup().ISTUP[indexParticle];
			particle.firstLastMotherIDs = in.hepeup().MOTHUP[indexParticle];
			particle.colourLineIndices = in.hepeup().ICOLUP[indexParticle];
			particle.spinInfo = in.hepeup().SPINUP[indexParticle];
			
			out.particles.push_back(particle);
		}
		
		out.subprocessCode = in.hepeup().IDPRUP;
		out.pdfScale = in.hepeup().SCALUP;
		out.alphaEM = in.hepeup().AQEDUP;
		out.alphaQCD = in.hepeup().AQCDUP;
	}
};

#endif


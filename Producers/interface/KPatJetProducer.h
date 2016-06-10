//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Fabio Colombo <fabio.colombo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Hauth <Thomas.Hauth@cern.ch>

#ifndef KAPPA_PATJETPRODUCER_H
#define KAPPA_PATJETPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KGenJetProducer.h"
#include <DataFormats/PatCandidates/interface/Jet.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KPatJetProducer : public KBaseMultiLVProducer<edm::View<pat::Jet>, KJets >
{
public:
	KPatJetProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::Jet>, KJets>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		ids(cfg.getParameter<std::vector<std::string> >("ids"))
	{
		genJet = new KGenJet;
		_event_tree->Bronch("genJet", "KGenJet", &genJet);
		names = new KJetMetadata;
		_run_tree->Bronch("jetMetadata", "KJetMetadata", &names);
		jecSet = "patJetCorrFactors";
	}

	static const std::string getLabel() { return "PatJets"; }

	inline std::string firstLetterUppercase(const std::string input)
	{
		char firstpart = toupper(input[0]);
		return firstpart + input.substr(1, input.size()-1);
	}


	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		for(auto id: ids)
		{
			if(std::find(names->tagNames.begin(), names->tagNames.end(), id) == names->tagNames.end())
			{
				names->tagNames.push_back(id);
			}
		}

		//fill the same discriminators also in binary IDs
		names->idNames = names->tagNames;

		return KBaseMultiLVProducer<edm::View<pat::Jet>, KJets>::onLumi(lumiBlock, setup);
	}

	virtual void onFirstObject(const SingleInputType &in, SingleOutputType &out) override
	{
		if( in.jecSetsAvailable())
		{
			for(auto set: in.availableJECSets())
			{
				if (KBaseProducer::verbosity > 0)
				{
					std::cout << "KPatJetProducer::onFirstObject: listing all available JEC sets below" << std::endl;
					std::cout << "Jet Energy Set : " << set << std::endl;
				}
			}
			if(in.availableJECSets()[0] == jecSet)
			{
				std::vector<std::string> levels;
				for ( auto level : in.availableJECLevels(jecSet))
				{
					levels.push_back(level);
					if (KBaseProducer::verbosity > 0)
						std::cout << "\t\t Level: " << level << std::endl;
				}
				names->jecSet = jecSet;
				names->jecLevels = levels;
			}
		} else
		{
			if (KBaseProducer::verbosity > 0)
				std::cout << "no JEC sets available" << std::endl;
		}
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		copyP4(in, out.p4);

		out.area = in.jetArea();
		out.nConstituents = in.nConstituents();
		out.nCharged = in.chargedMultiplicity();
		out.neutralHadronFraction = in.neutralHadronEnergyFraction();
		out.chargedHadronFraction = in.chargedHadronEnergyFraction();
		out.muonFraction = in.muonEnergyFraction();
		out.photonFraction = in.photonEnergyFraction();
		out.electronFraction = in.electronEnergyFraction();
		out.hfHadronFraction = in.HFHadronEnergyFraction();
		out.hfEMFraction = in.HFEMEnergyFraction();
		out.flavour = in.hadronFlavour();

// energy fraction definitions have changed in CMSSW 7.3.X
// fractions should add up to unity
#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 3) || (CMSSW_MAJOR_VERSION > 7)
		assert(out.neutralHadronFraction >= out.hfHadronFraction);
		assert(std::abs(out.neutralHadronFraction + out.chargedHadronFraction +
			out.muonFraction + out.photonFraction + out.electronFraction +
			out.hfEMFraction - 1.0f) < 0.001f);
#else
		assert(std::abs(out.neutralHadronFraction + out.chargedHadronFraction +
			out.muonFraction + out.photonFraction + out.electronFraction +
			out.hfHadronFraction + out.hfEMFraction - 1.0f) < 0.001f);
#endif
		assert(std::abs(in.neutralEmEnergyFraction() - in.photonEnergyFraction() -
			in.HFEMEnergyFraction()) < 0.001f);
		assert(std::abs(in.chargedEmEnergyFraction() - in.electronEnergyFraction()) < 0.001f);

		// tags
		for(auto id: names->tagNames)
		{
			if(in.hasUserFloat(id))
			{
				out.tags.push_back(in.userFloat(id));
			}
			else
			{
				out.tags.push_back(in.bDiscriminator(id));
			}
		}

		// write same thing as binary discriminator
		int digit = 0;
		out.binaryIds = 0;
		for(auto tag: out.tags)
		{
			if(tag > 0.5)
				out.binaryIds |= (1ull << digit);
			++digit;
		}
		//write out generator information
		//todo: catch if some daughters of genJets are not in genParticles collection
		//in this case, the determination of the decay mode fails and the cmsRun exits with "product not found"
		
		const reco::GenJet* recoGenJet = in.genJet();
		if (recoGenJet == NULL) // catch if null pointer is delivered from pat::Jet::genJet() and use an empty GenJet instead
			recoGenJet = new reco::GenJet;

		//write out JEC factors to re-correct jets on analysis level if wanted
		std::vector<float> levels;
		if (KBaseProducer::verbosity > 3)
			std::cout << "Getting JEC Set " << jecSet << std::endl;
		if (in.jecSetAvailable(jecSet))
		{
			for(size_t indexLevels = 0; indexLevels < names->jecLevels.size(); indexLevels++)
			{
				levels.push_back(static_cast<float>(in.jecFactor(names->jecLevels[indexLevels], "none", jecSet)));
				if (KBaseProducer::verbosity > 3)
					std::cout << "Getting JEC Level " << names->jecLevels[indexLevels] <<  ":" << levels[indexLevels] << std::endl;
			}
			out.corrections = levels;
		}

		KGenJetProducer::fillGenJet(*recoGenJet, *genJet); 
	}
private:
	KGenJet* genJet;
	KJetMetadata *names;
	std::vector<std::string> ids;
	std::string jecSet;

};

#endif

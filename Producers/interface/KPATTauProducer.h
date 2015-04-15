//Todo: fill pf candidates

#ifndef KAPPA_PATTAUPRODUCER_H
#define KAPPA_PATTAUPRODUCER_H

#include "KBaseMultiLVProducer.h"

#include <DataFormats/PatCandidates/interface/Tau.h>


class KPATTauProducer : public KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>
{
protected:

	virtual void fillChargeAndFlavour(const SingleInputType &in, SingleOutputType &out)
	{
		out.leptonInfo = KLeptonFlavour::TAU;
		assert(in.charge() == 1 || in.charge() == -1);
		if (in.charge() > 0)
			out.leptonInfo |= KLeptonChargeMask;
		out.leptonInfo |= KLeptonPFMask;

		if (in.leadPFChargedHadrCand().isNonnull())
		{
			if (in.leadPFChargedHadrCand()->trackRef().isNonnull())
				KTrackProducer::fillTrack(*in.leadPFChargedHadrCand()->trackRef(), out.track);
			else if (in.leadPFChargedHadrCand()->gsfTrackRef().isNonnull())
			{
			KTrackProducer::fillTrack(*in.leadPFChargedHadrCand()->gsfTrackRef(), out.track);
			out.leptonInfo |= KLeptonAlternativeTrackMask;
			}
		}
		//out.emFraction = in.emFraction(); //not available in current miniAOD samples
		out.decayMode = in.decayMode();
	}

	virtual void fillDiscriminators(const SingleInputType &in, SingleOutputType &out)
	{
		const std::vector<std::pair<std::string, float>> tauIDs = in.tauIDs();
		int digit = 0;
		for(auto discriminator: discriminatorMap[names[0]]->binaryDiscriminatorNames)
		{
			if(in.tauID(discriminator) > 0.5 )
				out.binaryDiscriminators |= (1ull << digit);
			digit++;
		}
		for(auto discriminator: discriminatorMap[names[0]]->floatDiscriminatorNames)
		{
			out.floatDiscriminators.push_back(in.tauID(discriminator));
		}
	}

public:
	KPATTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>(cfg, _event_tree, _lumi_tree, getLabel()) {
		const edm::ParameterSet &psBase = this->psBase;
		 names = psBase.getParameterNamesForType<edm::ParameterSet>();

		if(names.size() != 1)
		{
			std::cout << "Currently the PATTau Producer only supports one PSet" << std::endl;
			assert(false);
		}

		for(size_t i = 0; i < names.size(); ++i)
		{
			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>("taus");

			preselectionDiscr[names[i]] = pset.getParameter< std::vector<std::string> >("preselectOnDiscriminators");
			binaryDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrWhitelist");
			binaryDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrBlacklist");
			floatDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrWhitelist");
			floatDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrBlacklist");
		}

	}

	static const std::string getLabel() { return "PATTaus"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		return true;
	}


virtual bool acceptSingle(const SingleInputType &in) override
	{
		// propagate the selection on minPt/maxEta
		bool acceptTau = KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>::acceptSingle(in);

		for(auto discriminator: preselectionDiscr[names[0]])
		{
			if ( !in.isTauIDAvailable(discriminator) )
			{
				std::cout << "Configured Tau preselection discriminator " << discriminator << " is not available. Available discriminators are: " << std::endl;
				for(auto availableDiscriminator : in.tauIDs())
					std::cout << availableDiscriminator.first << std::endl;
			}
			acceptTau = acceptTau && (in.tauID(discriminator) > 0.5);
		}
		return acceptTau;
	}


	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// momentum:
		if(firstEvent)
		{
			onFirstEvent(in, out);
			firstEvent = false;
		}
		copyP4(in, out.p4);
		fillChargeAndFlavour(in, out);
		out.tauKey = createTauHash<pat::Tau>(in);
		fillDiscriminators(in, out);
	}

	virtual void onFirstEvent(const SingleInputType &in, SingleOutputType &out)
	{
		// Write out discriminators
		// Discriminators are saved as floats in the pat::Tau. 
		// The black/whitelisting mechanism is used to decide if a discriminato is used as binary or float.
		// The threshold between these two is 0.5
		out.binaryDiscriminators = 0;
		out.floatDiscriminators = std::vector<float>(0);
		const std::vector<std::pair<std::string, float>> tauIDs = in.tauIDs();
		discriminatorMap[names[0]] = new KTauMetadata();

		for(size_t i = 0; i < names.size(); ++i)
		{
			for(auto tauID : tauIDs)
			{
				if( KBaseProducer::regexMatch(tauID.first, binaryDiscrWhitelist[names[i]], binaryDiscrBlacklist[names[i]])) //regexmatch for binary discriminators
				{
					discriminatorMap[names[i]]->binaryDiscriminatorNames.push_back(tauID.first);
					if (this->verbosity > 0)
						std::cout << "Binary tau discriminator " << ": " << tauID.first << std::endl;
				}

				if( KBaseProducer::regexMatch(tauID.first, floatDiscrWhitelist[names[i]], floatDiscrBlacklist[names[i]])) //regexmatch for float discriminators
				{
					discriminatorMap[names[i]]->floatDiscriminatorNames.push_back(tauID.first);
					if (this->verbosity > 0)
						std::cout << "Float tau discriminator " << ": " << tauID.first << std::endl;
				}
			}
		}
	}
private:
	bool firstEvent;
	std::map<std::string, std::vector<std::string> > preselectionDiscr;
	std::map<std::string, std::vector<std::string> > binaryDiscrWhitelist, binaryDiscrBlacklist, floatDiscrWhitelist, floatDiscrBlacklist;
	std::map<std::string, KTauMetadata *> discriminatorMap;
	std::vector<std::string> names;
};

#endif

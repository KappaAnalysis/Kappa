//Todo: fill pf candidates

#ifndef KAPPA_PATTAUPRODUCER_H
#define KAPPA_PATTAUPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KTauProducer.h"

#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 4) || (CMSSW_MAJOR_VERSION > 7)
#include "KPackedPFCandidateProducer.h"
#endif

#include <DataFormats/PatCandidates/interface/Tau.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"
#include "boost/functional/hash.hpp"

#if ((CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21 && CMSSW_REVISION < 28) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0))
#include "RecoTauTag/RecoTau/interface/PFRecoTauClusterVariables.h"
#endif


class KPatTauProducer : public KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>
{
protected:

	virtual void fillChargeAndFlavour(const SingleInputType &in, SingleOutputType &out)
	{
		out.leptonInfo = KLeptonFlavour::TAU;
		//assert(in.charge() == 1 || in.charge() == -1);
		if (in.charge() > 0)
			out.leptonInfo |= KLeptonChargeMask;
		if(in.isPFTau())
			out.leptonInfo |= KLeptonPFMask;

#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 4) || (CMSSW_MAJOR_VERSION > 7)
		pat::PackedCandidate const* packedLeadTauCand = dynamic_cast<pat::PackedCandidate const*>(in.leadChargedHadrCand().get());
		out.dz = packedLeadTauCand->dz();
		out.dxy = packedLeadTauCand->dxy();
		if (packedLeadTauCand->bestTrack() != nullptr)
		{
			KTrackProducer::fillTrack(*packedLeadTauCand->bestTrack(), out.track);
		}
#else
		if (in.leadPFChargedHadrCand().isNonnull())
		{
			if (in.leadPFChargedHadrCand()->trackRef().isNonnull())
			{
				KTrackProducer::fillTrack(*in.leadPFChargedHadrCand()->trackRef(), out.track);
			}
			else if (in.leadPFChargedHadrCand()->gsfTrackRef().isNonnull())
			{
				KTrackProducer::fillTrack(*in.leadPFChargedHadrCand()->gsfTrackRef(), out.track);
				out.leptonInfo |= KLeptonAlternativeTrackMask;
			}
		}
#endif
		else // at least fill reference point
		{
			out.track.ref.SetXYZ(in.vertex().x(), in.vertex().y(), in.vertex().z());
		}
		if(in.isPFTau())
			out.emFraction = in.emFraction();

		out.decayMode = in.decayMode();
	}

	virtual void fillDiscriminators(const SingleInputType &in, SingleOutputType &out)
	{
		const std::vector<std::pair<std::string, float>> tauIDs = in.tauIDs();
		int digit = 0;
		out.binaryDiscriminators = 0;
		for(auto discriminator: discriminatorMap[names[0]]->binaryDiscriminatorNames)
		{
			if(in.tauID(discriminator) > 0.5 )
				out.binaryDiscriminators |= (1ull << digit);
			++digit;
		}

		out.floatDiscriminators.resize(n_float_dict);
		for(auto discriminator=realTauIdfloatmap[names[0]].begin(); discriminator != realTauIdfloatmap[names[0]].end(); discriminator++)
		{
			out.floatDiscriminators[discriminator->second] = in.tauID(discriminator->first);
		}
#if ((CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21 && CMSSW_REVISION < 28) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0))
		for(auto variable = extraTaufloatmap[names[0]].begin();  variable!= extraTaufloatmap[names[0]].end(); variable++)
		{  
			if (variable->first == EXTRATAUFLOATS::decayDistX ) out.floatDiscriminators[variable->second] = in.flightLength().x();
			else if (variable->first == EXTRATAUFLOATS::decayDistY) out.floatDiscriminators[variable->second] = in.flightLength().y();
			else if (variable->first == EXTRATAUFLOATS::decayDistZ) out.floatDiscriminators[variable->second] = in.flightLength().z();
			else if (variable->first == EXTRATAUFLOATS::decayDistM) out.floatDiscriminators[variable->second] =  std::sqrt(in.flightLength().x()*in.flightLength().x() 
																+ in.flightLength().y()*in.flightLength().y() 
																+ in.flightLength().z()*in.flightLength().z());
			else if (variable->first == EXTRATAUFLOATS::nPhoton ) out.floatDiscriminators[variable->second] = (float)clusterVariables_.tau_n_photons_total(in);
			else if (variable->first == EXTRATAUFLOATS::ptWeightedDetaStrip ) out.floatDiscriminators[variable->second] = clusterVariables_.tau_pt_weighted_deta_strip(in, in.decayMode());
			else if (variable->first == EXTRATAUFLOATS::ptWeightedDphiStrip ) out.floatDiscriminators[variable->second] = clusterVariables_.tau_pt_weighted_dphi_strip(in, in.decayMode());
			else if (variable->first == EXTRATAUFLOATS::ptWeightedDrSignal ) out.floatDiscriminators[variable->second]  = clusterVariables_.tau_pt_weighted_dr_signal(in, in.decayMode());
			else if (variable->first == EXTRATAUFLOATS::ptWeightedDrIsolation) out.floatDiscriminators[variable->second]= clusterVariables_.tau_pt_weighted_dr_iso(in, in.decayMode());
			else if (variable->first == EXTRATAUFLOATS::leadingTrackChi2 )  out.floatDiscriminators[variable->second] = in.leadingTrackNormChi2();
			else if (variable->first == EXTRATAUFLOATS::eRatio )  out.floatDiscriminators[variable->second] = clusterVariables_.tau_Eratio(in);
		}
#endif		
	}
	
	virtual void fillPFCandidates(const SingleInputType &in, SingleOutputType &out)
	{
#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 4) || (CMSSW_MAJOR_VERSION > 7)
		for(size_t i = 0; i < in.signalChargedHadrCands().size(); ++i)
		{
			KPFCandidate outCandidate;
			KPackedPFCandidateProducer::fillPackedPFCandidate(*(in.signalChargedHadrCands()[i].get()), outCandidate);
			out.chargedHadronCandidates.push_back(outCandidate);
		}
		for(size_t i = 0; i < in.signalNeutrHadrCands().size(); ++i)
		{
			KLV tmp;
			copyP4(in.signalNeutrHadrCands()[i].get()->p4(), tmp.p4);
			out.piZeroCandidates.push_back(tmp);
		}
		for(size_t i = 0; i < in.signalGammaCands().size(); ++i)
		{
			KPFCandidate outCandidate;
			KPackedPFCandidateProducer::fillPackedPFCandidate(*(in.signalGammaCands()[i].get()), outCandidate);
			out.gammaCandidates.push_back(outCandidate);
		}
#endif

		std::sort(out.chargedHadronCandidates.begin(), out.chargedHadronCandidates.end(), KLVSorter<KPFCandidate>());
		std::sort(out.piZeroCandidates.begin(), out.piZeroCandidates.end(), KLVSorter<KLV>());
		std::sort(out.gammaCandidates.begin(), out.gammaCandidates.end(), KLVSorter<KPFCandidate>());
	}

public:
	KPatTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		_lumi_tree_pointer(_lumi_tree)
	{
		const edm::ParameterSet &psBase = this->psBase;
		 names = psBase.getParameterNamesForType<edm::ParameterSet>();
		if(names.size() != 1)
		{
			std::cout << "Currently the PatTau Producer only supports one PSet" << std::endl;
			assert(false);
		}

		for(size_t i = 0; i < names.size(); ++i)
		{
			discriminatorMap[names[i]] = new KTauMetadata();
			_lumi_tree_pointer->Bronch(names[i].c_str(), "KTauMetadata", &discriminatorMap[names[i]]);
			
			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);

			preselectionDiscr[names[i]] = pset.getParameter< std::vector<std::string> >("preselectOnDiscriminators");
			binaryDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrWhitelist");
			binaryDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrBlacklist");
			floatDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrWhitelist");
			extrafloatDiscrlist[names[i]] = pset.getUntrackedParameter< std::vector<std::string> >("extrafloatDiscrlist", std::vector<std::string>(0) );
#if ((CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21 && CMSSW_REVISION < 28) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0))
			if (extrafloatDiscrlist[names[i]].size() > 0)
				std::cout << "Warining: extrafloatDiscrlist only available in CMSSW_8_0_21 or new" << std::endl;
#endif
			floatDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrBlacklist");
		}
	}

	static const std::string getLabel() { return "PatTaus"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		return true;
	}


virtual bool acceptSingle(const SingleInputType &in) override
	{
		// propagate the selection on minPt/maxEta
		bool acceptTau = KBaseMultiLVProducer<edm::View<pat::Tau>, KTaus>::acceptSingle(in);

		// reject taus with a charge different from +/- 1
		acceptTau = acceptTau && (in.charge() == 1 || in.charge() == -1);

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
		copyP4(in, out.p4);
		// hash of pointer as Id
		out.internalId = hasher(&in);
		fillChargeAndFlavour(in, out);
		out.tauKey = createTauHash<pat::Tau>(in);
		fillDiscriminators(in, out);
		if(in.isPFTau())
		{
			KTauProducer::fillPFCandidates(in, out);
		}
		else
		{
			KPatTauProducer::fillPFCandidates(in, out);
		}
	}

	virtual void onFirstObject(const SingleInputType &in, SingleOutputType &out) override
	{
		if(this->verbosity > 0)
		{
			if(!in.isPFTau())
				std::cout << "Warning: pat::Tau has not been made from PFTau. emFraction and some PFCandidates will not be filled properly" << std::endl;
		}
		// Write out discriminators
		// Discriminators are saved as floats in the pat::Tau. 
		// The black/whitelisting mechanism is used to decide if a discriminato is used as binary or float.
		// The threshold between these two is 0.5
		out.binaryDiscriminators = 0;
		n_float_dict = 0;
		out.floatDiscriminators = std::vector<float>(0); // Will be resized in each event
		
		const std::vector<std::pair<std::string, float>> tauIDs = in.tauIDs();
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
				        realTauIdfloatmap[names[i]][tauID.first] = discriminatorMap[names[i]]->floatDiscriminatorNames.size();
					discriminatorMap[names[i]]->floatDiscriminatorNames.push_back(tauID.first);		
					if (this->verbosity > 0)
						std::cout << "Float tau discriminator " << ": " << tauID.first << std::endl;
				}
			}
#if ((CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21) && CMSSW_REVISION < 28 || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0))
			for (auto extrafloatDiscr : extrafloatDiscrlist[names[i]]){
				EXTRATAUFLOATS add_value = string_to_extraTaufloats(extrafloatDiscr);
				if (add_value != EXTRATAUFLOATS::UNKNOWN){
					extraTaufloatmap[names[i]][add_value] = discriminatorMap[names[i]]->floatDiscriminatorNames.size();
					discriminatorMap[names[i]]->floatDiscriminatorNames.push_back(extrafloatDiscr);
				}
			}
#endif
			checkMapsize(discriminatorMap[names[i]]->floatDiscriminatorNames, "float Discriminators");
			checkMapsize(discriminatorMap[names[i]]->binaryDiscriminatorNames, "binary Discriminators");
			n_float_dict += discriminatorMap[names[i]]->floatDiscriminatorNames.size();
		}
	}
private:
	void checkMapsize(const std::vector<std::string> &map, const std::string &title)
	{
		if(map.size() > 64)
		{
			std::cout << title << " contains too many Elements(" << map.size() << ", max is 64" << std::endl;
			exit(1);
		}
	}
	std::map<std::string, std::vector<std::string> > preselectionDiscr;
	std::map<std::string, std::vector<std::string> > binaryDiscrWhitelist, binaryDiscrBlacklist, floatDiscrWhitelist, floatDiscrBlacklist, extrafloatDiscrlist;
#if ((CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 21 && CMSSW_REVISION < 28) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0))
	TauIdMVAAuxiliaries clusterVariables_;
	enum class EXTRATAUFLOATS : int
	{
		UNKNOWN = -1, decayDistX = 0, decayDistY = 1, decayDistZ = 2, decayDistM = 3,
		nPhoton = 4, ptWeightedDetaStrip = 5, ptWeightedDphiStrip = 6, ptWeightedDrSignal = 7,
		ptWeightedDrIsolation = 8, leadingTrackChi2 = 9, eRatio = 10
	};
	EXTRATAUFLOATS string_to_extraTaufloats(std::string in_string){
		if      (in_string == "decayDistX") return EXTRATAUFLOATS::decayDistX;
		else if (in_string == "decayDistY") return EXTRATAUFLOATS::decayDistY;
		else if (in_string == "decayDistZ") return EXTRATAUFLOATS::decayDistZ;
		else if (in_string == "decayDistM") return EXTRATAUFLOATS::decayDistM;
		else if (in_string == "nPhoton") return EXTRATAUFLOATS::nPhoton;
		else if (in_string == "ptWeightedDetaStrip") return EXTRATAUFLOATS::ptWeightedDetaStrip;
		else if (in_string == "ptWeightedDphiStrip") return EXTRATAUFLOATS::ptWeightedDphiStrip;
		else if (in_string == "ptWeightedDrSignal") return EXTRATAUFLOATS::ptWeightedDrSignal;
		else if (in_string == "ptWeightedDrIsolation") return EXTRATAUFLOATS::ptWeightedDrIsolation;
		else if (in_string == "leadingTrackChi2") return EXTRATAUFLOATS::leadingTrackChi2;
		else if (in_string == "eRatio") return EXTRATAUFLOATS::eRatio;
		std::cout<<"Warning: "<<in_string <<" is not implemented so far !!!!!"<<std::endl;
		return EXTRATAUFLOATS::UNKNOWN;
	}
	std::map<std::string, std::map< EXTRATAUFLOATS, int > > extraTaufloatmap;
#endif
	std::map<std::string, std::map< std::string, int > > realTauIdfloatmap;
	std::map<std::string, KTauMetadata *> discriminatorMap;
	std::vector<std::string> names;
	boost::hash<const pat::Tau*> hasher;
	int n_float_dict;
	
	TTree* _lumi_tree_pointer;
};

#endif

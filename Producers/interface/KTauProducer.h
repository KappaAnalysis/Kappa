//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Benjamin Treiber <benjamin.treiber@gmail.com>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

// todo: input needed for global mu+tau_h(3prong) event fit:
// - primary vertex refitted without tracks that belong to tau candidate
// - secondary vertex fitted using only 3 tracks from 3-prong tau candidate
// - reconstructed a1 candidate from 3 prongs, including covariance
// - for muon leg: muon helix parameters with covariance

#ifndef KAPPA_TAUPRODUCER_H
#define KAPPA_TAUPRODUCER_H

#include <DataFormats/TauReco/interface/PFTau.h>
#include <DataFormats/TauReco/interface/PFTauDiscriminator.h>

#include "KBasicTauProducer.h"

class KTauProducer : public KBasicTauProducer<reco::PFTau, reco::PFTauDiscriminator, KTaus>
{
public:
	KTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBasicTauProducer<reco::PFTau, reco::PFTauDiscriminator, KTaus>(cfg, _event_tree, _lumi_tree, getLabel()) {}

	static const std::string getLabel() { return "Taus"; }

	static int createRecoPFTauHash(const reco::PFTau tau)
	{
		return ( std::hash<double>()(tau.pt()) ^
		         std::hash<double>()(tau.eta()) ^
		         std::hash<double>()(tau.phi()) ^
		         std::hash<bool>()(tau.charge()) );
	}

protected:
	virtual bool isCorrectType(std::string className)
	{
		return className == "reco::PFTauDiscriminator";
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Fill fields of KBasicTau via base class
		KBasicTauProducer<reco::PFTau, reco::PFTauDiscriminator, KTaus>::fillSingle(in, out);

		// Fill additional fields from KTau
		out.tauKey = createRecoPFTauHash(in);

		for(size_t i = 0; i < in.signalPFChargedHadrCands().size(); i++)
		{
			KPFCandidate tmp;
			KPFCandidateProducer::fillPFCandidate(*in.signalPFChargedHadrCands().at(i), tmp);
			out.chargedHadronCandidates.push_back(tmp);
		}
		std::sort(out.chargedHadronCandidates.begin(), out.chargedHadronCandidates.end(), PFSorter);

		for(size_t i = 0; i < in.signalPiZeroCandidates().size(); i++)
		{
			KLV tmp;
			copyP4(in.signalPiZeroCandidates()[i].p4(), tmp.p4);
			out.piZeroCandidates.push_back(tmp);
		}
		std::sort(out.piZeroCandidates.begin(), out.piZeroCandidates.end(), LVSorter);

		for(size_t i = 0; i < in.signalPFGammaCands().size(); i++)
		{
			KPFCandidate tmp;
			KPFCandidateProducer::fillPFCandidate(*in.signalPFGammaCands().at(i), tmp);
			out.gammaCandidates.push_back(tmp);
		}
		std::sort(out.gammaCandidates.begin(), out.gammaCandidates.end(), PFSorter);
	}
private:
	KLVSorter<KPFCandidate> PFSorter;
	KLVSorter<KLV> LVSorter;
};

#endif

/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

// todo: input needed for global mu+tau_h(3prong) event fit:
// - primary vertex refitted without tracks that belong to tau candidate
// - secondary vertex fitted using only 3 tracks from 3-prong tau candidate
// - reconstructed a1 candidate from 3 prongs, including covariance
// - for muon leg: muon helix parameters with covariance

#ifndef KAPPA_PFTAUPRODUCER_H
#define KAPPA_PFTAUPRODUCER_H

#include "KMetadataProducer.h"
#include "KTauProducer.h"

#include <DataFormats/TauReco/interface/PFTau.h>
#include <DataFormats/TauReco/interface/PFTauDiscriminator.h>

class KPFTauProducer : public KTauProducer<reco::PFTau, reco::PFTauDiscriminator, KDataPFTaus>
{
public:
	KPFTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KTauProducer<reco::PFTau, reco::PFTauDiscriminator, KDataPFTaus>(cfg, _event_tree, _lumi_tree, getLabel()) {}

	static const std::string getLabel() { return "PFTaus"; }

	static int createRecoPFTauHash(const reco::PFTau tau)
	{
		return ( std::hash<double>()(tau.leadPFCand()->px()) ^
		         std::hash<double>()(tau.leadPFCand()->py()) ^
		         std::hash<double>()(tau.leadPFCand()->pz()) ^
		         std::hash<bool>()(tau.leadPFCand()->charge()) );
	}


protected:
	virtual bool isCorrectType(std::string className)
	{
		return className == "reco::PFTauDiscriminator";
	}
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Fill fields of KDataTau via base class
		KTauProducer<reco::PFTau, reco::PFTauDiscriminator, KDataPFTaus>::fillSingle(in, out);

		// Fill additional fields from KDataPFTau
		out.emFraction = in.emFraction();
		out.nSignalChargedHadrCands = in.signalPFChargedHadrCands().size();
		out.nSignalGammaCands = in.signalPFGammaCands().size();
		out.nSignalPiZeroCands = in.signalPiZeroCandidates().size();
		out.nSignalCands = in.signalPFCands().size();
		out.hpsDecayMode = in.decayMode();

		if(in.leadPFCand().isNonnull())
			copyP4(in.leadPFCand()->p4(), out.leadCand);
		if(in.leadPFChargedHadrCand().isNonnull()){
			copyP4(in.leadPFChargedHadrCand()->p4(), out.leadChargedHadrCand);
			if (in.leadPFChargedHadrCand()->trackRef().isNonnull())
				KTrackProducer::fillTrack(*in.leadPFChargedHadrCand()->trackRef(), out.track);
		}
		if(in.leadPFNeutralCand().isNonnull())
			copyP4(in.leadPFNeutralCand()->p4(), out.leadNeutralCand); // leading PFGamma candidate


		for(size_t i = 0; i < in.signalPFChargedHadrCands().size(); i++)
		{
			KPFCandidate tmp;
			KPFCandidateProducer::fillPFCandidate(*in.signalPFChargedHadrCands().at(i), tmp);
			out.signalChargedHadrCands.push_back(tmp);
		}
		std::sort(out.signalChargedHadrCands.begin(), out.signalChargedHadrCands.end(), sorter);

		for(size_t i = 0; i < in.signalPiZeroCandidates().size(); i++)
		{
			KDataLV tmp;
			copyP4(in.signalPiZeroCandidates()[i].p4(), tmp.p4);
			out.signalPiZeroCands.push_back(tmp);
		}
		std::sort(out.signalPiZeroCands.begin(), out.signalPiZeroCands.end(), KDataLVSorter);

		for(size_t i = 0; i < in.signalPFGammaCands().size(); i++)
		{
			KPFCandidate tmp;
			KPFCandidateProducer::fillPFCandidate(*in.signalPFGammaCands().at(i), tmp);
			out.signalGammaCands.push_back(tmp);
		}
		std::sort(out.signalGammaCands.begin(), out.signalGammaCands.end(), sorter);

		out.tauKey = createRecoPFTauHash(in);
		out.nSignalTracks = in.signalTracks().size();
	}
private:
	KLVSorter<KPFCandidate> sorter;
	KLVSorter<KDataLV> KDataLVSorter;
};

#endif

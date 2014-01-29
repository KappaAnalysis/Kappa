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
		out.nSignalNeutrHadrCands = in.signalPFNeutrHadrCands().size();
		out.nSignalPiZeroCands = in.signalPiZeroCandidates().size();
		out.nSignalCands = in.signalPFCands().size();
		out.hpsDecayMode = in.decayMode();

		if(in.leadPFCand().isNonnull())
		{
			// position of point of closest approach to beamspot
			out.vertexPoca.fake = false;
			out.vertexPoca.position = in.leadPFCand()->vertex();
			out.vertexPoca.chi2 = -1; // POCA is no fitted vertex -> no chi2, nDOF, cov. available
			out.vertexPoca.nDOF = -1;
			out.vertexPoca.nTracks = 1;
			out.vertexPoca.covariance = ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3> >(); //in.leadPFCand()->vertexCovariance());

			copyP4(in.leadPFCand()->p4(), out.leadTrack);
		}
		else
		{
			out.vertexPoca.fake = true;
		}

		if(in.leadPFChargedHadrCand().isNonnull())
			copyP4(in.leadPFChargedHadrCand()->p4(), out.leadChargedHadrTrack);
		if(in.leadPFNeutralCand().isNonnull())
			copyP4(in.leadPFNeutralCand()->p4(), out.leadNeutralTrack); // leading PFGamma candidate

		out.nSignalTracks = in.signalTracks().size();
	}
};

#endif

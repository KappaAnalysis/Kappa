/* Copyright (c) 2011 - All Rights Reserved
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_L2MUONPRODUCER_H
#define KAPPA_L2MUONPRODUCER_H

#include "KTrackProducer.h"
#include "KL1MuonProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/L1Trigger/interface/L1MuonParticle.h>
#include <DataFormats/MuonSeed/interface/L2MuonTrajectorySeed.h>
#include <DataFormats/MuonSeed/interface/L3MuonTrajectorySeed.h>
#include <DataFormats/RecoCandidate/interface/RecoChargedCandidate.h> 

#include "DataFormats/RecoCandidate/interface/IsoDeposit.h"
#include "DataFormats/RecoCandidate/interface/IsoDepositFwd.h"

//http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/CMSSW/DQM/HLTEvF/plugins/HLTMuonDQMSource.cc?revision=1.40&view=markup

struct KL2MuonTrajectorySeedProducer_Product
{
	typedef std::vector<KL1Muon> type;
	static const std::string id() { return "std::vector<KL1Muon>"; };
	static const std::string producer() { return "KL2MuonTrajectorySeedProducer"; };
};

struct KL3MuonTrajectorySeedProducer_Product
{
	typedef std::vector<KDataTrack> type;
	static const std::string id() { return "std::vector<KDataTrack>"; };
	static const std::string producer() { return "KL3MuonTrajectorySeedProducer"; };
};

struct KMuonTriggerCandidateProducer_Product
{
	typedef std::vector<KMuonTriggerCandidate> type;
	static const std::string id() { return "std::vector<KMuonTriggerCandidate>"; };
	static const std::string producer() { return "MuonTriggerCandidateProducer"; };
};


class KL2MuonTrajectorySeedProducer : public KBaseMultiProducer<std::vector<L2MuonTrajectorySeed>, KL2MuonTrajectorySeedProducer_Product>
{
public:
	KL2MuonTrajectorySeedProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<std::vector<L2MuonTrajectorySeed>, KL2MuonTrajectorySeedProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KL2MuonTrajectorySeedProducer() {};

protected:
	virtual void clearProduct(OutputType &output) { output.clear(); }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		out.clear();
		for (std::vector<L2MuonTrajectorySeed>::const_iterator it = in.begin(); it != in.end(); ++it)
		{
			const l1extra::L1MuonParticle * l1muon = it->l1Particle().get();
			KL1Muon tmpMuon;
			KL1MuonProducer::fillL1Muon(*l1muon, tmpMuon);
			out.push_back(tmpMuon);
		}
	}
};

class KL3MuonTrajectorySeedProducer : public KBaseMultiProducer<std::vector<L3MuonTrajectorySeed>, KL3MuonTrajectorySeedProducer_Product>
{
public:
	KL3MuonTrajectorySeedProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiProducer<std::vector<L3MuonTrajectorySeed>, KL3MuonTrajectorySeedProducer_Product>(cfg, _event_tree, _run_tree) {}
	virtual ~KL3MuonTrajectorySeedProducer() {};

protected:
	virtual void clearProduct(OutputType &output) { output.clear(); }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		//std::vector<int> particles = pset.getParameter<std::vector<int> >("selectedParticles");
		out.clear();
		for (std::vector<L3MuonTrajectorySeed>::const_iterator it = in.begin(); it != in.end(); ++it)
		{
			const reco::Track * l2track = it->l2Track().get();
			KDataTrack tmpTrack;
			KTrackProducer::fillTrack(*l2track, tmpTrack);
			out.push_back(tmpTrack);
		}
	}
};


class KMuonTriggerCandidateProducer : public KBaseMultiLVProducer<edm::View<reco::RecoChargedCandidate>, KMuonTriggerCandidateProducer_Product>
{
public:
	KMuonTriggerCandidateProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree) :
		KBaseMultiLVProducer<edm::View<reco::RecoChargedCandidate>, KMuonTriggerCandidateProducer_Product>(cfg, _event_tree, _run_tree)
		{}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		isoDeltaR = pset.getParameter<double>("isoDeltaR");
		// Retrieve additional input products
		edm::InputTag tagIsolation = pset.getParameter<edm::InputTag>("srcIsolation");

		if (tagIsolation.label() != "")
		{
			cEvent->getByLabel(tagIsolation, isoDeps);
			cEvent->getByLabel(tagIsolation, isoDepDecisions);
		}
		// Continue normally
		KBaseMultiLVProducer<edm::View<reco::RecoChargedCandidate>, KMuonTriggerCandidateProducer_Product>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		KTrackProducer::fillTrack(*(in.track()), out);

		if (isoDeps.isValid())
		{
			// Isolation
			edm::Ref< std::vector<reco::Track> > tk = in.track();
			reco::IsoDepositMap::value_type calDeposit= (*isoDeps)[tk];

			out.isoQuantity = calDeposit.depositWithin(isoDeltaR);
			out.isoDecision = (*isoDepDecisions)[tk];					// decision
		}
	}

private:
	edm::Handle< edm::ValueMap<reco::IsoDeposit> > isoDeps;
	edm::Handle< edm::ValueMap<bool> > isoDepDecisions;
	double isoDeltaR;
};

#endif

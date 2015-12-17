//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Benjamin Treiber <benjamin.treiber@gmail.com>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_EXTENDEDTAUPRODUCER_H
#define KAPPA_EXTENDEDTAUPRODUCER_H

#include "KBasicTauProducer.h"
#include "KTauProducer.h"
#include <FWCore/Framework/interface/EDProducer.h>

class KExtendedTauProducer : public KBasicTauProducer<reco::PFTau, reco::PFTauDiscriminator, KExtendedTaus>
{
public:
	KExtendedTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBasicTauProducer<reco::PFTau, reco::PFTauDiscriminator, KExtendedTaus>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)) {}

	static const std::string getLabel() { return "ExtendedTaus"; }

protected:
	virtual bool isCorrectType(std::string className)
	{
		return className == "reco::PFTauDiscriminator";
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		edm::InputTag barrelSuperClustersSource = pset.getParameter<edm::InputTag>("barrelSuperClustersSource");
		cEvent->getByLabel(barrelSuperClustersSource, pBarrelSuperClusters);
		
		edm::InputTag endcapSuperClustersSource = pset.getParameter<edm::InputTag>("endcapSuperClustersSource");
		cEvent->getByLabel(endcapSuperClustersSource, pEndcapSuperClusters);
		
		// Continue with base product: KBasicTaus
		KBasicTauProducer<reco::PFTau, reco::PFTauDiscriminator, KExtendedTaus>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Fill fields of KBasicTau via base class
		KBasicTauProducer<reco::PFTau, reco::PFTauDiscriminator, KExtendedTaus>::fillSingle(in, out);
		// Fill fields of KTau
		KTauProducer::fillTau(in, out);

		// Fill additional fields of KExtendedTau
		const reco::SuperClusterCollection & barrelSuperClusters = *pBarrelSuperClusters;
		for (size_t i = 0; i < barrelSuperClusters.size(); i++)
		{
			KLV tmp, tmpTau;
			float energy = barrelSuperClusters[i].energy();
			float theta  = 2 * atan(exp(-1. * barrelSuperClusters[i].eta()));
			tmp.p4.SetCoordinates(energy * sin(theta), barrelSuperClusters[i].eta(), barrelSuperClusters[i].phi(), 0.);
			tmpTau.p4.SetCoordinates(in.pt(), in.eta(), in.phi(), 0.);
			
			if (ROOT::Math::VectorUtil::DeltaR(tmp.p4, tmpTau.p4) < 0.1)
				out.superClusterBarrelCandidates.push_back(tmp);
		}
		std::sort(out.superClusterBarrelCandidates.begin(), out.superClusterBarrelCandidates.end(), LVSorter);

		const reco::SuperClusterCollection & endcapSuperClusters = *pEndcapSuperClusters;
		for (size_t i = 0; i < endcapSuperClusters.size(); i++)
		{
			KLV tmp, tmpTau;
			float energy = endcapSuperClusters[i].energy();
			float theta  = 2 * atan(exp(-1. * endcapSuperClusters[i].eta()));
			tmp.p4.SetCoordinates(energy * sin(theta), endcapSuperClusters[i].eta(), endcapSuperClusters[i].phi(), 0.);
			tmpTau.p4.SetCoordinates(in.pt(), in.eta(), in.phi(), 0.);
			
			if (ROOT::Math::VectorUtil::DeltaR(tmp.p4, tmpTau.p4) < 0.1)
				out.superClusterEndcapCandidates.push_back(tmp);
		}
		std::sort(out.superClusterEndcapCandidates.begin(), out.superClusterEndcapCandidates.end(), LVSorter);
	}
private:
	edm::Handle<reco::SuperClusterCollection> pBarrelSuperClusters;
	edm::Handle<reco::SuperClusterCollection> pEndcapSuperClusters;
	KLVSorter<KLV> LVSorter;
};

#endif

/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_CALOTAUPRODUCER_H
#define KAPPA_CALOTAUPRODUCER_H

#include "KMetadataProducer.h"
#include "KTauProducer.h"

#include <DataFormats/TauReco/interface/CaloTau.h>
#include <DataFormats/TauReco/interface/CaloTauDiscriminator.h>

class KCaloTauProducer : public KTauProducer<reco::CaloTau, reco::CaloTauDiscriminator, KDataCaloTaus>
{
public:
	KCaloTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KTauProducer<reco::CaloTau, reco::CaloTauDiscriminator, KDataCaloTaus>(cfg, _event_tree, _lumi_tree, getLabel()) {}

	static const std::string getLabel() { return "CaloTaus"; }

protected:
	virtual bool isCorrectType(std::string className)
	{
		return className == "reco::CaloTauDiscriminator";
	}
};

#endif

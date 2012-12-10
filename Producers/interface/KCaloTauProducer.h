#ifndef KAPPA_CALOTAUPRODUCER_H
#define KAPPA_CALOTAUPRODUCER_H

#include "KMetadataProducer.h"
#include "KTauProducer.h"

#include <DataFormats/TauReco/interface/CaloTau.h>
#include <DataFormats/TauReco/interface/CaloTauDiscriminator.h>

struct KCaloTauProducer_Product
{
	typedef std::vector<KDataCaloTau> type;
	static const std::string id() { return "std::vector<KDataCaloTau>"; };
	static const std::string producer() { return "KDataCaloTauProducer"; };
};

class KCaloTauProducer : public KTauProducer<reco::CaloTau, reco::CaloTauDiscriminator, KCaloTauProducer_Product>
{
public:
	KCaloTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KTauProducer<reco::CaloTau, reco::CaloTauDiscriminator, KCaloTauProducer_Product>(cfg, _event_tree, _lumi_tree)
	{
	}
protected:
	virtual bool isCorrectType(std::string className)
	{
	 return className == "reco::CaloTauDiscriminator";
	}
};

#endif

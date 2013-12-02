/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_ELECTRONPRODUCER_H
#define KAPPA_ELECTRONPRODUCER_H

#include "KBaseMultiLVProducer.h"

#include <bitset>
#include <TMath.h>

struct KElectronProducer_Product
{
	typedef std::vector<KDataElectron> type;
	static const std::string id() { return "std::vector<KDataElectron>"; };
	static const std::string producer() { return "KElectronProducer"; };
};

class KElectronProducer : public KBaseMultiLVProducer<edm::View<reco::GsfElectron>, KElectronProducer_Product>
{
public:
	KElectronProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree) :
		KBaseMultiLVProducer<edm::View<reco::GsfElectron>, KElectronProducer_Product>(cfg, _event_tree, _lumi_tree) {}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		// Momentum:
		copyP4(in, out.p4);

		// Charge, ...
		out.charge = in.charge();
	}

};

#endif

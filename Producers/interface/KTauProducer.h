#ifndef KAPPA_TAUPRODUCER_H
#define KAPPA_TAUPRODUCER_H

#include "KBaseMultiLVProducer.h"

template<typename TTau, typename TTauDiscriminator, typename TTauRef, typename TMeta, typename TProduct>
// Note: We need to use std::vector here, not edm::View, because otherwise
// we cannot use reco::CaloTauDiscriminator or reco::PFTauDescriminator,
// respectively, since they have std::vector somewhere hardcoded in their
// inheritance hierarchy. If we changed that to edm::View then
// cEvent->getManyByType does not find any discriminators anymore.
class KTauProducer : public KManualMultiLVProducer<std::vector<TTau>, TProduct>
{
public:
	KTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, typename TMeta::TauDiscriminatorMap& discr_map) :
		KManualMultiLVProducer<std::vector<TTau>, TProduct>(cfg, _event_tree, _run_tree),
		discriminator_map_(discr_map)
	{
	}

	virtual void fillProduct(
		const typename KManualMultiLVProducer<std::vector<TTau>, TProduct>::InputType &in,
		typename KManualMultiLVProducer<std::vector<TTau>, TProduct>::OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Get tau discriminators from event
		this->cEvent->getManyByType(discriminators_);

		// Get tau discriminators to use for this event
		discriminators_use_ = pset.getParameter<std::vector<std::string> >("discr");

		// Continue normally
		KManualMultiLVProducer<std::vector<TTau>, TProduct>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(
		const typename KManualMultiLVProducer<std::vector<TTau>, TProduct>::SingleInputType &in,
		typename KManualMultiLVProducer<std::vector<TTau>, TProduct>::SingleOutputType &out)
	{
		// Momentum:
		copyP4(in, out.p4);

		// Charge:
		out.charge = in.charge();

		// Discriminator flags:
		//edm::Ref<std::vector<TTau> > tauRef(this->handle, this->nCursor);
		TTauRef tauRef(this->handle, this->nCursor);
		out.discr = 0;
		for(typename std::vector<edm::Handle<TauDiscriminator> >::const_iterator iter = discriminators_.begin(); iter != discriminators_.end(); ++iter)
		{
			std::string discr_name = iter->provenance()->moduleLabel();
			typename TMeta::TauDiscriminatorMap::const_iterator name_iter = this->discriminator_map_.find(discr_name);
			if(name_iter != this->discriminator_map_.end())
			{
				// The discriminator does exist in our map so
				// we have an index in the discr bitfield
				// reserved for it. Now check whether we want
				// to use this discriminator for this tau
				// algorithm.
				for(std::vector<std::string>::const_iterator use_iter = discriminators_use_.begin(); use_iter != discriminators_use_.end(); ++use_iter)
				{
					if(this->regexMatch(discr_name, *use_iter))
					{
						// We have a match, so evaluate the discriminator
						if( (**iter)[tauRef] > 0.5)
							out.discr |= (1ull << name_iter->second);
						break;
					}
				}
			}
		}
	}

private:

	//typedef edm::AssociationVector<edm::RefProd<std::vector<TTau> >, std::vector<float> > TauDiscriminator; // Does not work since getManyByType does not find anything using this...
	typedef TTauDiscriminator TauDiscriminator;
	typename TMeta::TauDiscriminatorMap& discriminator_map_; // map from discriminator name to index

	std::vector<edm::Handle<TauDiscriminator> > discriminators_; // discriminators found in event
	std::vector<std::string> discriminators_use_; // discriminators to use (regexes)
};

#endif

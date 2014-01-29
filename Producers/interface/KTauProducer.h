/* Copyright (c) 2010 - All Rights Reserved
 *   Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
 *   Fred Stober <stober@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 */

#ifndef KAPPA_TAUPRODUCER_H
#define KAPPA_TAUPRODUCER_H

#include "KBaseMultiLVProducer.h"

template<typename TTau, typename TTauDiscriminator, typename TProduct>
// Note: We need to use std::vector here, not edm::View, because otherwise
// we cannot use reco::CaloTauDiscriminator or reco::PFTauDescriminator,
// respectively, since they have std::vector somewhere hardcoded in their
// inheritance hierarchy. If we changed that to edm::View then
// cEvent->getManyByType does not find any discriminators anymore.
class KTauProducer : public KBaseMultiLVProducer<std::vector<TTau>, TProduct>
{
public:
	KTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, const std::string &producerName) :
		KBaseMultiLVProducer<std::vector<TTau>, TProduct>(cfg, _event_tree, _lumi_tree, producerName)
	{
		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			if (this->verbosity > 0)
				std::cout << "booking tau discriminator metadata bronch for \"" << names[i] << "\"\n";

			tauDiscriminatorBitMap[names[i]] = std::map<std::string, unsigned int>();
			discrMetadataMap[names[i]] = new KTauDiscriminatorMetadata();
			_lumi_tree->Bronch(names[i].c_str(), "KTauDiscriminatorMetadata", &discrMetadataMap[names[i]]);

			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);

			discrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("discrWhitelist");
			discrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("discrBlacklist");
			tauDiscrProcessName[names[i]] = pset.getParameter< std::string >("tauDiscrProcessName");
		}
	}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			discrMetadataMap[names[i]]->discriminatorNames.clear();
			tauDiscriminatorBitMap[names[i]].clear();

			edm::Service<edm::ConstProductRegistry> reg;
			for (edm::ProductRegistry::ProductList::const_iterator it = reg->productList().begin(); it != reg->productList().end(); ++it)
			{
				edm::BranchDescription desc = it->second;

				const std::string& name = desc.moduleLabel();

				if (isCorrectType(desc.className()))
				{
					if (std::find(discrMetadataMap[names[i]]->discriminatorNames.begin(), discrMetadataMap[names[i]]->discriminatorNames.end(), name) == discrMetadataMap[names[i]]->discriminatorNames.end())
					{
						if (!KBaseProducer::regexMatch(name, discrWhitelist[names[i]], discrBlacklist[names[i]]))
							continue;

						discrMetadataMap[names[i]]->discriminatorNames.push_back(name);

						tauDiscriminatorBitMap[names[i]][name] = discrMetadataMap[names[i]]->discriminatorNames.size() - 1;

						if (this->verbosity > 0)
							std::cout << "Tau discriminator " << ": " << name << " "<< desc.processName() << std::endl;

						if (discrMetadataMap[names[i]]->discriminatorNames.size()>64)
							throw cms::Exception("Too many tau discriminators selected!");
					}
				}

			}

		}
		return true;
	}

	virtual void fillProduct(
		const typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::InputType &in,
		typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Get tau discriminators from event
		this->cEvent->getManyByType(currentTauDiscriminators);

		if (this->verbosity > 1)
			std::cout << "switching to " << name << " in Tau producer\n";

		// Get tau discriminators to use for this event
		currentDiscriminators = discrMetadataMap[name]->discriminatorNames;
		currentDiscrProcessName = tauDiscrProcessName[name];
		currentDiscriminatorMap = tauDiscriminatorBitMap[name];

		// Continue normally
		KBaseMultiLVProducer<std::vector<TTau>, TProduct>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(
		const typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::SingleInputType &in,
		typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::SingleOutputType &out)
	{
		// Momentum:
		copyP4(in, out.p4);

		// Charge:
		out.charge = in.charge();

		// Discriminator flags:
		out.discr = 0;
		edm::Ref<std::vector<TTau> > tauRef(this->handle, this->nCursor);
		for(typename std::vector<edm::Handle<TauDiscriminator> >::const_iterator iter = currentTauDiscriminators.begin(); iter != currentTauDiscriminators.end(); ++iter)
		{
			std::string discr_name = iter->provenance()->moduleLabel();
			std::string process_name = iter->provenance()->processName();
			if (this->verbosity > 1)
						  std::cout << "KTauProducer: moduleLabel: " << discr_name << " \n" << "              processName: " << iter->provenance()->processName() << " \n";

			std::map<std::string, unsigned int>::const_iterator name_iter = currentDiscriminatorMap.find(discr_name);
			if(name_iter != currentDiscriminatorMap.end())
			{
				// The discriminator does exist in our map so
				// we have an index in the discr bitfield
				// reserved for it. Now check whether we want
				// to use this discriminator for this tau
				// algorithm.
				for(std::vector<std::string>::const_iterator use_iter = currentDiscriminators.begin(); use_iter != currentDiscriminators.end(); ++use_iter)
				{
					if(this->regexMatch(discr_name, *use_iter) && this->regexMatch(process_name,currentDiscrProcessName))
					{
					        if (this->verbosity > 5)
						  std::cout << "KTauProducer: access " << discr_name << " with id = " << (**iter).keyProduct().id() << " using tau with id = " << tauRef.id() << " \n";
						// We have a match, so evaluate the discriminator
						if( (**iter)[tauRef] > 0.5)
							out.discr |= (1ull << name_iter->second);
						break;
					}
				}
			}
		}
	}

protected:
	std::map<std::string, std::vector<std::string> > discrWhitelist, discrBlacklist;
	std::map<std::string, KTauDiscriminatorMetadata *> discrMetadataMap;
	std::map<std::string, std::string > tauDiscrProcessName;
	std::map<std::string, std::map<std::string, unsigned int> > tauDiscriminatorBitMap;

	virtual bool isCorrectType(std::string className) = 0;
private:
	typedef TTauDiscriminator TauDiscriminator;

	std::vector<edm::Handle<TauDiscriminator> > currentTauDiscriminators; // discriminators found in event

	std::vector<std::string> currentDiscriminators; // discriminators to use (based on PSet)
	std::string currentDiscrProcessName; // process name to use for accessing discriminators (based on PSet)
	std::map<std::string, unsigned int> currentDiscriminatorMap; // discriminator-to-bit mapping to use (based on PSet)
};
#endif

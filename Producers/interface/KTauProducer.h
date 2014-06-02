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

			binaryTauDiscriminatorBitMap[names[i]] = std::map<std::string, unsigned int>();
			floatTauDiscriminatorBitMap[names[i]] = std::map<std::string, unsigned int>();
			discrMetadataMap[names[i]] = new KTauDiscriminatorMetadata();
			_lumi_tree->Bronch(names[i].c_str(), "KTauDiscriminatorMetadata", &discrMetadataMap[names[i]]);

			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);

			preselectionDiscr[names[i]] = pset.getParameter< std::vector<std::string> >("preselectOnDiscriminators");
			binaryDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrWhitelist");
			binaryDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrBlacklist");
			floatDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrWhitelist");
			floatDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrBlacklist");
			tauDiscrProcessName[names[i]] = pset.getParameter< std::string >("tauDiscrProcessName");
		}
	}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			discrMetadataMap[names[i]]->binaryDiscriminatorNames.clear();
			discrMetadataMap[names[i]]->floatDiscriminatorNames.clear();
			binaryTauDiscriminatorBitMap[names[i]].clear();
			floatTauDiscriminatorBitMap[names[i]].clear();

			edm::Service<edm::ConstProductRegistry> reg;
			for (edm::ProductRegistry::ProductList::const_iterator it = reg->productList().begin(); it != reg->productList().end(); ++it)
			{
				edm::BranchDescription desc = it->second;

				const std::string& module = desc.moduleLabel();
				const std::string& instance = desc.productInstanceName();
				std::string moduleInstance(module + instance);

				if (isCorrectType(desc.className()))
				{
					if (std::find(discrMetadataMap[names[i]]->binaryDiscriminatorNames.begin(), discrMetadataMap[names[i]]->binaryDiscriminatorNames.end(), moduleInstance) == discrMetadataMap[names[i]]->binaryDiscriminatorNames.end() && std::find(discrMetadataMap[names[i]]->floatDiscriminatorNames.begin(), discrMetadataMap[names[i]]->floatDiscriminatorNames.end(), moduleInstance) == discrMetadataMap[names[i]]->floatDiscriminatorNames.end())
					{
						if (KBaseProducer::regexMatch(moduleInstance, binaryDiscrWhitelist[names[i]], binaryDiscrBlacklist[names[i]]))
						{
							discrMetadataMap[names[i]]->binaryDiscriminatorNames.push_back(moduleInstance);

							binaryTauDiscriminatorBitMap[names[i]][moduleInstance] = discrMetadataMap[names[i]]->binaryDiscriminatorNames.size() - 1;

							if (this->verbosity > 0)
								std::cout << "Binary tau discriminator " << ": " << moduleInstance << " "<< desc.processName() << std::endl;

							if (discrMetadataMap[names[i]]->binaryDiscriminatorNames.size()>64)
								throw cms::Exception("Too many binary tau discriminators selected!");
						}
						
						if (KBaseProducer::regexMatch(moduleInstance, floatDiscrWhitelist[names[i]], floatDiscrBlacklist[names[i]]))
						{
							discrMetadataMap[names[i]]->floatDiscriminatorNames.push_back(moduleInstance);

							floatTauDiscriminatorBitMap[names[i]][moduleInstance] = discrMetadataMap[names[i]]->floatDiscriminatorNames.size() - 1;

							if (this->verbosity > 0)
								std::cout << "Float tau discriminator " << ": " << moduleInstance << " "<< desc.processName() << std::endl;
						}
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
		currentPreselDiscr = preselectionDiscr[name];
		currentDiscrProcessName = tauDiscrProcessName[name];
		
		currentBinaryDiscriminators = discrMetadataMap[name]->binaryDiscriminatorNames;
		currentBinaryDiscriminatorMap = binaryTauDiscriminatorBitMap[name];
		
		currentFloatDiscriminators = discrMetadataMap[name]->floatDiscriminatorNames;
		currentFloatDiscriminatorMap = floatTauDiscriminatorBitMap[name];

		// Continue normally
		KBaseMultiLVProducer<std::vector<TTau>, TProduct>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(
		const typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::SingleInputType &in,
		typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::SingleOutputType &out)
	{
		out.flavour = KLepton::MUON;
		
		// Momentum:
		copyP4(in, out.p4);

		// Charge:
		out.charge = in.charge();

		// Discriminators:
		edm::Ref<std::vector<TTau> > tauRef(this->handle, this->nCursor);
		out.binaryDiscriminators = 0;
		out.floatDiscriminators = std::vector<float>(currentFloatDiscriminators.size());
		
		// handle binary discriminators
		for(typename std::vector<edm::Handle<TauDiscriminator> >::const_iterator iter = currentTauDiscriminators.begin(); iter != currentTauDiscriminators.end(); ++iter)
		{
			std::string discr_module = iter->provenance()->moduleLabel();
			std::string discr_instance = iter->provenance()->productInstanceName();
			std::string process_name = iter->provenance()->processName();
			std::string discr_moduleInstance(discr_module + discr_instance);
			
			if (this->verbosity > 1)
						  std::cout << "KTauProducer: moduleLabel: " << discr_module << " \n" << "              processName: " << process_name << " \n";

			std::map<std::string, unsigned int>::const_iterator moduleInstance_iter = currentBinaryDiscriminatorMap.find(discr_moduleInstance);
			if(moduleInstance_iter != currentBinaryDiscriminatorMap.end())
			{
				// The discriminator does exist in our map so
				// we have an index in the discr bitfield
				// reserved for it. Now check whether we want
				// to use this discriminator for this tau
				// algorithm.
				for(std::vector<std::string>::const_iterator use_iter = currentBinaryDiscriminators.begin(); use_iter != currentBinaryDiscriminators.end(); ++use_iter)
				{
					if(this->regexMatch(discr_moduleInstance, *use_iter) && this->regexMatch(process_name,currentDiscrProcessName))
					{
						if (this->verbosity > 5)
							std::cout << "KTauProducer: access " << discr_moduleInstance << " with id = " << (**iter).keyProduct().id() << " using tau with id = " << tauRef.id() << " \n";
						// We have a match, so evaluate the discriminator
						if( (**iter)[tauRef] > 0.5)
							out.binaryDiscriminators |= (1ull << moduleInstance_iter->second);
						break;
					}
				}
			}

			moduleInstance_iter = currentFloatDiscriminatorMap.find(discr_moduleInstance);
			if(moduleInstance_iter != currentFloatDiscriminatorMap.end())
			{
				// The discriminator does exist in our map so
				// we have an index in the discr bitfield
				// reserved for it. Now check whether we want
				// to use this discriminator for this tau
				// algorithm.
				for(std::vector<std::string>::const_iterator use_iter = currentFloatDiscriminators.begin(); use_iter != currentFloatDiscriminators.end(); ++use_iter)
				{
					if(this->regexMatch(discr_moduleInstance, *use_iter) && this->regexMatch(process_name,currentDiscrProcessName))
					{
						if (this->verbosity > 5)
							std::cout << "KTauProducer: access " << discr_moduleInstance << " with id = " << (**iter).keyProduct().id() << " using tau with id = " << tauRef.id() << " \n";
						out.floatDiscriminators[moduleInstance_iter->second] = (**iter)[tauRef];
						break;
					}
				}
			}
		}
	}
	virtual bool acceptSingle(const typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::SingleInputType &in)
	{
		edm::Ref<std::vector<TTau> > tauRef(this->handle, this->nCursor);

		// preselect taus by given set of discriminators
		// do not use regex matching here, as we do not want to apply any preselection by "accident"
		for(typename std::vector<edm::Handle<TauDiscriminator> >::const_iterator iter = currentTauDiscriminators.begin(); iter != currentTauDiscriminators.end(); ++iter)
		{
			if ( !this->regexMatch(iter->provenance()->processName(),currentDiscrProcessName) )
				continue; // this tau discriminator does not belong to this tau

			std::string discr_module = iter->provenance()->moduleLabel();
			std::vector<std::string>::const_iterator module_iter = std::find(currentPreselDiscr.begin(),currentPreselDiscr.end(),discr_module);

			if( module_iter != currentPreselDiscr.end() ){
				if ( (**iter)[tauRef] < 0.5 ){
					if (this->verbosity > 1)
						std::cout << "KTauProducer::acceptSingle : " << *module_iter << " caused that this tau is not saved \n";

					return false;
				}
			}
		}

		return true;
	}

protected:
	std::map<std::string, std::vector<std::string> > preselectionDiscr;
	std::map<std::string, std::vector<std::string> > binaryDiscrWhitelist, binaryDiscrBlacklist, floatDiscrWhitelist, floatDiscrBlacklist;
	std::map<std::string, KTauDiscriminatorMetadata *> discrMetadataMap;
	std::map<std::string, std::string > tauDiscrProcessName;
	std::map<std::string, std::map<std::string, unsigned int> > binaryTauDiscriminatorBitMap;
	std::map<std::string, std::map<std::string, unsigned int> > floatTauDiscriminatorBitMap;

	virtual bool isCorrectType(std::string className) = 0;
private:
	typedef TTauDiscriminator TauDiscriminator;

	std::vector<edm::Handle<TauDiscriminator> > currentTauDiscriminators; // discriminators found in event

	std::vector<std::string> currentPreselDiscr; // discriminators to use for tau preselection (based on PSet)
	
	std::vector<std::string> currentBinaryDiscriminators; // binary discriminators to use (based on PSet)
	std::vector<std::string> currentFloatDiscriminators; // float discriminators to use (based on PSet)
	
	std::string currentDiscrProcessName; // process name to use for accessing discriminators (based on PSet)
	
	std::map<std::string, unsigned int> currentBinaryDiscriminatorMap; // binary discriminator-to-bit mapping to use (based on PSet)
	std::map<std::string, unsigned int> currentFloatDiscriminatorMap; // float discriminator-to-bit mapping to use (based on PSet)
};
#endif

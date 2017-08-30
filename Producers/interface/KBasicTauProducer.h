//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_BASICTAUPRODUCER_H
#define KAPPA_BASICTAUPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "../../DataFormats/interface/KTrack.h"
#include <FWCore/Framework/interface/EDProducer.h>

template<typename TTau, typename TTauDiscriminator, typename TProduct>
// Note: We need to use std::vector here, not edm::View, because otherwise
// we cannot use reco::CaloTauDiscriminator or reco::PFTauDescriminator,
// respectively, since they have std::vector somewhere hardcoded in their
// inheritance hierarchy. If we changed that to edm::View then
// cEvent->getManyByType does not find any discriminators anymore.
class KBasicTauProducer : public KBaseMultiLVProducer<std::vector<TTau>, TProduct>
{
public:
	KBasicTauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, const std::string &producerName, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<std::vector<TTau>, TProduct>(cfg, _event_tree, _lumi_tree, _run_tree, producerName, std::forward<edm::ConsumesCollector>(consumescollector)),
		VertexCollectionSource(cfg.getParameter<edm::InputTag>("vertexcollection"))
	{
		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			if (this->verbosity > 0)
				std::cout << "booking tau discriminator metadata bronch for \"" << names[i] << "\"\n";

			binaryTauDiscriminatorBitMap[names[i]] = std::map<std::string, unsigned int>();
			floatTauDiscriminatorBitMap[names[i]] = std::map<std::string, unsigned int>();
			discriminatorMap[names[i]] = new KTauMetadata();
			_lumi_tree->Bronch(names[i].c_str(), "KTauMetadata", &discriminatorMap[names[i]]);

			const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);

			preselectionDiscr[names[i]] = pset.getParameter< std::vector<std::string> >("preselectOnDiscriminators");
			binaryDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrWhitelist");
			binaryDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("binaryDiscrBlacklist");
			floatDiscrWhitelist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrWhitelist");
			floatDiscrBlacklist[names[i]] = pset.getParameter< std::vector<std::string> >("floatDiscrBlacklist");
			tauDiscrProcessName[names[i]] = pset.getParameter< std::string >("tauDiscrProcessName");
			this->VertexCollectionToken = consumescollector.consumes<reco::VertexCollection>(VertexCollectionSource);
		}
	}

	virtual bool onRun(edm::Run const &run, edm::EventSetup const &setup)
	{
		setup.get<TransientTrackRecord>().get("TransientTrackBuilder", trackBuilder);
		return true;
	}

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		const edm::ParameterSet &psBase = this->psBase;
		std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

		for (size_t i = 0; i < names.size(); ++i)
		{
			discriminatorMap[names[i]]->binaryDiscriminatorNames.clear();
			discriminatorMap[names[i]]->floatDiscriminatorNames.clear();
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
					if (std::find(discriminatorMap[names[i]]->binaryDiscriminatorNames.begin(),
					              discriminatorMap[names[i]]->binaryDiscriminatorNames.end(),
					              moduleInstance) == discriminatorMap[names[i]]->binaryDiscriminatorNames.end() &&
					    std::find(discriminatorMap[names[i]]->floatDiscriminatorNames.begin(),
					              discriminatorMap[names[i]]->floatDiscriminatorNames.end(),
					              moduleInstance) == discriminatorMap[names[i]]->floatDiscriminatorNames.end())
					{
						if (KBaseProducer::regexMatch(moduleInstance, binaryDiscrWhitelist[names[i]], binaryDiscrBlacklist[names[i]]))
						{
							discriminatorMap[names[i]]->binaryDiscriminatorNames.push_back(moduleInstance);

							binaryTauDiscriminatorBitMap[names[i]][moduleInstance] = discriminatorMap[names[i]]->binaryDiscriminatorNames.size() - 1;

							if (this->verbosity > 0)
								std::cout << "Binary tau discriminator " << ": " << moduleInstance << " "<< desc.processName() << std::endl;

							if (discriminatorMap[names[i]]->binaryDiscriminatorNames.size()>64)
								throw cms::Exception("Too many binary tau discriminators selected!");
						}
						
						if (KBaseProducer::regexMatch(moduleInstance, floatDiscrWhitelist[names[i]], floatDiscrBlacklist[names[i]]))
						{
							discriminatorMap[names[i]]->floatDiscriminatorNames.push_back(moduleInstance);

							floatTauDiscriminatorBitMap[names[i]][moduleInstance] = discriminatorMap[names[i]]->floatDiscriminatorNames.size() - 1;

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
		// Get vertices from event
		this->cEvent->getByToken(this->VertexCollectionToken, VertexHandle);

		// Get tau discriminators from event
		this->cEvent->getManyByType(currentTauDiscriminators);

		if (this->verbosity > 1)
			std::cout << "switching to " << name << " in BasicTau producer\n";

		// Get tau discriminators to use for this event
		currentPreselDiscr = preselectionDiscr[name];
		currentDiscrProcessName = tauDiscrProcessName[name];
		
		currentBinaryDiscriminators = discriminatorMap[name]->binaryDiscriminatorNames;
		currentBinaryDiscriminatorMap = binaryTauDiscriminatorBitMap[name];
		
		currentFloatDiscriminators = discriminatorMap[name]->floatDiscriminatorNames;
		currentFloatDiscriminatorMap = floatTauDiscriminatorBitMap[name];

		// Continue normally
		KBaseMultiLVProducer<std::vector<TTau>, TProduct>::fillProduct(in, out, name, tag, pset);
	}


	virtual void fillSingle(
		const typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::SingleInputType &in,
		typename KBaseMultiLVProducer<std::vector<TTau>, TProduct>::SingleOutputType &out)
	{
		// momentum:
		copyP4(in, out.p4);

		// charge and flavour (lepton type)
		out.leptonInfo = KLeptonFlavour::TAU;
		//assert(in.charge() == 1 || in.charge() == -1);
		if (in.charge() > 0)
			out.leptonInfo |= KLeptonChargeMask;
		out.leptonInfo |= KLeptonPFMask;

		//vertex for IP
		std::vector<reco::Vertex> pv;
		if (VertexHandle->size() == 0) throw cms::Exception("VertexHandle in KBasicTauProducer is empty");
		edm::View<reco::Vertex> vertices = *VertexHandle;
		pv.push_back(vertices.at(0));

		if (in.leadPFChargedHadrCand().isNonnull())
		{
			if (in.leadPFChargedHadrCand()->trackRef().isNonnull())
				KTrackProducer::fillTrack(*in.leadPFChargedHadrCand()->trackRef(), out.track, pv, trackBuilder.product());
			else if (in.leadPFChargedHadrCand()->gsfTrackRef().isNonnull())
			{
				KTrackProducer::fillTrack(*in.leadPFChargedHadrCand()->gsfTrackRef(), out.track, pv, trackBuilder.product());
				out.leptonInfo |= KLeptonAlternativeTrackMask;
			}
		}

		out.emFraction = in.emFraction();
		out.decayMode = in.decayMode();

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
						  std::cout << "KBasicTauProducer: moduleLabel: " << discr_module << " \n" << "              processName: " << process_name << " \n";

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
							std::cout << "KBasicTauProducer: access " << discr_moduleInstance << " with id = " << (**iter).keyProduct().id() << " using tau with id = " << tauRef.id() << " \n";
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
							std::cout << "KBasicTauProducer: access " << discr_moduleInstance << " with id = " << (**iter).keyProduct().id() << " using tau with id = " << tauRef.id() << " \n";
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

		// propagate the selection on minPt/maxEta
		bool acceptTau = KBaseMultiLVProducer<std::vector<TTau>, TProduct>::acceptSingle(in);

		// reject taus with a charge different from +/- 1
		acceptTau = acceptTau && (in.charge() == 1 || in.charge() == -1);

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
						std::cout << "KBasicTauProducer::acceptSingle : " << *module_iter << " caused that this tau is not saved \n";

					acceptTau = acceptTau && false;
				}
			}
		}
		// currently used for preselection on hpsPFTauDiscriminationByDecayModeFinding. miniAOD anyway only contains preselected taus, so maybe not necessary. 
		// should be implemented in the same way as other discriminators, can be retrieved by in.tauID 

		return acceptTau;
	}

protected:
	edm::InputTag VertexCollectionSource;
	edm::EDGetTokenT<reco::VertexCollection> VertexCollectionToken;
	std::map<std::string, std::vector<std::string> > preselectionDiscr;
	std::map<std::string, std::vector<std::string> > binaryDiscrWhitelist, binaryDiscrBlacklist, floatDiscrWhitelist, floatDiscrBlacklist;
	std::map<std::string, KTauMetadata *> discriminatorMap;
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

	edm::Handle<edm::View<reco::Vertex> > VertexHandle;
	edm::ESHandle<TransientTrackBuilder> trackBuilder;
};
	template<typename T>
	static int createTauHash(const T tau)
	{
	return ( std::hash<double>()(tau.pt()) ^
	         std::hash<double>()(tau.eta()) ^
	         std::hash<double>()(tau.phi()) ^
	         std::hash<bool>()(tau.charge()) );
	}
#endif

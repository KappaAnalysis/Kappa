//- Copyright (c) 2011 - All Rights Reserved
//-  * Raphael Friese <Raphael.Friese@cern.ch>

#ifndef KAPPA_TRIGGEROBJECTSTANDALONEPRODUCER_H
#define KAPPA_TRIGGEROBJECTSTANDALONEPRODUCER_H

#include "KBaseMultiProducer.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Math/interface/deltaR.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"

#include "DataFormats/L1Trigger/interface/L1JetParticle.h"
#include "DataFormats/L1Trigger/interface/L1JetParticleFwd.h"
#include "DataFormats/L1Trigger/interface/L1ParticleMap.h"
#include "DataFormats/L1Trigger/interface/L1ParticleMapFwd.h"
#include "DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutRecord.h"

#include <boost/algorithm/string/predicate.hpp>
/* Producer mainly written in analogy to
 *
 * https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD#Trigger
 *
 * Prescales are already prepared, although not used at the moment */



class KTriggerObjectStandaloneProducer : public KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KTriggerObjects>
{
public:
	KTriggerObjectStandaloneProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KTriggerObjects>(cfg, _event_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector), true)
	{
		triggerBits_ = cfg.getParameter<edm::InputTag>("bits");
		metFilterBits_ = cfg.getParameter<edm::InputTag>("metfilterbits");
		metFilterBitsList_ = cfg.getParameter<std::vector<std::string>>("metfilterbitslist");
		triggerObjects_ = cfg.getParameter<edm::InputTag>("objects");
		triggerPrescales_ = cfg.getParameter<edm::InputTag>("prescales");
		edm::InputTag l1tauJetSource_test =  cfg.getUntrackedParameter<edm::InputTag>("l1extratauJetSource",edm::InputTag("dummy"));
		save_l1extratau_=false;
		if (l1tauJetSource_test.label()!="dummy"){
		  std::cout<<"save l1extrataujetSource: "<<l1tauJetSource_test.label()<<std::endl;
		  save_l1extratau_=true;
		  l1tauJetSource_ = consumescollector.consumes<l1extra::L1JetParticleCollection>(l1tauJetSource_test);
		}
		
		toMetadata = new KTriggerObjectMetadata;
		_run_tree->Bronch("triggerObjectMetadata", "KTriggerObjectMetadata", &toMetadata);

		consumescollector.consumes<edm::TriggerResults>(triggerBits_);
		consumescollector.consumes<edm::TriggerResults>(metFilterBits_);
		consumescollector.consumes<pat::TriggerObjectStandAloneCollection>(triggerObjects_);
		consumescollector.consumes<pat::PackedTriggerPrescales>(triggerPrescales_);
		for(size_t j = 0; j < metFilterBitsList_.size(); j++) consumescollector.consumes<bool>(edm::InputTag(metFilterBitsList_[j]));
	
		
	}

	static const std::string getLabel() { return "TriggerObjectStandalone"; }


	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		toMetadata->menu = KInfoProducerBase::hltConfig.tableName();
		toMetadata->toFilter.clear();
		fillMetadata();
		return true;
	}

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KTriggerObjects>::onFirstEvent(event, setup);
		edm::Handle<edm::TriggerResults> metFilterBits;
		event.getByLabel(metFilterBits_, metFilterBits);
		// preselect met filters
		metFilterNames_ = event.triggerNames(*metFilterBits);
		for(size_t i = 0; i < metFilterBits->size(); i++)
		{
			std::string metFilterName = metFilterNames_.triggerName(i);
			if(metFilterName.find("Flag") != std::string::npos)
				selectedMetFilters_.push_back(i);
		}
		nMetFilters_ = selectedMetFilters_.size();
		if(nMetFilters_+metFilterBitsList_.size() >=(8* sizeof(int)))
		{
			std::cout << "Tried to read " << nMetFilters_ << " but only able to store " << (sizeof(int)*8) << " bits." << std::endl;
			assert(false);
		}
		for(auto i : selectedMetFilters_)
		{
			toMetadata->metFilterNames.push_back(metFilterNames_.triggerName(i));
		}
		for(auto i : metFilterBitsList_)
		{
			toMetadata->metFilterNames.push_back("Flag_"+i);
		}
		metFilterBitsListHandle_.resize(metFilterBitsList_.size());
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup) override
	{
		edm::Handle<edm::TriggerResults> triggerBits;
		edm::Handle<pat::TriggerObjectStandAloneCollection> triggerObjects;
		edm::Handle<pat::PackedTriggerPrescales> triggerPrescales;
		
		event.getByLabel(triggerBits_, triggerBits);
		event.getByLabel(metFilterBits_, metFilterBitsHandle_);
		event.getByLabel(triggerObjects_, triggerObjects);
		event.getByLabel(triggerPrescales_, triggerPrescales);
		for(size_t i = 0; i < metFilterBitsList_.size(); i++)
		{
			event.getByLabel(edm::InputTag(metFilterBitsList_[i]), metFilterBitsListHandle_[i]);
		}
		
		if (save_l1extratau_) event.getByToken( l1tauJetSource_, l1tauColl_ );
		
		//if (save_l1extratau_) event.getByLabel( tauJetSource_, tauColl_ );

		names_ = event.triggerNames(*triggerBits);

		std::vector<size_t> triggerBitsFired;

		for (unsigned int i = 0, n = triggerBits->size(); i < n; ++i) 
		{
			if(verbosity>0)
				std::cout<< i << " Trigger " << names_.triggerName(i) << ", prescale " << triggerPrescales->getPrescaleForIndex(i) << ": " << (triggerBits->accept(i) ? "PASS" : "fail (or not run)") << std::endl;

			if(triggerBits->accept(i))
				triggerBitsFired.push_back(i);
		}

		// check if any triggerObjects at all should be looped on
		signifTriggerBitFired_ = commonTriggerBits(triggerBitsFired, KInfoProducerBase::hltKappa2FWK);
		return KBaseMultiProducer::onEvent(event, setup);
	}

	bool commonTriggerBits(std::vector<size_t> triggerBitsFired, std::vector<size_t> triggerBitsSelected)
	{
		for(auto triggerBitSelected: triggerBitsSelected)
		{
			for(auto triggerBitFired: triggerBitsFired)
			{
				if(triggerBitSelected == triggerBitFired)
					{
					if(verbosity > 1)
						std::cout << "write out TriggerObject. " << triggerBitSelected << std::endl;
					return true;
				}
			}
		}
	return false;
	}

	std::vector<int> getHLTIndices(std::vector<std::string> pathNamesTriggerObject, std::vector<size_t> selectedPathNameIndices)
	{
		std::vector<int> hltIndices;

		HLTConfigProvider &hltConfig(KInfoProducerBase::hltConfig);
		for(auto pathNameTriggerObject : pathNamesTriggerObject)
		{
			for(auto hltIdx: selectedPathNameIndices)
			{
				if (hltConfig.triggerName(hltIdx) == pathNameTriggerObject)
				{
					hltIndices.push_back(hltIdx);
					const std::vector<std::string>& saveTagsModules = KInfoProducerBase::hltConfig.saveTagsModules(hltIdx);
					
					toMetadata->nFiltersPerHLT.push_back(saveTagsModules.size());

				}
			}
		}
		return hltIndices;
	}

	std::vector<int> getFilterIndices(std::vector<std::string> filterLabels)
	{
		std::vector<int> filterIndices;
		for(unsigned int i = 0; i < toMetadata->toFilter.size(); ++i)
		{
			if(toMetadata->toFilter[i] == "")
				continue;

			for(auto filterLabel: filterLabels)
			{
				if(filterLabel==toMetadata->toFilter[i])
					filterIndices.push_back(i);
			}
		}
		return filterIndices;
	}

	void fillMetadata(){ // this function is ueed to fill the metadata, which should be done only once per lumi (and not every event)

	  /* The Metadata will be saved once per run. It saves the mapping between the filter names and the Index. The index and the corresponding four vectors will be saved on event basis.
	  The toMetadata->toFilter saves all needed filters (as strings) and is organized blockwise, means are range of indices are reserved for a one trigger:
	  e.g. HLT_1:filter_1 , HLT_1:filter_2 ... HLT_2:filter_1 .... HLT_N:filter_N
	  
	  Here all filters will be saved togheter with the Trigger => the individual filters can occur multiple times, but this should fine since for our use cases this overhead is not to large
	  and also only stored per lumi section 

	  */
	  toMetadata->nFiltersPerHLT.clear();
	  toMetadata->toFilter.clear();
	  l1extratau_idxs_.clear();
	  
	   // allocate memory instead of pushing it in the loop
	  toMetadata->nFiltersPerHLT.resize(KInfoProducerBase::hltKappa2FWK.size());  // stores for each trigger the number of filters
	  // Loop over all triggers 
	  for (size_t i = 0; i < KInfoProducerBase::hltKappa2FWK.size(); ++i)
	  {
	      if (i == 0) // First Trigger is just  digitisation_step with no filters
		{
		  toMetadata->nFiltersPerHLT[i]=0; // no fillters for the First trigger
		  continue;
		}
	      // get HLT index
	      size_t hltIdx = KInfoProducerBase::hltKappa2FWK[i];
	      const std::vector<std::string>& saveTagsModules = KInfoProducerBase::hltConfig.saveTagsModules(hltIdx);
	      toMetadata->nFiltersPerHLT[i] = saveTagsModules.size();  // How much filter indicies does this trigger need
	      // get the trigger name
	      
	      // allocate memory 
	      toMetadata->toFilter.resize(toMetadata->getMaxFilterIndex(i));  // increase the vector of filternames for each trigger
	      for (size_t m = 0; m < saveTagsModules.size(); ++m){
		toMetadata->toFilter[toMetadata->getMinFilterIndex(i)+m] = saveTagsModules[m]; // save the filter name toMetadata->getMinFilterIndex(i)+m = is the actual index
	       }
	      
           // Add l1 extra collections here by hand. 
	     if (save_l1extratau_){
	        std::string triggername = KInfoProducerBase::hltConfig.triggerName(hltIdx);
		if (boost::algorithm::contains(triggername, "tau") || boost::algorithm::contains(triggername, "Tau")){
		  l1extratau_idxs_.push_back(toMetadata->getMaxFilterIndex(i)); // This object will be added as addtional filter at the end of the HLT filter colleciton
		  toMetadata->nFiltersPerHLT[i] +=1; // runs from 0 to N theerefore this comes after the push_back( akt_max_filter_idx )
		  toMetadata->toFilter.push_back(std::string("l1extratauccolltection")); // This object will be added as addtional filter at the end of the HLT filter colleciton 
		}
	      }
	      
	      if (verbosity > 0){
		std::cout << "KTriggerObjectStandaloneProducer::fillMetadata  Trigger: " <<  KInfoProducerBase::hltConfig.triggerName(hltIdx)
			  << ": N Filters: "<<(toMetadata->getMaxFilterIndex(i)-toMetadata->getMinFilterIndex(i))<<std::endl;
		if (verbosity > 1){
		    for (size_t m = toMetadata->getMinFilterIndex(i); m < toMetadata->getMaxFilterIndex(i); ++m){
		      std::cout <<"  idx: "<<m<<"\tfilter_name:"<<toMetadata->toFilter[m]<<std::endl;
		    }
		}
	      
	      }
	   }
	}
	  
protected:
	KTriggerObjectMetadata *toMetadata;
	//KTriggerObjects *trgObjects;
	std::map<size_t, std::vector<int>> toFWK2Kappa;
	//int objectIndex;
	int iLoop;

	virtual void fillProduct(const InputType &in, KTriggerObjects &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset) override
	{
		out.metFilterBits = 0;
		for(size_t i = 0; i < nMetFilters_; i++)
		{
			if(metFilterBitsHandle_->accept(selectedMetFilters_[i]))
				out.metFilterBits = ( out.metFilterBits | ( 1 << i ));
		}
		for(size_t i = 0; i < metFilterBitsList_.size(); i++)
		{
			if(*metFilterBitsListHandle_[i])
				out.metFilterBits = ( out.metFilterBits | ( 1 << (i+nMetFilters_) ));
		}


		if(!signifTriggerBitFired_)
			return;

		//objectIndex = 0;
		iLoop = 0;
		toFWK2Kappa.clear();
		out.trgObjects.clear();
		out.toIdxFilter.clear();
		out.toIdxFilter.resize(toMetadata->toFilter.size()); // the idx of this vector corresponds to one common trigger filter ojbect 
		for(auto obj : in)
		{
			//std::vector<std::string> filterLabels  = obj.filterLabels();
			std::vector<int>  akt_filter_indices = getFilterIndices(obj.filterLabels());
			if (akt_filter_indices.empty())
			  continue;
			
			
			KLV triggerObject;
			copyP4(obj.p4(), triggerObject.p4);
			save_triggerObject_for_indices(out,triggerObject, akt_filter_indices);

			//out.trgObjects.push_back(triggerObject);
			
			//for (auto currentIndex : akt_filter_indices){
			   // if (toFWK2Kappa.count(currentIndex) == 0) {
		           //      std::vector<int> toFWK2KappaSize;
		            //     toFWK2KappaSize.push_back(objectIndex);
			//	 toFWK2Kappa.insert(std::make_pair(currentIndex, toFWK2KappaSize));
		         //   }
		          //  else {
		           //   toFWK2Kappa[currentIndex].push_back(objectIndex);
		          //  }
		            //std::cout<<"ccc"<<std::endl;
		          //  out.toIdxFilter[currentIndex] = toFWK2Kappa[currentIndex];
		//	}
			
			//std::cout<<"dddd"<<std::endl;
			//objectIndex++;
			
			
			
			//obj.unpackPathNames(names_);
			//  fillMetadata(obj, out, name);
			//std::cout<<"!!!! "<<filterIndex<<" "<<toFWK2Kappa.size()<<std::endl;

			//auto pathNamesAll = obj.pathNames(false);
	
			iLoop++;
		}
		
		if (save_l1extratau_)
		{
			  for( l1extra::L1JetParticleCollection::const_iterator tauItr = l1tauColl_->begin() ; tauItr != l1tauColl_->end() ;++tauItr )
			  {
			   // std::cout << "  p4 (" << tauItr->px()  << ", " << tauItr->py() << ", " << tauItr->pz()<< ", " << tauItr->energy()<< ") et " << tauItr->et()<< " eta " << tauItr->eta()<< " phi " << tauItr->phi() << std::endl ;
			//  
			// KInfoProducerBase::hltConfig.saveTagsModules(hltIdx)  
			 //size_t currentIndex = toMetadata->getMinFilterIndex(i) + KInfoProducerBase::hltConfig.saveTagsModules(hltIdx).size();
			    KLV triggerObject;
			    copyP4(tauItr->p4(), triggerObject.p4);
			    save_triggerObject_for_indices(out,triggerObject, l1extratau_idxs_);

		       }
		   // std::cout<<"BBBBBBBBBBBBBBBBBBBBBBBBB"<<std::endl;
		}
		if (verbosity > 2)
		  print_saved_objects(out);
	}

	virtual void clearProduct(KTriggerObjects &prod)
	{
		prod.trgObjects.clear();
		prod.toIdxFilter.clear();
	}

private:
	edm::InputTag triggerBits_;
	edm::InputTag metFilterBits_;
	edm::Handle<edm::TriggerResults> metFilterBitsHandle_;
	
	bool save_l1extratau_;
	edm::Handle< l1extra::L1JetParticleCollection > l1tauColl_ ;
	edm::EDGetTokenT< l1extra::L1JetParticleCollection > l1tauJetSource_;
	std::vector<int> l1extratau_idxs_;
	std::vector<std::string> metFilterBitsList_;
	std::vector<edm::Handle<bool>> metFilterBitsListHandle_;
	
	
	
	edm::InputTag triggerObjects_;
	edm::InputTag triggerPrescales_;
	bool signifTriggerBitFired_;
	edm::TriggerNames names_;
	edm::TriggerNames metFilterNames_;
	size_t nMetFilters_;
	std::vector<size_t> selectedMetFilters_;
	void save_triggerObject_for_indices(KTriggerObjects &out, KLV &triggerObject, std::vector<int> &indices){
	  int objectindex = out.trgObjects.size(); // the new object will be stored 
	  out.trgObjects.push_back(triggerObject);
	  for (auto currentIndex : indices){
	     	if (toFWK2Kappa.count(currentIndex) == 0) {
		    std::vector<int> toFWK2KappaSize;
		    toFWK2KappaSize.push_back(objectindex);
		    toFWK2Kappa.insert(std::make_pair(currentIndex, toFWK2KappaSize));
		            }
		else {
		     toFWK2Kappa[currentIndex].push_back(objectindex);
		}
		out.toIdxFilter[currentIndex] = toFWK2Kappa[currentIndex]; 
	   }
	}
	
	void print_saved_objects(KTriggerObjects &out){
	  std::cout<<"-----------------------------------------------"<<std::endl;
	  for (std::map<size_t, std::vector<int>>::iterator it=toFWK2Kappa.begin(); it!=toFWK2Kappa.end(); ++it){
	   // std::cout << it->first <<"\t";
	      std::cout << toMetadata->toFilter[it->first] <<"\t => " << (it->second).size()<<" (";
	      bool erster=true;
	      for (std::vector<int>::iterator subit =(it->second).begin(); subit!= (it->second).end(); ++subit){
		if (!erster) std::cout<<",";
		else erster=false;
		std::cout<<" "<<*subit;
	      }	  
	      std::cout<<")";
	      for (std::vector<int>::iterator subit =(it->second).begin(); subit!= (it->second).end(); ++subit){
		std::cout<<" | "<<out.trgObjects[*subit].p4;
	      }	  
	      std::cout<<std::endl;  
	   }
	  std::cout<<"_______________________________________________"<<std::endl;
	}
		
	
};

#endif

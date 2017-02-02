// -*- C++ -*-
//
// Package:    RecoTauTag/RecoTau
// Class:      PATTauIdUpdater
// 
/**\class PATTauIdUpdater PATTauIdUpdater.cc RecoTauTag/RecoTau/plugins/PATTauIdUpdater.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Stefan Wayand
//         Created:  Mon, 30 Jan 2017 20:39:08 GMT
//
//
#if (CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION == 0 && CMSSW_REVISION >= 25) || (CMSSW_MAJOR_VERSION >= 8 && CMSSW_MINOR_VERSION > 0)



// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/PatCandidates/interface/Tau.h"
#include "DataFormats/PatCandidates/interface/PATTauDiscriminator.h"
//
// class declaration
//

class PATTauIdUpdater : public edm::stream::EDProducer<> {
   public:
      explicit PATTauIdUpdater(const edm::ParameterSet&);
      ~PATTauIdUpdater();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginStream(edm::StreamID) override;
      virtual void produce(edm::Event&, const edm::EventSetup&) override;
      virtual void endStream() override;

      //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
      //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

      // ----------member data ---------------------------
      
      edm::EDGetTokenT<pat::TauCollection> src;
      std::map< std::string, edm::EDGetTokenT<pat::PATTauDiscriminator> > update_PATTauDiscriminators;
      
};

//
PATTauIdUpdater::PATTauIdUpdater(const edm::ParameterSet& iConfig) :
 src(consumes<pat::TauCollection>(iConfig.getParameter<edm::InputTag>("src")))
{ 
  for (auto in_inputTag : iConfig.getParameter< std::vector<edm::InputTag> >("update_PATTauDiscriminators") ){   
    update_PATTauDiscriminators[in_inputTag.label()] = consumes<pat::PATTauDiscriminator>(in_inputTag);
  }
  produces<std::vector<pat::Tau> >();
}


PATTauIdUpdater::~PATTauIdUpdater()
{
 
   // do anything here that needs to be done at destruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
PATTauIdUpdater::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

  std::map<unsigned, std::map<std::string, float> >map_IdPair;
  edm::Handle<pat::TauCollection> taus;
  iEvent.getByToken(src,taus);
  
  //I didin't found a more elegant way, such that one have to loop three times over the tau input collection. 
  
  
  // First save the old ids
  for(unsigned iTau = 0; iTau < taus->size(); iTau++) {
    pat::TauRef inTau(taus,iTau);
    for (auto old_id : inTau->tauIDs()){         
      map_IdPair[iTau][old_id.first] = old_id.second; 
    }
  }
  
   // Second save the new ids or overwrite the some ids values
  for (auto gettoken :  update_PATTauDiscriminators){
    edm::Handle<pat::PATTauDiscriminator> inDiscriminators;
    iEvent.getByToken(gettoken.second, inDiscriminators);
    for(unsigned iTau = 0; iTau < taus->size(); iTau++) {
      pat::TauRef inTau(taus,iTau);
      map_IdPair[iTau][gettoken.first] = (*inDiscriminators)[inTau];
    }
  }
  
  
  // Last step make a copy of the original tau, but take the new ids
  auto outTaus = std::make_unique<std::vector<pat::Tau>>();
  outTaus->reserve(taus->size());
  for(unsigned iTau = 0; iTau < taus->size(); iTau++) {
    pat::TauRef inTau(taus,iTau);
    outTaus->push_back(*(inTau.get()) );
    pat::Tau & outTau = outTaus->back();
    std::vector<std::pair<std::string, float> > ids;
    ids.reserve(map_IdPair[iTau].size());
   
    for (auto new_id : map_IdPair[iTau] ){
      ids.push_back(std::pair<std::string, float>(new_id.first,new_id.second));  
    }
    outTau.setTauIDs(ids);
  }

  iEvent.put(std::move(outTaus));
 
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void
PATTauIdUpdater::beginStream(edm::StreamID)
{
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void
PATTauIdUpdater::endStream() {
}


// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PATTauIdUpdater::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PATTauIdUpdater);
#endif

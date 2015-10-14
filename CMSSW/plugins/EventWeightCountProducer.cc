// -*- C++ -*-
//
// Class:      EventWeightCountProducer
// 
/**\class EventWeightCountProducer EventWeightCountProducer.cc Kappa/Producers/plugins/EventWeightCountProducer.cc

Description: An event counter that fills a histogram with positive and negative weights in the lumi block 

*/

#if (CMSSW_MAJOR_VERSION >= 7)
// system include files
#include <memory>
#include <vector>
#include <algorithm>
#include <iostream>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Common/interface/MergeableCounter.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "TH1F.h"
class EventWeightCountProducer : public edm::one::EDProducer<edm::one::WatchLuminosityBlocks,
                                                       edm::EndLuminosityBlockProducer> {
public:
  explicit EventWeightCountProducer(const edm::ParameterSet&);
  ~EventWeightCountProducer();

private:
  virtual void produce(edm::Event &, const edm::EventSetup&) override;
  virtual void beginLuminosityBlock(const edm::LuminosityBlock &, const edm::EventSetup&) override;
  virtual void endLuminosityBlock(edm::LuminosityBlock const&, const edm::EventSetup&) override;
  virtual void endLuminosityBlockProduce(edm::LuminosityBlock &, const edm::EventSetup&) override;
      
  // ----------member data ---------------------------
  unsigned int nEvents;
  bool isMC;
  bool countNegWeightsOnly;
  edm::EDGetTokenT<GenEventInfoProduct> srcGenEventInfoToken_;
  edm::InputTag srcGenEventInfo_;
};



using namespace edm;
using namespace std;



EventWeightCountProducer::EventWeightCountProducer(const edm::ParameterSet& iConfig){
  produces<edm::MergeableCounter, edm::InLumi>();
  if (iConfig.existsAs<bool>("isMC"))
    isMC = iConfig.getParameter<bool>("isMC");
  else throw cms::Exception("Configuration")<<"Missing parameter input isMC \n";\

  if (iConfig.existsAs<bool>("countNegWeightsOnly"))
    countNegWeightsOnly = iConfig.getParameter<bool>("countNegWeightsOnly");
  else throw cms::Exception("Configuration")<<"Missing parameter countNegWeightsOnly \n";

  if(not isMC and countNegWeightsOnly)
  {
    throw cms::Exception("Configuration")<<"Configuration error: trying to count negative event weights in data \n";
  }


  if (isMC)
  {
	std::cout << "srcGenEventInfo da und es ist mc" << std::endl;
    srcGenEventInfo_ = iConfig.getParameter<edm::InputTag>("srcGenEventInfo");
    srcGenEventInfoToken_ = consumes<GenEventInfoProduct>(srcGenEventInfo_);
  }
  //else throw cms::Exception("Configuration")<<"Missing parameter input srcGenEventInfo \n";
}


EventWeightCountProducer::~EventWeightCountProducer(){}


void EventWeightCountProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup){

  if(not isMC || not countNegWeightsOnly)
  {
        nEvents++;
  }
  else
  {
    edm::Handle<GenEventInfoProduct> GenEventInfoHandle;
    iEvent.getByToken(srcGenEventInfoToken_, GenEventInfoHandle);
    if( GenEventInfoHandle->weight() < 0)
    {
        nEvents++;
    }
  }
  return;
}


void EventWeightCountProducer::beginLuminosityBlock(const LuminosityBlock & theLuminosityBlock, const EventSetup & theSetup) {
  nEvents = 0;
  return;
}

void EventWeightCountProducer::endLuminosityBlock(LuminosityBlock const& theLuminosityBlock, const EventSetup & theSetup) {}

void EventWeightCountProducer::endLuminosityBlockProduce(LuminosityBlock & theLuminosityBlock, const EventSetup & theSetup) {
  auto_ptr<edm::MergeableCounter> numEventsPtr(new edm::MergeableCounter);  
  numEventsPtr->value = nEvents;
  //totalEventsPtr->value = totalEvents;
  theLuminosityBlock.put(numEventsPtr);

  return;
}



//define this as a plug-in
DEFINE_FWK_MODULE(EventWeightCountProducer);
#endif


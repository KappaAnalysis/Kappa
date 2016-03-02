#ifndef Consumes_h
#define Consumes_h

#if CMSSW_MAJOR_VERSION < 6
namespace edm
{
    struct ConsumesCollector
    {
        template<typename T>
        void consumes(edm::InputTag const &in){}
    };
}

edm::ConsumesCollector(){
    edm::ConsumesCollector cons;
    return cons;
}
#endif

#if CMSSW_MAJOR_VERSION >= 6
#include "FWCore/Framework/interface/ConsumesCollector.h"
#endif
#endif

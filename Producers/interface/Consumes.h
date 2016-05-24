#ifndef Consumes_h
#define Consumes_h

#include "FWCore/Utilities/interface/InputTag.h"

#if CMSSW_MAJOR_VERSION < 6
namespace edm
{
    struct ConsumesCollector
    {
        template<typename T>
        void consumes(edm::InputTag const &in){}
        
        template<typename T, int n>
        void consumes(edm::InputTag const &in){}
    };
}

edm::ConsumesCollector consumesCollector();
#endif

#if CMSSW_MAJOR_VERSION >= 6
#include "FWCore/Framework/interface/ConsumesCollector.h"
#endif
#endif

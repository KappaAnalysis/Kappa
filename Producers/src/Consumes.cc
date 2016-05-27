#include "../interface/Consumes.h"

#if CMSSW_MAJOR_VERSION < 6
edm::ConsumesCollector consumesCollector()
{
    edm::ConsumesCollector cons;
    return cons;
}
#endif
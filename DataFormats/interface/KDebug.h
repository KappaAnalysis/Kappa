#ifndef KAPPA_DEBUG_H
#define KAPPA_DEBUG_H

#include <iostream>
#include "Kappa.h"

std::ostream &operator<<(std::ostream &os, const KLV &lv);
std::ostream &operator<<(std::ostream &os, const KDataLV &lv);
std::ostream &operator<<(std::ostream &os, const KDataBeamSpot &bs);
std::ostream &operator<<(std::ostream &os, const KDataMET &met);
std::ostream &operator<<(std::ostream &os, const KDataPFMET &met);
std::ostream &operator<<(std::ostream &os, const KTrackSummary &s);
std::ostream &operator<<(std::ostream &os, const KParton &p);
std::ostream &operator<<(std::ostream &os, const KDataJet &jet);
std::ostream &operator<<(std::ostream &os, const KDataTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataCaloTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataGenTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataVertex &vertex);
std::ostream &operator<<(std::ostream &os, const KProvenance &p);
std::ostream &operator<<(std::ostream &os, const KLumiMetadata &m);
std::ostream &operator<<(std::ostream &os, const KGenLumiMetadata &m);
std::ostream &operator<<(std::ostream &os, const KEventMetadata &m);
std::ostream &operator<<(std::ostream &os, const KGenEventMetadata &m);
std::ostream &displayHLT(std::ostream &os, const KLumiMetadata &metaLumi, const KEventMetadata &metaEvent);

#include "KDebug.hxx"

#endif

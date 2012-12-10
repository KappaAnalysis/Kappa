#ifndef KAPPA_DEBUG_H
#define KAPPA_DEBUG_H

#include <iostream>
#include <bitset>
#include "Kappa.h"

std::ostream &operator<<(std::ostream &os, const KLV &lv);
std::ostream &operator<<(std::ostream &os, const KDataLV &lv);
std::ostream &operator<<(std::ostream &os, const KDataBeamSpot &bs);
std::ostream &operator<<(std::ostream &os, const KDataMET &met);
std::ostream &operator<<(std::ostream &os, const KDataPFMET &met);
std::ostream &operator<<(std::ostream &os, const KTrackSummary &s);
std::ostream &operator<<(std::ostream &os, const KGenParticle &p);
std::ostream &operator<<(std::ostream &os, const KDataJet &jet);
std::ostream &operator<<(std::ostream &os, const KDataPFJet &jet);
std::ostream &operator<<(std::ostream &os, const KDataTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataCaloTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataGenTau &tau);
std::ostream &operator<<(std::ostream &os, const KDataVertex &vertex);
std::ostream &operator<<(std::ostream &os, const KVertexSummary &vs);
std::ostream &operator<<(std::ostream &os, const KJetArea &ja);
std::ostream &operator<<(std::ostream &os, const KDataHit &hit);
std::ostream &operator<<(std::ostream &os, const KPFCandidate &cand);
std::ostream &operator<<(std::ostream &os, const KFilterSummary &filter);
std::ostream &operator<<(std::ostream &os, const KProvenance &p);
std::ostream &operator<<(std::ostream &os, const KLumiMetadata &m);
std::ostream &operator<<(std::ostream &os, const KGenLumiMetadata &m);
std::ostream &operator<<(std::ostream &os, const KDataLumiMetadata &m);
std::ostream &operator<<(std::ostream &os, const KEventMetadata &m);
std::ostream &operator<<(std::ostream &os, const KTauDiscriminatorMetadata &m);
std::ostream &operator<<(std::ostream &os, const KGenEventMetadata &m);
std::ostream &displayHLT(std::ostream &os, const KLumiMetadata &metaLumi, const KEventMetadata &metaEvent);
std::ostream &displayTO(std::ostream &os, const size_t hltIdx, const KTriggerObjects *trgObj);

#include "KDebug.hxx"

#endif

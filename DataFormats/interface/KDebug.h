#ifndef KAPPA_DEBUG_H
#define KAPPA_DEBUG_H

#include <iostream>
#include "Kappa.h"

std::ostream &operator<<(std::ostream &os, const KLV &lv);
std::ostream &operator<<(std::ostream &os, const KBeamSpot &bs);
std::ostream &operator<<(std::ostream &os, const KBasicMET &met);
std::ostream &operator<<(std::ostream &os, const KMET &met);
std::ostream &operator<<(std::ostream &os, const KTrackSummary &s);
std::ostream &operator<<(std::ostream &os, const KGenParticle &p);
std::ostream &operator<<(std::ostream &os, const KElectron &e);
std::ostream &operator<<(std::ostream &os, const KCaloJet &jet);
std::ostream &operator<<(std::ostream &os, const KBasicJet &jet);
std::ostream &operator<<(std::ostream &os, const KJet &jet);
std::ostream &operator<<(std::ostream &os, const KBasicTau &tau);
std::ostream &operator<<(std::ostream &os, const KGenTau &tau);
std::ostream &operator<<(std::ostream &os, const KVertex &vertex);
std::ostream &operator<<(std::ostream &os, const KVertexSummary &vs);
std::ostream &operator<<(std::ostream &os, const KTaupairVerticesMap &pvs);
std::ostream &operator<<(std::ostream &os, const KPileupDensity &pu);
std::ostream &operator<<(std::ostream &os, const KHit &hit);
std::ostream &operator<<(std::ostream &os, const KPFCandidate &cand);
std::ostream &operator<<(std::ostream &os, const KFilterSummary &filter);
std::ostream &operator<<(std::ostream &os, const KProvenance &p);
std::ostream &operator<<(std::ostream &os, const KLumiInfo &m);
std::ostream &operator<<(std::ostream &os, const KGenLumiInfo &m);
std::ostream &operator<<(std::ostream &os, const KDataLumiInfo &m);
std::ostream &operator<<(std::ostream &os, const KEventInfo &m);
std::ostream &operator<<(std::ostream &os, const KTauMetadata &m);
std::ostream &operator<<(std::ostream &os, const KMuonMetadata &m);
std::ostream &operator<<(std::ostream &os, const KGenEventInfo &m);
std::ostream &displayHLT(std::ostream &os, const KLumiInfo &metaLumi, const KEventInfo &metaEvent);
std::ostream &displayTO(std::ostream &os, const size_t hltIdx, const KTriggerObjects *trgObj);

#include "KDebug.hxx"

#endif

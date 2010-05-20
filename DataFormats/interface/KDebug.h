#ifndef KAPPA_DEBUG_H
#define KAPPA_DEBUG_H

#include <iostream>
#include "../src/classes.h"

template<typename T>
void printvec(std::ostream &os, const T &v)
{
	os << "Size: " << v.size() << std::endl;
	for (typename T::const_iterator it = v.begin(); it != v.end(); ++it)
		os << " " << *it;
	os << std::endl;
}

// Need thin wrapper class for ostream operator overloading
// - overkill here, but simplifies vector output later
template<typename T> struct KLVWrap { KLVWrap(const T &_p4) : p4(_p4) {}; const T &p4; };

template<typename T>
std::ostream &operator<<(std::ostream &os, const KLVWrap<T> &lv)
{
	return os << "(pt=" << lv.p4.pt() << ", eta=" << lv.p4.eta() << ", phi="
		<< lv.p4.phi() << ", E=" << lv.p4.E()  << ", m=" << lv.p4.M() << ")";
}

std::ostream &operator<<(std::ostream &os, const KLV &lv)
{
	return os << KLVWrap<KLV::KInternalLV>(lv.p4);
}

std::ostream &operator<<(std::ostream &os, const KDataLV &lv)
{
	return os << KLVWrap<KDataLV::KInternalLV>(lv.p4);
}

std::ostream &operator<<(std::ostream &os, const KDataMET &met)
{
	return os << KLVWrap<KDataLV::KInternalLV>(met.p4) << " sumEt=" << met.sumEt;
}

std::ostream &operator<<(std::ostream &os, const KDataPFMET &met)
{
	return os << static_cast<KDataMET>(met) << " cEMF=" << met.chargedEMFraction;
}

std::ostream &operator<<(std::ostream &os, const KTrackSummary &s)
{
	return os << "#Tracks=" << s.nTracks << ", #HQ Tracks=" << s.nTracksHQ;
}

std::ostream &operator<<(std::ostream &os, const KParton &v)
{
	bool neg = (v.pdgid & (1 << KPartonChargeMask)) != 0;
	unsigned status = (v.pdgid >> KPartonStatusMask) % 8;
	int id = (v.pdgid % (1 << KPartonStatusMask)) * (neg ? -1 : 1);
	return os << status << "|" << id << "|" << v.p4;
}

std::ostream &operator<<(std::ostream &os, const KDataJet &jet)
{
	os << static_cast<KDataLV>(jet) << std::endl;
	os << "emf: " << jet.emf << " area: " << jet.area << " detEta: " << jet.detectorEta << std::endl;
	os << "Const: " << jet.nConst << " n90: " << jet.n90 << " n90Hits: " << jet.n90Hits << std::endl;
	os << "fHPD: " << jet.fHPD << " fRBX: " << jet.fRBX << " HCAL noise: " << jet.noiseHCAL << std::endl;
	os << "nTrack_Calo: " << jet.nTracksAtCalo << " nTrack_Vertex: " << jet.nTracksAtVertex;
	return os;
}

////////////////////////////////////////////////////////////
// KMetadata.h
////////////////////////////////////////////////////////////
std::ostream &operator<<(std::ostream &os, const KProvenance &p)
{
	if (p.names.size() != p.branches.size())
		return os << "Provenance corrupted!" << std::endl;
	for (size_t i = 0; i < p.names.size(); ++i)
		os << p.names[i] << " = " << p.branches[i] << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KLumiMetadata &m)
{
	os << "Run: " << m.nRun << " " << m.nLumi << std::endl;
	os << "HLT names "; printvec(os, m.hltNames);
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenLumiMetadata &m)
{
	os << static_cast<KLumiMetadata>(m) << std::endl;
	return os << "ext. xSec: " << m.xSectionExt << " int. xSec: " << m.xSectionInt << std::endl;
}

std::ostream &operator<<(std::ostream &os, const KEventMetadata &m)
{
	return os << "Event ID = " << m.nRun << ":" << m.nLumi << ":" << m.nBX << ":" << m.nEvent;
}

std::ostream &operator<<(std::ostream &os, const KGenEventMetadata &m)
{
	os << static_cast<KEventMetadata>(m) << std::endl;
	return os << "Weight: " << m.weight;
}

#endif

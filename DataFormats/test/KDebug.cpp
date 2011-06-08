#include "../interface/KDebug.h"

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

std::ostream &operator<<(std::ostream &os, const KDataBeamSpot &bs)
{
	return os << bs.position << " betaStar=" << bs.betaStar;
}

std::ostream &operator<<(std::ostream &os, const KDataMET &met)
{
	return os << static_cast<KDataLV>(met) << " sumEt=" << met.sumEt;
}

std::ostream &operator<<(std::ostream &os, const KDataPFMET &met)
{
	return os << static_cast<KDataMET>(met) << " cEMF=" << met.chargedEMEtFraction << " cHADF=" << met.chargedHadEtFraction << " nEMF=" << met.neutralEMEtFraction << " nHADF=" << met.neutralHadEtFraction << " MuonF=" << met.muonEtFraction << " type6F=" << met.type6EtFraction << " type7F=" << met.type7EtFraction;
}

std::ostream &operator<<(std::ostream &os, const KTrackSummary &s)
{
	return os << "#Tracks=" << s.nTracks << ", #HQ Tracks=" << s.nTracksHQ;
}

std::ostream &operator<<(std::ostream &os, const KParton &p)
{
	return os << p.status() << "|" << p.pdgId() << "|" << KLVWrap<KParton::KInternalLV>(p.p4);
}

std::ostream &operator<<(std::ostream &os, const KDataJet &jet)
{
	os << static_cast<KDataLV>(jet) << std::endl;
	os << "Const: " << jet.nConst << " n90: " << jet.n90 << " n90Hits: " << jet.n90Hits << std::endl;
	os << "fHPD: " << jet.fHPD << " fRBX: " << jet.fRBX << " HCAL noise: " << jet.noiseHCAL << std::endl;
	os << "fEM: " << jet.fEM << " fHO: " << jet.fHO << " area: " << jet.area << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KDataTau &tau)
{
	return os << static_cast<KDataLV>(tau) << " charge=" << tau.charge;
}

std::ostream &operator<<(std::ostream &os, const KDataCaloTau &tau)
{
	return os << static_cast<KDataLV>(tau) << " charge=" << tau.charge;
}

std::ostream &operator<<(std::ostream &os, const KDataGenTau &tau)
{
	return os << static_cast<const KParton&>(tau) << " p4_vis=" << static_cast<RMLV>(tau.p4_vis) << " decayMode=" << tau.decayMode << " vertex=" << tau.vertex;
}

std::ostream &operator<<(std::ostream &os, const KDataVertex &vertex)
{
	return os << vertex.position << " nTracks=" << vertex.nTracks << " fake=" << vertex.fake << " chi2=" << vertex.chi2 << " nDOF=" << vertex.nDOF;
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
	os << "HLT names "; displayVector(os, m.hltNames);
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenLumiMetadata &m)
{
	os << static_cast<KLumiMetadata>(m) << std::endl;
	return os
		<< "ext. xSec: " << m.xSectionExt << " "
		<< "int. xSec: " << m.xSectionInt
		<< std::endl;
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

void displayHLT(std::ostream &os, KLumiMetadata *metaLumi, KEventMetadata *metaEvent)
{
	for (size_t hltIdx = 0; hltIdx < metaLumi->hltNames.size(); ++hltIdx)
		if (metaEvent->bitsHLT & ((unsigned long long)1 << hltIdx))
			os << hltIdx << ":" << metaLumi->hltNames[hltIdx] << " ";
		os << std::endl;
}

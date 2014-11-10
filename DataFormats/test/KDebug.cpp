/* Copyright (c) 2010 - All Rights Reserved
 *   Corinna Guenth <cguenth@ekpcms5.ekpplus.cluster>
 *   Fred Stober <stober@cern.ch>
 *   Joram Berger <joram.berger@cern.ch>
 *   Manuel Zeise <zeise@cern.ch>
 *   Thomas Hauth <Thomas.Hauth@cern.ch>
 */

#include "../interface/KDebug.h"
#include <bitset>

std::ostream &operator<<(std::ostream &os, const KLV &lv)
{
	return os << "(pt=" << lv.p4.pt() << ", eta=" << lv.p4.eta() << ", phi="
		<< lv.p4.phi() << ", E=" << lv.p4.E()  << ", m=" << lv.p4.M() << ")";
}

std::ostream &operator<<(std::ostream &os, const KBeamSpot &bs)
{
	return os << bs.position << " betaStar=" << bs.betaStar;
}

std::ostream &operator<<(std::ostream &os, const KBasicMET &met)
{
	return os << static_cast<const KLV>(met) << " sumEt=" << met.sumEt;
}

std::ostream &operator<<(std::ostream &os, const KMET &met)
{
	os << static_cast<const KBasicMET>(met) << std::endl;
	os << "\tCharged (em,had): " << met.chargedEMEtFraction << ", " << met.chargedHadEtFraction << std::endl;
	os << "\tNeutral (em,had): " << met.neutralEMEtFraction << ", " << met.neutralHadEtFraction << std::endl;
	os << "\tMuonF=" << met.muonEtFraction << " type6F=" << met.type6EtFraction << " type7F=" << met.type7EtFraction;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KTrackSummary &s)
{
	return os << "#Tracks=" << s.nTracks << " #HQ Tracks=" << s.nTracksHQ;
}

std::ostream &operator<<(std::ostream &os, const KGenParticle &p)
{
	return os << static_cast<const KLV>(p)
		<< " status=" << p.status() << " pdgid=" << p.pdgId() << " charge=" << p.charge();
}

std::ostream &operator<<(std::ostream &os, const KElectron &e)
{
	return os << static_cast<const KLV>(e);
}

std::ostream &operator<<(std::ostream &os, const KCaloJet &jet)
{
	os << static_cast<const KLV>(jet) << std::endl;
	os << "\t#Const=" << jet.nConst << " n90Hits=" << jet.n90Hits << std::endl;
	os << "\tfHPD=" << jet.fHPD << " fRBX=" << jet.fRBX << std::endl;
	return os << "\tfEM=" << jet.fEM << " fHO=" << jet.fHO << " area=" << jet.area;
}

std::ostream &operator<<(std::ostream &os, const KBasicJet &jet)
{
	os << static_cast<const KLV>(jet) << std::endl;
	os << "\tCharged (em,had): " << jet.chargedEMFraction << ", " << jet.chargedHadFraction << std::endl;
	os << "\tNeutral (em,had): " << jet.neutralEMFraction << ", " << jet.neutralHadFraction << std::endl;
	return os << "\t#Const=" << jet.nConst << " #Charged=" << jet.nCharged << " area=" << jet.area;
}

std::ostream &operator<<(std::ostream &os, const KJet &jet)
{
	os << static_cast<const KBasicJet>(jet) << std::endl;
	os << "taggers: " << std::endl;
    for (size_t i = 0; i < jet.taggers.size(); ++i)
        os << jet.taggers[i] << " " << std::endl;
	return os << "\tpuJetId: " << jet.puJetID << std::endl;
}

std::ostream &operator<<(std::ostream &os, const KBasicTau &tau)
{
	return os << static_cast<const KLV>(tau) << " charge=" << tau.charge;
}

std::ostream &operator<<(std::ostream &os, const KGenTau &tau)
{
	return os << static_cast<const KGenParticle>(tau)
		<< " visible=" << static_cast<const KLV>(tau.visible)
		<< " decayMode=" << tau.decayMode << " vertex=" << tau.vertex;
}

std::ostream &operator<<(std::ostream &os, const KVertex &vertex)
{
	return os << vertex.position
		<< " #Tracks=" << vertex.nTracks << " fake=" << vertex.fake
		<< " chi2=" << vertex.chi2 << " DOF=" << vertex.nDOF;
}

std::ostream &operator<<(std::ostream &os, const KVertexSummary &vs)
{
	return os << vs.pv << " #Vertices=" << vs.nVertices;
}

std::ostream &operator<<(std::ostream &os, const KTaupairVerticesMap &pvs)
{
	for(size_t i = 0; i < pvs.diTauKey.size(); ++i)
		os << "diTauKey=" << pvs.diTauKey[i] << " Vertex:" << pvs.vertices[i] << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KPileupDensity &pu)
{
	return os << "rho=" << pu.rho << " sigma=" << pu.sigma;
}

std::ostream &operator<<(std::ostream &os, const KHit &hit)
{
	return os << "theta=" << hit.theta << " phi=" << hit.phi
		<< " pAbs=" << hit.pAbs << " Eloss=" << hit.energyLoss;
}

std::ostream &operator<<(std::ostream &os, const KPFCandidate &cand)
{
	return os << static_cast<const KLV>(cand)
		<< " charge=" << cand.charge() << " pdgid=" << cand.pdgId()
		<< " deltaP=" << cand.deltaP
		<< " Eecal=" << cand.ecalEnergy << " Ehcal=" << cand.hcalEnergy;
}

std::ostream &operator<<(std::ostream &os, const KFilterSummary &filter)
{
	return os << "Filters=" << std::bitset<16>(filter.presence)
		<< " decision=" << std::bitset<16>(filter.decision);
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

std::ostream &operator<<(std::ostream &os, const KLumiInfo &m)
{
	os << "Run: " << m.nRun << " " << m.nLumi << std::endl;
	os << "HLT names "; displayVector(os, m.hltNames);
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenLumiInfo &m)
{
	os << static_cast<const KLumiInfo>(m) << std::endl;
	return os
		<< "ext. xSec: " << m.xSectionExt << " "
		<< "int. xSec: " << m.xSectionInt;
}

std::ostream &operator<<(std::ostream &os, const KDataLumiInfo &m)
{
	os << static_cast<const KLumiInfo>(m) << std::endl;
	return os
		<< "Delivered=" << m.avgInsDelLumi << "+/-" << m.avgInsDelLumiErr << std::endl
		<< "Recorded=" << m.avgInsRecLumi << "+/-" << m.avgInsRecLumiErr << std::endl
		<< "deadtime=" << m.deadFrac << " length=" << m.lumiSectionLength << " quality=" << m.lumiSecQual;
}

std::ostream &operator<<(std::ostream &os, const KEventInfo &m)
{
	return os << "Event ID = " << m.nRun << ":" << m.nLumi << ":" << m.nBX << ":" << m.nEvent;
}

std::ostream &operator<<(std::ostream &os, const KTauMetadata &m)
{
	for (std::vector<std::string>::const_iterator it = m.binaryDiscriminatorNames.begin(); it != m.binaryDiscriminatorNames.end(); ++it)
		os << "Binary tau discriminator: " << *it << std::endl;
	for (std::vector<std::string>::const_iterator it = m.floatDiscriminatorNames.begin(); it != m.floatDiscriminatorNames.end(); ++it)
		os << "Float tau discriminator: " << *it << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KMuonMetadata &m)
{
	for (std::vector<std::string>::const_iterator it = m.hltNames.begin(); it != m.hltNames.end(); ++it)
		os << "Muon HLT trigger objects: " << *it << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenEventInfo &m)
{
	os << static_cast<const KEventInfo>(m) << std::endl;
	return os
		<< "Weight: " << m.weight
		<< "#PU: " << m.numPUInteractionsTruth;
}

std::ostream &displayHLT(std::ostream &os, const KLumiInfo &metaLumi, const KEventInfo &metaEvent)
{
	for (size_t hltIdx = 0; hltIdx < metaLumi.hltNames.size(); ++hltIdx)
		if (metaEvent.bitsHLT & ((unsigned long long)1 << hltIdx))
			os << hltIdx << ":" << metaLumi.hltNames[hltIdx] << "(" << metaLumi.hltPrescales[hltIdx] << ")" << " ";
		os << std::endl;
	return os;
}

std::ostream &displayTO(std::ostream &os, const size_t hltIdx, const KTriggerObjects *trgObj)
{
	for (size_t i = 0; i < trgObj->toIdxFilter[hltIdx].size(); ++i)
		os << trgObj->trgObjects[trgObj->toIdxFilter[hltIdx][i]] << " ";
	return os << std::endl;
}

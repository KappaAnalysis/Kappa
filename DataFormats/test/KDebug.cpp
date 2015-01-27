//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Corinna Guenth <cguenth@ekpcms5.ekpplus.cluster>
//-  * Dominik Haitz <dhaitz@ekp.uni-karlsruhe.de>
//-  * Fabio Colombo <fabio.colombo@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Raphael Friese <Raphael.Friese@cern.ch>
//-  * Thomas Hauth <Thomas.Hauth@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#include "../interface/KDebug.h"
#include <bitset>

std::ostream &operator<<(std::ostream &os, const KLV &lv)
{
	return os << "(pt=" << lv.p4.pt() << ", eta=" << lv.p4.eta() << ", phi="
		<< lv.p4.phi() << ", E=" << lv.p4.E()  << ", m=" << lv.p4.M() << ")";
}

std::ostream &operator<<(std::ostream &os, const KBeamSpot &bs)
{
	os << bs.position << " beta*=" << bs.betaStar;
	os << " beamWidth=(" << bs.beamWidthX << ", " << bs.beamWidthY << ")";
	os << " dx/dz=" << bs.dxdz << " dy/dz=" << bs.dydz << " sigmaZ=" << bs.sigmaZ;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KBasicMET &met)
{
	os << static_cast<const KLV>(met) << " sumEt=" << met.sumEt;
	os << " sig=(" << met.significance(0,0) << ", " << met.significance(1,0) << "; ";
	os << met.significance(0,1) << ", " << met.significance(1,1) << ")";
	return os;
}

std::ostream &operator<<(std::ostream &os, const KMET &met)
{
	os << static_cast<const KBasicMET>(met) << std::endl;
	os << "\tCHF=" << met.chargedHadronFraction << " NHF=" << met.neutralHadronFraction;
	os << " HFHadF=" << met.hfHadronFraction << " HFEMF=" << met.hfEMFraction << std::endl;
	os << "\teF=" << met.electronFraction << " photF=" << met.photonFraction;
	os << " muF=" << met.muonFraction << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KTrackSummary &s)
{
	return os << "nTracks=" << s.nTracks << " (HQ=" << s.nTracksHQ << ")";
}

std::ostream &operator<<(std::ostream &os, const KTrack &trk)
{
	os << static_cast<const KLV>(trk);
	os << "+-(" << trk.errPt << ", " << trk.errEta << ", " << trk.errPhi << ")" << std::endl;
	os << "\tcharge=" << int(trk.charge) << " chi2/nDOF=" << trk.chi2 << "/" << trk.nDOF;
	os << " ref=" << trk.ref << "+-(" << trk.errDxy << ",, " << trk.errDz << ")" << std::endl;
	os << "\thits: nPX=" << trk.nValidPixelHits << " nST=" << trk.nValidStripHits;
	os << " nMU=" << trk.nValidMuonHits << " nIN=" << trk.nInnerHits;
	os << "; layers: nPX=" << trk.nPixelLayers << " nST=" << trk.nStripLayers;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KParticle &p)
{
	return os << static_cast<const KLV>(p)
		<< " status=" << p.status() << " pdgid=" << p.pdgId() << " charge=" << p.charge();
}

std::ostream &operator<<(std::ostream &os, const KGenParticle &p)
{
	return os << static_cast<const KParticle>(p)
		<< " status=" << p.status() << " pdgid=" << p.pdgId() << " charge=" << p.charge();
}

std::ostream &operator<<(std::ostream &os, const KElectron &e)
{
	os << static_cast<const KLepton>(e);
	os << " track=" << e.trackIso << " ecal=" << e.ecalIso << " hcal=" << e.hcal1Iso << "+" << e.hcal2Iso << std::endl;
	os << "\tH/EM=" << e.hadronicOverEm << " fbrem=" << e.fbrem << " Eecal=" << e.ecalEnergy << "+-" << e.ecalEnergyErr;
	os << " DpTrack=" << e.trackMomentumErr << " Dp" << e.electronMomentumErr;
	os << " type=" << int(e.electronType) << " flags=" << std::bitset<8>(e.fiducialFlags) << std::endl;
	os << "\tvtx: eta=" << e.dEtaIn << " phi=" << e.dPhiIn << " sigma=" << e.sigmaIetaIeta;
	os << "; supercluster: pos=" << e.superclusterPosition;
	os << " E/p=" << e.eSuperClusterOverP << " E=" << e.superclusterEnergy;
	if (e.electronIds.size() > 0)
		os << "\n\tIds: ";
	for (size_t i = 0; i < e.electronIds.size(); ++i)
		os << e.electronIds[i] << ", ";
	return os;
}

std::ostream &operator<<(std::ostream &os, const KCaloJet &jet)
{
	os << static_cast<const KLV>(jet) << std::endl;
	os << "\tnConstituents=" << jet.nConstituents << " n90Hits=" << jet.n90Hits << " area=" << jet.area << std::endl;
	os << "\tfHPD=" << jet.fHPD << " fRBX=" << jet.fRBX << " fEM=" << jet.fEM << " fHO=" << jet.fHO;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KBasicJet &jet)
{
	os << static_cast<const KLV>(jet) << std::endl;
	os << "\tCHF=" << jet.chargedHadronFraction << " NHF=" << jet.neutralHadronFraction;
	os << " HFHadF=" << jet.hfHadronFraction << " HFEMF=" << jet.hfEMFraction << std::endl;
	os << "\teF=" << jet.electronFraction << " photF=" << jet.photonFraction << " muF=" << jet.muonFraction << std::endl;
	return os << "\tnConst=" << jet.nConstituents << " nCharged=" << jet.nCharged << " area=" << jet.area;
}

std::ostream &operator<<(std::ostream &os, const KJet &jet)
{
	os << static_cast<const KBasicJet>(jet) << std::endl;
	if (jet.tags.size() > 0)
		os << "\ttags: ";
	for (size_t i = 0; i < jet.tags.size(); ++i)
		os << jet.tags[i] << ", ";
	return os << "\tIDs: " << std::bitset<8>(jet.binaryIds);
}

std::ostream &operator<<(std::ostream &os, const KLepton &lep)
{
	// flavour as [E], [M] or [T]
	os << static_cast<const KLV>(lep) << " [" << "?EMT!!!"[int(lep.flavour())];
	os <<  "] charge=" << lep.charge();
	os << " IDs(CHSVTMLA)=" << std::bitset<8>(lep.ids) << std::endl;
	if (lep.isAlternativeTrack())  // mark alternative track with *
		os << "\ttrack*:";
	else
		os << "\ttrack: ";
	os << lep.track << std::endl;
	os << "\tiso: pf(CH,NH,PH,PU)=(" << lep.sumChargedHadronPt << ", " << lep.sumNeutralHadronEt;
	os << ", " << lep.sumPhotonEt << ", " << lep.sumPUPt << ")=" << lep.pfIso();
	return os;
}

std::ostream &operator<<(std::ostream &os, const KBasicTau &tau)
{
	os << static_cast<const KLepton>(tau) << std::endl;
	os << "\tdecayMode=" << tau.decayMode << " emFraction=" << tau.emFraction << std::endl;
	for (size_t i = 0; i < tau.floatDiscriminators.size(); ++i)
		os << tau.floatDiscriminators[i] << ", ";
	os << "\tIDs=" << std::bitset<64>(tau.binaryDiscriminators);
	return os;
}

std::ostream &operator<<(std::ostream &os, const KTau &tau)
{
	os << static_cast<const KBasicTau>(tau) << std::endl;
	os << "\tnPi0=" << tau.piZeroCandidates.size();
	os << " nCHad=" << tau.chargedHadronCandidates.size();
	os << " nGamma=" << tau.gammaCandidates.size();
	os << " key=" << tau.tauKey;
	return os;
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
		<< " nTracks=" << vertex.nTracks << " valid=" << vertex.valid
		<< " chi2/nDOF=" << vertex.chi2 << "/" << vertex.nDOF;
}

std::ostream &operator<<(std::ostream &os, const KVertexSummary &vs)
{
	return os << "pv=" << vs.pv << "; nVertices=" << vs.nVertices;
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
	return os << "filters=" << std::bitset<16>(filter.presence)
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

std::ostream &operator<<(std::ostream &os, const KLumiInfo &info)
{
	os << "Run:LS=" << info.nRun << ":" << info.nLumi << " flags=" << info.bitsUserFlags << std::endl;
	//if (info.hltNames.size() > 0)
		os << "\tHLTs(prescale)=";
	for (size_t i = 0; i < info.hltNames.size(); ++i)
		os << info.hltNames[i] << "(" << info.hltPrescales[i] << "), ";
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenLumiInfo &info)
{
	os << static_cast<const KLumiInfo>(info) << std::endl;
	os << "\txSec(ext)=" << info.xSectionExt << " xSec(int)=" << info.xSectionInt;
	os << " filterEff=" << info.filterEff;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KDataLumiInfo &info)
{
	os << static_cast<const KLumiInfo>(info) << std::endl;
	os << "\tdel=" << info.avgInsDelLumi << "+-" << info.avgInsDelLumiErr;
	os << " rec=" << info.avgInsRecLumi << "+-" << info.avgInsRecLumiErr << std::endl;
	os << "\tdeadtime=" << info.deadFrac << " length=" << info.lumiSectionLength;
	os << " quality=" << info.lumiSecQual << " nFill=" << info.nFill;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KEventInfo &i)
{
	os << "Event=" << i.nRun << ":" << i.nLumi << ":" << i.nBX << ":" << i.nEvent;
	os << " flags=" << std::bitset<32>(i.bitsUserFlags);
	os << " rnd=" << i.randomNumber << " minWght=" << i.minVisPtFilterWeight << std::endl;
	os << "\tTrigger: L1=" << std::bitset<64>(i.bitsL1) << std::endl;
	os << "\t        HLT=" << std::bitset<64>(i.bitsHLT);
	return os;
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

std::ostream &operator<<(std::ostream &os, const KGenEventInfo &i)
{
	os << static_cast<const KEventInfo>(i) << std::endl;
	os << "\tweight=" << i.weight << " bin=" << i.binValue << " alphaQCD=" << i.alphaQCD << std::endl;
	os << "\tnPU(-2..2)=(" << int(i.nPUm2) << ", " << i.nPUm1 << int(i.nPU) << ", " << int(i.nPUp1) << ", " << int(i.nPUp2) << ") nPUMean=" << i.nPUMean;
	return os;
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

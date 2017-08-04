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

/* Extension of ostream to understand Kappa objects
 * This can be used in the analysis code as: cout << jet;
 * Basic rules for the output:
 *  - use minimal space (preferably one line)
 *  - stay roughly below 80 characters per line
 *  - don't show deprecated members
 *  - group members logically
 *  - avoid redundant information
 *  - don't show the object name at the beginning
 *  - don't put a new line at the end
 *  - use static_cast whereever possible
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
	os << bs.position << " beta*=" << bs.betaStar;
	os << " beamWidth=(" << bs.beamWidthX << ", " << bs.beamWidthY << ")";
	os << " dx/dz=" << bs.dxdz << " dy/dz=" << bs.dydz << " sigmaZ=" << bs.sigmaZ;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KMET &met)
{
	os << static_cast<const KLV>(met) << " sumEt=" << met.sumEt;
	os << "\tCHF=" << met.chargedHadronFraction << " NHF=" << met.neutralHadronFraction;
	os << " HFHadF=" << met.hfHadronFraction << " HFEMF=" << met.hfEMFraction << std::endl;
	os << "\teF=" << met.electronFraction << " photF=" << met.photonFraction;
	os << " muF=" << met.muonFraction;
	os << " sig=(" << met.significance(0,0) << ", " << met.significance(1,0) << "; ";
	os << met.significance(0,1) << ", " << met.significance(1,1) << ")";
	return os;
}

std::ostream &operator<<(std::ostream &os, const KTrackSummary &s)
{
	return os << "nTracks=" << s.nTracks << " (HQ=" << s.nTracksHQ << ")";
}

std::ostream &operator<<(std::ostream &os, const KTrack &trk)
{
	os << static_cast<const KLV>(trk);
	os << "+-(" << trk.errPt() << ", " << trk.errEta() << ", " << trk.errPhi() << ")" << std::endl;
	os << "\tcharge=" << int(trk.charge) << " chi2/nDOF=" << trk.chi2 << "/" << trk.nDOF;
	os << " ref=" << trk.ref << "+-(" << trk.errDxy() << ", " << trk.errDz() << ")" << std::endl;
	os << "\thits: nPX=" << trk.nValidPixelHits << " nST=" << trk.nValidStripHits;
	os << " nMU=" << trk.nValidMuonHits << " nIN=" << trk.nInnerHits;
	os << "; layers: nPX=" << trk.nPixelLayers << " nST=" << trk.nStripLayers;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KParticle &p)
{
	return os << static_cast<const KLV>(p)
		<< " pdgid=" << p.pdgId << " charge=" << p.charge();
}

std::ostream &operator<<(std::ostream &os, const KGenParticle &p)
{
	os << static_cast<const KParticle>(p) << std::endl;
	os << "\tdaughters(" << p.daughterIndices.size() << ")";
	if (p.daughterIndices.size() > 0)
		os << "=" << p.daughterIndices[0];
	for (size_t i = 1; i < p.daughterIndices.size(); ++i)
		os << p.daughterIndices[i] << ", ";
	return os;
}

std::ostream &operator<<(std::ostream &os, const KLHEParticle &p)
{
	os << "(px=" << p.p4.px() << ", py=" << p.p4.py() << ", pz="
	   << p.p4.pz() << ", E=" << p.p4.E()  << ", m=" << p.p4.M() << ")"
	   << ", pdgid=" << p.pdgId << ", status=" << p.status;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KLHEParticles &particles)
{
	for (std::vector<KLHEParticle>::const_iterator p = particles.particles.begin(); p != particles.particles.end(); ++p)
	{
		os << *p << std::endl;
	}
	os << "subprocessCode=" << particles.subprocessCode
	   << ", pdfScale=" << particles.pdfScale << ", alphaEM=" << particles.alphaEM << ", alphaQCD=" << particles.alphaQCD;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenPhoton &p)
{
	os << static_cast<const KLV>(p) << std::endl;
	os << "\ttype=" << int(p.type) << " mother=" << p.mother;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KElectron &e)
{
	os << static_cast<const KLepton>(e);
	os << " track=" << e.trackIso << " ecal=" << e.ecalIso << " hcal=" << e.hcal1Iso << "+" << e.hcal2Iso << std::endl;
	os << "\tH/EM=" << e.hadronicOverEm << " fbrem=" << e.fbrem << " Eecal=" << e.ecalEnergy << "+-" << e.ecalEnergyErr;
	os << " DpTrack=" << e.trackMomentumErr << " Dp=" << e.electronMomentumErr;
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
	os << static_cast<const KBasicJet>(jet);
	os << "\tflavour=" << jet.flavour;
	os << "\tIDs=" << std::bitset<8>(jet.binaryIds);
	if (jet.tags.size() > 0)
		os << std::endl << "\ttags: ";
	for (size_t i = 0; i < jet.tags.size(); ++i)
		os << jet.tags[i] << ", ";
	return os;
}

std::ostream &operator<<(std::ostream &os, const KPhoton &phot)
{
	os << static_cast<const KLV>(phot);
	os << "\tIDs=" << std::bitset<8>(phot.ids) << " sigmaIetaIeta=" << phot.sigmaIetaIeta << std::endl;
	os << "\tiso: pf(CH,NH,PH,PU)=(" << phot.sumChargedHadronPt << ", " << phot.sumNeutralHadronEt;
	os << ", " << phot.sumPhotonEt << ", " << phot.sumPUPt << ")=" << phot.pfIso();
	return os;
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

std::ostream &operator<<(std::ostream &os, const KLeptonPair &leptonPair)
{
	return os << "dca3D = " << leptonPair.dca3D << " +/- " << leptonPair.dca3DError << ", "
	          << "dca2D = " << leptonPair.dca2D << " +/- " << leptonPair.dca2DError;
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

std::ostream &operator<<(std::ostream &os, const KExtendedTau &tau)
{
	os << static_cast<const KBasicTau>(tau) << std::endl;
	os << "\tnBarrelSuperClusters=" << tau.superClusterBarrelCandidates.size();
	os << " nEndcapSuperClusters=" << tau.superClusterEndcapCandidates.size();
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenTau &tau)
{
	return os << static_cast<const KGenParticle>(tau)
		<< " visible=" << tau.visible << " decayMode=" << int(tau.decayMode)
		<< " vertex=" << tau.vertex;
}

std::ostream &operator<<(std::ostream &os, const KGenJet &jet)
{
	return os << jet.p4;
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

std::ostream &operator<<(std::ostream &os, const KTriggerObjects &to)
{
	os << "Trigger objects: Indices";
	if (to.trgObjects.size() != to.toIdxFilter.size())
		os << "\nTrigger objects are broken!" << std::endl;
	for(size_t i = 0; i < to.trgObjects.size(); ++i)
	{
		os << "\n\t" << to.trgObjects[i] << ": ";
		for (size_t j=0; j < to.toIdxFilter[i].size(); ++j)
			os << to.toIdxFilter[i][j] << ", ";
	}
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
		<< " charge=" << cand.charge() << " pdgid=" << cand.pdgId
		<< " deltaP=" << cand.deltaP
		<< " Eecal=" << cand.ecalEnergy << " Ehcal=" << cand.hcalEnergy;
}

std::ostream &operator<<(std::ostream &os, const KFilterSummary &filter)
{
	return os << "filters=" << std::bitset<16>(filter.presence)
		<< " decision=" << std::bitset<16>(filter.decision);
}

std::ostream &operator<<(std::ostream &os, const KHCALNoiseSummary &noise)
{
	os << "badRBXTS=" << noise.hasBadRBXTS4TS5;
	os << " iso-noise: E="<< noise.isolatedNoiseSumE;
	os << " Et=" << noise.isolatedNoiseSumEt;
	os << " nChannels=" << noise.numIsolatedNoiseChannels;
	os << "; hit-time=" << noise.min25GeVHitTime;
	os << ".." << noise.max25GeVHitTime;
	os << " E2=" << noise.minE2Over10TS;
	os << ".." << noise.maxE2Over10TS;
	os << " RBXEMP>=" << noise.minRBXEMF;
	os << " RBX-hits<=" << noise.maxRBXHits;
	os << " HPD-hits<=" << noise.maxHPDHits;
	os << " HPD-other<=" << noise.maxHPDNoOtherHits;
	os << " n0<=" << noise.maxZeros;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KL1Muon &mu)
{
	return os << static_cast<const KLV>(mu) << " state=" << std::bitset<16>(mu.state);
}

std::ostream &operator<<(std::ostream &os, const KMuon &mu)
{
	os << static_cast<const KLepton>(mu) << std::endl;
	os << "\tglobal track: " << mu.globalTrack << std::endl;
	os << "\tbest track: dxy=" << mu.dxy << " dz=" << mu.dz << std::endl;
	os << "\tiso: track=" << mu.trackIso << " ecal=" << mu.ecalIso;
	os << " hcal=" << mu.hcalIso << " pfIso03=" << mu.pfIso03 << std::endl;
	os << "\tnChambers=" << mu.nChambers << " nMatches=" << mu.nMatches;
	os << " nStations=" << mu.nMatchedStations;
	os << " type=" << int(mu.type) << std::endl;
	os << "\tpropagated: eta=" << mu.eta_propagated << " phi=" << mu.phi_propagated << std::endl;
	os << "\thltMatch=" << std::bitset<64>(mu.hltMatch);
	return os;
}

std::ostream &operator<<(std::ostream &os, const KMuonTriggerCandidate &cand)
{
	os << static_cast<const KTrack>(cand);
	os << " decision=" << cand.isoDecision << " quantity=" << cand.isoQuantity;
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

std::ostream &operator<<(std::ostream &os, const KLumiInfo &info)
{
	os << "Run:LS=" << info.nRun << ":" << info.nLumi << " flags=" << info.bitsUserFlags;
	if (info.hltNames.size() != info.hltPrescales.size())
		return os << "\nHLT prescales corrupted!" << std::endl;
	if (info.hltNames.size() > 0)
		os << "\n\tHLTs(prescale)=";
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
	os << " minWght=" << i.minVisPtFilterWeight << std::endl;
	os << "\tTrigger: L1=" << std::bitset<64>(i.bitsL1) << std::endl;
	os << "\t        HLT=";
	for (size_t index = 0; index < i.bitsHLT.size(); index++)
		os << (i.bitsHLT[index]);
	os << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KTauMetadata &m)
{
	for (std::vector<std::string>::const_iterator it = m.binaryDiscriminatorNames.begin(); it != m.binaryDiscriminatorNames.end(); ++it)
		os << "tau discriminator (binary): " << *it << std::endl;
	for (std::vector<std::string>::const_iterator it = m.floatDiscriminatorNames.begin(); it != m.floatDiscriminatorNames.end(); ++it)
		os << "tau discriminator (float):  " << *it << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KMuonMetadata &m)
{
	for (std::vector<std::string>::const_iterator it = m.hltNames.begin(); it != m.hltNames.end(); ++it)
		os << "muon HLT trigger objects: " << *it << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenEventInfoMetadata &m)
{
	for(auto name: m.lheWeightNames)
		os << name << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KElectronMetadata &m)
{
	for (std::vector<std::string>::const_iterator it = m.idNames.begin(); it != m.idNames.end(); ++it)
		os << "electron IDs: " << *it << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KJetMetadata &m)
{
	for (std::vector<std::string>::const_iterator it = m.tagNames.begin(); it != m.tagNames.end(); ++it)
		os << "jet tags (float): " << *it << std::endl;
	for (std::vector<std::string>::const_iterator it = m.idNames.begin(); it != m.idNames.end(); ++it)
		os << "jet IDs (binary): " << *it << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KTriggerObjectMetadata &m)
{
	os << "Trigger menu: '" << m.menu << "'";
	if (m.toFilter.size() > 0)
		os << " filters:" << std::endl;
	for (size_t i=0; i < m.toFilter.size(); ++i)
		os << "Trigger object filter (n): " << m.toFilter[i] << " (" << m.nFiltersPerHLT[i] << ")" << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KFilterMetadata &m)
{
	for (std::vector<std::string>::const_iterator it = m.filternames.begin(); it != m.filternames.end(); ++it)
		os << "filter names: " << *it << std::endl;
	return os;
}

std::ostream &operator<<(std::ostream &os, const KGenEventInfo &i)
{
	os << static_cast<const KEventInfo>(i) << std::endl;
	os << "\tweight=" << i.weight << " bin=" << i.binValue << " alphaQCD=" << i.alphaQCD << std::endl;
	os << "\tx1=" << i.x1 << " x2=" << i.x2 << " qScale=" << i.qScale << std::endl;
	os << "\tnPU=(" << int(i.nPUm2) << "--, " << int(i.nPUm1) << "-, ";
	os << int(i.nPU) << ", " << int(i.nPUp1) << "+, " << int(i.nPUp2) << "++) nPUMean=" << i.nPUMean;
	return os;
}

std::ostream &displayHLT(std::ostream &os, const KLumiInfo &metaLumi, const KEventInfo &metaEvent)
{
	for (size_t hltIdx = 0; hltIdx < metaLumi.hltNames.size(); ++hltIdx)
		if (metaEvent.bitsHLT[hltIdx])
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

#ifndef KDATAFORMAT_H
#define KDATAFORMAT_H

#include "KBasic.h"
#include "KElectron.h"
#include "KInfo.h"
#include "KJetMET.h"
#include "KLepton.h"
#include "KMuon.h"
#include "KParticle.h"
#include "KRoot.h"
#include "KTau.h"
#include "KTrack.h"

template<typename T>
struct TypeName;

#define REGISTER_NAME_OF_TYPE(X,Y)     \
	template<> struct TypeName<X>      \
	{                                  \
		static const char *name()      \
		{                              \
			return (#X);               \
		}                              \
		static const char *long_name() \
		{                              \
			return (#Y);               \
		}                              \
	}                                  \

REGISTER_NAME_OF_TYPE(KBasicJet,KBasicJet);
REGISTER_NAME_OF_TYPE(KBasicJets,std::vector<KBasicJet>);
REGISTER_NAME_OF_TYPE(KBasicMET,KBasicMET);
REGISTER_NAME_OF_TYPE(KBasicTau,KBasicTau);
REGISTER_NAME_OF_TYPE(KBasicTaus,std::vector<KBasicTau>);
REGISTER_NAME_OF_TYPE(KBeamSpot,KBeamSpot);
REGISTER_NAME_OF_TYPE(KBeamSpots,std::vector<KBeamSpot>);
REGISTER_NAME_OF_TYPE(KCaloJet,KCaloJet);
REGISTER_NAME_OF_TYPE(KCaloJets,std::vector<KCaloJet>);
REGISTER_NAME_OF_TYPE(KElectron,KElectron);
REGISTER_NAME_OF_TYPE(KElectrons,std::vector<KElectron>);
REGISTER_NAME_OF_TYPE(KFilterSummary,KFilterSummary);
REGISTER_NAME_OF_TYPE(KGenParticle,KGenParticle);
REGISTER_NAME_OF_TYPE(KGenParticles,std::vector<KGenParticle>);
REGISTER_NAME_OF_TYPE(KGenPhoton,KGenPhoton);
REGISTER_NAME_OF_TYPE(KGenPhotons,std::vector<KGenPhoton>);
REGISTER_NAME_OF_TYPE(KGenTau,KGenTau);
REGISTER_NAME_OF_TYPE(KGenTaus,std::vector<KGenTau>);
REGISTER_NAME_OF_TYPE(KHCALNoiseSummary,KHCALNoiseSummary);
REGISTER_NAME_OF_TYPE(KHit,KHit);
REGISTER_NAME_OF_TYPE(KHits,std::vector<KHit>);
REGISTER_NAME_OF_TYPE(KJet,KJet);
REGISTER_NAME_OF_TYPE(KJets,std::vector<KJet>);
REGISTER_NAME_OF_TYPE(KPileupDensity,KPileupDensity);
REGISTER_NAME_OF_TYPE(KL1Muon,KL1Muon);
REGISTER_NAME_OF_TYPE(KL1Muons,std::vector<KL1Muon>);
REGISTER_NAME_OF_TYPE(KLV,KLV);
REGISTER_NAME_OF_TYPE(KLVs,std::vector<KLV>);
REGISTER_NAME_OF_TYPE(KLepton,KLepton);
REGISTER_NAME_OF_TYPE(KLeptons,std::vector<KLepton>);
REGISTER_NAME_OF_TYPE(KMET,KMET);
REGISTER_NAME_OF_TYPE(KMuon,KMuon);
REGISTER_NAME_OF_TYPE(KMuons,std::vector<KMuon>);
REGISTER_NAME_OF_TYPE(KMuonTriggerCandidate,KMuonTriggerCandidate);
REGISTER_NAME_OF_TYPE(KMuonTriggerCandidates,std::vector<KMuonTriggerCandidate>);
REGISTER_NAME_OF_TYPE(KParticle,KParticle);
REGISTER_NAME_OF_TYPE(KParticles,std::vector<KParticle>);
REGISTER_NAME_OF_TYPE(KPFCandidate,KPFCandidate);
REGISTER_NAME_OF_TYPE(KPFCandidates,std::vector<KPFCandidate>);
REGISTER_NAME_OF_TYPE(KTau,KTau);
REGISTER_NAME_OF_TYPE(KTaus,std::vector<KTau>);
REGISTER_NAME_OF_TYPE(KTrack,KTrack);
REGISTER_NAME_OF_TYPE(KTracks,std::vector<KTrack>);
REGISTER_NAME_OF_TYPE(KTrackSummary,KTrackSummary);
REGISTER_NAME_OF_TYPE(KTriggerObjects,KTriggerObjects);
REGISTER_NAME_OF_TYPE(KVertex,KVertex);
REGISTER_NAME_OF_TYPE(KVertices,std::vector<KVertex>);
REGISTER_NAME_OF_TYPE(KVertexSummary,KVertexSummary);
REGISTER_NAME_OF_TYPE(KTaupairVerticesMap,KTaupairVerticesMap);
REGISTER_NAME_OF_TYPE(KTaupairVerticesMaps,std::vector<KTaupairVerticesMap>);
REGISTER_NAME_OF_TYPE(KElectronMetadata,KElectronMetadata);
REGISTER_NAME_OF_TYPE(KFilterMetadata,KFilterMetadata);
REGISTER_NAME_OF_TYPE(KJetMetadata,KJetMetadata);
REGISTER_NAME_OF_TYPE(KMuonMetadata,KMuonMetadata);
REGISTER_NAME_OF_TYPE(KTauMetadata,KTauMetadata);
REGISTER_NAME_OF_TYPE(KTriggerObjectMetadata,KTriggerObjectMetadata);
REGISTER_NAME_OF_TYPE(KProvenance,KProvenance);
REGISTER_NAME_OF_TYPE(KLumiInfo,KLumiInfo);
REGISTER_NAME_OF_TYPE(KGenLumiInfo,KGenLumiInfo);
REGISTER_NAME_OF_TYPE(KDataLumiInfo,KDataLumiInfo);
REGISTER_NAME_OF_TYPE(KEventInfo,KEventInfo);
REGISTER_NAME_OF_TYPE(KGenEventInfo,KGenEventInfo);

#endif

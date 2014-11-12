#ifndef KDATAFORMAT_H
#define KDATAFORMAT_H

#include "KBasic.h"
#include "KElectron.h"
#include "KJetMET.h"
#include "KLorentzVector.h"
#include "KMetadata.h"
#include "KMuon.h"
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

REGISTER_NAME_OF_TYPE(KDataBeamSpot,KDataBeamSpot);
REGISTER_NAME_OF_TYPE(KDataBeamSpots,std::vector<KDataBeamSpot>);
REGISTER_NAME_OF_TYPE(KDataCaloTau,KDataCaloTau);
REGISTER_NAME_OF_TYPE(KDataCaloTaus,std::vector<KDataCaloTau>);
REGISTER_NAME_OF_TYPE(KDataGenTau,KDataGenTau);
REGISTER_NAME_OF_TYPE(KDataGenTaus,std::vector<KDataGenTau>);
REGISTER_NAME_OF_TYPE(KDataHit,KDataHit);
REGISTER_NAME_OF_TYPE(KDataHits,std::vector<KDataHit>);
REGISTER_NAME_OF_TYPE(KDataJet,KDataJet);
REGISTER_NAME_OF_TYPE(KDataJets,std::vector<KDataJet>);
REGISTER_NAME_OF_TYPE(KDataLV,KDataLV);
REGISTER_NAME_OF_TYPE(KDataLVs,std::vector<KDataLV>);
REGISTER_NAME_OF_TYPE(KLepton,KLepton);
REGISTER_NAME_OF_TYPE(KLeptons,std::vector<KLepton>);
REGISTER_NAME_OF_TYPE(KDataMET,KDataMET);
REGISTER_NAME_OF_TYPE(KDataMuon,KDataMuon);
REGISTER_NAME_OF_TYPE(KDataMuons,std::vector<KDataMuon>);
REGISTER_NAME_OF_TYPE(KDataElectron,KDataElectron);
REGISTER_NAME_OF_TYPE(KDataElectrons,std::vector<KDataElectron>);
REGISTER_NAME_OF_TYPE(KDataPFJet,KDataPFJet);
REGISTER_NAME_OF_TYPE(KDataPFJets,std::vector<KDataPFJet>);
REGISTER_NAME_OF_TYPE(KDataPFMET,KDataPFMET);
REGISTER_NAME_OF_TYPE(KDataPFTaggedJet,KDataPFTaggedJet);
REGISTER_NAME_OF_TYPE(KDataPFTaggedJets,std::vector<KDataPFTaggedJet>);
REGISTER_NAME_OF_TYPE(KDataPFTau,KDataPFTau);
REGISTER_NAME_OF_TYPE(KDataPFTaus,std::vector<KDataPFTau>);
REGISTER_NAME_OF_TYPE(KDataTau,KDataTau);
REGISTER_NAME_OF_TYPE(KDataTaus,std::vector<KDataTau>);
REGISTER_NAME_OF_TYPE(KDataTrack,KDataTrack);
REGISTER_NAME_OF_TYPE(KDataTracks,std::vector<KDataTrack>);
REGISTER_NAME_OF_TYPE(KDataVertex,KDataVertex);
REGISTER_NAME_OF_TYPE(KDataVertices,std::vector<KDataVertex>);
REGISTER_NAME_OF_TYPE(KFilterSummary,KFilterSummary);
REGISTER_NAME_OF_TYPE(KGenParticle,KGenParticle);
REGISTER_NAME_OF_TYPE(KGenParticles,std::vector<KGenParticle>);
REGISTER_NAME_OF_TYPE(KGenPhoton,KGenPhoton);
REGISTER_NAME_OF_TYPE(KGenPhotons,std::vector<KGenPhoton>);
REGISTER_NAME_OF_TYPE(KHCALNoiseSummary,KHCALNoiseSummary);
REGISTER_NAME_OF_TYPE(KJetArea,KJetArea);
REGISTER_NAME_OF_TYPE(KL1Muon,KL1Muon);
REGISTER_NAME_OF_TYPE(KL1Muons,std::vector<KL1Muon>);
REGISTER_NAME_OF_TYPE(KLV,KLV);
REGISTER_NAME_OF_TYPE(KLVs,std::vector<KLV>);
REGISTER_NAME_OF_TYPE(KMuonTriggerCandidate,KMuonTriggerCandidate);
REGISTER_NAME_OF_TYPE(KMuonTriggerCandidates,std::vector<KMuonTriggerCandidate>);
REGISTER_NAME_OF_TYPE(KPFCandidate,KPFCandidate);
REGISTER_NAME_OF_TYPE(KPFCandidates,std::vector<KPFCandidate>);
REGISTER_NAME_OF_TYPE(KTrackSummary,KTrackSummary);
REGISTER_NAME_OF_TYPE(KTriggerObjects,KTriggerObjects);
REGISTER_NAME_OF_TYPE(KVertexSummary,KVertexSummary);
REGISTER_NAME_OF_TYPE(KTriggerInfos,KTriggerInfos);
REGISTER_NAME_OF_TYPE(KFilterMetadata,KFilterMetadata);
REGISTER_NAME_OF_TYPE(KTaggerMetadata,KTaggerMetadata);
REGISTER_NAME_OF_TYPE(KMuonMetadata,KMuonMetadata);
REGISTER_NAME_OF_TYPE(KTauDiscriminatorMetadata,KTauDiscriminatorMetadata);
REGISTER_NAME_OF_TYPE(KUnbiasedDiTauPV,KUnbiasedDiTauPV);
REGISTER_NAME_OF_TYPE(KUnbiasedDiTauPVs,std::vector<KUnbiasedDiTauPV>);
REGISTER_NAME_OF_TYPE(KProvenance,KProvenance);
REGISTER_NAME_OF_TYPE(KLumiMetadata,KLumiMetadata);
REGISTER_NAME_OF_TYPE(KGenLumiMetadata,KGenLumiMetadata);
REGISTER_NAME_OF_TYPE(KDataLumiMetadata,KDataLumiMetadata);
REGISTER_NAME_OF_TYPE(KEventMetadata,KEventMetadata);
REGISTER_NAME_OF_TYPE(KGenEventMetadata,KGenEventMetadata);

#endif

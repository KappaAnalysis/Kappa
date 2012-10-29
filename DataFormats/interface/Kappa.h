#ifndef KDATAFORMAT_H
#define KDATAFORMAT_H

#include "KBasic.h"
#include "KJetMET.h"
#include "KLorentzVector.h"
#include "KMetadata.h"
#include "KMuon.h"
#include "KTau.h"
#include "KTrack.h"

template<typename T>
struct TypeName;

#define REGISTER_NAME_OF_TYPE(X)  \
	template<> struct TypeName<X> \
	{                             \
		static const char *name() \
		{                         \
			return (#X);          \
		}                         \
	}                             \

REGISTER_NAME_OF_TYPE(KDataLV);
REGISTER_NAME_OF_TYPE(KDataLVs);
REGISTER_NAME_OF_TYPE(KLV);
REGISTER_NAME_OF_TYPE(KLVs);
REGISTER_NAME_OF_TYPE(KDataMET);
REGISTER_NAME_OF_TYPE(KDataPFMET);
REGISTER_NAME_OF_TYPE(KDataJet);
REGISTER_NAME_OF_TYPE(KDataJets);
REGISTER_NAME_OF_TYPE(KDataPFJet);
REGISTER_NAME_OF_TYPE(KDataPFJets);
REGISTER_NAME_OF_TYPE(KDataTrack);
REGISTER_NAME_OF_TYPE(KDataTracks);
REGISTER_NAME_OF_TYPE(KTrackSummary);
REGISTER_NAME_OF_TYPE(KDataVertex);
REGISTER_NAME_OF_TYPE(KDataVertices);
REGISTER_NAME_OF_TYPE(KVertexSummary);
REGISTER_NAME_OF_TYPE(KDataBeamSpot);
REGISTER_NAME_OF_TYPE(KDataBeamSpots);
REGISTER_NAME_OF_TYPE(KGenParticle);
REGISTER_NAME_OF_TYPE(KGenParticles);
REGISTER_NAME_OF_TYPE(KDataMuon);
REGISTER_NAME_OF_TYPE(KDataMuons);
REGISTER_NAME_OF_TYPE(KDataTau);
REGISTER_NAME_OF_TYPE(KDataTaus);
REGISTER_NAME_OF_TYPE(KDataCaloTau);
REGISTER_NAME_OF_TYPE(KDataCaloTaus);
REGISTER_NAME_OF_TYPE(KDataPFTau);
REGISTER_NAME_OF_TYPE(KDataPFTaus);
REGISTER_NAME_OF_TYPE(KDataGenTau);
REGISTER_NAME_OF_TYPE(KDataGenTaus);
REGISTER_NAME_OF_TYPE(KDataHit);
REGISTER_NAME_OF_TYPE(KDataHits);
REGISTER_NAME_OF_TYPE(KL1Muon);
REGISTER_NAME_OF_TYPE(KL1Muons);
REGISTER_NAME_OF_TYPE(KPFCandidate);
REGISTER_NAME_OF_TYPE(KPFCandidates);
REGISTER_NAME_OF_TYPE(KGenPhoton);
REGISTER_NAME_OF_TYPE(KGenPhotons);
REGISTER_NAME_OF_TYPE(KJetArea);
REGISTER_NAME_OF_TYPE(KHCALNoiseSummary);
REGISTER_NAME_OF_TYPE(KTriggerInfos);
REGISTER_NAME_OF_TYPE(KTriggerObjects);
REGISTER_NAME_OF_TYPE(KMuonTriggerCandidate);
REGISTER_NAME_OF_TYPE(KMuonTriggerCandidates);
REGISTER_NAME_OF_TYPE(KProvenance);
REGISTER_NAME_OF_TYPE(KLumiMetadata);
REGISTER_NAME_OF_TYPE(KGenLumiMetadata);
REGISTER_NAME_OF_TYPE(KDataLumiMetadata);
REGISTER_NAME_OF_TYPE(KEventMetadata);
REGISTER_NAME_OF_TYPE(KGenEventMetadata);

#endif

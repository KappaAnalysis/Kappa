#ifndef KDATAFORMAT_CLASSES_H
#define KDATAFORMAT_CLASSES_H

#define G__DICTIONARY
#include "../interface/KBasic.h"
#include "../interface/KElectron.h"
#include "../interface/KJetMET.h"
#include "../interface/KLorentzVector.h"
#include "../interface/KMetadata.h"
#include "../interface/KMuon.h"
#include "../interface/KTau.h"
#include "../interface/KTrack.h"

namespace
{
	struct dictionary
	{
		RMFLV_Store dict_RMFLV_Store;
		RMFLV dict_RMFLV;

		RMDLV_Store dict_RMDLV_Store;
		RMDLV dict_RMDLV;

		KBasicJet dict_KBasicJet;
		KBasicJets dict_KBasicJets;
		KBasicMET dict_KBasicMET;
		KBasicTau dict_KBasicTau;
		KBasicTaus dict_KBasicTaus;
		KBeamSpot dict_KBeamSpot;
		KBeamSpots dict_KBeamSpots;
		KCaloJet dict_KCaloJet;
		KCaloJets dict_KCaloJets;
		KCaloTau dict_KCaloTau;
		KCaloTaus dict_KCaloTaus;
		KElectron dict_KElectron;
		KElectrons dict_KElectrons;
		KFilterSummary dict_KFilterSummary;
		KGenParticle dict_KGenParticle;
		KGenParticles dict_KGenParticles;
		KGenPhoton dict_KGenPhoton;
		KGenPhotons dict_KGenPhotons;
		KGenTau dict_KGenTau;
		KGenTaus dict_KGenTaus;
		KHCALNoiseSummary dict_KHCALNoiseSummary;
		KHit dict_KHit;
		KHits dict_KHits;
		KJet dict_KJet;
		KJets dict_KJets;
		KPileupDensity dict_KPileupDensity;
		KL1Muon dict_KL1Muon;
		KL1Muons dict_KL1Muons;
		KLV dict_KLV;
		KLVs dict_KLVs;
		KLepton dict_KLepton;
		KLeptons dict_KLeptons;
		KMET dict_KMET;
		KMuon dict_KMuon;
		KMuons dict_KMuons;
		KMuonTriggerCandidate dict_KMuonTriggerCandidate;
		KMuonTriggerCandidates dict_KMuonTriggerCandidates;
		KPFCandidate dict_KPFCandidate;
		KPFCandidates dict_KPFCandidates;
		KTau dict_KTau;
		KTaus dict_KTaus;
		KTrack dict_KTrack;
		KTracks dict_KTracks;
		KTrackSummary dict_KTrackSummary;
		KTriggerObjects dict_KTriggerObjects;
		KVertex dict_KVertex;
		KVertices dict_KVertices;
		KVertexSummary dict_KVertexSummary;
		KTaupairVerticesMap dict_KTaupairVerticesMap;
		KTaupairVerticesMaps dict_KTaupairVerticesMaps;

		KElectronIdMetadata dict_KElectronIdMetadata;
		KFilterMetadata dict_KFilterMetadata;
		KTaggerMetadata dict_KTaggerMetadata;
		KMuonMetadata dict_KMuonMetadata;
		KTauDiscriminatorMetadata dict_KTauDiscriminatorMetadata;
		KTriggerInfos dict_KTriggerInfos;

		KProvenance dict_KProvenance;

		KLumiMetadata dict_KLumiMetadata;
		KGenLumiMetadata dict_KGenLumiMetadata;
		KDataLumiMetadata dict_KDataLumiMetadata;

		KEventMetadata dict_KEventMetadata;
		KGenEventMetadata dict_KGenEventMetadata;

	};
}

#endif

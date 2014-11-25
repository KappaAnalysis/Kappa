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

		KDataBeamSpot dict_KDataBeamSpot;
		KDataBeamSpots dict_KDataBeamSpots;
		KDataCaloTau dict_KDataCaloTau;
		KDataCaloTaus dict_KDataCaloTaus;
		KDataGenTau dict_KDataGenTau;
		KDataGenTaus dict_KDataGenTaus;
		KDataHit dict_KDataHit;
		KDataHits dict_KDataHits;
		KDataJet dict_KDataJet;
		KDataJets dict_KDataJets;
		KLV dict_KLV;
		KLVs dict_KLVs;
		KLepton dict_KLepton;
		KLeptons dict_KLeptons;
		KDataMET dict_KDataMET;
		KDataMuon dict_KDataMuon;
		KDataMuons dict_KDataMuons;
		KDataElectron dict_KDataElectron;
		KDataElectrons dict_KDataElectrons;
		KDataPFJet dict_KDataPFJet;
		KDataPFJets dict_KDataPFJets;
		KDataPFMET dict_KDataPFMET;
		KDataPFTaggedJet dict_KDataPFTaggedJet;
		KDataPFTaggedJets dict_KDataPFTaggedJets;
		KDataPFTau dict_KDataPFTau;
		KDataPFTaus dict_KDataPFTaus;
		KDataTau dict_KDataTau;
		KDataTaus dict_KDataTaus;
		KDataTrack dict_KDataTrack;
		KDataTracks dict_KDataTracks;
		KDataVertex dict_KDataVertex;
		KDataVertices dict_KDataVertices;
		KFilterSummary dict_KFilterSummary;
		KGenParticle dict_KGenParticle;
		KGenParticles dict_KGenParticles;
		KGenPhoton dict_KGenPhoton;
		KGenPhotons dict_KGenPhotons;
		KHCALNoiseSummary dict_KHCALNoiseSummary;
		KJetArea dict_KJetArea;
		KL1Muon dict_KL1Muon;
		KL1Muons dict_KL1Muons;
		KMuonTriggerCandidate dict_KMuonTriggerCandidate;
		KMuonTriggerCandidates dict_KMuonTriggerCandidates;
		KPFCandidate dict_KPFCandidate;
		KPFCandidates dict_KPFCandidates;
		KTrackSummary dict_KTrackSummary;
		KTriggerObjects dict_KTriggerObjects;
		KVertexSummary dict_KVertexSummary;
		KTaupairVerticesMap dict_KTaupairVerticesMap;
		KTaupairVerticesMaps dict_KTaupairVerticesMaps;

		KElectronIdMetadata dict_KElectronIdMetadata;
		KFilterMetadata dict_KFilterMetadata;
		KTaggerMetadata dict_KTaggerMetadata;
		KMuonMetadata dict_KMuonMetadata;
		KUnbiasedDiTauPV dict_KUnbiasedDiTauPV;
		KUnbiasedDiTauPVs dict_KUnbiasedDiTauPVs;
		KTauDiscriminatorMetadata dict_KTauDiscriminatorMetadata;
		KTriggerInfo dict_KTriggerInfo;

		KProvenance dict_KProvenance;

		KLumiMetadata dict_KLumiMetadata;
		KGenLumiMetadata dict_KGenLumiMetadata;
		KDataLumiMetadata dict_KDataLumiMetadata;

		KEventMetadata dict_KEventMetadata;
		KGenEventMetadata dict_KGenEventMetadata;

	};
}

#endif

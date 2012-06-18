#ifndef KDATAFORMAT_CLASSES_H
#define KDATAFORMAT_CLASSES_H

#define G__DICTIONARY
#include "../interface/KBasic.h"
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

		RMDataLV_Store dict_RMDataLV_Store;
		RMDataLV dict_RMDataLV;

		RMLV_Store dict_RMLV_Store;
		RMLV dict_RMLV;



		KDataLV dict_KDataLV;
		KDataLVs dict_KDataLVs;

		KLV dict_KLV;
		KLVs dict_KLVs;

		KDataMET dict_KDataMET;
		KDataPFMET dict_KDataPFMET;

		KDataJet dict_KDataJet;
		KDataJets dict_KDataJets;

		KDataPFJet dict_KDataPFJet;
		KDataPFJets dict_KDataPFJets;

		KDataTrack dict_KDataTrack;
		KDataTracks dict_KDataTracks;

		KTrackSummary dict_KTrackSummary;

		KDataVertex dict_KDataVertex;
		KDataVertices dict_KDataVertices;

		KVertexSummary dict_KVertexSummary;

		KDataBeamSpot dict_KDataBeamSpot;
		KDataBeamSpots dict_KDataBeamSpots;

		KParton dict_KParton;
		KPartons dict_KPartons;

		KDataMuon dict_KDataMuon;
		KDataMuons dict_KDataMuons;

		KDataTau dict_KDataTau;
		KDataTaus dict_KDataTaus;

		KDataCaloTau dict_KDataCaloTau;
		KDataCaloTaus dict_KDataCaloTaus;

		KDataPFTau dict_KDataPFTau;
		KDataPFTaus dict_KDataPFTaus;

		KDataGenTau dict_KDataGenTau;
		KDataGenTaus dict_KDataGenTaus;

		KDataHit dict_KDataHit;
		KDataHits dict_KDataHits;

		KL1Muon dict_KL1Muon;
		KL1Muons dict_KL1Muons;

		KPFCandidate dict_KPFCandidate;
		KPFCandidates dict_KPFCandidates;

		KGenPhoton dict_KGenPhoton;
		KGenPhotons dict_KGenPhotons;

		KJetArea dict_KJetArea;

		KTriggerInfos dict_KTriggerInfos;
		KTriggerObjects dict_KTriggerObjects;

		KMuonTriggerCandidate dict_KMuonTriggerCandidate;
		KMuonTriggerCandidates dict_KMuonTriggerCandidates;


		KProvenance dict_KProvenance;

		KLumiMetadata dict_KLumiMetadata;
		KGenLumiMetadata dict_KGenLumiMetadata;
		KDataLumiMetadata dict_KDataLumiMetadata;

		KEventMetadata dict_KEventMetadata;
		KGenEventMetadata dict_KGenEventMetadata;

	};
}

#endif

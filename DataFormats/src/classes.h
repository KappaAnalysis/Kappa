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

		RMDataLV_Store dict_rmdatalv_store;
		RMDataLV dict_rmdatalv;

		RMLV_Store dict_rmlv_store;
		RMLV dict_rmlv;



		KDataLV dict_kdatalv;
		KDataLVs dict_kdatalvs;

		KLV dict_klv;
		KLVs dict_klvs;

		KDataMET dict_kdatamet;
		KDataPFMET dict_kdatapfmet;

		KDataJet dict_kdatajet;
		KDataJets dict_kdatajets;

		KDataPFJet dict_kdatapfjet;
		KDataPFJets dict_kdatapfjets;

		KDataTrack dict_kdatatrack;
		KDataTracks dict_kdatatracks;

		KTrackSummary dict_ktracksummary;

		KDataVertex dict_kdatavertex;
		KDataVertices dict_kdatavertices;

		KVertexSummary dict_kvertexsummary;

		KDataBeamSpot dict_kdatabeamspot;
		KDataBeamSpots dict_kdatabeamspots;

		KParton dict_kparton;
		KPartons dict_kpartons;

		KDataMuon dict_kdatamuon;
		KDataMuons dict_kdatamuons;

		KDataTau dict_kdatatau;
		KDataTaus dict_kdatataus;

		KDataCaloTau dict_kdatacalotau;
		KDataCaloTaus dict_kdatacalotaus;

		KDataPFTau dict_kdatapftau;
		KDataPFTaus dict_kdatapftaus;

		KDataGenTau dict_kdatagentau;
		KDataGenTaus dict_kdatagentaus;

		KDataHit dict_kdatahit;
		KDataHits dict_kdatahits;

		KL1Muon dict_kl1muon;
		KL1Muons dict_kl1muons;

		KPFCandidate dict_kpfcandidate;
		KPFCandidates dict_kpfcandidates;

		KGenPhoton dict_genphoton;
		KGenPhotons dict_genphotons;

		KJetArea dict_kjetarea;


		KProvenance dict_kprovenance;

		KLumiMetadata dict_klumimetadata;
		KGenLumiMetadata dict_kgenlumimetadata;
		KDataLumiMetadata dict_kdatalumimetadata;

		KEventMetadata dict_keventmetadata;
		KGenEventMetadata dict_kgeneventmetadata;

	};
}

#endif

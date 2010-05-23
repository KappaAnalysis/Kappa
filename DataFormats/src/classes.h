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

		RMDataLV_Store kappa_rmdatalv_store;
		RMDataLV kappa_rmdatalv;

		RMLV_Store kappa_rmlv_store;
		RMLV kappa_rmlv;



		KDataLV kappa_datalv;
		KDataLVs kappa_datalvs;

		KLV kappa_lv;
		KLVs kappa_lvs;

		KDataMET kappa_datamet;
		KDataPFMET kappa_datapfmet;

		KDataJet kappa_datajet;
		KDataJets kappa_datajets;

		KDataPFJet kappa_datapfjet;
		KDataPFJets kappa_datapfjets;

		KDataTrack kappa_datatrack;
		KDataTracks kappa_datatracks;

		KTrackSummary kappa_tracksummary;

		KDataVertex kappa_datavertex;
		KDataVertices kappa_datavertices;

		KParton kappa_parton;
		KPartons kappa_partons;

		KDataMuon kappa_datamuon;
		KDataMuons kappa_datamuons;

		KDataTau kappa_datatau;
		KDataTaus kappa_datataus;

		KDataCaloTau kappa_datacalotau;
		KDataCaloTaus kappa_datacalotaus;

		KDataPFTau kappa_datapftau;
		KDataPFTaus kappa_datapftaus;

		KDataGenTau kappa_datagentau;
		KDataGenTaus kappa_datagentaus;


		KProvenance kappa_provenance;

		KLumiMetadata kappa_lumimetadata;
		KGenLumiMetadata kappa_genlumimetadata;

		KEventMetadata kappa_eventmetadata;
		KGenEventMetadata kappa_geneventmetadata;

	};
}

#endif

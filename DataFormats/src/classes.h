#ifndef KDATAFORMAT_H
#define KDATAFORMAT_H

#define G__DICTIONARY
#include "../interface/KTau.h"
#include "../interface/KMetadata.h"
#include "../interface/KLorentzVector.h"
#include "../interface/KBasic.h"
#include "../interface/KMuon.h"

namespace
{
	struct dictionary
	{

		RMDataLV_Store kappa_mdatalv_store;
		RMDataLV kappa_mdatalv;

		RMLV_Store kappa_mlv_store;
		RMLV kappa_mlv;



		KDataLV kappa_datalv;
		KDataLVs kappa_datalvs;

		KLV kappa_lv;
		KLVs kappa_lvs;

		KDataMET kappa_datamet;

		KDataJet kappa_datajet;
		KDataJets kappa_datajets;

		KDataPFJet kappa_datapfjet;
		KDataPFJets kappa_datapfjets;

		KDataTrack kappa_datatrack;
		KDataTracks kappa_datatracks;

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
